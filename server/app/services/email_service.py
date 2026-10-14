import uuid
import json
import datetime
import smtplib
import asyncio
import logging
import os
import re
import hashlib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from email.utils import formatdate, make_msgid
from html import escape
from typing import Optional, Tuple, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models import Agent, Message, MessageAttachment, ReviewItem, SecurityEvent, SmtpConfig, OutboundJob, WebhookEndpoint, WebhookDelivery, UnsubscribeToken
from app.config import settings
from app.services.smtp_secrets import decrypt_password
from app.schemas import ThreatScanResult
from app.services.threat_scanner import ThreatScanner
from app.services.ws_manager import ws_manager
from app.services.webhook_events import (
    enqueue_email_webhook_event,
    enqueue_inbound_security_webhook_event,
)
from app.services.recipient_suppressions import canonicalize_recipient, get_recipient_suppression
from app.services.unsubscribe import issue_token, public_base_url

logger = logging.getLogger("email_service")
SMTP_ACCEPTANCE_UNKNOWN = "SMTP relay connection ended during message submission; relay acceptance is unknown"

def _send_smtp_sync(
    host: str,
    port: int,
    username: str,
    password: str,
    use_tls: bool,
    use_ssl: bool,
    from_addr: str,
    to_addr: str,
    subject: str,
    body_text: str,
    body_html: Optional[str] = None,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
    reply_to: Optional[str] = None,
    custom_msg_id: Optional[str] = None,
    attachments: Optional[List[Dict[str, Any]]] = None,
    unsubscribe_url: Optional[str] = None,
    feedback_correlation_id: Optional[str] = None,
) -> Tuple[bool, str]:
    submission_started = False
    try:
        msg = MIMEMultipart("mixed") if attachments else MIMEMultipart("alternative")
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        if reply_to:
            msg["Reply-To"] = reply_to
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = custom_msg_id or make_msgid()
        if feedback_correlation_id:
            msg["X-Open-Agent-Email-Message-ID"] = feedback_correlation_id
        if unsubscribe_url:
            msg["List-Unsubscribe"] = f"<{unsubscribe_url}>"
            msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        body = MIMEMultipart("alternative") if attachments else msg
        visible_text = body_text
        if unsubscribe_url:
            visible_text = body_text.rstrip() + "\n\nTo stop receiving these emails, unsubscribe here:\n" + unsubscribe_url
        part1 = MIMEText(visible_text, "plain", "utf-8")
        body.attach(part1)

        if body_html:
            html_body = body_html
            if unsubscribe_url:
                html_body += (
                    '<p style="font-size:12px;color:#666">'
                    f'<a href="{escape(unsubscribe_url, quote=True)}">Unsubscribe from future emails</a>'
                    "</p>"
                )
            part2 = MIMEText(html_body, "html", "utf-8")
            body.attach(part2)
        if attachments:
            msg.attach(body)
            for attachment in attachments:
                content_type = attachment.get("content_type") or "application/octet-stream"
                maintype, _, subtype = content_type.partition("/")
                if not subtype or not re.fullmatch(r"[A-Za-z0-9!#$&^_.+-]+", maintype + subtype):
                    maintype, subtype = "application", "octet-stream"
                part = MIMEBase(maintype, subtype)
                part.set_payload(attachment["content"])
                encoders.encode_base64(part)
                filename = os.path.basename(attachment.get("filename") or "attachment")
                filename = re.sub(r"[\r\n\x00-\x1f\x7f]", "_", filename)[:255] or "attachment"
                part.add_header("Content-Disposition", "attachment", filename=filename)
                msg.attach(part)

        if use_ssl or port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            if use_tls:
                server.starttls()

        if username and password:
            server.login(username, password)

        message_data = msg.as_string()
        submission_started = True
        refused = server.sendmail(from_addr, [to_addr], message_data)
        try:
            server.quit()
        except Exception as e:
            # QUIT happens after sendmail returned, so it cannot change that result.
            logger.debug(f"SMTP transaction result was received but QUIT failed: {e}")
        if refused:
            refusal_codes = [str(response[0]) for response in refused.values() if response]
            return False, f"SMTP relay refused the recipient (code {refusal_codes[0] if refusal_codes else 'unknown'})"
        return True, "Accepted by upstream SMTP relay"
    except (smtplib.SMTPServerDisconnected, TimeoutError, ConnectionError, OSError) as e:
        if submission_started:
            logger.error("SMTP relay connection ended during message submission; acceptance is unknown")
            return False, SMTP_ACCEPTANCE_UNKNOWN
        logger.error(f"SMTP delivery failed: {e}")
        return False, str(e)
    except Exception as e:
        logger.error(f"SMTP delivery failed: {e}")
        return False, str(e)


class EmailService:

    @staticmethod
    def generate_message_id(domain: str = "agents.local") -> str:
        return f"<msg_{uuid.uuid4().hex[:16]}@{domain}>"

    @staticmethod
    def reply_headers(original: Message) -> Tuple[str, Optional[str]]:
        parent_id = original.raw_message_id or original.rfc_message_id
        refs = []
        for source in (original.references or "", parent_id):
            for token in source.split():
                if token not in refs:
                    refs.append(token)
        # Keep the newest IDs when the RFC header would exceed the stored header limit.
        selected = []
        for token in reversed(refs):
            candidate = [token, *selected]
            if len(" ".join(candidate)) > 255:
                break
            selected = candidate
        return parent_id, " ".join(selected) or None

    @classmethod
    async def dispatch_to_upstream(
        cls,
        db: AsyncSession,
        message: Message,
        agent: Agent
    ) -> Tuple[str, str]:
        """
        Dispatches an accepted outbound email:
        - If recipient is a local agent, performs local loopback delivery.
        - Local loopback is delivered directly to the recipient inbox.
        - External SMTP success means accepted by the relay, not delivered to the recipient.
        """
        # A suppression may have been added after queuing or while awaiting review.
        # Recheck immediately before either local loopback or external SMTP dispatch.
        if await get_recipient_suppression(db, agent.email, message.recipient):
            return "blocked", "Recipient is suppressed for this inbox; no delivery attempt was made"

        # 1. Local loopback check
        recip_agent_res = await db.execute(select(Agent).where(Agent.email == message.recipient))
        recip_agent = recip_agent_res.scalar_one_or_none()
        if recip_agent:
            logger.info(f"Local loopback delivery to agent {recip_agent.email}")
            await ws_manager.send_agent_message(recip_agent.email, "email.received", {
                "id": message.id,
                "agent_email": recip_agent.email,
                "direction": "inbound",
                "sender": message.sender,
                "recipient": message.recipient,
                "subject": message.subject,
                "status": "delivered",
                "thread_id": message.thread_id,
                "created_at": message.created_at.isoformat()
            })
            return "delivered", "Delivered locally to agent inbox (loopback)"

        # 2. Upstream SMTP relay check
        smtp_res = await db.execute(select(SmtpConfig).where(SmtpConfig.id == "default"))
        config = smtp_res.scalar_one_or_none()
        if not config or not config.enabled or not config.host:
            logger.info(f"Upstream SMTP relay not configured. Could not deliver to {message.recipient}")
            return "failed", "Upstream SMTP relay is not configured or enabled"

        from_addr = config.from_email or agent.email
        unsubscribe_url = None
        base_url = public_base_url()
        if base_url:
            raw_token, token_hash = issue_token()
            db.add(UnsubscribeToken(
                token_hash=token_hash,
                agent_email=agent.email,
                recipient=canonicalize_recipient(message.recipient),
            ))
            # Persist before SMTP can accept mail containing this capability.
            await db.commit()
            unsubscribe_url = f"{base_url}/unsubscribe/{raw_token}"
        port_num = int(config.port) if str(config.port).isdigit() else 587
        try:
            smtp_password = decrypt_password(config.password)
        except RuntimeError as exc:
            logger.error("SMTP credential decryption failed: %s", exc)
            return "failed", "SMTP relay credential is unavailable; verify SMTP_CONFIG_ENCRYPTION_KEY"
        success, info = await asyncio.to_thread(
            _send_smtp_sync,
            host=config.host,
            port=port_num,
            username=config.username,
            password=smtp_password,
            use_tls=config.use_tls,
            use_ssl=config.use_ssl,
            from_addr=from_addr,
            to_addr=message.recipient,
            subject=message.subject,
            body_text=message.body_text,
            body_html=message.body_html,
            in_reply_to=message.in_reply_to,
            references=message.references,
            reply_to=agent.email,
            custom_msg_id=message.rfc_message_id,
            unsubscribe_url=unsubscribe_url,
            feedback_correlation_id=message.id if settings.SES_FEEDBACK_TOPIC_ARN.strip() else None,
            attachments=[{"filename": a.filename, "content_type": a.content_type, "content": a.content}
                         for a in (await db.execute(select(MessageAttachment).where(MessageAttachment.message_id == message.id))).scalars().all()]
        )
        if not success and info == SMTP_ACCEPTANCE_UNKNOWN:
            return "delivery_unknown", info
        return ("accepted_by_relay" if success else "failed"), info

    @classmethod
    async def process_inbound(
        cls,
        db: AsyncSession,
        agent: Agent,
        sender: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        spf_status: str = "unverified",
        dkim_status: str = "unverified",
        dmarc_status: str = "unverified",
        auth_evidence: Optional[Dict[str, Any]] = None,
        inbound_dedup_hash: Optional[str] = None,
        verified_domain: Optional[str] = None,
        raw_message_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
    ) -> Tuple[Message, ThreatScanResult, Optional[ReviewItem]]:
        """
        Processes inbound email:
        1. Evaluates Threat & Prompt Injection via ThreatScanner
        2. Applies Agent's sensitivity and HITL rules
        3. Creates Message & optionally ReviewItem
        4. Broadcasts over WebSockets
        """
        scan_result = ThreatScanner.scan(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            sensitivity=agent.threat_sensitivity
        )

        if inbound_dedup_hash:
            existing_result = await db.execute(select(Message).where(
                Message.agent_email == agent.email,
                Message.inbound_dedup_hash == inbound_dedup_hash,
            ))
            existing = existing_result.scalar_one_or_none()
            if existing:
                return existing, scan_result, None

        raw_message_id = " ".join((raw_message_id or "").split())[:998] or None
        in_reply_to = " ".join((in_reply_to or "").split())[:255] or None
        references = " ".join((references or "").split())[:255] or None

        if raw_message_id:
            duplicate = await db.execute(
                select(Message).where(
                    Message.agent_email == agent.email,
                    Message.raw_message_id == raw_message_id,
                )
            )
            existing_message = duplicate.scalar_one_or_none()
            if existing_message:
                review_result = await db.execute(
                    select(ReviewItem).where(ReviewItem.message_id == existing_message.id)
                )
                return existing_message, scan_result, review_result.scalar_one_or_none()

        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        reference_ids = [token for token in (references or "").split() if token]
        if in_reply_to:
            reference_ids.append(in_reply_to)
        parent_query = None
        if reference_ids:
            parent_query = await db.execute(
                select(Message)
                .where(
                    Message.agent_email == agent.email,
                    or_(
                        Message.rfc_message_id.in_(reference_ids),
                        Message.raw_message_id.in_(reference_ids),
                    ),
                )
                .order_by(Message.created_at.desc())
                .limit(1)
            )
        parent_message = parent_query.scalar_one_or_none() if parent_query else None
        thread_id = parent_message.thread_id if parent_message else f"th_{uuid.uuid4().hex[:12]}"

        review_item = None
        if scan_result.verdict == "block":
            status = "blocked"
        elif scan_result.verdict == "review" or (agent.hitl_enabled and scan_result.threat_score >= 0.40):
            status = "pending_review"
        else:
            status = "delivered"

        threat_details_json = json.dumps([t.model_dump() for t in scan_result.detected_threats])

        message = Message(
            id=msg_id,
            agent_email=agent.email,
            direction="inbound",
            sender=sender,
            recipient=agent.email,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            thread_id=thread_id,
            raw_message_id=raw_message_id,
            in_reply_to=in_reply_to,
            references=references,
            rfc_message_id=rfc_id,
            spf_status=spf_status,
            dkim_status=dkim_status,
            dmarc_status=dmarc_status,
            auth_evidence=auth_evidence,
            inbound_dedup_hash=inbound_dedup_hash,
            verified_domain=verified_domain or (sender.split("@")[-1] if "@" in sender else None),
            status=status,
            threat_score=scan_result.threat_score,
            threat_details=threat_details_json,
            created_at=datetime.datetime.utcnow()
        )
        db.add(message)
        for attachment in attachments or []:
            db.add(MessageAttachment(
                id=f"att_{uuid.uuid4().hex[:16]}", message_id=msg_id,
                filename=attachment["filename"], content_type=attachment["content_type"],
                size_bytes=len(attachment["content"]), content=attachment["content"],
            ))

        if scan_result.detected_threats:
            sec_event = SecurityEvent(
                id=f"sec_{uuid.uuid4().hex[:12]}",
                agent_email=agent.email,
                threat_type=scan_result.detected_threats[0].threat_type,
                severity=scan_result.detected_threats[0].severity,
                details=scan_result.analysis_summary,
                created_at=datetime.datetime.utcnow()
            )
            db.add(sec_event)

        if status == "pending_review":
            review_item = ReviewItem(
                id=f"rev_{uuid.uuid4().hex[:12]}",
                message_id=msg_id,
                agent_email=agent.email,
                reason=f"Threat score {scan_result.threat_score}: {scan_result.analysis_summary}",
                threat_score=scan_result.threat_score,
                status="pending",
                created_at=datetime.datetime.utcnow()
            )
            db.add(review_item)
        # Snapshot only the notification metadata. The event is committed atomically
        # with the inbound message; webhook network I/O runs in its own worker.
        if status == "delivered":
            endpoints = (await db.execute(select(WebhookEndpoint).where(
                WebhookEndpoint.agent_email == agent.email,
                WebhookEndpoint.enabled.is_(True),
            ))).scalars().all()
            event_metadata = {
                "agent_email": agent.email,
                "direction": "inbound",
                "sender": sender,
                "recipient": agent.email,
                "status": status,
                "thread_id": thread_id,
                "created_at": message.created_at.isoformat(),
            }
            for endpoint in endpoints:
                event_id = f"evt_{uuid.uuid4().hex}"
                db.add(WebhookDelivery(
                    id=event_id,
                    endpoint_id=endpoint.id,
                    agent_email=agent.email,
                    event_type="email.received",
                    payload={"id": event_id, "message_id": msg_id, **event_metadata},
                    status="pending",
                    attempts=0,
                    available_at=message.created_at,
                    created_at=message.created_at,
                ))
        elif status == "pending_review" and review_item:
            await enqueue_email_webhook_event(
                db,
                agent_email=agent.email,
                event_type="email.review_requested",
                message_id=message.id,
                direction=message.direction,
                review_id=review_item.id,
                status=message.status,
                created_at=message.created_at,
            )
        if scan_result.detected_threats:
            threat = scan_result.detected_threats[0]
            await enqueue_inbound_security_webhook_event(
                db,
                event_type="email.flagged",
                message_id=message.id,
                agent_email=agent.email,
                status=message.status,
                created_at=message.created_at,
                threat_category=threat.threat_type,
                threat_severity=threat.severity,
                threat_score=scan_result.threat_score,
            )
        if scan_result.verdict == "block":
            threat = scan_result.detected_threats[0] if scan_result.detected_threats else None
            await enqueue_inbound_security_webhook_event(
                db,
                event_type="email.blocked",
                message_id=message.id,
                agent_email=agent.email,
                status=message.status,
                created_at=message.created_at,
                threat_category=threat.threat_type if threat else "other",
                threat_severity=threat.severity if threat else "unknown",
                threat_score=scan_result.threat_score,
            )
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            if not inbound_dedup_hash:
                raise
            existing_result = await db.execute(select(Message).where(
                Message.agent_email == agent.email,
                Message.inbound_dedup_hash == inbound_dedup_hash,
            ))
            existing = existing_result.scalar_one_or_none()
            if not existing:
                raise
            return existing, scan_result, None
        await db.refresh(message)

        msg_payload = {
            "id": message.id,
            "agent_email": message.agent_email,
            "direction": message.direction,
            "sender": message.sender,
            "recipient": message.recipient,
            "subject": message.subject,
            "status": message.status,
            "threat_score": message.threat_score,
            "thread_id": message.thread_id,
            "created_at": message.created_at.isoformat()
        }

        if status == "delivered":
            await ws_manager.send_agent_message(agent.email, "email.received", msg_payload)
            await ws_manager.broadcast_event("email.received", msg_payload)

            if agent.auto_reply_enabled and scan_result.threat_score < 0.2:
                reply_text = f"Hello, thank you for reaching out to {agent.display_name}. We have received your inquiry regarding '{subject}' and an agent is processing it."
                await cls.send_outbound(
                    db=db,
                    agent=agent,
                    recipient=sender,
                    subject=f"Re: {subject}",
                    body_text=reply_text,
                    thread_id=thread_id,
                    in_reply_to=rfc_id
                )
        elif status == "pending_review":
            await ws_manager.broadcast_event("review.created", {
                "review_id": review_item.id if review_item else None,
                "message": msg_payload,
                "reason": scan_result.analysis_summary
            })
        else:
            await ws_manager.broadcast_event("email.blocked", msg_payload)

        return message, scan_result, review_item

    @classmethod
    async def send_outbound(
        cls,
        db: AsyncSession,
        agent: Agent,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        thread_id: Optional[str] = None,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        idempotency_key: Optional[str] = None,
    ) -> Message:
        """
        Sends an outbound email as the agent.
        If HITL approval gate is enabled, places message into pending_review.
        Otherwise, delivers to local inbox or upstream SMTP relay.
        """
        raw_recipient = recipient
        try:
            recipient = canonicalize_recipient(recipient)
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc)) from exc
        request_hash = None
        if idempotency_key is not None:
            idempotency_key = idempotency_key.strip()
            if not idempotency_key or len(idempotency_key) > 128:
                raise HTTPException(status_code=400, detail="Idempotency-Key must contain 1 to 128 characters")
            request_fields = {
                "recipient": recipient,
                "subject": subject,
                "body_text": body_text,
                "body_html": body_html,
                "thread_id": thread_id,
                "in_reply_to": in_reply_to,
                "references": references,
                "attachments": [
                    {"filename": item["filename"], "content_type": item["content_type"],
                     "content_sha256": hashlib.sha256(item["content"]).hexdigest()}
                    for item in attachments or []
                ],
            }
            canonical_request = json.dumps(request_fields, sort_keys=True, separators=(",", ":"))
            request_hash = hashlib.sha256(canonical_request.encode("utf-8")).hexdigest()
            legacy_request_hash = None
            if raw_recipient != recipient:
                legacy_request = json.dumps(
                    {**request_fields, "recipient": raw_recipient},
                    sort_keys=True,
                    separators=(",", ":"),
                )
                legacy_request_hash = hashlib.sha256(legacy_request.encode("utf-8")).hexdigest()
            result = await db.execute(select(Message).where(
                Message.agent_email == agent.email,
                Message.idempotency_key == idempotency_key,
            ))
            existing = result.scalar_one_or_none()
            if existing:
                matches_current = existing.request_hash == request_hash
                matches_legacy = (
                    legacy_request_hash is not None
                    and existing.request_hash == legacy_request_hash
                    and existing.recipient == raw_recipient
                )
                if not matches_current and not matches_legacy:
                    raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request")
                return existing

        # Preserve idempotent retries of a message already accepted before the
        # recipient was suppressed, while blocking creation of any new message.
        suppression = await get_recipient_suppression(db, agent.email, recipient)
        if suppression:
            raise HTTPException(
                status_code=422,
                detail="This inbox has suppressed outbound email to the requested recipient.",
            )

        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        tid = thread_id or f"th_{uuid.uuid4().hex[:12]}"

        # Check HITL approval gate
        if agent.hitl_enabled:
            status = "pending_review"
        else:
            status = "sending"

        message = Message(
            id=msg_id,
            agent_email=agent.email,
            direction="outbound",
            is_read=True,
            sender=agent.email,
            recipient=recipient,
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            thread_id=tid,
            in_reply_to=in_reply_to,
            references=references or in_reply_to,
            rfc_message_id=rfc_id,
            spf_status="unverified",
            dkim_status="unverified",
            dmarc_status="unverified",
            verified_domain=None,
            status=status,
            threat_score=0.0,
            threat_details="[]",
            created_at=datetime.datetime.utcnow()
        )
        message.idempotency_key = idempotency_key
        message.request_hash = request_hash
        db.add(message)

        for attachment in attachments or []:
            db.add(MessageAttachment(
                id=f"att_{uuid.uuid4().hex[:16]}", message_id=msg_id,
                filename=attachment["filename"], content_type=attachment["content_type"],
                size_bytes=len(attachment["content"]), content=attachment["content"],
            ))

        review_item = None
        if status == "pending_review":
            review_item = ReviewItem(
                id=f"rev_{uuid.uuid4().hex[:12]}",
                message_id=msg_id,
                agent_email=agent.email,
                reason=f"Outbound approval gate active for {agent.display_name}",
                threat_score=0.0,
                status="pending",
                created_at=datetime.datetime.utcnow()
            )
            db.add(review_item)
            await enqueue_email_webhook_event(
                db,
                agent_email=agent.email,
                event_type="email.review_requested",
                message_id=message.id,
                direction=message.direction,
                review_id=review_item.id,
                status=message.status,
                created_at=message.created_at,
            )
        else:
            db.add(OutboundJob(
                id=f"out_{uuid.uuid4().hex[:24]}",
                message_id=msg_id,
                status="pending",
                attempts=0,
                available_at=datetime.datetime.utcnow(),
                created_at=datetime.datetime.utcnow(),
            ))

        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            if not idempotency_key:
                raise
            result = await db.execute(select(Message).where(
                Message.agent_email == agent.email,
                Message.idempotency_key == idempotency_key,
            ))
            existing = result.scalar_one_or_none()
            if not existing:
                raise
            if existing.request_hash != request_hash:
                raise HTTPException(status_code=409, detail="Idempotency-Key was already used with a different request")
            return existing
        await db.refresh(message)

        event_data = {
            "id": message.id,
            "agent_email": message.agent_email,
            "direction": message.direction,
            "sender": message.sender,
            "recipient": message.recipient,
            "subject": message.subject,
            "status": message.status,
            "thread_id": message.thread_id,
            "created_at": message.created_at.isoformat()
        }

        if status == "pending_review":
            await ws_manager.broadcast_event("review.created", {
                "review_id": review_item.id if review_item else None,
                "message": event_data,
                "reason": f"Outbound approval gate active for {agent.display_name}"
            })
        else:
            await ws_manager.send_agent_message(agent.email, "email.queued", event_data)
            await ws_manager.broadcast_event("email.queued", event_data)

        return message

    @classmethod
    async def forward_to_human(
        cls,
        db: AsyncSession,
        agent: Agent,
        original: Message,
        recipient: str,
        note: Optional[str] = None,
    ) -> Message:
        recipient = recipient.strip()
        local_part, separator, domain = recipient.rpartition("@")
        if not separator or not local_part or "." not in domain or any(ch.isspace() for ch in recipient):
            raise ValueError("Enter a valid human recipient email address")
        original_sender = original.sender
        original_recipient = original.recipient
        timestamp = original.created_at.isoformat() if original.created_at else "unknown"
        body_parts = [
            f"{agent.display_name} is handing this email to you for human review.",
        ]
        if note and note.strip():
            body_parts.extend(["", "Context from the agent:", note.strip()])
        body_parts.extend([
            "",
            "---------- Forwarded message ----------",
            f"From: {original_sender}",
            f"To: {original_recipient}",
            f"Date: {timestamp}",
            f"Subject: {original.subject}",
            f"Message-ID: {original.rfc_message_id}",
            "",
            original.body_text,
        ])
        subject = original.subject if original.subject.lower().startswith("fwd:") else f"Fwd: {original.subject}"
        attachment_rows = (await db.execute(
            select(MessageAttachment).where(MessageAttachment.message_id == original.id)
        )).scalars().all()
        return await cls.send_outbound(
            db=db,
            agent=agent,
            recipient=recipient,
            subject=subject,
            body_text="\n".join(body_parts),
            thread_id=original.thread_id,
            attachments=[{"filename": a.filename, "content_type": a.content_type, "content": a.content}
                         for a in attachment_rows],
        )
