import datetime
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Agent, Contact
from app.schemas import ContactCreate, ContactResponse, ContactUpdate
from app.security import require_agent_access, require_write


router = APIRouter(
    prefix="/v1/agents/{email}/contacts",
    tags=["Contacts"],
    dependencies=[Depends(require_agent_access)],
)


async def _ensure_agent_exists(agent_email: str, db: AsyncSession) -> None:
    result = await db.execute(select(Agent.id).where(Agent.email == agent_email))
    if result.scalar_one_or_none() is None:
        raise HTTPException(status_code=404, detail="Agent inbox not found")


async def _get_contact(agent_email: str, contact_id: str, db: AsyncSession) -> Contact:
    result = await db.execute(
        select(Contact).where(Contact.agent_email == agent_email, Contact.id == contact_id)
    )
    contact = result.scalar_one_or_none()
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


async def _ensure_unique_email(agent_email: str, address: str, db: AsyncSession, exclude_id: str | None = None) -> None:
    query = select(Contact.id).where(Contact.agent_email == agent_email, Contact.email == address)
    if exclude_id:
        query = query.where(Contact.id != exclude_id)
    if (await db.execute(query)).scalar_one_or_none() is not None:
        raise HTTPException(status_code=409, detail="A contact with this email already exists in this inbox")


@router.get("", response_model=List[ContactResponse])
async def list_contacts(email: str, limit: int = Query(100, ge=1, le=500), db: AsyncSession = Depends(get_db)):
    await _ensure_agent_exists(email, db)
    result = await db.execute(
        select(Contact).where(Contact.agent_email == email).order_by(Contact.name, Contact.email).limit(limit)
    )
    return result.scalars().all()


@router.post("", response_model=ContactResponse, status_code=201, dependencies=[Depends(require_write)])
async def create_contact(email: str, payload: ContactCreate, db: AsyncSession = Depends(get_db)):
    await _ensure_agent_exists(email, db)
    await _ensure_unique_email(email, payload.email, db)
    now = datetime.datetime.utcnow()
    contact = Contact(
        id=f"ct_{uuid.uuid4().hex[:12]}",
        agent_email=email,
        email=payload.email,
        name=payload.name,
        company=payload.company,
        notes=payload.notes,
        created_at=now,
        updated_at=now,
    )
    db.add(contact)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A contact with this email already exists in this inbox") from None
    await db.refresh(contact)
    return contact


@router.patch("/{contact_id}", response_model=ContactResponse, dependencies=[Depends(require_write)])
async def update_contact(email: str, contact_id: str, payload: ContactUpdate, db: AsyncSession = Depends(get_db)):
    contact = await _get_contact(email, contact_id, db)
    changes = payload.model_dump(exclude_unset=True)
    if "email" in changes:
        await _ensure_unique_email(email, changes["email"], db, exclude_id=contact.id)
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


@router.delete("/{contact_id}", status_code=204, dependencies=[Depends(require_write)])
async def delete_contact(email: str, contact_id: str, db: AsyncSession = Depends(get_db)):
    contact = await _get_contact(email, contact_id, db)
    await db.delete(contact)
    await db.commit()
    return Response(status_code=204)
