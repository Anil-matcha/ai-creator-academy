"""Typed synchronous client for Open Agent Email's core agent workflows."""

from __future__ import annotations

import base64
import json
from typing import Any, TypedDict
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import HTTPRedirectHandler, Request, build_opener
from urllib.parse import urlsplit


class Attachment(TypedDict):
    filename: str
    content_type: str
    content_base64: str


class Message(TypedDict, total=False):
    id: str
    agent_email: str
    direction: str
    sender: str
    recipient: str
    subject: str
    body_text: str
    body_html: str | None
    thread_id: str
    status: str
    created_at: str


class OtpResult(TypedDict, total=False):
    found: bool
    code: str
    message_id: str
    received_at: str
    sender: str
    subject: str


class MessagePage(TypedDict):
    items: list[Message]
    next_cursor: str | None


class AgentEmailError(Exception):
    """An API or transport error. The bearer token is never included in errors."""

    def __init__(self, message: str, *, status_code: int | None = None, detail: Any = None):
        super().__init__(message)
        self.status_code = status_code
        self.detail = detail


class _NoRedirect(HTTPRedirectHandler):
    """Do not let urllib forward bearer credentials to a redirect target."""

    def redirect_request(self, req: Request, fp: Any, code: int, msg: str, headers: Any, newurl: str) -> None:
        return None


def attachment_from_bytes(
    filename: str, content: bytes, content_type: str = "application/octet-stream"
) -> Attachment:
    """Build an API attachment object from raw file bytes."""
    return {
        "filename": filename,
        "content_type": content_type,
        "content_base64": base64.b64encode(content).decode("ascii"),
    }


class AgentEmailClient:
    """Synchronous REST client. Use an inbox-scoped API key where possible."""

    def __init__(self, base_url: str, api_key: str, *, timeout: float = 15.0):
        base_url = base_url.strip().rstrip("/")
        parsed = urlsplit(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.hostname:
            raise ValueError("base_url must be an absolute http:// or https:// URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("base_url cannot contain credentials, a query, or a fragment")
        if parsed.scheme == "http" and parsed.hostname not in {"localhost", "127.0.0.1", "::1"}:
            raise ValueError("HTTP is allowed only for localhost; use HTTPS for remote servers")
        if not api_key or any(char.isspace() for char in api_key):
            raise ValueError("api_key must be a non-empty token without whitespace")
        if not 0 < timeout <= 60:
            raise ValueError("timeout must be greater than 0 and no more than 60 seconds")
        self.base_url = base_url
        self._api_key = api_key
        self.timeout = timeout
        self._opener = build_opener(_NoRedirect())

    @staticmethod
    def _inbox_path(inbox: str) -> str:
        return quote(inbox, safe="")

    def _request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str | int | float] | None = None,
        payload: dict[str, Any] | None = None,
        idempotency_key: str | None = None,
    ) -> Any:
        url = f"{self.base_url}{path}"
        if query:
            url += "?" + urlencode(query)
        headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
        data = None
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if idempotency_key is not None:
            if not 1 <= len(idempotency_key) <= 128:
                raise ValueError("idempotency_key must contain 1–128 characters")
            headers["Idempotency-Key"] = idempotency_key
        request = Request(url, data=data, headers=headers, method=method)
        try:
            with self._opener.open(request, timeout=self.timeout) as response:
                raw = response.read()
        except HTTPError as exc:
            raw = exc.read(64 * 1024)
            try:
                body = json.loads(raw.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                body = None
            detail = body.get("detail") if isinstance(body, dict) else body
            raise AgentEmailError(
                f"Open Agent Email API returned HTTP {exc.code}",
                status_code=exc.code,
                detail=detail,
            ) from None
        except (URLError, TimeoutError, OSError) as exc:
            # Avoid including request headers or URL credentials in transport diagnostics.
            reason = getattr(exc, "reason", None)
            raise AgentEmailError(f"Open Agent Email request failed: {reason or type(exc).__name__}") from None
        if not raw:
            return None
        try:
            return json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise AgentEmailError("Open Agent Email returned invalid JSON") from exc

    def list_messages(
        self,
        inbox: str,
        *,
        direction: str | None = None,
        status: str | None = None,
        thread_id: str | None = None,
        limit: int = 50,
    ) -> list[Message]:
        """List messages, newest first (server limit is 1–500)."""
        if not 1 <= limit <= 500:
            raise ValueError("limit must be between 1 and 500")
        query: dict[str, str | int | float] = {"limit": limit}
        for key, value in (("direction", direction), ("status", status), ("thread_id", thread_id)):
            if value is not None:
                query[key] = value
        return self._request("GET", f"/v1/agents/{self._inbox_path(inbox)}/messages", query=query)

    def get_message(self, inbox: str, message_id: str) -> Message:
        """Fetch one message by ID."""
        return self._request(
            "GET", f"/v1/agents/{self._inbox_path(inbox)}/messages/{quote(message_id, safe='')}"
        )

    def get_message_page(
        self,
        inbox: str,
        *,
        direction: str | None = None,
        query: str | None = None,
        limit: int = 50,
        cursor: str | None = None,
    ) -> MessagePage:
        """Fetch a stable, cursor-paginated inbox page, optionally searching sender/subject."""
        if not 1 <= limit <= 100:
            raise ValueError("limit must be between 1 and 100")
        if direction is not None and direction not in {"inbound", "outbound"}:
            raise ValueError("direction must be 'inbound' or 'outbound'")
        if query is not None and len(query) > 200:
            raise ValueError("query must be no more than 200 characters")
        params: dict[str, str | int | float] = {"limit": limit}
        if direction is not None:
            params["direction"] = direction
        if query:
            params["q"] = query
        if cursor:
            params["cursor"] = cursor
        return self._request(
            "GET", f"/v1/agents/{self._inbox_path(inbox)}/messages/page", query=params
        )

    def send_message(
        self,
        inbox: str,
        *,
        recipient: str,
        subject: str,
        body_text: str,
        body_html: str | None = None,
        thread_id: str | None = None,
        attachments: list[Attachment] | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Send a message, optionally with a retry-safe idempotency key."""
        payload: dict[str, Any] = {"recipient": recipient, "subject": subject, "body_text": body_text}
        if body_html is not None:
            payload["body_html"] = body_html
        if thread_id is not None:
            payload["thread_id"] = thread_id
        if attachments:
            payload["attachments"] = attachments
        return self._request(
            "POST", f"/v1/agents/{self._inbox_path(inbox)}/messages", payload=payload,
            idempotency_key=idempotency_key,
        )

    def reply_message(
        self,
        inbox: str,
        message_id: str,
        *,
        body_text: str,
        body_html: str | None = None,
        attachments: list[Attachment] | None = None,
        idempotency_key: str | None = None,
    ) -> Message:
        """Reply in the original message thread."""
        payload: dict[str, Any] = {"body_text": body_text}
        if body_html is not None:
            payload["body_html"] = body_html
        if attachments:
            payload["attachments"] = attachments
        return self._request(
            "POST",
            f"/v1/agents/{self._inbox_path(inbox)}/messages/{quote(message_id, safe='')}/reply",
            payload=payload,
            idempotency_key=idempotency_key,
        )

    def get_recent_otp(
        self,
        inbox: str,
        *,
        since_seconds: int = 600,
        wait_seconds: float = 0,
    ) -> OtpResult:
        """Find a recent contextual verification code without fetching the email body."""
        if not 1 <= since_seconds <= 86400:
            raise ValueError("since_seconds must be between 1 and 86400")
        if not 0 <= wait_seconds <= 10:
            raise ValueError("wait_seconds must be between 0 and 10")
        return self._request(
            "GET",
            f"/v1/agents/{self._inbox_path(inbox)}/messages/otp",
            query={"since_seconds": since_seconds, "wait_seconds": wait_seconds},
        )
