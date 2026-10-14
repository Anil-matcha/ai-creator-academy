"""Durable single-message dispatch worker backed by the application database."""

import asyncio
import datetime
import logging

from sqlalchemy import or_, select, update

from app.database import AsyncSessionLocal
from app.models import Agent, Message, OutboundJob
from app.services.email_service import EmailService
from app.services.ws_manager import ws_manager

logger = logging.getLogger("outbound_worker")
MAX_ATTEMPTS = 8
LEASE_SECONDS = 300


async def _dispatch_one() -> bool:
    now = datetime.datetime.utcnow()
    stale_before = now - datetime.timedelta(seconds=LEASE_SECONDS)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(OutboundJob)
            .where(or_(
                (OutboundJob.status == "pending") & (OutboundJob.available_at <= now),
                (OutboundJob.status == "processing") & (OutboundJob.locked_at < stale_before),
            ))
            .order_by(OutboundJob.available_at, OutboundJob.created_at)
            .limit(1)
        )
        job = result.scalar_one_or_none()
        if not job:
            return False

        old_status = job.status
        claim = update(OutboundJob).where(
            OutboundJob.id == job.id,
            OutboundJob.status == old_status,
            (OutboundJob.available_at <= now) if old_status == "pending" else (OutboundJob.locked_at < stale_before),
        ).values(status="processing", locked_at=now, attempts=OutboundJob.attempts + 1)
        claimed = await db.execute(claim)
        if claimed.rowcount != 1:
            await db.rollback()
            return True
        await db.commit()
        await db.refresh(job)

        message = await db.get(Message, job.message_id)
        agent = await db.get(Agent, message.agent_email) if message else None
        if not message or not agent:
            status, info = "failed", "Outbound message or owning agent no longer exists"
        else:
            try:
                status, info = await EmailService.dispatch_to_upstream(db, message, agent)
            except Exception as exc:
                logger.exception("Outbound dispatch failed for message %s", job.message_id)
                status, info = "failed", f"Dispatch error: {type(exc).__name__}"

        job = await db.get(OutboundJob, job.id)
        message = await db.get(Message, job.message_id)
        if status == "failed" and job.attempts < MAX_ATTEMPTS:
            delay = min(3600, 2 ** min(job.attempts, 10))
            job.status = "pending"
            job.available_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=delay)
            job.locked_at = None
            job.last_error = info
            if message:
                message.status = "sending"
                message.delivery_error = info
            await db.commit()
            logger.warning("Outbound message %s failed; retry %s scheduled", job.message_id, job.attempts)
            return True

        job.status = "failed" if status == "failed" else "complete"
        job.locked_at = None
        job.last_error = info if status == "failed" else None
        if message:
            message.status = status
            message.delivery_error = info if status == "failed" else None
        await db.commit()

        if message:
            payload = {
                "id": message.id,
                "agent_email": message.agent_email,
                "direction": message.direction,
                "sender": message.sender,
                "recipient": message.recipient,
                "subject": message.subject,
                "status": status,
                "thread_id": message.thread_id,
                "created_at": message.created_at.isoformat(),
                "delivery_error": message.delivery_error,
            }
            event_name = {
                "failed": "email.failed",
                "accepted_by_relay": "email.accepted",
                "delivered": "email.sent",
            }[status]
            await ws_manager.send_agent_message(message.agent_email, event_name, payload)
            await ws_manager.broadcast_event(event_name, payload)
        return True


async def run_outbound_worker() -> None:
    while True:
        try:
            found = await _dispatch_one()
            if not found:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Outbound worker iteration failed")
            await asyncio.sleep(1)

