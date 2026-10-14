import datetime
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Message, OutboundJob, OutboundRetryEvent
from app.schemas import OutboundJobResponse, OutboundRetryEventResponse
from app.security import Principal, require_admin

router = APIRouter(prefix="/v1/outbox", tags=["Outbound Queue"], dependencies=[Depends(require_admin)])


@router.get("", response_model=List[OutboundJobResponse])
async def list_outbound_jobs(
    status: Optional[str] = Query(None, description="pending, processing, complete, failed, or uncertain"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(OutboundJob)
    if status:
        if status not in {"pending", "processing", "complete", "failed", "uncertain"}:
            raise HTTPException(status_code=400, detail="Invalid outbox status")
        query = query.where(OutboundJob.status == status)
    result = await db.execute(query.order_by(OutboundJob.created_at.desc()).limit(limit))
    return result.scalars().all()


@router.post("/{job_id}/retry", response_model=OutboundJobResponse)
async def retry_outbound_job(
    job_id: str,
    confirm_duplicate_risk: bool = Query(
        False,
        description="Required when retrying an uncertain job because the SMTP relay may already have accepted it.",
    ),
    principal: Principal = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    retried_at = datetime.datetime.utcnow()
    current = await db.get(OutboundJob, job_id)
    if not current:
        raise HTTPException(status_code=404, detail="Outbound job not found")
    previous_status = current.status
    if previous_status not in {"failed", "uncertain"}:
        raise HTTPException(status_code=409, detail="Only failed or uncertain jobs can be retried")
    if previous_status == "uncertain" and not confirm_duplicate_risk:
        raise HTTPException(
            status_code=409,
            detail="Delivery is unknown; retry may send a duplicate. Retry again with confirm_duplicate_risk=true to proceed.",
        )
    prior_attempts = current.attempts
    prior_error = current.last_error
    result = await db.execute(
        update(OutboundJob)
        .where(OutboundJob.id == job_id, OutboundJob.status == previous_status)
        .values(
            status="pending",
            attempts=0,
            available_at=retried_at,
            locked_at=None,
            last_error=None,
            retried_by=principal.principal_id,
            retried_at=retried_at,
        )
    )
    if result.rowcount != 1:
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried")

    db.add(OutboundRetryEvent(
        id=str(uuid.uuid4()),
        job_id=job_id,
        actor=principal.principal_id,
        requested_at=retried_at,
        previous_attempts=prior_attempts,
        previous_error=prior_error,
        previous_status=previous_status,
    ))

    job = await db.get(OutboundJob, job_id)
    message = await db.get(Message, job.message_id)
    if message:
        message.status = "sending"
        message.delivery_error = None
    await db.commit()
    await db.refresh(job)
    return job


@router.get("/{job_id}/retries", response_model=List[OutboundRetryEventResponse])
async def list_outbound_retry_events(
    job_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    if not await db.scalar(select(OutboundJob.id).where(OutboundJob.id == job_id)):
        raise HTTPException(status_code=404, detail="Outbound job not found")
    result = await db.execute(
        select(OutboundRetryEvent)
        .where(OutboundRetryEvent.job_id == job_id)
        .order_by(OutboundRetryEvent.requested_at.desc())
        .limit(limit)
    )
    return result.scalars().all()
