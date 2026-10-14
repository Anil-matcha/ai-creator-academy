import uuid
import json
import datetime
import smtplib
import asyncio
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate, make_msgid
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Agent, Message, ReviewItem, SecurityEvent, SmtpConfig
from app.schemas import ThreatScanResult
from app.services.threat_scanner import ThreatScanner
from app.services.ws_manager import ws_manager

logger = logging.getLogger("email_service")

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
    custom_msg_id: Optional[str] = None
) -> Tuple[bool, str]:
    try:
        msg = MIMEMultipart("alternative")
        msg["From"] = from_addr
        msg["To"] = to_addr
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = custom_msg_id or make_msgid()
        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        part1 = MIMEText(body_text, "plain", "utf-8")
        msg.attach(part1)

        if body_html:
            part2 = MIMEText(body_html, "html", "utf-8")
            msg.attach(part2)

        if use_ssl or port == 465:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            if use_tls:
                server.starttls()

        if username and password:
            server.login(username, password)

        server.sendmail(from_addr, [to_addr], msg.as_string())
        server.quit()
        return True, "Delivered to upstream SMTP relay"
    except Exception as e:
        logger.error(f"SMTP delivery failed: {e}")
        return False, str(e)


class EmailService:

    @staticmethod
    def generate_message_id(domain: str = "agents.local") -> str:
        return f"<msg_{uuid.uuid4().hex[:16]}@{domain}>"

    @classmethod
    async def dispatch_to_upstream(
        cls,
        db: AsyncSession,
        message: Message,
        agent: Agent
    ) -> Tuple[bool, str]:
        """
        Dispatches an accepted outbound email:
        - If recipient is a local agent, performs local loopback delivery.
        - If recipient is external and Upstream SMTP is configured, relays via SMTP.
        - If upstream SMTP is not configured, logs gateway acceptance.
        """
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
            return True, "Delivered locally to agent inbox (loopback)"

        # 2. Upstream SMTP relay check
        smtp_res = await db.execute(select(SmtpConfig).where(SmtpConfig.id == "default"))
        config = smtp_res.scalar_one_or_none()
        if not config or not config.enabled or not config.host:
            logger.info(f"Upstream SMTP relay not configured. Message stored locally for {message.recipient}")
            return True, "Gateway accepted (Upstream SMTP relay not enabled in Settings)"

        from_addr = config.from_email or agent.email
        port_num = int(config.port) if str(config.port).isdigit() else 587
        success, info = await asyncio.to_thread(
            _send_smtp_sync,
            host=config.host,
            port=port_num,
            username=config.username,
            password=config.password,
            use_tls=config.use_tls,
            use_ssl=config.use_ssl,
            from_addr=from_addr,
            to_addr=message.recipient,
            subject=message.subject,
            body_text=message.body_text,
            body_html=message.body_html,
            in_reply_to=message.in_reply_to,
            references=message.references,
            custom_msg_id=message.rfc_message_id
        )
        return success, info

    @classmethod
    async def process_inbound(
        cls,
        db: AsyncSession,
        agent: Agent,
        sender: str,
        subject: str,
        body_text: str,
        body_html: Optional[str] = None,
        spf_status: str = "pass",
        dkim_status: str = "pass",
        dmarc_status: str = "pass",
        verified_domain: Optional[str] = None
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

        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        thread_id = f"th_{uuid.uuid4().hex[:12]}"

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
            rfc_message_id=rfc_id,
            spf_status=spf_status,
            dkim_status=dkim_status,
            dmarc_status=dmarc_status,
            verified_domain=verified_domain or (sender.split("@")[-1] if "@" in sender else None),
            status=status,
            threat_score=scan_result.threat_score,
            threat_details=threat_details_json,
            created_at=datetime.datetime.utcnow()
        )
        db.add(message)

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

        await db.commit()
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
        references: Optional[str] = None
    ) -> Message:
        """
        Sends an outbound email as the agent.
        If HITL approval gate is enabled, places message into pending_review.
        Otherwise, delivers to local inbox or upstream SMTP relay.
        """
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        tid = thread_id or f"th_{uuid.uuid4().hex[:12]}"

        # Check HITL approval gate
        if agent.hitl_enabled:
            status = "pending_review"
        else:
            status = "delivered"

        message = Message(
            id=msg_id,
            agent_email=agent.email,
            direction="outbound",
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
        db.add(message)

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

        await db.commit()
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
            # Actually dispatch via SMTP / local loopback
            await cls.dispatch_to_upstream(db, message, agent)
            await ws_manager.send_agent_message(agent.email, "email.sent", event_data)
            await ws_manager.broadcast_event("email.sent", event_data)

        return message
