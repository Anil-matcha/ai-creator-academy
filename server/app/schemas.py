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


# --- Domain Schemas ---
class DomainCreate(BaseModel):
    domain: str = Field(..., example="agents.mycompany.com")

class DomainResponse(BaseModel):
    id: str
    domain: str
    status: str
    mx_record: str
    mx_status: str
    spf_record: str
    spf_status: str
    dkim_selector: str
    dkim_record: str
    dkim_status: str
    dmarc_record: str
    dmarc_status: str
    created_at: datetime

    class Config:
        from_attributes = True

# --- SMTP Config Schemas ---
class SmtpConfigUpdate(BaseModel):
    host: str = Field("", example="smtp.gmail.com")
    port: str = Field("587", example="587")
    username: str = Field("", example="user@gmail.com")
    password: Optional[str] = Field(None, example="app_password")
    use_tls: bool = True
    use_ssl: bool = False
    from_email: str = Field("", example="agent@mycompany.com")
    enabled: bool = False

class SmtpConfigResponse(BaseModel):
    id: str
    host: str
    port: str
    username: str
    password_configured: bool
    use_tls: bool
    use_ssl: bool
    from_email: str
    enabled: bool
    updated_at: Optional[datetime] = None

class SmtpTestRequest(BaseModel):
    test_recipient: str = Field(..., example="recipient@example.com")

class SmtpTestResponse(BaseModel):
    success: bool
    message: str

# --- API Key Schemas ---
class ApiKeyCreate(BaseModel):
    name: str = Field(..., example="Cursor AI Integration")
    scope: str = Field("full_access", example="full_access")

class ApiKeyResponse(BaseModel):
    id: str
    name: str
    prefix: str
    scope: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyCreatedResponse(BaseModel):
    id: str
    name: str
    key: str
    prefix: str
    scope: str
    created_at: datetime

# --- Stats Schema ---
class StatsResponse(BaseModel):
    total_agents: int
    total_messages: int
    inbound_count: int
    outbound_count: int
    pending_reviews: int
    threats_neutralized: int
    active_websockets: int

