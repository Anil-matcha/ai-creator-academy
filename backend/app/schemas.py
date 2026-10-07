from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

# --- Agent Schemas ---
class AgentCreate(BaseModel):
    email: str = Field(..., example="support@agents.local")
    display_name: str = Field(..., example="Support AI Agent")
    description: Optional[str] = "Tier-1 Autonomous Email Support"
    threat_sensitivity: str = Field("medium", example="medium")  # off, low, medium, high
    hitl_enabled: bool = True
    auto_reply_enabled: bool = False
    auto_reply_prompt: Optional[str] = "You are an autonomous AI assistant replying concisely via email."

class AgentUpdate(BaseModel):
    display_name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    threat_sensitivity: Optional[str] = None
    hitl_enabled: Optional[bool] = None
    auto_reply_enabled: Optional[bool] = None
    auto_reply_prompt: Optional[str] = None

class AgentResponse(BaseModel):
    id: str
    email: str
    display_name: str
    description: str
    status: str
    threat_sensitivity: str
    hitl_enabled: bool
    auto_reply_enabled: bool
    auto_reply_prompt: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# --- Threat Scan Schemas ---
class ThreatDetail(BaseModel):
    threat_type: str
    severity: str
    confidence: float
    description: str
    matched_pattern: Optional[str] = None

class ThreatScanResult(BaseModel):
    threat_score: float
    verdict: str  # allow, review, block
    detected_threats: List[ThreatDetail]
    analysis_summary: str


# --- Message Schemas ---
class MessageSendRequest(BaseModel):
    recipient: str = Field(..., example="customer@example.com")
    subject: str = Field(..., example="Update on your support ticket #492")
    body_text: str = Field(..., example="Hello! We have reviewed your inquiry and resolved the issue.")
    body_html: Optional[str] = None
    thread_id: Optional[str] = None

class MessageReplyRequest(BaseModel):
    body_text: str = Field(..., example="Thank you for confirming. I am closing this ticket now.")
    body_html: Optional[str] = None

class MessageResponse(BaseModel):
    id: str
    agent_email: str
    direction: str
    sender: str
    recipient: str
    subject: str
    body_text: str
    body_html: Optional[str]
    thread_id: str
    in_reply_to: Optional[str]
    references: Optional[str]
    rfc_message_id: str
    spf_status: str
    dkim_status: str
    dmarc_status: str
    verified_domain: Optional[str]
    status: str
    threat_score: float
    threat_details: str
    created_at: datetime

    class Config:
        from_attributes = True


# --- Review / HITL Schemas ---
class ReviewDecisionRequest(BaseModel):
    action: str = Field(..., example="approve")  # approve, reject
    notes: Optional[str] = None

class ReviewItemResponse(BaseModel):
    id: str
    message_id: str
    agent_email: str
    reason: str
    threat_score: float
    status: str
    reviewer_notes: Optional[str]
    created_at: datetime
    resolved_at: Optional[datetime]
    message: Optional[MessageResponse] = None

    class Config:
        from_attributes = True


# --- Simulation Schemas ---
class SimulateInboundRequest(BaseModel):
    agent_email: str = Field(..., example="support@agents.local")
    sender: str = Field("user@company.com", example="user@company.com")
    subject: str = Field("Help with billing invoice", example="Help with billing invoice")
    body_text: str = Field("Could you please review invoice INV-8821?", example="Could you please review invoice INV-8821?")
    body_html: Optional[str] = None
    spf_status: str = "pass"
    dkim_status: str = "pass"
    dmarc_status: str = "pass"
    verified_domain: Optional[str] = "company.com"

class SimulateInboundResponse(BaseModel):
    message: MessageResponse
    threat_scan: ThreatScanResult
    action_taken: str  # delivered, held_for_hitl_review, blocked
    review_id: Optional[str] = None


# --- Stats Schema ---
class StatsResponse(BaseModel):
    total_agents: int
    total_messages: int
    inbound_count: int
    outbound_count: int
    pending_reviews: int
    threats_neutralized: int
    active_websockets: int
