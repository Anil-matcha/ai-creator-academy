# Open Agent Email

<div align="center">

### The Open-Source Email Gateway & Authenticated Inboxes for AI Agents.

Give autonomous AI agents real, two-way email inboxes with cryptographic SPF/DKIM/DMARC evidence, prompt-injection content screening, and human-in-the-loop review gates.

**FastAPI Backend** · **Next.js 15 & Tailwind CSS v4 Dashboard** · **Model Context Protocol (MCP)** · **Async SQLite / PostgreSQL**

</div>

---

## 🌟 Key Capabilities

1. **Two-Way Agent Inboxes**: Create dedicated email addresses for agents (e.g., `support@agents.local`, `sales@agents.local`, `security@agents.local`).
2. **RFC Thread Topology**: Automatically tracks `Message-ID`, `In-Reply-To`, and `References` so AI agents participate in real Outlook/Gmail threads seamlessly.
3. **Inbound Prompt-Injection Screening**: Built-in heuristic threat scanner intercepts indirect prompt injections, hidden CSS/zero-font smuggling, jailbreak delimiters, and Markdown image exfiltration.
4. **Human-in-the-Loop (HITL) Queue**: Dangerous or sensitive emails are placed in `pending_review` until approved or rejected by a human operator in the dashboard or via MCP.
5. **Real-Time WebSocket Streaming**: Agents subscribe to `/v1/agents/{email}/ws` to stream new emails in real time without needing public URLs or ngrok tunnels.
6. **Model Context Protocol (MCP) Server**: Point Cursor, Claude Code, or Windsurf at `http://localhost:8000/mcp/rpc` to give coding agents direct email capabilities.
7. **Interactive Simulator**: Test clean customer emails or simulate sophisticated prompt-injection attacks directly in the UI with instant diagnosis.

---

## 🏗️ Architecture

```
       Customer (Gmail / Outlook)  ·  External Systems
                       │            ▲
         Inbound Email │            │ Outbound Send / Reply
                       ▼            │
         ┌──────────────────────────────────────┐
         │     Open Agent Email Gateway         │
         │  • SPF / DKIM / DMARC verification   │
         │  • Heuristic Prompt-Injection Scan   │
         │  • Human-in-the-Loop (HITL) Queue    │
         │  • RFC Threading (In-Reply-To)       │
         └──────────────────┬───────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
    Next.js Dashboard            Autonomous AI Agents
    • Live Inbox View            • WebSocket Stream (:8000/v1/agents/{email}/ws)
    • HITL Review Queue          • MCP Server (:8000/mcp/rpc)
    • Attack Simulator           • REST API (:8000/v1)
```

---

## 🚀 Quickstart

### 1. Start the FastAPI Backend

```bash
cd backend
# Create virtual environment
python -m venv .venv

# Activate venv:
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the backend
python run.py
```

- API Server: `http://127.0.0.1:8000`
- Interactive OpenAPI Docs: `http://127.0.0.1:8000/docs`
- MCP Endpoint: `http://127.0.0.1:8000/mcp/info`

### 2. Start the Next.js Frontend Dashboard

```bash
cd frontend
npm install
npm run dev
```

Open `http://localhost:3000` in your browser.

---

## 🤖 Connecting to Coding Agents via MCP

### Cursor Setup
Add to `.cursor/mcp.json` or `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "open-agent-email": {
      "url": "http://127.0.0.1:8000/mcp/rpc"
    }
  }
}
```

### Claude Code Setup
```bash
claude mcp add open-agent-email http://127.0.0.1:8000/mcp/rpc
```

### Available MCP Tools
- `list_agents`: View available agent email inboxes.
- `list_messages`: Read inbound and outbound emails for an inbox.
- `get_message`: Fetch full email body and security scan details.
- `send_message`: Send an outbound email.
- `reply_to_message`: Reply in-thread with RFC headers preserved.
- `list_reviews`: View held emails awaiting human approval.
- `approve_review`: Approve and release a held message.
- `reject_review`: Reject a suspicious message.

---

## 🔒 Threat Screening Rules

The scanner flags:
- **Instruction Overrides**: `Ignore previous instructions`, `Disregard system directives`, etc.
- **Hidden Text & Evasion**: `display:none`, `font-size:0`, `visibility:hidden`, zero-width Unicode characters.
- **Chat Delimiter Smuggling**: `<|im_start|>`, `[INST]`, `### System:`.
- **Data Exfiltration**: Markdown image link traps and credential requests.
- **Base64 Smuggling**: Decodes and inspects obfuscated instructions.

Thresholds are configurable per-agent: `off`, `low`, `medium`, or `high`.

---

## 📄 License
Apache 2.0
