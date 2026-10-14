"""Bounded SPF and DKIM checks for messages received by the SMTP listener."""

import asyncio
import email
from email import policy
import logging

import dkim
import dns.exception
import dns.resolver
import spf

logger = logging.getLogger(__name__)

SPF_QUERY_TIMEOUT_SECONDS = 8
DKIM_QUERY_TIMEOUT_SECONDS = 5
MAX_DKIM_SIGNATURES = 5


def _check_spf(peer_ip: str | None, mail_from: str, helo_domain: str) -> str:
    if not peer_ip:
        return "unverified"
    try:
        result, _explanation = spf.check2(
            i=peer_ip,
            s=mail_from,
            h=helo_domain or "unknown",
            querytime=SPF_QUERY_TIMEOUT_SECONDS,
        )
        return result if result in {
            "pass", "fail", "softfail", "neutral", "none", "permerror", "temperror"
        } else "unverified"
    except Exception:
        logger.exception("SPF evaluation failed unexpectedly")
        return "unverified"


def _check_dkim(raw_message: bytes) -> str:
    message = email.message_from_bytes(raw_message, policy=policy.default)
    signature_count = len(message.get_all("DKIM-Signature", []))
    if signature_count == 0:
        return "none"

    try:
        verifier = dkim.DKIM(raw_message, timeout=DKIM_QUERY_TIMEOUT_SECONDS)
    except dkim.DKIMException:
        return "fail"
    except Exception:
        logger.exception("Could not initialize DKIM verification")
        return "unverified"

    for index in range(min(signature_count, MAX_DKIM_SIGNATURES)):
        try:
            if verifier.verify(idx=index):
                return "pass"
        except dns.exception.Timeout:
            return "temperror"
        except dns.resolver.NoNameservers:
            return "temperror"
        except dkim.DKIMException:
            # A malformed signature or invalid key fails this signature.
            logger.info("DKIM signature %d did not verify", index)
        except Exception:
            logger.exception("Unexpected error during DKIM verification")
            return "unverified"

    # If signatures remain unchecked, a valid signature may be among them.
    return "unverified" if signature_count > MAX_DKIM_SIGNATURES else "fail"


async def evaluate_inbound_authentication(
    raw_message: bytes,
    peer_ip: str | None,
    mail_from: str,
    helo_domain: str,
) -> tuple[str, str]:
    """Evaluate SPF and DKIM away from the asyncio SMTP event loop."""
    spf_result, dkim_result = await asyncio.gather(
        asyncio.to_thread(_check_spf, peer_ip, mail_from, helo_domain),
        asyncio.to_thread(_check_dkim, raw_message),
    )
    return spf_result, dkim_result
