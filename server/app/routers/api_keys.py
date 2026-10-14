import uuid
import secrets
import hashlib
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import ApiKey, Agent
from app.schemas import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse
from app.security import require_admin

router = APIRouter(prefix="/v1/api-keys", tags=["API Keys"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[ApiKeyResponse], dependencies=[Depends(require_admin)])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=ApiKeyCreatedResponse, status_code=201, dependencies=[Depends(require_admin)])
async def create_api_key(payload: ApiKeyCreate, db: AsyncSession = Depends(get_db)):
    agent = await db.execute(select(Agent).where(Agent.email == payload.agent_email))
    if agent.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Agent not found")
    token_secret = secrets.token_urlsafe(32)
    prefix = f"oae_{token_secret[:8]}"
    full_key = f"{prefix}_{token_secret[8:]}"
    key_hash = hashlib.sha256(full_key.encode("utf-8")).hexdigest()

    key_id = f"key_{uuid.uuid4().hex[:12]}"
    api_key = ApiKey(
        id=key_id,
        name=payload.name,
        prefix=prefix,
        key_hash=key_hash,
        scope=payload.scope,
        agent_email=payload.agent_email,
        created_at=datetime.datetime.utcnow()
    )
    db.add(api_key)
    await db.commit()
    await db.refresh(api_key)

    return ApiKeyCreatedResponse(
        id=api_key.id,
        name=api_key.name,
        key=full_key,
        prefix=api_key.prefix,
        scope=api_key.scope,
        agent_email=api_key.agent_email,
        created_at=api_key.created_at
    )

@router.delete("/{key_id}", status_code=204, dependencies=[Depends(require_admin)])
async def revoke_api_key(key_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).where(ApiKey.id == key_id))
    api_key = result.scalar_one_or_none()
    if not api_key:
        raise HTTPException(status_code=404, detail="API key not found")

    await db.delete(api_key)
    await db.commit()
    return None
