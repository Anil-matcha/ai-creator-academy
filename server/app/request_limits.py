"""HTTP request body size guard for REST and MCP endpoints."""

import json
from collections.abc import Callable
from typing import Any


class RequestBodyTooLarge(Exception):
    pass


class RequestBodyLimitMiddleware:
    def __init__(self, app, max_bytes: int):
        self.app = app
        self.max_bytes = max_bytes

    async def _reject(self, send: Callable) -> None:
        body = json.dumps({"detail": "Request body exceeds configured size limit"}).encode("utf-8")
        await send({
            "type": "http.response.start",
            "status": 413,
            "headers": [(b"content-type", b"application/json"), (b"content-length", str(len(body)).encode())],
        })
        await send({"type": "http.response.body", "body": body})

    async def __call__(self, scope: dict[str, Any], receive: Callable, send: Callable) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        content_lengths = [value for name, value in scope.get("headers", []) if name.lower() == b"content-length"]
        if content_lengths:
            try:
                if any(int(value) > self.max_bytes for value in content_lengths):
                    await self._reject(send)
                    return
            except ValueError:
                pass  # The streaming check below still enforces the cap.

        consumed = 0

        async def receive_limited():
            nonlocal consumed
            message = await receive()
            if message["type"] == "http.request":
                consumed += len(message.get("body", b""))
                if consumed > self.max_bytes:
                    raise RequestBodyTooLarge
            return message

        try:
            await self.app(scope, receive_limited, send)
        except RequestBodyTooLarge:
            await self._reject(send)
