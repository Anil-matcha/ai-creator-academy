"""Small, dependency-free client for the Open Agent Email REST API."""

from .client import (
    AgentEmailClient,
    AgentEmailError,
    Attachment,
    Contact,
    ContactCreate,
    ContactUpdate,
    Message,
    MessagePage,
    OtpResult,
    Suppression,
    attachment_from_bytes,
)
from .webhooks import verify_webhook_signature

__all__ = [
    "AgentEmailClient",
    "AgentEmailError",
    "Attachment",
    "Contact",
    "ContactCreate",
    "ContactUpdate",
    "Message",
    "MessagePage",
    "OtpResult",
    "Suppression",
    "attachment_from_bytes",
    "verify_webhook_signature",
]
