import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Domain
from app.schemas import DomainCreate, DomainResponse
from app.security import require_admin

router = APIRouter(prefix="/v1/domains", tags=["Domains"], dependencies=[Depends(require_admin)])

@router.get("", response_model=List[DomainResponse])
async def list_domains(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Domain).order_by(Domain.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=DomainResponse, status_code=201)
async def create_domain(payload: DomainCreate, db: AsyncSession = Depends(get_db)):
    clean_domain = payload.domain.strip().lower()
    if not clean_domain or "." not in clean_domain:
        raise HTTPException(status_code=400, detail="Invalid domain name format")

    existing = await db.execute(select(Domain).where(Domain.domain == clean_domain))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"Domain {clean_domain} is already registered")

    dom_id = f"dom_{uuid.uuid4().hex[:12]}"
    new_domain = Domain(
        id=dom_id,
        domain=clean_domain,
        status="pending_dns",
        mx_record=f"10 mx.{clean_domain}",
        mx_status="pending",
        spf_record=f"v=spf1 include:_spf.openagent.dev ~all",
        spf_status="pending",
        dkim_selector="default",
        dkim_record="v=DKIM1; k=rsa; p=MIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQD2d+j7rF7oQ7v7v0n...IDAQAB",
        dkim_status="pending",
        dmarc_record=f"v=DMARC1; p=quarantine; rua=mailto:dmarc@{clean_domain}",
        dmarc_status="pending",
        created_at=datetime.datetime.utcnow()
    )
    db.add(new_domain)
    await db.commit()
    await db.refresh(new_domain)
    return new_domain

@router.post("/{domain_name}/verify", response_model=DomainResponse)
async def verify_domain(domain_name: str, db: AsyncSession = Depends(get_db)):
    clean_domain = domain_name.strip().lower()
    res = await db.execute(select(Domain).where(Domain.domain == clean_domain))
    domain = res.scalar_one_or_none()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")

    raise HTTPException(status_code=501, detail="DNS verification is not implemented yet; records have not been verified")

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
