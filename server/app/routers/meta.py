"""Service discovery, caller identity, per-inbox metrics and protection policy."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Agent, Message, ReviewItem
from app.security import Principal, get_principal, require_admin, require_agent_access

router = APIRouter(tags=["Meta"])


@router.get("/v1/info")
async def info():
    """Unauthenticated discovery document for SDKs and CLIs."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "api_version": "v1",
        "shared_domain": settings.SHARED_DOMAIN,
        "mcp_endpoint": "/mcp/rpc",
        "features": [
            "rest", "mcp", "websocket", "webhooks", "human_review", "templates", "contacts",
            "suppressions", "scheduled_send", "labels", "trash", "conversations", "otp",
        ],
    }


@router.get("/v1/whoami")
async def whoami(principal: Principal = Depends(get_principal)):
    return {
        "kind": "admin" if principal.is_admin else "agent_key",
        "scope": "admin" if principal.is_admin else principal.scope,
        "agent_email": principal.agent_email,
        "principal_id": principal.principal_id,
    }


@router.get("/v1/agents/{email}/metrics", dependencies=[Depends(require_agent_access)])
async def agent_metrics(email: str, db: AsyncSession = Depends(get_db)):
    if not await db.scalar(select(Agent.id).where(Agent.email == email)):
        raise HTTPException(status_code=404, detail="Agent not found")
    rows = (await db.execute(
        select(Message.direction, Message.status, func.count())
        .where(Message.agent_email == email, Message.deleted_at.is_(None))
        .group_by(Message.direction, Message.status)
    )).all()
    by_status: dict = {"inbound": {}, "outbound": {}}
    for direction, status, count in rows:
        by_status[direction][status] = count
    unread = await db.scalar(select(func.count()).select_from(Message).where(
        Message.agent_email == email, Message.direction == "inbound",
        Message.is_read.is_(False), Message.deleted_at.is_(None)))
    pending = await db.scalar(select(func.count()).select_from(ReviewItem).where(
        ReviewItem.agent_email == email, ReviewItem.status == "pending"))
    return {
        "agent_email": email,
        "messages": {d: sum(v.values()) for d, v in by_status.items()},
        "by_status": by_status,
        "unread": unread or 0,
        "pending_reviews": pending or 0,
    }


class ProtectionUpdate(BaseModel):
    threat_sensitivity: str = Field(..., pattern="^(off|low|medium|high)$")
    hitl_enabled: bool


@router.get("/v1/agents/{email}/protection", dependencies=[Depends(require_agent_access)])
async def get_protection(email: str, db: AsyncSession = Depends(get_db)):
    agent = await db.scalar(select(Agent).where(Agent.email == email))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return {"threat_sensitivity": agent.threat_sensitivity, "hitl_enabled": agent.hitl_enabled}


@router.put("/v1/agents/{email}/protection", dependencies=[Depends(require_admin)])
async def update_protection(email: str, body: ProtectionUpdate, db: AsyncSession = Depends(get_db)):
    """Administrator-only: an agent key must not be able to weaken its own approval gate."""
    agent = await db.scalar(select(Agent).where(Agent.email == email))
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    agent.threat_sensitivity = body.threat_sensitivity
    agent.hitl_enabled = body.hitl_enabled
    await db.commit()
    return {"threat_sensitivity": agent.threat_sensitivity, "hitl_enabled": agent.hitl_enabled}
