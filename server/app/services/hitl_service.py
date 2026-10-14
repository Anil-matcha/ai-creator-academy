import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from fastapi import HTTPException

from app.models import Agent, ReviewItem, Message
from app.services.ws_manager import ws_manager

class HitlService:

    @classmethod
    async def resolve_review(
        cls,
        db: AsyncSession,
        review_id: str,
        action: str,  # approve or reject
        notes: str = None,
        reviewer_id: str = "",
    ) -> ReviewItem:
        """
        Human reviewer approves or rejects a held message.
        """
        if action not in {"approve", "reject"}:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'")

        result = await db.execute(
            update(ReviewItem)
            .where(ReviewItem.id == review_id, ReviewItem.status == "pending")
            .values(
                status="approved" if action == "approve" else "rejected",
                resolved_at=datetime.datetime.utcnow(),
                reviewer_notes=notes,
                reviewed_by=reviewer_id,
            )
        )
        if result.rowcount != 1:
            exists = await db.scalar(select(ReviewItem.id).where(ReviewItem.id == review_id))
            if not exists:
                raise HTTPException(status_code=404, detail="Review item not found")
            raise HTTPException(status_code=409, detail="Review was already resolved by another request")

        review = await db.get(ReviewItem, review_id)
        message = await db.get(Message, review.message_id)
        if message:
            message.status = ("sending" if message.direction == "outbound" else "delivered") if action == "approve" else "rejected"
        # Persist the decision before performing network delivery so a retry cannot approve it twice.
        await db.commit()

        if message and action == "approve":
            msg_payload = {
                "id": message.id,
                "agent_email": message.agent_email,
                "direction": message.direction,
                "sender": message.sender,
                "recipient": message.recipient,
                "subject": message.subject,
                "status": message.status,
                "thread_id": message.thread_id,
                "created_at": message.created_at.isoformat(),
            }
            if message.direction == "outbound":
                agent_res = await db.execute(select(Agent).where(Agent.email == message.agent_email))
                agent = agent_res.scalar_one_or_none()
                if agent:
                    from app.services.email_service import EmailService
                    dispatch_status, delivery_info = await EmailService.dispatch_to_upstream(db, message, agent)
                else:
                    dispatch_status, delivery_info = "failed", "Agent inbox no longer exists"
                message.status = dispatch_status
                message.delivery_error = delivery_info if dispatch_status == "failed" else None
                await db.commit()
                msg_payload["status"] = message.status
                msg_payload["delivery_error"] = message.delivery_error
                event_name = {
                    "failed": "email.failed",
                    "accepted_by_relay": "email.accepted",
                    "delivered": "email.sent",
                }[dispatch_status]
                await ws_manager.send_agent_message(message.agent_email, event_name, msg_payload)
                await ws_manager.broadcast_event(event_name, msg_payload)
            else:
                await ws_manager.send_agent_message(message.agent_email, "email.received", msg_payload)
                await ws_manager.broadcast_event("email.received", msg_payload)

        await db.refresh(review)

        # Broadcast review resolved
        await ws_manager.broadcast_event("review.resolved", {
            "review_id": review.id,
            "message_id": review.message_id,
            "status": review.status,
            "notes": notes
        })

        return review
