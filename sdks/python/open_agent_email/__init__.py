"""Small, dependency-free client for the Open Agent Email REST API."""

from .client import (
    AgentEmailClient,
    AgentEmailError,
    Attachment,
    Message,
    OtpResult,
    attachment_from_bytes,
)

__all__ = [
    "AgentEmailClient",
    "AgentEmailError",
    "Attachment",
    "Message",
    "OtpResult",
    "attachment_from_bytes",
]
