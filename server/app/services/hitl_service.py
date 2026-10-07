import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models import ReviewItem, Message
from app.services.ws_manager import ws_manager

class HitlService:

    @classmethod
    async def resolve_review(
        cls,
        db: AsyncSession,
        review_id: str,
        action: str,  # approve or reject
        notes: str = None
    ) -> ReviewItem:
        """
        Human reviewer approves or rejects a held message.
        """
        result = await db.execute(select(ReviewItem).where(ReviewItem.id == review_id))
        review = result.scalar_one_or_none()
        if not review:
            raise HTTPException(status_code=404, detail="Review item not found")

        if review.status != "pending":
            raise HTTPException(status_code=400, detail=f"Review is already {review.status}")

        msg_result = await db.execute(select(Message).where(Message.id == review.message_id))
        message = msg_result.scalar_one_or_none()

        now = datetime.datetime.utcnow()
        review.resolved_at = now
        review.reviewer_notes = notes

        if action == "approve":
            review.status = "approved"
            if message:
                message.status = "delivered"
                
                # Fetch agent
                agent_res = await db.execute(select(Agent).where(Agent.email == message.agent_email))
                agent = agent_res.scalar_one_or_none()

                msg_payload = {
                    "id": message.id,
                    "agent_email": message.agent_email,
                    "direction": message.direction,
                    "sender": message.sender,
                    "recipient": message.recipient,
                    "subject": message.subject,
                    "status": "delivered",
                    "thread_id": message.thread_id,
                    "created_at": message.created_at.isoformat()
                }

                if message.direction == "outbound" and agent:
                    # Dispatch to upstream SMTP relay or local loopback
                    from app.services.email_service import EmailService
                    await EmailService.dispatch_to_upstream(db, message, agent)
                    await ws_manager.send_agent_message(message.agent_email, "email.sent", msg_payload)
                    await ws_manager.broadcast_event("email.sent", msg_payload)
                else:
                    # Inbound email approved by reviewer - deliver to agent
                    await ws_manager.send_agent_message(message.agent_email, "email.received", msg_payload)
                    await ws_manager.broadcast_event("email.received", msg_payload)
        elif action == "reject":
            review.status = "rejected"
            if message:
                message.status = "rejected"
        else:
            raise HTTPException(status_code=400, detail="Invalid action. Must be 'approve' or 'reject'")

        await db.commit()
        await db.refresh(review)

        # Broadcast review resolved
        await ws_manager.broadcast_event("review.resolved", {
            "review_id": review.id,
            "message_id": review.message_id,
            "status": review.status,
            "notes": notes
        })

        return review
