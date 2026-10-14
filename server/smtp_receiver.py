"""
Real-world Inbound SMTP Receiver Daemon for Open Agent Email.
Listens on TCP port 2525 (in dev/local) or port 25 (in production) to receive real SMTP emails
from external mail transfer agents (MTAs) such as Gmail, Outlook, or test scripts.
"""

import asyncio
import email
import hashlib
from email import policy
from email.utils import parseaddr
import logging
import re
import ssl
import sys
import os

# Add server directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import AsyncSessionLocal
from app.models import Agent
from app.services.email_service import EmailService
from app.services.mail_auth import evaluate_inbound_authentication
from sqlalchemy import select, func

logging.basicConfig(level=logging.INFO, format="%(asctime)s [SMTP] %(message)s")
logger = logging.getLogger("smtp_receiver")

PORT = int(os.environ.get("SMTP_PORT", 2525))
HOST = os.environ.get("SMTP_HOST", "127.0.0.1")
MAX_MESSAGE_BYTES = int(os.environ.get("SMTP_MAX_MESSAGE_BYTES", 20 * 1024 * 1024))
MAX_ATTACHMENT_BYTES = int(os.environ.get("SMTP_MAX_ATTACHMENT_BYTES", 10 * 1024 * 1024))
MAX_ATTACHMENTS = int(os.environ.get("SMTP_MAX_ATTACHMENTS", 10))
READ_TIMEOUT_SECONDS = float(os.environ.get("SMTP_READ_TIMEOUT_SECONDS", 60))
DATA_TIMEOUT_SECONDS = float(os.environ.get("SMTP_DATA_TIMEOUT_SECONDS", 300))
MAX_CONNECTIONS = int(os.environ.get("SMTP_MAX_CONNECTIONS", 100))
STREAM_LINE_LIMIT = int(os.environ.get("SMTP_LINE_LIMIT_BYTES", 16 * 1024))
TLS_CERT_FILE = os.environ.get("SMTP_TLS_CERT_FILE", "").strip()
TLS_KEY_FILE = os.environ.get("SMTP_TLS_KEY_FILE", "").strip()
REQUIRE_STARTTLS = os.environ.get("SMTP_REQUIRE_STARTTLS", "false").strip().lower() in {"1", "true", "yes"}
if not 1 <= PORT <= 65535:
    raise ValueError("SMTP_PORT must be between 1 and 65535")
if min(
    READ_TIMEOUT_SECONDS,
    DATA_TIMEOUT_SECONDS,
    MAX_CONNECTIONS,
    STREAM_LINE_LIMIT,
    MAX_MESSAGE_BYTES,
    MAX_ATTACHMENT_BYTES,
    MAX_ATTACHMENTS,
) <= 0:
    raise ValueError("SMTP limits and timeouts must be greater than zero")
if MAX_ATTACHMENT_BYTES > MAX_MESSAGE_BYTES:
    raise ValueError("SMTP_MAX_ATTACHMENT_BYTES cannot exceed SMTP_MAX_MESSAGE_BYTES")
if bool(TLS_CERT_FILE) != bool(TLS_KEY_FILE):
    raise ValueError("Set both SMTP_TLS_CERT_FILE and SMTP_TLS_KEY_FILE to enable STARTTLS")
TLS_CONTEXT = None
if TLS_CERT_FILE and TLS_KEY_FILE:
    TLS_CONTEXT = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    TLS_CONTEXT.load_cert_chain(TLS_CERT_FILE, TLS_KEY_FILE)
CONNECTIONS = asyncio.Semaphore(MAX_CONNECTIONS)

def safe_attachment_name(filename: str) -> str:
    filename = filename.replace("\\", "/").rsplit("/", 1)[-1]
    filename = "".join(ch if ch >= " " and ch not in "\x7f" else "_" for ch in filename)
    return filename[:255] or "attachment"

def safe_content_type(content_type: str) -> str:
    import re
    if re.fullmatch(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+", content_type or ""):
        return content_type
    return "application/octet-stream"


def extract_smtp_path(line: str, command: str) -> str | None:
    """Parse an SMTP reverse/forward path while ignoring ESMTP parameters."""
    match = re.match(rf"^{re.escape(command)}:\s*(<[^>\r\n]*>|[^\s]+)(?:\s+.*)?$", line, re.IGNORECASE)
    if not match:
        return None
    path = match.group(1)
    if path.startswith("<"):
        if not path.endswith(">"):
            return None
        return path[1:-1]
    if any(char in path for char in "<>"):
        return None
    return path

class SmtpSession:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer
        self.mail_from = ""
        self.mail_from_set = False
        self.rcpt_to = []
        self.helo_domain = ""
        self.peer_ip = None
        self.tls_active = False

    async def send_response(self, code: int, message: str):
        self.writer.write(f"{code} {message}\r\n".encode("utf-8"))
        await self.writer.drain()

    async def handle(self):
        peer = self.writer.get_extra_info("peername")
        self.peer_ip = peer[0] if isinstance(peer, tuple) and peer else None
        logger.info(f"Incoming connection from {peer}")
        await self.send_response(220, "open-agent-email SMTP Gateway Ready")

        data_mode = False
        data_buffer = bytearray()
        data_too_large = False
        data_started_at = None

        while True:
            timeout = READ_TIMEOUT_SECONDS
            if data_mode and data_started_at is not None:
                remaining = DATA_TIMEOUT_SECONDS - (asyncio.get_running_loop().time() - data_started_at)
                if remaining <= 0:
                    await self.send_response(421, "Message input timed out")
                    break
                timeout = min(timeout, remaining)
            try:
                line_bytes = await asyncio.wait_for(self.reader.readline(), timeout=timeout)
            except asyncio.TimeoutError:
                try:
                    await self.send_response(421, "SMTP connection timed out")
                except (ConnectionError, OSError):
                    pass
                break
            if not line_bytes:
                break

            if data_mode:
                if line_bytes.strip() == b".":
                    data_mode = False
                    if data_too_large:
                        await self.send_response(552, "Message exceeds configured size limit")
                    else:
                        try:
                            await self.process_email(bytes(data_buffer))
                            await self.send_response(250, "Message accepted for agent delivery")
                        except ValueError as exc:
                            await self.send_response(552, str(exc))
                    data_buffer.clear()
                    data_too_large = False
                    data_started_at = None
                    self.mail_from = ""
                    self.mail_from_set = False
                    self.rcpt_to = []
                else:
                    if len(data_buffer) + len(line_bytes) > MAX_MESSAGE_BYTES:
                        data_too_large = True
                        data_buffer.clear()
                    elif not data_too_large:
                        data_buffer.extend(line_bytes)
                continue

            line = line_bytes.decode("utf-8", errors="ignore").strip()
            if not line:
                continue

            cmd_upper = line.upper()
            command_name = line.split(maxsplit=1)[0].upper()
            if command_name in {"EHLO", "HELO"}:
                helo_parts = line.split(maxsplit=1)
                self.helo_domain = helo_parts[1].strip() if len(helo_parts) > 1 else ""
                self.mail_from = ""
                self.mail_from_set = False
                self.rcpt_to = []
                if command_name == "EHLO":
                    capabilities = ["250-open-agent-email"]
                    if TLS_CONTEXT and not self.tls_active:
                        capabilities.append("250-STARTTLS")
                    capabilities.extend([f"250-SIZE {MAX_MESSAGE_BYTES}", "250-8BITMIME", "250 HELP"])
                    self.writer.write(("\r\n".join(capabilities) + "\r\n").encode("ascii"))
                    await self.writer.drain()
                else:
                    await self.send_response(250, "Hello, pleased to meet you")
            elif cmd_upper.startswith("MAIL FROM:"):
                sender_path = extract_smtp_path(line, "MAIL FROM")
                if REQUIRE_STARTTLS and not self.tls_active:
                    await self.send_response(530, "STARTTLS is required before mail transfer")
                elif sender_path is None:
                    await self.send_response(501, "Invalid reverse path")
                else:
                    self.mail_from = sender_path
                    self.mail_from_set = True
                    self.rcpt_to = []
                    await self.send_response(250, "Sender OK")
            elif cmd_upper.startswith("RCPT TO:"):
                recipient_path = extract_smtp_path(line, "RCPT TO")
                if not self.mail_from_set:
                    await self.send_response(503, "Specify MAIL FROM first")
                elif not recipient_path:
                    await self.send_response(501, "Invalid forward path")
                else:
                    async with AsyncSessionLocal() as db:
                        res = await db.execute(select(Agent).where(func.lower(Agent.email) == recipient_path.lower(), Agent.status == "active"))
                        known_agent = res.scalar_one_or_none()
                    if known_agent:
                        self.rcpt_to.append(known_agent.email)
                        await self.send_response(250, "Recipient OK")
                    else:
                        await self.send_response(550, "No active agent inbox for recipient")
            elif cmd_upper == "DATA":
                if REQUIRE_STARTTLS and not self.tls_active:
                    await self.send_response(530, "STARTTLS is required before mail transfer")
                elif not self.mail_from_set or not self.rcpt_to:
                    await self.send_response(503, "Specify at least one valid recipient before DATA")
                else:
                    data_mode = True
                    data_buffer.clear()
                    data_too_large = False
                    data_started_at = asyncio.get_running_loop().time()
                    await self.send_response(354, "Start mail input; end with <CRLF>.<CRLF>")
            elif cmd_upper == "STARTTLS":
                if not TLS_CONTEXT:
                    await self.send_response(502, "STARTTLS is not configured")
                elif self.tls_active:
                    await self.send_response(503, "TLS is already active")
                else:
                    await self.send_response(220, "Ready to start TLS")
                    try:
                        await self.writer.start_tls(TLS_CONTEXT, ssl_handshake_timeout=10)
                    except (ssl.SSLError, asyncio.TimeoutError, ConnectionError, OSError):
                        logger.info("SMTP STARTTLS handshake failed for %s", self.peer_ip)
                        break
                    self.tls_active = True
                    self.helo_domain = ""
                    self.mail_from = ""
                    self.mail_from_set = False
                    self.rcpt_to = []
            elif cmd_upper == "QUIT":
                await self.send_response(221, "Bye")
                break
            elif cmd_upper == "RSET":
                self.mail_from = ""
                self.mail_from_set = False
                self.rcpt_to = []
                data_buffer.clear()
                data_too_large = False
                data_started_at = None
                await self.send_response(250, "Reset OK")
            elif cmd_upper == "NOOP":
                await self.send_response(250, "OK")
            else:
                await self.send_response(500, "Command unrecognized")

        self.writer.close()
        await self.writer.wait_closed()

    async def process_email(self, raw_bytes: bytes):
        msg = email.message_from_bytes(raw_bytes, policy=policy.default)
        sender_header = str(msg.get("From", self.mail_from or "unknown@sender.com"))
        sender = parseaddr(sender_header)[1] or sender_header
        subject = msg.get("Subject", "(No Subject)")
        raw_message_id = str(msg.get("Message-ID", "")).strip() or None
        in_reply_to = str(msg.get("In-Reply-To", "")).strip() or None
        references = str(msg.get("References", "")).strip() or None

        # Extract text and html
        body_text = ""
        body_html = None
        attachments = []
        attachment_total = 0

        if msg.is_multipart():
            for part in msg.walk():
                if part.is_multipart():
                    continue
                ctype = part.get_content_type()
                filename = part.get_filename()
                disposition = part.get_content_disposition()
                if filename or disposition == "attachment":
                    payload = part.get_payload(decode=True) or b""
                    if len(attachments) >= MAX_ATTACHMENTS:
                        raise ValueError(f"Message contains more than {MAX_ATTACHMENTS} attachments")
                    if len(payload) > MAX_ATTACHMENT_BYTES:
                        raise ValueError(f"Attachment exceeds {MAX_ATTACHMENT_BYTES} byte limit")
                    attachment_total += len(payload)
                    if attachment_total > MAX_MESSAGE_BYTES:
                        raise ValueError("Attachments exceed configured total size limit")
                    attachments.append({"filename": safe_attachment_name(filename or "attachment"), "content_type": safe_content_type(ctype), "content": payload})
                elif ctype == "text/plain" and not body_text:
                    payload = part.get_payload(decode=True)
                    body_text = payload.decode("utf-8", errors="ignore") if payload else ""
                elif ctype == "text/html" and not body_html:
                    payload = part.get_payload(decode=True)
                    body_html = payload.decode("utf-8", errors="ignore") if payload else ""
        else:
            payload = msg.get_payload(decode=True)
            filename = msg.get_filename()
            if filename or msg.get_content_disposition() == "attachment":
                payload = payload or b""
                if len(payload) > MAX_ATTACHMENT_BYTES:
                    raise ValueError(f"Attachment exceeds {MAX_ATTACHMENT_BYTES} byte limit")
                if len(attachments) >= MAX_ATTACHMENTS:
                    raise ValueError(f"Message contains more than {MAX_ATTACHMENTS} attachments")
                attachments.append({"filename": safe_attachment_name(filename or "attachment"), "content_type": safe_content_type(msg.get_content_type()), "content": payload})
            else:
                body_text = payload.decode("utf-8", errors="ignore") if payload else ""

        if not body_text and body_html:
            body_text = body_html

        spf_status, dkim_status, dmarc_status, auth_evidence = await evaluate_inbound_authentication(
            raw_message=raw_bytes,
            peer_ip=getattr(self, "peer_ip", None),
            mail_from=self.mail_from,
            helo_domain=self.helo_domain,
        )
        inbound_dedup_hash = hashlib.sha256(
            self.mail_from.strip().lower().encode("utf-8", errors="replace") + b"\0" + raw_bytes
        ).hexdigest()

        # An SMTP transaction can have multiple RCPT TO commands. Deliver one
        # copy into each accepted inbox and avoid duplicate copies for repeated RCPTs.
        for target_recipient in dict.fromkeys(self.rcpt_to):
            logger.info(f"Ingesting real SMTP mail from '{sender}' to '{target_recipient}'")
            async with AsyncSessionLocal() as db:
                res = await db.execute(select(Agent).where(Agent.email == target_recipient))
                agent = res.scalar_one_or_none()
                if not agent:
                    logger.warning(f"No configured agent found for recipient {target_recipient}. Dropping recipient copy.")
                    continue
                message, scan_result, review = await EmailService.process_inbound(
                    db=db,
                    agent=agent,
                    sender=sender,
                    subject=subject,
                    body_text=body_text or "(Empty Body)",
                    body_html=body_html,
                    spf_status=spf_status,
                    dkim_status=dkim_status,
                    dmarc_status=dmarc_status,
                    auth_evidence=auth_evidence,
                    inbound_dedup_hash=inbound_dedup_hash,
                    raw_message_id=raw_message_id,
                    in_reply_to=in_reply_to,
                    references=references,
                    attachments=attachments,
                )
                logger.info(f"Delivered message {message.id} to agent {agent.email}. Verdict: {scan_result.verdict}")

async def _handle_connection(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    if CONNECTIONS.locked():
        writer.write(b"421 Too many SMTP connections; try again later\r\n")
        try:
            await asyncio.wait_for(writer.drain(), timeout=2)
        except (asyncio.TimeoutError, ConnectionError, OSError):
            pass
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass
        return

    await CONNECTIONS.acquire()
    try:
        await SmtpSession(reader, writer).handle()
    except (ConnectionError, OSError, ValueError) as exc:
        logger.info(f"SMTP connection closed: {exc}")
    except Exception:
        logger.exception("Unhandled SMTP session error")
    finally:
        CONNECTIONS.release()
        writer.close()
        try:
            await writer.wait_closed()
        except (ConnectionError, OSError):
            pass


async def start_smtp_server(host: str = HOST, port: int = PORT):
    server = await asyncio.start_server(
        _handle_connection,
        host,
        port,
        limit=STREAM_LINE_LIMIT,
    )
    logger.info(f"Open Agent Email SMTP Receiver listening on {host}:{port}")
    return server

async def main():
    server = await start_smtp_server()
    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())

