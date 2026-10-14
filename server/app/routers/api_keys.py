import uuid
import secrets
import hashlib
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.database import get_db
from app.models import ApiKey, Agent
from app.schemas import ApiKeyCreate, ApiKeyResponse, ApiKeyCreatedResponse
from app.security import require_admin
from app.services.cursors import decode_cursor, encode_cursor

router = APIRouter(prefix="/v1/api-keys", tags=["API Keys"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[ApiKeyResponse], dependencies=[Depends(require_admin)])
async def list_api_keys(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ApiKey).order_by(ApiKey.created_at.desc()))
    return result.scalars().all()


@router.get("/page")
async def list_api_keys_page(limit: int = Query(50, ge=1, le=200), cursor: str | None = Query(None, max_length=2048),
                             db: AsyncSession = Depends(get_db)):
    scope = "/v1/api-keys"
    query = select(ApiKey).order_by(ApiKey.created_at.desc(), ApiKey.id.desc())
    if cursor:
        key, item_id = decode_cursor(cursor, scope=scope)
        try:
            created_at = datetime.datetime.fromisoformat(key)
        except ValueError:
            decode_cursor("invalid", scope=scope)
        query = query.where(or_(ApiKey.created_at < created_at, and_(ApiKey.created_at == created_at, ApiKey.id < item_id)))
    rows = list((await db.execute(query.limit(limit + 1))).scalars().all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(scope=scope, key=rows[-1].created_at.isoformat(), item_id=rows[-1].id) if has_more and rows else None
    return {"items": [ApiKeyResponse.model_validate(row) for row in rows], "next_cursor": next_cursor}

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
        created_at=datetime.datetime.utcnow(),
        expires_at=(
            datetime.datetime.utcnow() + datetime.timedelta(days=payload.expires_in_days)
            if payload.expires_in_days is not None else None
        ),
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
        created_at=api_key.created_at,
        expires_at=api_key.expires_at,
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
