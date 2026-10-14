"""Transactional helpers for enqueueing metadata-only email webhook events."""

import datetime
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import WebhookDelivery, WebhookEndpoint


async def enqueue_email_webhook_event(
    db: AsyncSession,
    *,
    agent_email: str,
    event_type: str,
    message_id: str,
    direction: str,
    review_id: str,
    status: str,
    created_at: datetime.datetime,
) -> None:
    """Add one durable delivery per enabled endpoint in the message inbox.

    The caller owns the transaction and must commit this together with the
    associated message/review transition. Payloads intentionally contain only
    stable identifiers and lifecycle metadata.
    """
    endpoints = (await db.execute(select(WebhookEndpoint).where(
        WebhookEndpoint.agent_email == agent_email,
        WebhookEndpoint.enabled.is_(True),
    ))).scalars().all()
    timestamp = created_at.isoformat()
    for endpoint in endpoints:
        event_id = f"evt_{uuid.uuid4().hex}"
        payload: dict[str, Any] = {
            "id": event_id,
            "message_id": message_id,
            "agent_email": agent_email,
            "direction": direction,
            "review_id": review_id,
            "status": status,
            "created_at": timestamp,
        }
        db.add(WebhookDelivery(
            id=event_id,
            endpoint_id=endpoint.id,
            agent_email=agent_email,
            event_type=event_type,
            payload=payload,
            status="pending",
            attempts=0,
            available_at=created_at,
            created_at=created_at,
        ))


async def enqueue_email_received_webhook_event(
    db: AsyncSession,
    *,
    agent_email: str,
    sender: str,
    recipient: str,
    thread_id: str,
    status: str,
    message_id: str,
    created_at: datetime.datetime,
) -> None:
    """Queue the existing inbound receipt contract for an inbox release."""
    endpoints = (await db.execute(select(WebhookEndpoint).where(
        WebhookEndpoint.agent_email == agent_email,
        WebhookEndpoint.enabled.is_(True),
    ))).scalars().all()
    for endpoint in endpoints:
        event_id = f"evt_{uuid.uuid4().hex}"
        db.add(WebhookDelivery(
            id=event_id,
            endpoint_id=endpoint.id,
            agent_email=agent_email,
            event_type="email.received",
            payload={
                "id": event_id,
                "message_id": message_id,
                "agent_email": agent_email,
                "direction": "inbound",
                "sender": sender,
                "recipient": recipient,
                "status": status,
                "thread_id": thread_id,
                "created_at": created_at.isoformat(),
            },
            status="pending",
            attempts=0,
            available_at=created_at,
            created_at=created_at,
        ))


async def enqueue_outbound_status_webhook_event(
    db: AsyncSession,
    *,
    event_type: str,
    message_id: str,
    agent_email: str,
    recipient: str,
    status: str,
    created_at: datetime.datetime,
) -> None:
    """Queue metadata-only outbound lifecycle events for this inbox."""
    endpoints = (await db.execute(select(WebhookEndpoint).where(
        WebhookEndpoint.agent_email == agent_email,
        WebhookEndpoint.enabled.is_(True),
    ))).scalars().all()
    for endpoint in endpoints:
        event_id = f"evt_{uuid.uuid4().hex}"
        db.add(WebhookDelivery(
            id=event_id,
            endpoint_id=endpoint.id,
            agent_email=agent_email,
            event_type=event_type,
            payload={
                "id": event_id,
                "message_id": message_id,
                "agent_email": agent_email,
                "recipient": recipient,
                "status": status,
                "created_at": created_at.isoformat(),
            },
            status="pending",
            attempts=0,
            available_at=created_at,
            created_at=created_at,
        ))
