import datetime
from sqlalchemy import Column, String, Boolean, Float, Text, DateTime, ForeignKey, Index, Integer, LargeBinary
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


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(64), primary_key=True, index=True)
    agent_email = Column(String(255), ForeignKey("agents.email"), index=True, nullable=False)
    direction = Column(String(16), nullable=False)  # inbound, outbound
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
    verified_domain = Column(String(255), nullable=True)
    delivery_error = Column(Text, nullable=True)
    
    # State & Threat
    status = Column(String(32), default="delivered", index=True)  # delivered, accepted_by_relay, sending, pending_review, rejected, blocked, failed
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


class ReviewItem(Base):
    __tablename__ = "review_items"

    id = Column(String(64), primary_key=True, index=True)
    message_id = Column(String(64), ForeignKey("messages.id"), unique=True, nullable=False)
    agent_email = Column(String(255), index=True, nullable=False)
    reason = Column(String(255), nullable=False)
    threat_score = Column(Float, default=0.0)
    status = Column(String(32), default="pending", index=True)  # pending, approved, rejected
    reviewer_notes = Column(Text, nullable=True)
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
    password = Column(String(255), nullable=False, default="")
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    from_email = Column(String(255), nullable=False, default="")
    enabled = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

