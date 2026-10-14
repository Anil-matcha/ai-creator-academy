"""Administrator-managed, inbox-scoped webhook endpoints and delivery history."""

import base64
import binascii
import datetime
import json
import secrets
import uuid
from typing import Optional
from urllib.parse import urlsplit, urlunsplit

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import and_, delete, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, WebhookDelivery, WebhookEndpoint
from app.security import Principal, require_admin
from app.services.smtp_secrets import encrypt_secret
from app.services.webhook_delivery import validate_webhook_url

router = APIRouter(prefix="/v1/webhooks", tags=["Webhooks"], dependencies=[Depends(require_admin)])
MAX_ENDPOINTS_PER_INBOX = 50
DELIVERY_STATUSES = {"pending", "processing", "delivered", "failed"}


def _encode_delivery_cursor(item: WebhookDelivery, endpoint_id: Optional[str], status: Optional[str]) -> str:
    payload = {
        "created_at": item.created_at.isoformat(),
        "id": item.id,
        "endpoint_id": endpoint_id,
        "status": status,
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_delivery_cursor(cursor: str, endpoint_id: Optional[str], status: Optional[str]):
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        raw = base64.b64decode(padded.encode("ascii"), altchars=b"-_", validate=True)
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or set(payload) != {"created_at", "id", "endpoint_id", "status"}:
            raise ValueError
        if payload["endpoint_id"] != endpoint_id or payload["status"] != status:
            raise ValueError("filter mismatch")
        if not isinstance(payload["id"], str) or not payload["id"] or len(payload["id"]) > 64:
            raise ValueError
        if payload["endpoint_id"] is not None and not isinstance(payload["endpoint_id"], str):
            raise ValueError
        if payload["status"] is not None and not isinstance(payload["status"], str):
            raise ValueError
        created_at = datetime.datetime.fromisoformat(payload["created_at"])
        if created_at.tzinfo is not None:
            raise ValueError
        return created_at, payload["id"]
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, TypeError, KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail="Invalid or incompatible delivery cursor") from exc


class WebhookCreate(BaseModel):
    agent_email: str = Field(min_length=3, max_length=255)
    url: str = Field(min_length=9, max_length=2048)
    enabled: bool = True


class WebhookUpdate(BaseModel):
    url: Optional[str] = Field(None, min_length=9, max_length=2048)
    enabled: Optional[bool] = None


class WebhookResponse(BaseModel):
    id: str
    agent_email: str
    url: str
    enabled: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime


class WebhookCreated(WebhookResponse):
    signing_secret: str


def _endpoint_response(endpoint: WebhookEndpoint) -> dict:
    parsed = urlsplit(endpoint.url)
    display_url = urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "[redacted]" if parsed.query else "", ""))
    return {"id": endpoint.id, "agent_email": endpoint.agent_email, "url": display_url,
            "enabled": endpoint.enabled, "created_at": endpoint.created_at, "updated_at": endpoint.updated_at}


@router.post("", response_model=WebhookCreated, status_code=201)
async def create_webhook(payload: WebhookCreate, db: AsyncSession = Depends(get_db)):
    agent_result = await db.execute(select(Agent).where(
        Agent.email == payload.agent_email.strip().lower(),
    ).with_for_update())
    agent = agent_result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent inbox not found")
    endpoint_count = await db.scalar(select(func.count()).select_from(WebhookEndpoint).where(
        WebhookEndpoint.agent_email == agent.email,
    ))
    if endpoint_count >= MAX_ENDPOINTS_PER_INBOX:
        raise HTTPException(status_code=409, detail=f"An inbox can have at most {MAX_ENDPOINTS_PER_INBOX} webhook endpoints")
    try:
        url = validate_webhook_url(payload.url)
        raw_secret = "whsec_" + secrets.token_urlsafe(32)
        encrypted = encrypt_secret(raw_secret, "webhook signing secret")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    now = datetime.datetime.utcnow()
    endpoint = WebhookEndpoint(id=f"wh_{uuid.uuid4().hex}", agent_email=agent.email, url=url,
                               signing_secret=encrypted, enabled=payload.enabled, created_at=now, updated_at=now)
    db.add(endpoint)
    await db.commit()
    await db.refresh(endpoint)
    return {**_endpoint_response(endpoint), "signing_secret": raw_secret}


@router.get("")
async def list_webhooks(agent_email: Optional[str] = Query(None, max_length=255),
                        limit: int = Query(100, ge=1, le=200), db: AsyncSession = Depends(get_db)):
    query = select(WebhookEndpoint)
    if agent_email:
        query = query.where(WebhookEndpoint.agent_email == agent_email.strip().lower())
    endpoints = (await db.execute(query.order_by(WebhookEndpoint.created_at.desc()).limit(limit))).scalars().all()
    return [_endpoint_response(item) for item in endpoints]


@router.patch("/{endpoint_id}", response_model=WebhookResponse)
async def update_webhook(endpoint_id: str, payload: WebhookUpdate, db: AsyncSession = Depends(get_db)):
    endpoint = await db.get(WebhookEndpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    if payload.url is not None:
        try:
            endpoint.url = validate_webhook_url(payload.url)
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
    if payload.enabled is not None:
        endpoint.enabled = payload.enabled
    endpoint.updated_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(endpoint)
    return _endpoint_response(endpoint)


@router.post("/{endpoint_id}/test", status_code=202)
async def send_test_webhook(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    """Queue a signed synthetic event to verify an enabled endpoint."""
    endpoint = await db.get(WebhookEndpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    if not endpoint.enabled:
        raise HTTPException(status_code=409, detail="Enable the webhook endpoint before sending a test event")

    now = datetime.datetime.utcnow()
    delivery_id = f"evt_{uuid.uuid4().hex}"
    db.add(WebhookDelivery(
        id=delivery_id,
        endpoint_id=endpoint.id,
        agent_email=endpoint.agent_email,
        event_type="webhook.test",
        payload={
            "id": delivery_id,
            "event_type": "webhook.test",
            "test": True,
            "created_at": now.isoformat(),
            "message": "Synthetic test event; no email was sent or received.",
        },
        status="pending",
        attempts=0,
        available_at=now,
        created_at=now,
    ))
    await db.commit()
    return {"delivery_id": delivery_id, "status": "pending"}


@router.delete("/{endpoint_id}", status_code=204)
async def delete_webhook(endpoint_id: str, db: AsyncSession = Depends(get_db)):
    endpoint = await db.get(WebhookEndpoint, endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=404, detail="Webhook endpoint not found")
    await db.execute(delete(WebhookDelivery).where(WebhookDelivery.endpoint_id == endpoint_id))
    await db.delete(endpoint)
    await db.commit()


@router.get("/deliveries")
async def list_deliveries(endpoint_id: Optional[str] = Query(None, max_length=64),
                          status: Optional[str] = Query(None), limit: int = Query(100, ge=1, le=200),
                          db: AsyncSession = Depends(get_db)):
    if status and status not in {"pending", "processing", "delivered", "failed"}:
        raise HTTPException(status_code=400, detail="Invalid webhook delivery status")
    query = select(WebhookDelivery)
    if endpoint_id:
        query = query.where(WebhookDelivery.endpoint_id == endpoint_id)
    if status:
        query = query.where(WebhookDelivery.status == status)
    items = (await db.execute(query.order_by(WebhookDelivery.created_at.desc()).limit(limit))).scalars().all()
    return [{"id": item.id, "endpoint_id": item.endpoint_id, "agent_email": item.agent_email,
             "event_type": item.event_type, "payload": item.payload, "status": item.status,
             "attempts": item.attempts, "last_error": item.last_error, "created_at": item.created_at,
             "delivered_at": item.delivered_at, "replayed_by": item.replayed_by,
             "replayed_at": item.replayed_at, "replay_count": item.replay_count} for item in items]


@router.get("/deliveries/page")
async def page_deliveries(endpoint_id: Optional[str] = Query(None, max_length=64),
                          status: Optional[str] = Query(None), limit: int = Query(50, ge=1, le=100),
                          cursor: Optional[str] = Query(None, max_length=2048),
                          db: AsyncSession = Depends(get_db)):
    if status and status not in DELIVERY_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid webhook delivery status")

    query = select(WebhookDelivery)
    if endpoint_id:
        query = query.where(WebhookDelivery.endpoint_id == endpoint_id)
    if status:
        query = query.where(WebhookDelivery.status == status)
    if cursor is not None:
        created_at, delivery_id = _decode_delivery_cursor(cursor, endpoint_id, status)
        query = query.where(or_(
            WebhookDelivery.created_at < created_at,
            and_(WebhookDelivery.created_at == created_at, WebhookDelivery.id < delivery_id),
        ))

    rows = (await db.execute(query.order_by(
        WebhookDelivery.created_at.desc(), WebhookDelivery.id.desc(),
    ).limit(limit + 1))).scalars().all()
    has_more = len(rows) > limit
    items = rows[:limit]
    next_cursor = _encode_delivery_cursor(items[-1], endpoint_id, status) if has_more and items else None
    return {
        "items": [{"id": item.id, "endpoint_id": item.endpoint_id, "agent_email": item.agent_email,
                   "event_type": item.event_type, "payload": item.payload, "status": item.status,
                   "attempts": item.attempts, "last_error": item.last_error, "created_at": item.created_at,
                   "delivered_at": item.delivered_at, "replayed_by": item.replayed_by,
                   "replayed_at": item.replayed_at, "replay_count": item.replay_count} for item in items],
        "next_cursor": next_cursor,
    }


@router.post("/deliveries/{delivery_id}/replay")
async def replay_delivery(delivery_id: str, principal: Principal = Depends(require_admin),
                          db: AsyncSession = Depends(get_db)):
    now = datetime.datetime.utcnow()
    delivery = await db.get(WebhookDelivery, delivery_id)
    if not delivery:
        raise HTTPException(status_code=404, detail="Webhook delivery not found")
    if delivery.status not in {"failed", "delivered"}:
        raise HTTPException(status_code=409, detail="Only failed or previously delivered events can be replayed")
    endpoint = await db.get(WebhookEndpoint, delivery.endpoint_id)
    if not endpoint:
        raise HTTPException(status_code=409, detail="Webhook endpoint no longer exists")
    if not endpoint.enabled:
        raise HTTPException(status_code=409, detail="Enable the webhook endpoint before replaying this event")
    result = await db.execute(update(WebhookDelivery).where(
        WebhookDelivery.id == delivery_id, WebhookDelivery.status == delivery.status,
    ).values(status="pending", attempts=0, available_at=now, locked_at=None, lease_token=None,
             last_error=None, delivered_at=None, replayed_by=principal.principal_id,
             replayed_at=now, replay_count=WebhookDelivery.replay_count + 1))
    if result.rowcount != 1:
        raise HTTPException(status_code=409, detail="Webhook delivery changed; retry")
    await db.commit()
    return {"id": delivery_id, "status": "pending", "replayed_at": now}
