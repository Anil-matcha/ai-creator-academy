from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Agent
from app.schemas import (
    SimulateInboundRequest,
    SimulateInboundResponse,
    ThreatScanResult,
    MessageResponse
)
from app.services.threat_scanner import ThreatScanner
from app.services.email_service import EmailService

router = APIRouter(prefix="/v1/simulate", tags=["Simulator & Threat Lab"])

@router.post("/inbound", response_model=SimulateInboundResponse)
async def simulate_inbound_email(
    req: SimulateInboundRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Simulates receiving an external email from an outside sender.
    Evaluates SPF/DKIM/DMARC and scans for prompt injections.
    """
    res = await db.execute(select(Agent).where(Agent.email == req.agent_email))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail=f"Target agent {req.agent_email} does not exist")

    message, scan_result, review_item = await EmailService.process_inbound(
        db=db,
        agent=agent,
        sender=req.sender,
        subject=req.subject,
        body_text=req.body_text,
        body_html=req.body_html,
        spf_status=req.spf_status,
        dkim_status=req.dkim_status,
        dmarc_status=req.dmarc_status,
        verified_domain=req.verified_domain
    )

    action_taken = "delivered"
    if message.status == "pending_review":
        action_taken = "held_for_hitl_review"
    elif message.status == "blocked":
        action_taken = "blocked"

    return SimulateInboundResponse(
        message=MessageResponse.model_validate(message),
        threat_scan=scan_result,
        action_taken=action_taken,
        review_id=review_item.id if review_item else None
    )

@router.post("/threat-eval", response_model=ThreatScanResult)
async def evaluate_threat_text(
    subject: str = "",
    body_text: str = "",
    body_html: str = "",
    sensitivity: str = "medium"
):
    """
    Dry-run threat scan without persisting to database.
    Useful for interactive Prompt Injection playground.
    """
    return ThreatScanner.scan(
        subject=subject,
        body_text=body_text,
        body_html=body_html,
        sensitivity=sensitivity
    )
