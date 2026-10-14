"""Validation and decoding for API/MCP supplied outbound attachments."""

import base64
import binascii
import os
import re
from typing import Any

from fastapi import HTTPException

from app.config import settings


def decode_attachment_inputs(items: Any) -> list[dict[str, Any]]:
    if items is None:
        return []
    if not isinstance(items, list) or len(items) > settings.OUTBOUND_MAX_ATTACHMENTS:
        raise HTTPException(status_code=413, detail="Too many attachments")

    decoded: list[dict[str, Any]] = []
    total_bytes = 0
    for item in items:
        if not isinstance(item, dict):
            raise HTTPException(status_code=422, detail="Each attachment must be an object")
        filename = item.get("filename")
        content_type = item.get("content_type", "application/octet-stream")
        encoded = item.get("content_base64")
        if not isinstance(filename, str) or not filename.strip() or len(filename) > 255:
            raise HTTPException(status_code=422, detail="Attachment filename must contain 1 to 255 characters")
        if not isinstance(content_type, str) or len(content_type) > 255:
            raise HTTPException(status_code=422, detail="Invalid attachment content type")
        if not re.fullmatch(r"[A-Za-z0-9!#$&^_.+-]+/[A-Za-z0-9!#$&^_.+-]+", content_type):
            content_type = "application/octet-stream"
        if not isinstance(encoded, str):
            raise HTTPException(status_code=422, detail="Attachment content_base64 is required")
        try:
            content = base64.b64decode(encoded, validate=True)
        except (binascii.Error, ValueError):
            raise HTTPException(status_code=422, detail="Attachment content must be valid base64") from None
        if len(content) > settings.OUTBOUND_MAX_ATTACHMENT_BYTES:
            raise HTTPException(status_code=413, detail="Attachment exceeds configured size limit")
        total_bytes += len(content)
        if total_bytes > settings.OUTBOUND_MAX_TOTAL_ATTACHMENT_BYTES:
            raise HTTPException(status_code=413, detail="Attachments exceed configured total size limit")
        safe_name = os.path.basename(filename.replace("\\", "/"))
        safe_name = "".join(char if char >= " " and char not in "\x7f" else "_" for char in safe_name)[:255]
        decoded.append({"filename": safe_name or "attachment", "content_type": content_type, "content": content})
    return decoded
