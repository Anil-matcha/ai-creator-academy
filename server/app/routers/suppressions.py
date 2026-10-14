import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, RecipientSuppression
from app.schemas import RecipientSuppressionCreate, RecipientSuppressionResponse
from app.security import require_agent_access, require_write

router = APIRouter(
    prefix="/v1/agents/{email}/suppressions",
    tags=["Recipient Suppressions"],
    dependencies=[Depends(require_agent_access)],
)


@router.get("", response_model=List[RecipientSuppressionResponse])
async def list_suppressions(
    email: str,
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    if not await db.scalar(select(Agent.email).where(Agent.email == email)):
        raise HTTPException(status_code=404, detail="Agent not found")
    result = await db.execute(
        select(RecipientSuppression)
        .where(RecipientSuppression.agent_email == email)
        .order_by(RecipientSuppression.created_at.desc(), RecipientSuppression.id.desc())
        .limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=RecipientSuppressionResponse, status_code=201, dependencies=[Depends(require_write)])
async def add_suppression(
    email: str,
    request: RecipientSuppressionCreate,
    db: AsyncSession = Depends(get_db),
):
    if not await db.scalar(select(Agent.email).where(Agent.email == email)):
        raise HTTPException(status_code=404, detail="Agent not found")
    entry = await db.scalar(
        select(RecipientSuppression).where(
            RecipientSuppression.agent_email == email,
            RecipientSuppression.email == str(request.email),
        )
    )
    if entry:
        return entry
    entry = RecipientSuppression(
        id=f"sup_{uuid.uuid4().hex[:20]}",
        agent_email=email,
        email=str(request.email),
        reason=request.reason,
    )
    db.add(entry)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        entry = await db.scalar(
            select(RecipientSuppression).where(
                RecipientSuppression.agent_email == email,
                RecipientSuppression.email == str(request.email),
            )
        )
        if entry:
            return entry
        raise
    await db.refresh(entry)
    return entry


@router.delete("/{suppression_id}", status_code=204, dependencies=[Depends(require_write)])
async def remove_suppression(
    email: str,
    suppression_id: str,
    db: AsyncSession = Depends(get_db),
):
    entry = await db.scalar(
        select(RecipientSuppression).where(
            RecipientSuppression.id == suppression_id,
            RecipientSuppression.agent_email == email,
        )
    )
    if not entry:
        raise HTTPException(status_code=404, detail="Suppression not found")
    await db.delete(entry)
    await db.commit()
    return None
