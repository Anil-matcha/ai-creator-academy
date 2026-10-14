import datetime
from sqlalchemy import Column, String, Boolean, Float, Text, DateTime, ForeignKey, Index, Integer, LargeBinary, UniqueConstraint, JSON
from sqlalchemy.orm import relationship
from app.database import Base

class Agent(Base):
    __tablename__ = "agents"

    id = Column(String(64), primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    display_name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    status = Column(String(32), default="active")  # active, paused
    threat_sensitivity = Column(String(32), default="medium")  # off, low, medium, high
    hitl_enabled = Column(Boolean, default=True)
    auto_reply_enabled = Column(Boolean, default=False)
    auto_reply_prompt = Column(Text, default="You are an autonomous AI assistant replying concisely via email.")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    messages = relationship("Message", back_populates="agent", cascade="all, delete-orphan")
    api_keys = relationship("ApiKey", back_populates="agent", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="agent", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"
    __table_args__ = (UniqueConstraint("agent_email", "email", name="uq_contacts_agent_email_email"),)

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    name = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False, default="")
    notes = Column(Text, nullable=False, default="")
    import_batch_id = Column(String(64), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    agent = relationship("Agent", back_populates="contacts")


class ContactEngagement(Base):
    """Inbox-scoped follow-up state; due dates never trigger outbound mail."""
    __tablename__ = "contact_engagements"
    __table_args__ = (
        UniqueConstraint("agent_email", "contact_id", name="uq_engagement_agent_contact"),
        Index("ix_engagement_due", "agent_email", "next_due_at"),
    )

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(64), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    stage = Column(String(32), nullable=False, default="new")
    next_due_at = Column(DateTime, nullable=True, index=True)
    due_notified_at = Column(DateTime, nullable=True)
    notes = Column(Text, nullable=False, default="")
    replied_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ContactConsentEvent(Base):
    """Append-only inbox-scoped record of an operator-entered consent change."""
    __tablename__ = "contact_consent_events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    contact_id = Column(String(64), ForeignKey("contacts.id", ondelete="CASCADE"), nullable=False, index=True)
    action = Column(String(16), nullable=False)  # granted, revoked
    source = Column(String(255), nullable=False)
    evidence = Column(String(1000), nullable=False, default="")
    note = Column(String(1000), nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)


class EmailTemplate(Base):
    """Reusable, inbox-scoped message content; templates never send by themselves."""
    __tablename__ = "email_templates"
    __table_args__ = (UniqueConstraint("agent_email", "name", name="uq_email_templates_agent_name"),)

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    subject = Column(String(512), nullable=False)
    body_text = Column(Text, nullable=False, default="")
    body_html = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class ContactImportBatch(Base):
    __tablename__ = "contact_import_batches"

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    contact_ids = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class RecipientSuppression(Base):
    """Recipient addresses an inbox has explicitly blocked from outbound mail."""
    __tablename__ = "recipient_suppressions"
    __table_args__ = (UniqueConstraint("agent_email", "email", name="uq_suppressions_agent_email_email"),)

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String(255), nullable=False)
    reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class ProviderFeedbackReceipt(Base):
    """Durable SNS message IDs prevent feedback retries from being re-applied."""
    __tablename__ = "provider_feedback_receipts"

    provider_event_id = Column(String(255), primary_key=True)
    provider = Column(String(32), nullable=False, default="ses")
    received_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class UnsubscribeToken(Base):
    """Hashed, inbox-and-recipient scoped public unsubscribe capability."""
    __tablename__ = "unsubscribe_tokens"

    token_hash = Column(String(64), primary_key=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    recipient = Column(String(255), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    used_at = Column(DateTime, nullable=True)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (
        UniqueConstraint("agent_email", "idempotency_key", name="uq_messages_agent_idempotency_key"),
        UniqueConstraint("agent_email", "inbound_dedup_hash", name="uq_messages_agent_inbound_dedup_hash"),
    )

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email"), index=True, nullable=False)
    direction = Column(String(16), nullable=False)  # inbound, outbound
    is_read = Column(Boolean, nullable=False, default=False, index=True)
    sender = Column(String(255), nullable=False)
    recipient = Column(String(255), nullable=False)
    subject = Column(String(512), default="(No Subject)")
    body_text = Column(Text, nullable=False)
    body_html = Column(Text, nullable=True)
    
    # RFC Threading
    thread_id = Column(String(64), index=True, nullable=False)
    raw_message_id = Column(String(998), nullable=True, index=True)
    in_reply_to = Column(String(255), nullable=True)
    references = Column(Text, nullable=True)
    rfc_message_id = Column(String(255), unique=True, index=True, nullable=False)
    
    # Authentication & Security
    spf_status = Column(String(32), default="unverified")
    dkim_status = Column(String(32), default="unverified")
    dmarc_status = Column(String(32), default="unverified")
    auth_evidence = Column(JSON, nullable=True)
    verified_domain = Column(String(255), nullable=True)
    delivery_error = Column(Text, nullable=True)
    provider_delivery_status = Column(String(32), nullable=True, index=True)
    provider_delivery_error = Column(Text, nullable=True)
    idempotency_key = Column(String(128), nullable=True)
    request_hash = Column(String(64), nullable=True)
    inbound_dedup_hash = Column(String(64), nullable=True)
    
    # State & Threat
    status = Column(String(32), default="delivered", index=True)  # delivered, accepted_by_relay, sending, delivery_unknown, pending_review, rejected, blocked, failed
    threat_score = Column(Float, default=0.0)
    threat_details = Column(Text, default="[]")  # JSON encoded list of threats detected
    
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)

    agent = relationship("Agent", back_populates="messages")
    review_item = relationship("ReviewItem", back_populates="message", uselist=False, cascade="all, delete-orphan")
    attachments = relationship("MessageAttachment", back_populates="message", cascade="all, delete-orphan")


class MessageAttachment(Base):
    __tablename__ = "message_attachments"

    id = Column(String(64), primary_key=True, index=True)
    message_id = Column(String(64), ForeignKey("messages.id", ondelete="CASCADE"), nullable=False, index=True)
    filename = Column(String(255), nullable=False)
    content_type = Column(String(255), nullable=False, default="application/octet-stream")
    size_bytes = Column(Integer, nullable=False)
    content = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

    message = relationship("Message", back_populates="attachments")


class OutboundJob(Base):
    __tablename__ = "outbound_jobs"

    id = Column(String(64), primary_key=True, index=True)
    message_id = Column(String(64), ForeignKey("messages.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    status = Column(String(24), nullable=False, default="pending", index=True)  # pending, processing, complete, failed, uncertain, blocked
    attempts = Column(Integer, nullable=False, default=0)
    available_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    locked_at = Column(DateTime, nullable=True, index=True)
    last_error = Column(Text, nullable=True)
    retried_by = Column(String(128), nullable=True)
    retried_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)


class OutboundRetryEvent(Base):
    __tablename__ = "outbound_retry_events"

    id = Column(String(64), primary_key=True, index=True)
    job_id = Column(String(64), ForeignKey("outbound_jobs.id", ondelete="CASCADE"), nullable=False, index=True)
    actor = Column(String(128), nullable=False)
    requested_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    previous_attempts = Column(Integer, nullable=False)
    previous_error = Column(Text, nullable=True)
    previous_status = Column(String(24), nullable=True)


class WebhookEndpoint(Base):
    __tablename__ = "webhook_endpoints"

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=False, index=True)
    url = Column(Text, nullable=False)
    event_types = Column(JSON, nullable=False, default=lambda: ["*"])
    signing_secret = Column(Text, nullable=False)
    previous_signing_secret = Column(Text, nullable=True)
    previous_secret_expires_at = Column(DateTime, nullable=True)
    enabled = Column(Boolean, nullable=False, default=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)


class WebhookDelivery(Base):
    __tablename__ = "webhook_deliveries"

    id = Column(String(64), primary_key=True, index=True)  # stable event ID
    endpoint_id = Column(String(64), ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), nullable=False, index=True)
    agent_email = Column(String(255), nullable=False, index=True)
    event_type = Column(String(64), nullable=False, default="email.received")
    payload = Column(JSON, nullable=False)  # immutable event snapshot; intentionally excludes body and attachments
    status = Column(String(24), nullable=False, default="pending", index=True)  # pending, processing, delivered, failed
    attempts = Column(Integer, nullable=False, default=0)
    available_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    locked_at = Column(DateTime, nullable=True, index=True)
    lease_token = Column(String(64), nullable=True, index=True)
    last_error = Column(String(255), nullable=True)
    replayed_by = Column(String(128), nullable=True)
    replayed_at = Column(DateTime, nullable=True)
    replay_count = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow, index=True)
    delivered_at = Column(DateTime, nullable=True)


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(String(64), primary_key=True, index=True)
    message_id = Column(String(64), ForeignKey("messages.id"), unique=True, nullable=False)
    agent_email = Column(String(255), index=True, nullable=False)
    reason = Column(String(255), nullable=False)
    threat_score = Column(Float, default=0.0)
    status = Column(String(32), default="pending", index=True)  # pending, approved, rejected
    reviewer_notes = Column(Text, nullable=True)
    reviewed_by = Column(String(128), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)
    resolved_at = Column(DateTime, nullable=True)

    message = relationship("Message", back_populates="review_item")


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(String(64), primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    prefix = Column(String(16), nullable=False)
    key_hash = Column(String(128), nullable=False)
    scope = Column(String(64), default="full_access")
    agent_email = Column(String(255), ForeignKey("agents.email", ondelete="CASCADE"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    expires_at = Column(DateTime, nullable=True, index=True)

    agent = relationship("Agent", back_populates="api_keys")


class SecurityEvent(Base):
    __tablename__ = "security_events"

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), index=True, nullable=False)
    threat_type = Column(String(64), nullable=False)
    severity = Column(String(32), default="medium")  # low, medium, high, critical
    details = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, index=True)


class Domain(Base):
    __tablename__ = "domains"

    id = Column(String(64), primary_key=True, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=False)
    status = Column(String(32), default="pending_dns")  # verified, pending_dns
    mx_record = Column(String(255), nullable=False)
    mx_status = Column(String(32), default="pending")  # verified, pending
    spf_record = Column(String(255), nullable=False)
    spf_status = Column(String(32), default="pending")  # verified, pending
    dkim_selector = Column(String(64), default="default")
    dkim_record = Column(Text, nullable=False)
    dkim_status = Column(String(32), default="pending")  # verified, pending
    dmarc_record = Column(String(255), nullable=False)
    dmarc_status = Column(String(32), default="pending")  # verified, pending
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class SmtpConfig(Base):
    __tablename__ = "smtp_configs"

    id = Column(String(64), primary_key=True, default="default")
    host = Column(String(255), nullable=False, default="")
    port = Column(String(16), default="587")
    username = Column(String(255), nullable=False, default="")
    password = Column(Text, nullable=False, default="")
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    from_email = Column(String(255), nullable=False, default="")
    enabled = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

