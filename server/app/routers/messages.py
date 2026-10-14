from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.database import get_db
from app.models import Agent, Message
from app.schemas import MessageResponse, MessageSendRequest, MessageReplyRequest, MessageForwardRequest
from app.services.email_service import EmailService
from app.security import require_agent_access, require_write

router = APIRouter(prefix="/v1/agents/{email}/messages", tags=["Messages"], dependencies=[Depends(require_agent_access)])

@router.get("", response_model=List[MessageResponse])
async def list_messages(
    email: str,
    direction: Optional[str] = Query(None, description="inbound or outbound"),
    status: Optional[str] = Query(None, description="delivered, pending_review, rejected, blocked, failed"),
    thread_id: Optional[str] = Query(None),
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    query = select(Message).where(Message.agent_email == email)
    if direction:
        query = query.where(Message.direction == direction)
    if status:
        query = query.where(Message.status == status)
    if thread_id:
        query = query.where(Message.thread_id == thread_id)
    
    query = query.order_by(Message.created_at.desc()).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(email: str, message_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(and_(Message.id == message_id, Message.agent_email == email)))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg

@router.post("", response_model=MessageResponse, status_code=201, dependencies=[Depends(require_write)])
async def send_message(email: str, req: MessageSendRequest, db: AsyncSession = Depends(get_db)):
    # Verify agent exists
    ag_res = await db.execute(select(Agent).where(Agent.email == email))
    agent = ag_res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    message = await EmailService.send_outbound(
        db=db,
        agent=agent,
        recipient=req.recipient,
        subject=req.subject,
        body_text=req.body_text,
        body_html=req.body_html,
        thread_id=req.thread_id
    )
    return message

@router.post("/{message_id}/reply", response_model=MessageResponse, status_code=201, dependencies=[Depends(require_write)])
async def reply_message(email: str, message_id: str, req: MessageReplyRequest, db: AsyncSession = Depends(get_db)):
    # Verify agent exists
    ag_res = await db.execute(select(Agent).where(Agent.email == email))
    agent = ag_res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    # Fetch original message
    m_res = await db.execute(select(Message).where(and_(Message.id == message_id, Message.agent_email == email)))
    original_msg = m_res.scalar_one_or_none()
    if not original_msg:
        raise HTTPException(status_code=404, detail="Target message to reply to was not found")

    reply_recipient = original_msg.sender if original_msg.direction == "inbound" else original_msg.recipient
    subject = original_msg.subject
    if not subject.lower().startswith("re:"):
        subject = f"Re: {subject}"

    reply_msg = await EmailService.send_outbound(
        db=db,
        agent=agent,
        recipient=reply_recipient,
        subject=subject,
        body_text=req.body_text,
        body_html=req.body_html,
        thread_id=original_msg.thread_id,
        in_reply_to=original_msg.rfc_message_id,
        references=f"{original_msg.references or ''} {original_msg.rfc_message_id}".strip()
    )
    return reply_msg

@router.post("/{message_id}/forward", response_model=MessageResponse, status_code=201, dependencies=[Depends(require_write)])
async def forward_message(email: str, message_id: str, req: MessageForwardRequest, db: AsyncSession = Depends(get_db)):
    agent_res = await db.execute(select(Agent).where(Agent.email == email))
    agent = agent_res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    original_res = await db.execute(
        select(Message).where(and_(Message.id == message_id, Message.agent_email == email))
    )
    original = original_res.scalar_one_or_none()
    if not original:
        raise HTTPException(status_code=404, detail="Message not found")

    try:
        return await EmailService.forward_to_human(
            db=db,
            agent=agent,
            original=original,
            recipient=req.recipient,
            note=req.note,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

@router.get("/thread/{thread_id}", response_model=List[MessageResponse])
async def get_thread(email: str, thread_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message)
        .where(and_(Message.agent_email == email, Message.thread_id == thread_id))
        .order_by(Message.created_at.asc())
    )
    return result.scalars().all()
