import uuid
import json
import datetime
from typing import Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import Agent, Message, ReviewItem, SecurityEvent
from app.schemas import ThreatScanResult
from app.services.threat_scanner import ThreatScanner
from app.services.ws_manager import ws_manager

class EmailService:

    @staticmethod
    def generate_message_id(domain: str = "agents.local") -> str:
        return f"<msg_{uuid.uuid4().hex[:16]}@{domain}>"

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
        # 1. Threat Scan
        scan_result = ThreatScanner.scan(
            subject=subject,
            body_text=body_text,
            body_html=body_html,
            sensitivity=agent.threat_sensitivity
        )

        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        thread_id = f"th_{uuid.uuid4().hex[:12]}"

        # Determine message status & HITL routing
        review_item = None
        if scan_result.verdict == "block":
            status = "blocked"
        elif scan_result.verdict == "review" or (agent.hitl_enabled and scan_result.threat_score >= 0.40):
            status = "pending_review"
        else:
            status = "delivered"

        threat_details_json = json.dumps([t.model_dump() for t in scan_result.detected_threats])

        # Create message record
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

        # Log security event if threats detected
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

        # If flagged for human review
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

        # Broadcast WebSocket notification
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

            # Auto-reply handling if enabled and clean
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
        Sends an outbound email as the agent. Handles RFC threading headers.
        """
        msg_id = f"msg_{uuid.uuid4().hex[:12]}"
        rfc_id = cls.generate_message_id(agent.email.split("@")[-1])
        tid = thread_id or f"th_{uuid.uuid4().hex[:12]}"

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
            spf_status="pass",
            dkim_status="pass",
            dmarc_status="pass",
            verified_domain=agent.email.split("@")[-1],
            status="delivered",
            threat_score=0.0,
            threat_details="[]",
            created_at=datetime.datetime.utcnow()
        )
        db.add(message)
        await db.commit()
        await db.refresh(message)

        # Broadcast outbound sent event
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
        await ws_manager.send_agent_message(agent.email, "email.sent", event_data)
        await ws_manager.broadcast_event("email.sent", event_data)

        return message
