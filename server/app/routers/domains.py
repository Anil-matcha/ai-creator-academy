import uuid
import datetime
import asyncio
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Domain
from app.schemas import DomainCreate, DomainResponse
from app.security import require_admin
from app.services import domain_dns
from app.services.smtp_secrets import encrypt_secret

router = APIRouter(prefix="/v1/domains", tags=["Domains"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[DomainResponse])
async def list_domains(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Domain).order_by(Domain.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=DomainResponse, status_code=201)
async def create_domain(payload: DomainCreate, db: AsyncSession = Depends(get_db)):
    clean_domain = payload.domain.strip().lower().rstrip(".")
    if not domain_dns.valid_domain(clean_domain):
        raise HTTPException(status_code=400, detail="Invalid domain name format")

    existing = await db.execute(select(Domain).where(Domain.domain == clean_domain))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Domain {clean_domain} is already registered")

    private_pem, public_b64 = await asyncio.to_thread(domain_dns.generate_dkim_keypair)
    try:
        encrypted_key = encrypt_secret(private_pem, "domain DKIM private key")
    except RuntimeError as exc:
        # Never store a signing key in plaintext.
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    records = domain_dns.expected_records(clean_domain, public_b64)

    new_domain = Domain(
        id=f"dom_{uuid.uuid4().hex[:12]}",
        domain=clean_domain,
        status="pending_dns",
        mx_record=records.mx,
        mx_status="pending",
        spf_record=records.spf,
        spf_status="pending",
        dkim_selector=domain_dns.DKIM_SELECTOR,
        dkim_record=records.dkim,
        dkim_status="pending",
        dmarc_record=records.dmarc,
        dmarc_status="pending",
        dkim_private_key=encrypted_key,
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_domain)
    await db.commit()
    await db.refresh(new_domain)
    return new_domain

@router.post("/{domain_name}/verify", response_model=DomainResponse)
async def verify_domain(domain_name: str, db: AsyncSession = Depends(get_db)):
    clean_domain = domain_name.strip().lower().rstrip(".")
    res = await db.execute(select(Domain).where(Domain.domain == clean_domain))
    domain = res.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if not domain.dkim_private_key:
        raise HTTPException(
            status_code=409,
            detail="This domain was registered with placeholder DKIM data; delete and register it again",
        )

    public_b64 = domain.dkim_record.partition("p=")[2].strip()
    mx, spf, dkim, dmarc = await asyncio.gather(
        asyncio.to_thread(domain_dns.check_mx, clean_domain),
        asyncio.to_thread(domain_dns.check_spf, clean_domain),
        asyncio.to_thread(domain_dns.check_dkim, clean_domain, domain.dkim_selector, public_b64),
        asyncio.to_thread(domain_dns.check_dmarc, clean_domain),
    )
    domain.mx_status, domain.spf_status, domain.dkim_status, domain.dmarc_status = mx, spf, dkim, dmarc
    domain.status = domain_dns.overall_status(mx, spf, dkim)
    domain.last_checked_at = datetime.datetime.utcnow()
    await db.commit()
    await db.refresh(domain)
    return domain

@router.delete("/{domain_name}", status_code=204)
async def delete_domain(domain_name: str, db: AsyncSession = Depends(get_db)):
    clean_domain = domain_name.strip().lower()
    res = await db.execute(select(Domain).where(Domain.domain == clean_domain))
    domain = res.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    await db.delete(domain)
    await db.commit()
    return None
