"""Small, dependency-free client for the Open Agent Email REST API."""

from .client import (
    AgentEmailClient,
    AgentEmailError,
    Attachment,
    Contact,
    ContactCreate,
    ContactEngagement,
    ContactUpdate,
    IdempotencyKeyReuseError,
    Message,
    MessagePage,
    OtpResult,
    RateLimitError,
    Suppression,
    attachment_from_bytes,
)
from .webhooks import (
    WebhookSignatureError,
    construct_event,
    sign_webhook,
    sign_webhook_v1,
    verify_webhook_signature,
)

__all__ = [
    "AgentEmailClient",
    "AgentEmailError",
    "Attachment",
    "Contact",
    "ContactCreate",
    "ContactEngagement",
    "ContactUpdate",
    "IdempotencyKeyReuseError",
    "RateLimitError",
    "Message",
    "MessagePage",
    "OtpResult",
    "Suppression",
    "attachment_from_bytes",
    "WebhookSignatureError",
    "construct_event",
    "sign_webhook",
    "sign_webhook_v1",
    "verify_webhook_signature",
]
