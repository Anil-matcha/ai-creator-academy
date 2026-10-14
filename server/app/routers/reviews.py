from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import ReviewItem
from app.schemas import ReviewItemResponse, ReviewDecisionRequest
from app.services.hitl_service import HitlService
from app.security import Principal, require_reviewer

router = APIRouter(prefix="/v1/reviews", tags=["HITL Reviews"])

@router.get("", response_model=List[ReviewItemResponse])
async def list_reviews(
    status: Optional[str] = Query(
        None,
        description="Filter by review status",
        pattern="^(pending|approved|rejected)$",
    ),
    agent_email: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    principal: Principal = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db)
):
    query = select(ReviewItem).options(selectinload(ReviewItem.message))
    if status:
        query = query.where(ReviewItem.status == status)
    if agent_email:
        query = query.where(ReviewItem.agent_email == agent_email)
    if not principal.is_admin:
        query = query.where(ReviewItem.agent_email == principal.agent_email)
    
    query = query.order_by(ReviewItem.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{review_id}", response_model=ReviewItemResponse)
async def get_review(review_id: str, principal: Principal = Depends(require_reviewer), db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(ReviewItem)
        .options(selectinload(ReviewItem.message))
        .where(ReviewItem.id == review_id)
    )
    rev = result.scalar_one_or_none()
    if not rev:
        raise HTTPException(status_code=404, detail="Review item not found")
    if not principal.is_admin and rev.agent_email != principal.agent_email:
        raise HTTPException(status_code=404, detail="Review item not found")
    return rev

@router.post("/{review_id}/approve", response_model=ReviewItemResponse)
async def approve_review(
    review_id: str,
    body: Optional[ReviewDecisionRequest] = None,
    principal: Principal = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db)
):
    notes = body.notes if body else "Approved by human reviewer"
    if not principal.is_admin:
        review_agent = await db.scalar(select(ReviewItem.agent_email).where(ReviewItem.id == review_id))
        if review_agent != principal.agent_email:
            raise HTTPException(status_code=404, detail="Review item not found")
    review = await HitlService.resolve_review(
        db=db,
        review_id=review_id,
        action="approve",
        notes=notes,
        reviewer_id=principal.principal_id,
    )
    # Reload with message
    res = await db.execute(
        select(ReviewItem).options(selectinload(ReviewItem.message)).where(ReviewItem.id == review_id)
    )
    return res.scalar_one()

@router.post("/{review_id}/reject", response_model=ReviewItemResponse)
async def reject_review(
    review_id: str,
    body: Optional[ReviewDecisionRequest] = None,
    principal: Principal = Depends(require_reviewer),
    db: AsyncSession = Depends(get_db)
):
    notes = body.notes if body else "Rejected by human reviewer"
    if not principal.is_admin:
        review_agent = await db.scalar(select(ReviewItem.agent_email).where(ReviewItem.id == review_id))
        if review_agent != principal.agent_email:
            raise HTTPException(status_code=404, detail="Review item not found")
    review = await HitlService.resolve_review(
        db=db,
        review_id=review_id,
        action="reject",
        notes=notes,
        reviewer_id=principal.principal_id,
    )
    # Reload with message
    res = await db.execute(
        select(ReviewItem).options(selectinload(ReviewItem.message)).where(ReviewItem.id == review_id)
    )
    return res.scalar_one()
