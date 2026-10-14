"""Helpers for validating signed Open Agent Email webhook requests."""

from __future__ import annotations

import hashlib
import hmac
import time


def verify_webhook_signature(
    raw_body: bytes,
    *,
    event_id: str,
    timestamp: str,
    signature: str,
    secret: str,
    tolerance_seconds: int = 300,
) -> bool:
    """Verify a webhook MAC and timestamp before parsing or processing its body.

    The signature covers the exact raw request bytes. A valid signature does not
    prevent replay within the timestamp window; receivers should also persist
    processed event IDs and reject duplicates.
    """
    if (
        not isinstance(raw_body, bytes)
        or not isinstance(event_id, str)
        or not isinstance(timestamp, str)
        or not isinstance(signature, str)
        or not isinstance(secret, str)
        or not event_id
        or len(event_id) > 256
        or not secret
    ):
        return False
    if (
        isinstance(tolerance_seconds, bool)
        or not isinstance(tolerance_seconds, int)
        or not 0 <= tolerance_seconds <= 86400
        or not timestamp.isascii()
        or not timestamp.isdigit()
    ):
        return False
    if (
        len(timestamp) > 12
        or len(signature) != 71
        or not signature.startswith("sha256=")
        or any(char not in "0123456789abcdef" for char in signature[7:])
    ):
        return False
    try:
        sent_at = int(timestamp)
    except ValueError:
        return False
    if abs(time.time() - sent_at) > tolerance_seconds:
        return False
    try:
        secret_bytes = secret.encode("utf-8")
        message = timestamp.encode("ascii") + b"." + event_id.encode("utf-8") + b"." + raw_body
    except UnicodeEncodeError:
        return False
    digest = hmac.new(secret_bytes, message, hashlib.sha256).hexdigest()
    expected = f"sha256={digest}"
    return hmac.compare_digest(expected, signature)
