import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Message, OutboundJob
from app.schemas import OutboundJobResponse
from app.security import Principal, require_admin

router = APIRouter(prefix="/v1/outbox", tags=["Outbound Queue"], dependencies=[Depends(require_admin)])


@router.get("", response_model=List[OutboundJobResponse])
async def list_outbound_jobs(
    status: Optional[str] = Query(None, description="pending, processing, complete, or failed"),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    query = select(OutboundJob)
    if status:
        if status not in {"pending", "processing", "complete", "failed"}:
            raise HTTPException(status_code=400, detail="Invalid outbox status")
        query = query.where(OutboundJob.status == status)
    result = await db.execute(query.order_by(OutboundJob.created_at.desc()).limit(limit))
    return result.scalars().all()


@router.post("/{job_id}/retry", response_model=OutboundJobResponse)
async def retry_outbound_job(
    job_id: str,
    principal: Principal = Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    retried_at = datetime.datetime.utcnow()
    result = await db.execute(
        update(OutboundJob)
        .where(OutboundJob.id == job_id, OutboundJob.status == "failed")
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
        exists = await db.scalar(select(OutboundJob.id).where(OutboundJob.id == job_id))
        if not exists:
            raise HTTPException(status_code=404, detail="Outbound job not found")
        raise HTTPException(status_code=409, detail="Only failed jobs can be retried")

    job = await db.get(OutboundJob, job_id)
    message = await db.get(Message, job.message_id)
    if message:
        message.status = "sending"
        message.delivery_error = None
    await db.commit()
    await db.refresh(job)
    return job
