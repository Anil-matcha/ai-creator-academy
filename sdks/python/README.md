# Open Agent Email Python SDK

A small synchronous Python client for the core agent-to-human email workflows. It uses only the Python standard library and supports Python 3.11+.

## Quickstart

Create an inbox-scoped API key with read access (or full access to send), then:

```python
from open_agent_email import AgentEmailClient

client = AgentEmailClient(
    "https://mail.example.com",
    api_key="oae_live_your_inbox_key",
    timeout=15,
)

messages = client.list_messages("agent@example.com", limit=20, direction="inbound")
for message in messages:
    print(message["id"], message["sender"], message["subject"])

page = client.get_message_page("agent@example.com", query="invoice", limit=50)
for message in page["items"]:
    print(message["id"], message["subject"])
if page["next_cursor"]:
    next_page = client.get_message_page(
        "agent@example.com", query="invoice", limit=50, cursor=page["next_cursor"]
    )

message = client.get_message("agent@example.com", messages[0]["id"])
print(message["body_text"])

result = client.get_recent_otp("agent@example.com", since_seconds=600, wait_seconds=5)
if result.get("found"):
    print("Verification code:", result["code"])
```

`get_message_page` searches sender and subject and accepts only `inbound` or `outbound` direction filters. Keep the same search and direction parameters when following a `next_cursor`.

The SDK sends the key in the `Authorization: Bearer` header. Keep it in a secret manager or environment variable, and use HTTPS except for local development. The client never prints or includes the token in its API exceptions. Each socket operation uses a bounded timeout (15 seconds by default, configurable up to 60 seconds).

## Send and reply

```python
sent = client.send_message(
    "agent@example.com",
    recipient="person@example.net",
    subject="Your support request",
    body_text="Hi Alex, I have an update for you.",
    idempotency_key="ticket-492-update-1",  # reuse on retry of the same request
)

reply = client.reply_message(
    "agent@example.com",
    message_id="inbound-message-id",
    body_text="Thanks for the details. I will follow up shortly.",
    idempotency_key="inbound-message-id-reply-1",
)
```

The server requires a full-access key to send. Idempotency keys must be 1–128 characters; reusing a key with changed content returns HTTP 409.

## Attachments

Attachments are submitted as base64 JSON. Use `attachment_from_bytes` to construct the value without managing the encoding yourself:

```python
from pathlib import Path
from open_agent_email import AgentEmailClient, attachment_from_bytes

client = AgentEmailClient("https://mail.example.com", api_key="oae_live_your_inbox_key")
pdf = attachment_from_bytes(
    "invoice.pdf",
    Path("invoice.pdf").read_bytes(),
    "application/pdf",
)
client.send_message(
    "agent@example.com",
    recipient="person@example.net",
    subject="Invoice",
    body_text="The invoice is attached.",
    attachments=[pdf],
    idempotency_key="invoice-2026-10-14",
)
```

The server defaults to at most 10 attachments, 10 MiB per file, and 20 MiB total decoded content; the encoded JSON request is also subject to the server's request-size limit.

## Errors

`AgentEmailError` includes `status_code` and the server's safe `detail` (when available). Handle 401/403 as credential or scope issues, 404 as a missing inbox/message, 409 as an idempotency conflict, and transport/timeout failures as retryable only when using the same idempotency key for sends.

```python
from open_agent_email import AgentEmailError

try:
    client.send_message(...)
except AgentEmailError as exc:
    print(exc.status_code, exc.detail)
```

## Verify inbound webhooks

Verify the signature against the exact raw request body before decoding JSON. Then deduplicate the event ID in durable storage; retries and manual replays reuse that ID.

```python
from open_agent_email import verify_webhook_signature

valid = verify_webhook_signature(
    raw_body,  # exact bytes read from the request, before JSON parsing
    event_id=request.headers.get("X-Webhook-Event-Id", ""),
    timestamp=request.headers.get("X-Webhook-Timestamp", ""),
    signature=request.headers.get("X-Webhook-Signature", ""),
    secret=signing_secret,
    tolerance_seconds=300,
)
if not valid:
    return Response(status_code=401)

event = json.loads(raw_body)
# Atomically record the event ID and apply the event; reject an already-recorded ID.
```

The helper checks the timestamp window and compares the HMAC-SHA256 signature in constant time. The receiver still needs an atomic event-ID deduplication store to handle retries safely. Route on the payload's `event_type`; acknowledge `webhook.test` without treating it as an email.

## Local install

From the repository root:

```bash
python -m pip install ./sdks/python
```
