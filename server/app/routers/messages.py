import base64
import binascii
import json
import re
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.database import get_db
from app.models import Agent, Message, MessageAttachment
from app.schemas import MessageResponse, MessagePageResponse, MessageAttachmentResponse, MessageSendRequest, MessageReplyRequest, MessageForwardRequest, RecentOtpResponse
from app.services.email_service import EmailService
from app.services.attachment_utils import decode_attachment_inputs
from app.services.otp_finder import find_recent_otp
from app.security import require_agent_access, require_write

router = APIRouter(prefix="/v1/agents/{email}/messages", tags=["Messages"], dependencies=[Depends(require_agent_access)])


def _encode_message_cursor(
    created_at: datetime,
    message_id: str,
    *,
    inbox: str,
    direction: str | None,
    query: str,
    read_status: str,
) -> str:
    payload = json.dumps(
        {
            "v": 1,
            "created_at": created_at.isoformat(),
            "id": message_id,
            "inbox": inbox,
            "direction": direction,
            "query": query,
            "read_status": read_status,
        },
        separators=(",", ":"),
    ).encode("utf-8")
    return base64.urlsafe_b64encode(payload).decode("ascii").rstrip("=")


def _decode_message_cursor(
    cursor: str,
    *,
    inbox: str,
    direction: str | None,
    query: str,
    read_status: str,
) -> tuple[datetime, str]:
    if len(cursor) > 512 or not re.fullmatch(r"[A-Za-z0-9_-]+", cursor):
        raise HTTPException(status_code=400, detail="Invalid message cursor")
    try:
        padded = cursor + "=" * (-len(cursor) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded.encode("ascii")))
        created_at = datetime.fromisoformat(payload["created_at"])
        message_id = payload["id"]
        if payload.get("v") != 1 or not isinstance(message_id, str) or not message_id or len(message_id) > 64:
            raise ValueError("invalid cursor fields")
        if (payload.get("inbox") != inbox or payload.get("direction") != direction
                or payload.get("query") != query or payload.get("read_status", "all") != read_status):
            raise ValueError("cursor filters changed")
        if created_at.tzinfo is not None:
            raise ValueError("cursor timestamp must be naive")
        return created_at, message_id
    except (binascii.Error, UnicodeDecodeError, json.JSONDecodeError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid message cursor") from None

@router.get("", response_model=List[MessageResponse])
async def list_messages(
    email: str,
    direction: Optional[str] = Query(None, description="inbound or outbound"),
    status: Optional[str] = Query(None, description="delivered, accepted_by_relay, sending, delivery_unknown, pending_review, rejected, blocked, failed"),
    thread_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=500),
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


@router.get("/otp", response_model=RecentOtpResponse, summary="Find a recent inbox verification code")
async def get_recent_otp(
    email: str,
    since_seconds: int = Query(600, ge=1, le=86400, description="Search delivered inbound mail from this many seconds ago"),
    wait_seconds: float = Query(0, ge=0, le=10, description="Wait up to 10 seconds for a matching message"),
    db: AsyncSession = Depends(get_db),
):
    match = await find_recent_otp(
        db,
        email,
        since_seconds=since_seconds,
        wait_seconds=wait_seconds,
    )
    return match or {"found": False}


@router.get("/page", response_model=MessagePageResponse)
async def page_messages(
    email: str,
    limit: int = Query(50, ge=1, le=100),
    direction: Optional[str] = Query(None, pattern="^(inbound|outbound)$"),
    read_status: str = Query("all", pattern="^(unread|read|all)$"),
    q: Optional[str] = Query(None, max_length=200, description="Search sender and subject"),
    cursor: Optional[str] = Query(None, max_length=512),
    db: AsyncSession = Depends(get_db),
):
    query = select(Message).where(Message.agent_email == email)
    normalized_query = (q or "").strip()
    if direction:
        query = query.where(Message.direction == direction)
    if read_status == "unread":
        query = query.where(Message.is_read.is_(False))
    elif read_status == "read":
        query = query.where(Message.is_read.is_(True))
    if normalized_query:
        search = normalized_query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        pattern = f"%{search}%"
        query = query.where(
            or_(Message.sender.ilike(pattern, escape="\\"), Message.subject.ilike(pattern, escape="\\"))
        )
    if cursor:
        cursor_created_at, cursor_id = _decode_message_cursor(
            cursor,
            inbox=email,
            direction=direction,
            query=normalized_query,
            read_status=read_status,
        )
        query = query.where(
            or_(
                Message.created_at < cursor_created_at,
                and_(Message.created_at == cursor_created_at, Message.id < cursor_id),
            )
        )
    query = query.order_by(Message.created_at.desc(), Message.id.desc()).limit(limit + 1)
    result = await db.execute(query)
    messages = result.scalars().all()
    has_more = len(messages) > limit
    items = messages[:limit]
    next_cursor = _encode_message_cursor(
        items[-1].created_at,
        items[-1].id,
        inbox=email,
        direction=direction,
        query=normalized_query,
        read_status=read_status,
    ) if has_more and items else None
    return {"items": items, "next_cursor": next_cursor}


@router.post("/{message_id}/read", response_model=MessageResponse, dependencies=[Depends(require_write)])
async def mark_message_read(email: str, message_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Message).where(
            Message.id == message_id,
            Message.agent_email == email,
            Message.direction == "inbound",
        )
    )
    message = result.scalar_one_or_none()
    if not message:
        raise HTTPException(status_code=404, detail="Inbound message not found")
    message.is_read = True
    await db.commit()
    await db.refresh(message)
    return message

@router.get("/{message_id}", response_model=MessageResponse)
async def get_message(email: str, message_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Message).where(and_(Message.id == message_id, Message.agent_email == email)))
    msg = result.scalar_one_or_none()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    return msg

@router.get("/{message_id}/attachments", response_model=List[MessageAttachmentResponse])
async def list_message_attachments(email: str, message_id: str, db: AsyncSession = Depends(get_db)):
    message_result = await db.execute(
        select(Message.id).where(and_(Message.id == message_id, Message.agent_email == email))
    )
    if not message_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Message not found")
    result = await db.execute(
        select(MessageAttachment).where(MessageAttachment.message_id == message_id).order_by(MessageAttachment.created_at)
    )
    return result.scalars().all()

@router.get("/{message_id}/attachments/{attachment_id}")
async def download_message_attachment(email: str, message_id: str, attachment_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(MessageAttachment)
        .join(Message, Message.id == MessageAttachment.message_id)
        .where(and_(Message.id == message_id, Message.agent_email == email, MessageAttachment.id == attachment_id))
    )
    attachment = result.scalar_one_or_none()
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")
    filename = attachment.filename.replace('"', "_").replace("\\", "_").replace("\r", "_").replace("\n", "_")
    return Response(
        content=attachment.content,
        media_type=attachment.content_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "X-Content-Type-Options": "nosniff"},
    )

@router.post("", response_model=MessageResponse, status_code=201, dependencies=[Depends(require_write)])
async def send_message(email: str, req: MessageSendRequest, request: Request, db: AsyncSession = Depends(get_db)):
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
        thread_id=req.thread_id,
        attachments=decode_attachment_inputs([item.model_dump() for item in req.attachments] if req.attachments else None),
        idempotency_key=request.headers.get("Idempotency-Key"),
    )
    return message

@router.post("/{message_id}/reply", response_model=MessageResponse, status_code=201, dependencies=[Depends(require_write)])
async def reply_message(email: str, message_id: str, req: MessageReplyRequest, request: Request, db: AsyncSession = Depends(get_db)):
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
    in_reply_to, references = EmailService.reply_headers(original_msg)

    reply_msg = await EmailService.send_outbound(
        db=db,
        agent=agent,
        recipient=reply_recipient,
        subject=subject,
        body_text=req.body_text,
        body_html=req.body_html,
        thread_id=original_msg.thread_id,
        in_reply_to=in_reply_to,
        references=references,
        attachments=decode_attachment_inputs([item.model_dump() for item in req.attachments] if req.attachments else None),
        idempotency_key=request.headers.get("Idempotency-Key"),
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
async def get_thread(
    email: str,
    thread_id: str,
    limit: int = Query(500, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Message)
        .where(and_(Message.agent_email == email, Message.thread_id == thread_id))
        .order_by(Message.created_at.asc())
        .limit(limit)
    )
    return result.scalars().all()
