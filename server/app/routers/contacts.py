import datetime
import csv
import io
import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, Request, Response
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy import select, delete, func, and_, or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import AsyncSessionLocal, get_db
from app.models import Agent, Contact, ContactConsentEvent, ContactImportBatch, RecipientSuppression
from app.schemas import ContactCreate, ContactResponse, ContactUpdate, ContactConsentWrite, ContactConsentHistoryResponse
from pydantic import ValidationError
from app.security import require_agent_access, require_write
from app.services.cursors import decode_cursor, encode_cursor
from app.security import Principal
from app.services.idempotency import reserve_idempotency, complete_idempotency, release_idempotency_claim


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


@router.get("/page")
async def list_contacts_page(email: str, limit: int = Query(50, ge=1, le=200),
                             cursor: str | None = Query(None, max_length=2048), db: AsyncSession = Depends(get_db)):
    await _ensure_agent_exists(email, db)
    scope = f"/v1/agents/{email}/contacts"
    query = select(Contact).where(Contact.agent_email == email).order_by(Contact.name, Contact.email).limit(limit + 1)
    if cursor:
        key, _ = decode_cursor(cursor, scope=scope)
        try:
            name, address = key.split("\0", 1)
        except ValueError:
            decode_cursor("invalid", scope=scope)
        query = query.where(or_(Contact.name > name, and_(Contact.name == name, Contact.email > address)))
    rows = list((await db.execute(query)).scalars().all())
    has_more = len(rows) > limit
    rows = rows[:limit]
    next_cursor = encode_cursor(scope=scope, key=f"{rows[-1].name}\0{rows[-1].email}", item_id=rows[-1].id) if has_more and rows else None
    return {"items": [ContactResponse.model_validate(row) for row in rows], "next_cursor": next_cursor}


@router.post("", response_model=ContactResponse, status_code=201, dependencies=[Depends(require_write)])
async def create_contact(email: str, payload: ContactCreate, request: Request,
                         principal: Principal = Depends(require_agent_access),
                         db: AsyncSession = Depends(get_db)):
    await _ensure_agent_exists(email, db)
    key = request.headers.get("Idempotency-Key")
    decision = None
    if key is not None:
        raw_body = await request.body()
        try:
            decision = await reserve_idempotency(
                f"{principal.principal_id}:contacts:create", key,
                {"agent_email": email, "body": raw_body.decode("latin1")})
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if decision.outcome == "replay":
            return JSONResponse(status_code=decision.response_status or 201,
                                content=decision.response_body,
                                headers=decision.response_headers or {})
        if decision.outcome != "reserved":
            messages = {
                "conflict": "Idempotency-Key was already used with a different request",
                "in_progress": "Idempotency-Key request is still in progress; retry unchanged",
                "expired_in_progress": "Idempotency-Key request did not finish; operator recovery is required",
            }
            raise HTTPException(status_code=409, detail=messages[decision.outcome])
    try:
        await _ensure_unique_email(email, payload.email, db)
    except HTTPException:
        if decision is not None:
            await release_idempotency_claim(AsyncSessionLocal, decision)
        raise
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
    if decision is not None:
        await db.flush()
        response_body = jsonable_encoder(ContactResponse.model_validate(contact))
        await complete_idempotency(db, decision, status=201, body=response_body)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=409, detail="A contact with this email already exists in this inbox") from None
    await db.refresh(contact)
    if decision is not None:
        return JSONResponse(status_code=201, content=response_body)
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


@router.get("/{contact_id}/consent", response_model=ContactConsentHistoryResponse)
async def get_contact_consent(email: str, contact_id: str, db: AsyncSession = Depends(get_db)):
    await _get_contact(email, contact_id, db)
    result = await db.execute(
        select(ContactConsentEvent).where(
            ContactConsentEvent.agent_email == email,
            ContactConsentEvent.contact_id == contact_id,
        ).order_by(ContactConsentEvent.id.desc()).limit(100)
    )
    events = result.scalars().all()
    return {"current": events[0].action if events else "unknown", "events": events}


@router.post("/{contact_id}/consent", response_model=ContactConsentHistoryResponse, status_code=201, dependencies=[Depends(require_write)])
async def record_contact_consent(email: str, contact_id: str, payload: ContactConsentWrite, db: AsyncSession = Depends(get_db)):
    await _get_contact(email, contact_id, db)
    event = ContactConsentEvent(
        agent_email=email,
        contact_id=contact_id,
        action=payload.action,
        source=payload.source,
        evidence=payload.evidence,
        note=payload.note,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(event)
    await db.commit()
    return await get_contact_consent(email, contact_id, db)


@router.post("/imports", dependencies=[Depends(require_write)])
async def import_contacts(email: str, request: Request,
                          principal: Principal = Depends(require_agent_access),
                          db: AsyncSession = Depends(get_db)):
    """Import inert contacts from a bounded CSV with email,name,company,notes columns."""
    await _ensure_agent_exists(email, db)
    body = bytearray()
    async for chunk in request.stream():
        if len(body) + len(chunk) > 1_000_000:
            raise HTTPException(status_code=413, detail="CSV file must be at most 1 MB")
        body.extend(chunk)
    try:
        raw_body = bytes(body)
        text = raw_body.decode("utf-8-sig")
        rows = csv.DictReader(io.StringIO(text, newline=""), strict=True)
        raw_headers = rows.fieldnames or []
        normalized_headers = [str(header or "").strip().lower() for header in raw_headers]
        allowed_headers = {"email", "name", "company", "notes"}
        if len(set(normalized_headers)) != len(normalized_headers):
            raise HTTPException(status_code=400, detail="CSV headers must be unique after trimming and case normalization")
        unexpected_headers = set(normalized_headers) - allowed_headers
        if unexpected_headers:
            raise HTTPException(status_code=400, detail="CSV may contain only email, name, company, and notes columns")
        # DictReader otherwise silently overwrites duplicate header names.
        rows.fieldnames = normalized_headers
        headers = set(normalized_headers)
        if "email" not in headers:
            raise HTTPException(status_code=400, detail="CSV must include an email header")
        parsed = list(rows)
    except (UnicodeDecodeError, csv.Error):
        raise HTTPException(status_code=400, detail="CSV is malformed or is not UTF-8") from None
    if not parsed:
        raise HTTPException(status_code=400, detail="CSV must contain at least one contact row")
    if len(parsed) > 1000:
        raise HTTPException(status_code=413, detail="CSV may contain at most 1,000 data rows")

    # Normalize header casing/spacing and reject overlong records before writing anything.
    if any(None in row or any(value is None for value in row.values()) for row in parsed):
        raise HTTPException(status_code=400, detail="Every CSV row must have exactly the same number of columns as the header")
    normalized_rows = [{str(k or "").strip().lower(): (v or "").strip() for k, v in row.items()} for row in parsed]
    key = request.headers.get("Idempotency-Key")
    decision = None
    if key is not None:
        try:
            decision = await reserve_idempotency(
                f"{principal.principal_id}:contacts:imports:create", key,
                {"agent_email": email, "body": raw_body.decode("latin1")})
        except ValueError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        if decision.outcome == "replay":
            return JSONResponse(status_code=decision.response_status or 200,
                                content=decision.response_body,
                                headers=decision.response_headers or {})
        if decision.outcome != "reserved":
            messages = {
                "conflict": "Idempotency-Key was already used with a different request",
                "in_progress": "Idempotency-Key request is still in progress; retry unchanged",
                "expired_in_progress": "Idempotency-Key request did not finish; operator recovery is required",
            }
            raise HTTPException(status_code=409, detail=messages[decision.outcome])
    addresses = [row.get("email", "").strip().lower() for row in normalized_rows if row.get("email", "").strip()]
    existing = set((await db.execute(select(Contact.email).where(Contact.agent_email == email, Contact.email.in_(addresses)))).scalars().all())
    suppressed = set((await db.execute(select(RecipientSuppression.email).where(RecipientSuppression.agent_email == email, RecipientSuppression.email.in_(addresses)))).scalars().all())
    seen: set[str] = set()
    batch_id = f"ci_{uuid.uuid4().hex[:16]}"
    now = datetime.datetime.utcnow()
    outcomes = []
    created_ids = []
    new_contacts = []
    for index, row in enumerate(normalized_rows, start=2):
        address = row.get("email", "").lower()
        name = row.get("name", "") or address
        company, notes = row.get("company", ""), row.get("notes", "")
        try:
            validated = ContactCreate(email=address, name=name, company=company, notes=notes)
            address, name, company, notes = validated.email, validated.name, validated.company, validated.notes
        except ValidationError:
            outcomes.append({"row": index, "email": address, "status": "skipped", "reason": "invalid_row"})
            continue
        reason = None
        if address in seen:
            reason = "duplicate_in_file"
        elif address in existing:
            reason = "already_exists"
        elif address in suppressed:
            reason = "suppressed"
        if reason:
            outcomes.append({"row": index, "email": address, "status": "skipped", "reason": reason})
            continue
        seen.add(address)
        contact_id = f"ct_{uuid.uuid4().hex[:12]}"
        new_contacts.append(Contact(id=contact_id, agent_email=email, email=address, name=name, company=company, notes=notes, import_batch_id=batch_id, created_at=now, updated_at=now))
        created_ids.append(contact_id)
        outcomes.append({"row": index, "email": address, "status": "created"})
    batch = ContactImportBatch(id=batch_id, agent_email=email, contact_ids=created_ids, created_at=now)
    response_body = {"batch_id": batch_id, "created": len(created_ids), "skipped": len(outcomes) - len(created_ids), "results": outcomes,
                     "notice": "Imported contacts are records only. This operation does not send email or record consent."}
    db.add(batch)
    db.add_all(new_contacts)
    if decision is not None:
        await complete_idempotency(db, decision, status=200, body=response_body)
    await db.commit()
    if decision is not None:
        return JSONResponse(status_code=200, content=response_body)
    return response_body


@router.get("/imports")
async def list_contact_imports(email: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(ContactImportBatch).where(ContactImportBatch.agent_email == email).order_by(ContactImportBatch.created_at.desc()).limit(50))
    batches = result.scalars().all()
    return [{"batch_id": batch.id, "created_at": batch.created_at, "created": len(batch.contact_ids)} for batch in batches]


@router.delete("/imports/{batch_id}", dependencies=[Depends(require_write)])
async def reverse_contact_import(email: str, batch_id: str, confirm: str = Query(""), db: AsyncSession = Depends(get_db)):
    if confirm != "DELETE":
        raise HTTPException(status_code=400, detail="Pass confirm=DELETE to reverse this import")
    result = await db.execute(select(ContactImportBatch).where(ContactImportBatch.agent_email == email, ContactImportBatch.id == batch_id))
    batch = result.scalar_one_or_none()
    if batch is None:
        raise HTTPException(status_code=404, detail="Contact import batch not found")
    deleted_result = await db.execute(
        delete(Contact).where(
            Contact.agent_email == email,
            Contact.import_batch_id == batch.id,
            Contact.updated_at == Contact.created_at,
        )
    )
    deleted = deleted_result.rowcount or 0
    retained = await db.scalar(
        select(func.count()).select_from(Contact).where(Contact.agent_email == email, Contact.import_batch_id == batch.id)
    ) or 0
    await db.delete(batch)
    await db.commit()
    return {"batch_id": batch_id, "deleted": deleted, "retained_after_edits": retained}
