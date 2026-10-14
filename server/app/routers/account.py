"""Administrator views across every inbox: suppressions, contacts and a data export.

Contacts and suppressions stay stored per inbox (the existing tables); these routes are
read/write views over those rows, not separate records.
"""

import datetime
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import Field, field_validator
from sqlalchemy import and_, delete, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, Contact, EmailTemplate, RecipientSuppression, WebhookEndpoint
from app.routers.contacts import _ensure_unique_email
from app.routers.webhooks import _endpoint_response
from app.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.security import require_admin
from app.services.cursors import decode_cursor, encode_cursor

router = APIRouter(tags=["Account"], dependencies=[Depends(require_admin)])

EXPORT_DEFAULT_LIMIT = 5000
EXPORT_MAX_LIMIT = 20000


def _normalize_address(address: str) -> str:
    return address.strip().lower()


def _suppression_row(row: RecipientSuppression) -> dict:
    return {"id": row.id, "agent_email": row.agent_email, "email": row.email,
            "reason": row.reason, "created_at": row.created_at}


# --- Suppressions -----------------------------------------------------------------

@router.get("/v1/account/suppressions")
async def list_account_suppressions(
    address: Optional[str] = Query(None, max_length=320),
    limit: int = Query(200, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    query = select(RecipientSuppression)
    if address:
        query = query.where(RecipientSuppression.email == _normalize_address(address))
    rows = (await db.execute(query.order_by(RecipientSuppression.created_at.desc(),
                                            RecipientSuppression.id).limit(limit))).scalars().all()
    return {"items": [_suppression_row(r) for r in rows]}


@router.get("/v1/account/suppressions/page")
async def list_account_suppressions_page(
    address: Optional[str] = Query(None, max_length=320),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None, max_length=2048),
    db: AsyncSession = Depends(get_db),
):
    normalized = _normalize_address(address) if address else None
    scope = f"/v1/account/suppressions?address={normalized or ''}"
    query = select(RecipientSuppression)
    if normalized:
        query = query.where(RecipientSuppression.email == normalized)
    if cursor:
        key, item_id = decode_cursor(cursor, scope=scope)
        try:
            created_at = datetime.datetime.fromisoformat(key)
        except ValueError:
            decode_cursor("invalid", scope=scope)
        query = query.where(or_(RecipientSuppression.created_at < created_at,
                                and_(RecipientSuppression.created_at == created_at,
                                     RecipientSuppression.id > item_id)))
    rows = list((await db.execute(query.order_by(RecipientSuppression.created_at.desc(),
                                                 RecipientSuppression.id).limit(limit + 1))).scalars().all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(scope=scope, key=rows[-1].created_at.isoformat(), item_id=rows[-1].id) if has_more and rows else None
    return {"items": [_suppression_row(r) for r in rows], "next_cursor": next_cursor}


@router.delete("/v1/account/suppressions/{address}")
async def remove_account_suppression(address: str, db: AsyncSession = Depends(get_db)):
    """Remove an address from every inbox's suppression list."""
    result = await db.execute(
        delete(RecipientSuppression).where(RecipientSuppression.email == _normalize_address(address))
    )
    if result.rowcount == 0:
        await db.rollback()
        raise HTTPException(status_code=404, detail="Address is not suppressed in any inbox")
    await db.commit()
    return {"address": _normalize_address(address), "removed": result.rowcount}


# --- Contacts (cross-inbox view over the per-inbox rows) ---------------------------

class AccountContactCreate(ContactCreate):
    # Plain string: inbox addresses may use special-use domains (e.g. agents.local) that
    # EmailStr rejects. The value is checked against existing inboxes before use.
    agent_email: str = Field(..., min_length=3, max_length=255)

    @field_validator("agent_email", mode="before")
    @classmethod
    def _normalize_agent(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


async def _matching_contacts(db: AsyncSession, address: str, agent_email: Optional[str]) -> list[Contact]:
    query = select(Contact).where(Contact.email == _normalize_address(address))
    if agent_email:
        query = query.where(Contact.agent_email == agent_email.strip().lower())
    rows = (await db.execute(query.order_by(Contact.agent_email))).scalars().all()
    if not rows:
        raise HTTPException(status_code=404, detail="Contact not found")
    return rows


async def _single_contact(db: AsyncSession, address: str, agent_email: Optional[str]) -> Contact:
    rows = await _matching_contacts(db, address, agent_email)
    if len(rows) > 1:
        raise HTTPException(
            status_code=409,
            detail="This address exists in several inboxes; pass agent_email to choose one",
        )
    return rows[0]


@router.get("/v1/contacts")
async def list_account_contacts(
    agent_email: Optional[str] = Query(None, max_length=255),
    q: Optional[str] = Query(None, max_length=200, description="Match address, name or company"),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
):
    query = select(Contact)
    if agent_email:
        query = query.where(Contact.agent_email == agent_email.strip().lower())
    if q and q.strip():
        pattern = "%" + q.strip().lower().replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        query = query.where(
            func.lower(Contact.email).like(pattern, escape="\\")
            | func.lower(Contact.name).like(pattern, escape="\\")
            | func.lower(Contact.company).like(pattern, escape="\\")
        )
    rows = (await db.execute(query.order_by(Contact.agent_email, Contact.email).limit(limit))).scalars().all()
    return {"items": [ContactResponse.model_validate(r).model_dump(mode="json") for r in rows]}


@router.get("/v1/contacts/page")
async def list_account_contacts_page(
    agent_email: Optional[str] = Query(None, max_length=255),
    q: Optional[str] = Query(None, max_length=200, description="Match address, name or company"),
    limit: int = Query(50, ge=1, le=200),
    cursor: Optional[str] = Query(None, max_length=2048),
    db: AsyncSession = Depends(get_db),
):
    normalized_agent = agent_email.strip().lower() if agent_email else None
    normalized_q = q.strip().lower() if q and q.strip() else None
    scope = f"/v1/contacts?agent_email={normalized_agent or ''}&q={normalized_q or ''}"
    query = select(Contact)
    if normalized_agent:
        query = query.where(Contact.agent_email == normalized_agent)
    if normalized_q:
        pattern = "%" + normalized_q.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_") + "%"
        query = query.where(func.lower(Contact.email).like(pattern, escape="\\")
                            | func.lower(Contact.name).like(pattern, escape="\\")
                            | func.lower(Contact.company).like(pattern, escape="\\"))
    if cursor:
        key, _ = decode_cursor(cursor, scope=scope)
        try:
            agent_key, email_key = key.split("\0", 1)
        except ValueError:
            decode_cursor("invalid", scope=scope)
        query = query.where(or_(Contact.agent_email > agent_key,
                                and_(Contact.agent_email == agent_key, Contact.email > email_key)))
    rows = list((await db.execute(query.order_by(Contact.agent_email, Contact.email).limit(limit + 1))).scalars().all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(scope=scope, key=f"{rows[-1].agent_email}\0{rows[-1].email}", item_id=rows[-1].id) if has_more and rows else None
    return {"items": [ContactResponse.model_validate(r).model_dump(mode="json") for r in rows], "next_cursor": next_cursor}


@router.post("/v1/contacts", response_model=ContactResponse, status_code=201)
async def create_account_contact(payload: AccountContactCreate, db: AsyncSession = Depends(get_db)):
    if await db.scalar(select(Agent.id).where(Agent.email == payload.agent_email)) is None:
        raise HTTPException(status_code=404, detail="Agent inbox not found")
    await _ensure_unique_email(payload.agent_email, payload.email, db)
    now = datetime.datetime.utcnow()
    contact = Contact(id=f"ct_{uuid.uuid4().hex[:12]}", agent_email=payload.agent_email, email=payload.email,
                      name=payload.name, company=payload.company, notes=payload.notes,
                      created_at=now, updated_at=now)
    db.add(contact)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A contact with this email already exists in this inbox") from None
    await db.refresh(contact)
    return contact


@router.get("/v1/contacts/{address}")
async def get_account_contact(address: str, agent_email: Optional[str] = Query(None, max_length=255),
                              db: AsyncSession = Depends(get_db)):
    """Every inbox's record for this address (or one inbox with agent_email)."""
    rows = await _matching_contacts(db, address, agent_email)
    return {"items": [ContactResponse.model_validate(r).model_dump(mode="json") for r in rows]}


@router.patch("/v1/contacts/{address}", response_model=ContactResponse)
async def update_account_contact(address: str, payload: ContactUpdate,
                                 agent_email: Optional[str] = Query(None, max_length=255),
                                 db: AsyncSession = Depends(get_db)):
    contact = await _single_contact(db, address, agent_email)
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes and changes["email"] is not None:
        await _ensure_unique_email(contact.agent_email, changes["email"], db, exclude_id=contact.id)
    for field, value in changes.items():
        if value is not None:
            setattr(contact, field, value)
    contact.updated_at = datetime.datetime.utcnow()
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A contact with this email already exists in this inbox") from None
    await db.refresh(contact)
    return contact


@router.delete("/v1/contacts/{address}", status_code=204)
async def delete_account_contact(address: str, agent_email: Optional[str] = Query(None, max_length=255),
                                 db: AsyncSession = Depends(get_db)):
    contact = await _single_contact(db, address, agent_email)
    await db.delete(contact)
    await db.commit()


# --- Export ------------------------------------------------------------------------

@router.get("/v1/account/export")
async def export_account(
    limit_per_collection: int = Query(EXPORT_DEFAULT_LIMIT, ge=1, le=EXPORT_MAX_LIMIT),
    db: AsyncSession = Depends(get_db),
):
    """Configuration and directory data for backup or migration.

    Excludes message bodies, attachments, API keys and key hashes, SMTP credentials, and
    webhook signing secrets (webhook URLs have query strings redacted). Each collection is
    capped; `truncated` and `truncated_collections` say when rows were left out.
    """
    truncated: list[str] = []

    async def collect(name: str, query, shape):
        rows = (await db.execute(query.limit(limit_per_collection + 1))).scalars().all()
        if len(rows) > limit_per_collection:
            truncated.append(name)
            rows = rows[:limit_per_collection]
        return [shape(r) for r in rows]

    agents = await collect("agents", select(Agent).order_by(Agent.created_at, Agent.id), lambda a: {
        "id": a.id, "email": a.email, "display_name": a.display_name, "description": a.description,
        "status": a.status, "threat_sensitivity": a.threat_sensitivity, "hitl_enabled": a.hitl_enabled,
        "auto_reply_enabled": a.auto_reply_enabled, "created_at": a.created_at, "deleted_at": a.deleted_at,
    })
    contacts = await collect("contacts", select(Contact).order_by(Contact.agent_email, Contact.id), lambda c: {
        "id": c.id, "agent_email": c.agent_email, "email": c.email, "name": c.name, "company": c.company,
        "notes": c.notes, "created_at": c.created_at,
    })
    templates = await collect("templates", select(EmailTemplate).order_by(EmailTemplate.agent_email, EmailTemplate.id),
                              lambda t: {"id": t.id, "agent_email": t.agent_email, "name": t.name, "subject": t.subject,
                                         "body_text": t.body_text, "body_html": t.body_html})
    suppressions = await collect("suppressions",
                                 select(RecipientSuppression).order_by(RecipientSuppression.agent_email,
                                                                       RecipientSuppression.id), _suppression_row)
    webhooks = await collect("webhook_endpoints",
                             select(WebhookEndpoint).order_by(WebhookEndpoint.agent_email, WebhookEndpoint.id),
                             _endpoint_response)
    return {
        "exported_at": datetime.datetime.utcnow(),
        "limit_per_collection": limit_per_collection,
        "truncated": bool(truncated),
        "truncated_collections": truncated,
        "counts": {"agents": len(agents), "contacts": len(contacts), "templates": len(templates),
                   "suppressions": len(suppressions), "webhook_endpoints": len(webhooks)},
        "agents": agents,
        "contacts": contacts,
        "templates": templates,
        "suppressions": suppressions,
        "webhook_endpoints": webhooks,
    }
