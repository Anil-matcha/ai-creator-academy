"""Bounded SPF and DKIM checks for messages received by the SMTP listener."""

import asyncio
import datetime
import email
from email import policy
from email.utils import getaddresses
import logging
import re
import time

import dkim
import dns.exception
import dns.resolver
import spf
from checkdmarc.dmarc import parse_dmarc_record

logger = logging.getLogger(__name__)

SPF_QUERY_TIMEOUT_SECONDS = 8
DKIM_QUERY_TIMEOUT_SECONDS = 5
MAX_DKIM_SIGNATURES = 5
DMARC_DNS_TIMEOUT_SECONDS = 1.5
DMARC_TOTAL_TIMEOUT_SECONDS = 8
DMARC_RELEVANT_TAGS = {"p", "sp", "np", "psd", "adkim", "aspf"}


def _check_spf(peer_ip: str | None, mail_from: str, helo_domain: str) -> str:
    if not peer_ip or (not mail_from and not helo_domain):
        return "unverified"
    try:
        result, _explanation = spf.check2(
            i=peer_ip,
            s=mail_from,
            h=helo_domain,
            querytime=SPF_QUERY_TIMEOUT_SECONDS,
        )
        return result if result in {
            "pass", "fail", "softfail", "neutral", "none", "permerror", "temperror"
        } else "unverified"
    except Exception:
        logger.exception("SPF evaluation failed unexpectedly")
        return "unverified"


def _check_dkim(raw_message: bytes) -> tuple[str, list[str]]:
    message = email.message_from_bytes(raw_message, policy=policy.default)
    signature_count = len(message.get_all("DKIM-Signature", []))
    if signature_count == 0:
        return "none", []

    try:
        verifier = dkim.DKIM(raw_message, timeout=DKIM_QUERY_TIMEOUT_SECONDS)
    except dkim.DKIMException:
        return "fail", []
    except Exception:
        logger.exception("Could not initialize DKIM verification")
        return "unverified", []

    passing_domains = []
    for index in range(min(signature_count, MAX_DKIM_SIGNATURES)):
        try:
            if verifier.verify(idx=index):
                signing_domain = verifier.signature_fields.get(b"d", b"").decode("ascii", errors="ignore").strip().rstrip(".").lower()
                if signing_domain:
                    passing_domains.append(signing_domain)
        except dns.exception.Timeout:
            return "temperror", passing_domains
        except dns.resolver.NoNameservers:
            return "temperror", passing_domains
        except dkim.DKIMException:
            # A malformed signature or invalid key fails this signature.
            logger.info("DKIM signature %d did not verify", index)
        except Exception:
            logger.exception("Unexpected error during DKIM verification")
            return "unverified", passing_domains

    # If signatures remain unchecked, a valid signature may be among them.
    if passing_domains:
        return "pass", passing_domains
    return ("unverified", []) if signature_count > MAX_DKIM_SIGNATURES else ("fail", [])


def _get_record_tags(record: str, domain: str) -> dict[str, str]:
    """Parse only the DMARC tags used for policy/alignment, without report DNS lookups."""
    relevant_parts = []
    for part in record.split(";")[1:]:
        match = re.fullmatch(r"\s*([A-Za-z]+)\s*=\s*(.*?)\s*", part)
        if match and match.group(1).lower() in DMARC_RELEVANT_TAGS:
            relevant_parts.append(f"{match.group(1)}={match.group(2)}")
    sanitized_record = "v=DMARC1" + (";" + ";".join(relevant_parts) if relevant_parts else "")
    parsed = parse_dmarc_record(sanitized_record, domain, timeout=DMARC_DNS_TIMEOUT_SECONDS, retries=0)
    return {tag: str(value["value"]).lower() for tag, value in parsed["tags"].items()}


class DMARCDNSBudgetExceeded(Exception):
    pass


def _direct_dmarc_record(domain: str, deadline: float) -> tuple[str, dict[str, str]] | None:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise DMARCDNSBudgetExceeded
    lookup_timeout = min(DMARC_DNS_TIMEOUT_SECONDS, remaining)
    resolver = dns.resolver.Resolver()
    resolver.timeout = lookup_timeout
    resolver.lifetime = lookup_timeout
    try:
        answers = resolver.resolve(f"_dmarc.{domain}", "TXT", search=False)
    except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
        return None
    except dns.exception.DNSException:
        raise

    records = []
    for answer in answers:
        chunks = getattr(answer, "strings", None)
        raw_record = b"".join(chunks).decode("utf-8", errors="replace") if chunks else answer.to_text().strip('"')
        if re.match(r"^[vV]\s*=\s*DMARC1(?:\s*;|$)", raw_record):
            records.append(raw_record)
    # RFC 9989 says multiple DMARC records at one name are all discarded.
    if len(records) != 1:
        return None
    try:
        return records[0], _get_record_tags(records[0], domain)
    except Exception:
        logger.info("Ignoring invalid DMARC record at %s", domain)
        return None


def _dmarc_tree(domain: str, deadline: float) -> list[tuple[str, str, dict[str, str]]]:
    """Return DMARC records on a bounded RFC 9989 tree walk for a domain."""
    labels = domain.split(".")
    targets = [domain]
    # The initial full-name query plus at most seven parent queries bounds a
    # maliciously deep From/signing domain to the RFC's eight-query limit.
    first_parent = 1 if len(labels) <= 8 else len(labels) - 7
    targets.extend(".".join(labels[index:]) for index in range(first_parent, len(labels)))
    records: list[tuple[str, str, dict[str, str]]] = []
    for target in targets[:8]:
        found = _direct_dmarc_record(target, deadline)
        if found:
            record, tags = found
            records.append((target, record, tags))
            if tags.get("psd") in {"n", "y"}:
                break
    return records


def _organizational_domain(domain: str, records: list[tuple[str, str, dict[str, str]]]) -> str:
    if not records:
        return domain
    for location, _record, tags in records:
        if tags.get("psd") == "n":
            return location
        if tags.get("psd") == "y":
            domain_labels = domain.split(".")
            psd_labels = location.split(".")
            if len(domain_labels) > len(psd_labels) and domain_labels[-len(psd_labels):] == psd_labels:
                return ".".join(domain_labels[-len(psd_labels) - 1:])
            return domain
    return min((location for location, _record, _tags in records), key=lambda name: len(name.split(".")))


def _check_dmarc(raw_message: bytes, mail_from: str, helo_domain: str, spf_status: str, dkim_status: str, dkim_domains: list[str]) -> str:
    message = email.message_from_bytes(raw_message, policy=policy.default)
    from_headers = message.get_all("From", [])
    addresses = getaddresses([str(value) for value in from_headers])
    if len(from_headers) != 1 or len(addresses) != 1 or "@" not in addresses[0][1]:
        return "unverified"
    try:
        author_domain = _normalize_domain(addresses[0][1].rsplit("@", 1)[1])
    except ValueError:
        return "unverified"
    try:
        deadline = time.monotonic() + DMARC_TOTAL_TIMEOUT_SECONDS
        author_tree = _dmarc_tree(author_domain, deadline)
        exact_record = next((item for item in author_tree if item[0] == author_domain), None)
        if exact_record:
            policy_tags = exact_record[2]
        elif author_tree:
            policy_domain = _organizational_domain(author_domain, author_tree)
            policy_record = next((item for item in author_tree if item[0] == policy_domain), None)
            if not policy_record:
                # A PSD record applies when no record exists at its child org domain.
                policy_record = next((item for item in author_tree if item[2].get("psd") == "y"), None)
            if not policy_record:
                return "none"
            policy_tags = policy_record[2]
        else:
            return "none"

        try:
            spf_domain = _normalize_domain(mail_from.rsplit("@", 1)[-1] if mail_from else helo_domain)
        except ValueError:
            spf_domain = ""
        spf_align_mode = policy_tags.get("aspf", "r")
        dkim_align_mode = policy_tags.get("adkim", "r")
        candidate_domains: list[tuple[str, str]] = []
        if spf_status == "pass" and spf_domain:
            candidate_domains.append(("spf", spf_domain))
        if dkim_status == "pass":
            candidate_domains.extend(("dkim", domain) for domain in dkim_domains)

        if not candidate_domains:
            if spf_status in {"unverified", "temperror"} or dkim_status in {"unverified", "temperror"}:
                return "unverified"
            return "fail"

        trees: dict[str, list[tuple[str, str, dict[str, str]]]] = {author_domain: author_tree}
        author_org = _organizational_domain(author_domain, author_tree)
        uncertain_alignment = False
        for mechanism, identity_domain in candidate_domains:
            try:
                identity_domain = _normalize_domain(identity_domain)
            except ValueError:
                uncertain_alignment = True
                continue
            if identity_domain == author_domain:
                return "pass"
            alignment_mode = spf_align_mode if mechanism == "spf" else dkim_align_mode
            if alignment_mode == "s":
                continue
            if identity_domain not in trees:
                trees[identity_domain] = _dmarc_tree(identity_domain, deadline)
            identity_org = _organizational_domain(identity_domain, trees[identity_domain])
            if identity_org == author_org:
                return "pass"
            if not trees[identity_domain] or not author_tree:
                uncertain_alignment = True

        if uncertain_alignment:
            return "unverified"
        if spf_status in {"unverified", "temperror"} or dkim_status in {"unverified", "temperror"}:
            return "unverified"
        return "fail"
    except (dns.exception.DNSException, DMARCDNSBudgetExceeded):
        logger.info("DMARC DNS lookup was inconclusive for %s", author_domain)
        return "temperror"
    except Exception:
        logger.exception("DMARC evaluation failed unexpectedly")
        return "unverified"


def _normalize_domain(domain: str) -> str:
    normalized = domain.strip().rstrip(".").encode("idna").decode("ascii").lower()
    labels = normalized.split(".")
    if not normalized or len(normalized) > 253 or any(
        not label or len(label) > 63 or not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]*[a-z0-9])?", label)
        for label in labels
    ):
        raise ValueError("Invalid domain name")
    return normalized


async def evaluate_inbound_authentication(
    raw_message: bytes,
    peer_ip: str | None,
    mail_from: str,
    helo_domain: str,
) -> tuple[str, str, str, dict]:
    """Evaluate SPF, DKIM, and DMARC away from the asyncio SMTP event loop."""
    spf_result, dkim_result = await asyncio.gather(
        asyncio.to_thread(_check_spf, peer_ip, mail_from, helo_domain),
        asyncio.to_thread(_check_dkim, raw_message),
    )
    dkim_status, dkim_domains = dkim_result
    dmarc_result = await asyncio.to_thread(
        _check_dmarc, raw_message, mail_from, helo_domain, spf_result, dkim_status, dkim_domains
    )
    message = email.message_from_bytes(raw_message, policy=policy.default)
    from_values = [str(value) for value in message.get_all("From", [])]
    evidence = {
        "evaluated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "peer_ip": peer_ip[:64] if peer_ip else None,
        "smtp_mail_from": mail_from[:320],
        "helo_domain": helo_domain[:253],
        "from_header": [value[:512] for value in from_values[:1]],
        "spf": {"status": spf_result, "identity": (mail_from or (f"postmaster@{helo_domain}" if helo_domain else ""))[:320] or None},
        "dkim": {"status": dkim_status, "passing_domains": dkim_domains[:MAX_DKIM_SIGNATURES]},
        "dmarc": {"status": dmarc_result},
    }
    return spf_result, dkim_status, dmarc_result, evidence
