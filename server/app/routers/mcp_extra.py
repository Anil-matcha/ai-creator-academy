"""Additional MCP tools. Each delegates to the same code paths as the REST API."""

import datetime
import json

from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Agent, EmailTemplate, RecipientSuppression
from app.routers import contacts, conversations, messages, meta, suppressions
from app.schemas import MessageLabelsUpdate, RecipientSuppressionCreate
from app.security import Principal

_EMAIL = {"agent_email": {"type": "string", "description": "Agent inbox address"}}
_MSG = {**_EMAIL, "message_id": {"type": "string"}}


def _tool(name, description, properties=None, required=None):
    return {"name": name, "description": description,
            "inputSchema": {"type": "object", "properties": properties or {}, "required": required or []}}


EXT_TOOLS = [
    _tool("whoami", "Describe the credential making this call (admin or inbox-scoped key, scope, inbox)."),
    _tool("list_conversations", "List recent email threads with message/unread counts, participants and labels.",
          {**_EMAIL, "limit": {"type": "integer", "minimum": 1, "maximum": 200, "default": 50}}, ["agent_email"]),
    _tool("get_conversation", "Fetch every message in one thread, oldest first.",
          {**_EMAIL, "conversation_id": {"type": "string"}}, ["agent_email", "conversation_id"]),
    _tool("get_message_lifecycle", "Chronological timeline of review, queueing, retries and provider delivery outcomes.",
          _MSG, ["agent_email", "message_id"]),
    _tool("get_agent_metrics", "Message counts by direction/status plus unread and pending-review totals.",
          _EMAIL, ["agent_email"]),
    _tool("get_protection", "Read the inbox's threat sensitivity and outbound approval gate.", _EMAIL, ["agent_email"]),
    _tool("update_protection", "Administrator only: set threat sensitivity (off/low/medium/high) and the approval gate.",
          {**_EMAIL, "threat_sensitivity": {"type": "string", "enum": ["off", "low", "medium", "high"]},
           "hitl_enabled": {"type": "boolean"}}, ["agent_email", "threat_sensitivity", "hitl_enabled"]),
    _tool("update_message_labels", "Replace a message's labels (triage tags such as needs-human).",
          {**_MSG, "labels": {"type": "array", "items": {"type": "string"}, "maxItems": 20}},
          ["agent_email", "message_id", "labels"]),
    _tool("delete_message", "Move a message to trash; cancels a scheduled send that has not been submitted.",
          _MSG, ["agent_email", "message_id"]),
    _tool("restore_message", "Restore a trashed message to the inbox.", _MSG, ["agent_email", "message_id"]),
    _tool("list_contacts", "List the inbox's contacts.",
          {**_EMAIL, "limit": {"type": "integer", "minimum": 1, "maximum": 500, "default": 100}}, ["agent_email"]),
    _tool("list_templates", "List the inbox's saved email templates.", _EMAIL, ["agent_email"]),
    _tool("list_suppressions", "List recipients this inbox will not email.", _EMAIL, ["agent_email"]),
    _tool("create_agent_suppression", "Block outbound email to one recipient from this inbox.",
          {**_EMAIL, "email": {"type": "string"}, "reason": {"type": "string"}}, ["agent_email", "email"]),
]

EXT_ADMIN = {"update_protection"}
EXT_WRITE = {"update_message_labels", "delete_message", "restore_message", "create_agent_suppression"}
EXT_READ = {"list_conversations", "get_conversation", "get_message_lifecycle", "get_agent_metrics",
            "get_protection", "list_contacts", "list_templates", "list_suppressions"}
EXT_NAMES = {t["name"] for t in EXT_TOOLS}


def _dump(value):
    if isinstance(value, list):
        return [_dump(v) for v in value]
    if isinstance(value, dict):
        return {k: _dump(v) for k, v in value.items()}
    if isinstance(value, BaseModel):
        return value.model_dump(mode="json")
    if isinstance(value, datetime.datetime):
        return value.isoformat()
    if hasattr(value, "__table__"):
        return {c.name: _dump(getattr(value, c.name)) for c in value.__table__.columns
                if c.name not in {"body_html", "content", "key_hash"}}
    return value


def _int(args, key, default, lo, hi):
    value = args.get(key, default)
    if isinstance(value, bool) or not isinstance(value, int) or not lo <= value <= hi:
        raise ValueError(f"{key} must be an integer between {lo} and {hi}")
    return value


async def run_ext_tool(db: AsyncSession, name: str, args: dict, principal: Principal) -> str:
    email = args.get("agent_email")
    if name == "whoami":
        return json.dumps(await meta.whoami(principal))
    if name == "list_conversations":
        return json.dumps(_dump(await conversations.list_conversations(email, _int(args, "limit", 50, 1, 200), db)))
    if name == "get_conversation":
        return json.dumps(_dump(await conversations.get_conversation(email, args["conversation_id"], db)))
    if name == "get_message_lifecycle":
        return json.dumps(_dump(await messages.get_message_lifecycle(email, args["message_id"], db)))
    if name == "get_agent_metrics":
        return json.dumps(await meta.agent_metrics(email, db))
    if name == "get_protection":
        return json.dumps(await meta.get_protection(email, db))
    if name == "update_protection":
        body = meta.ProtectionUpdate(threat_sensitivity=args["threat_sensitivity"], hitl_enabled=args["hitl_enabled"])
        return json.dumps(await meta.update_protection(email, body, db))
    if name == "update_message_labels":
        req = MessageLabelsUpdate(labels=args["labels"])
        return json.dumps(_dump(await messages.update_message_labels(email, args["message_id"], req, db)))
    if name == "delete_message":
        return json.dumps(_dump(await messages.trash_message(email, args["message_id"], db)))
    if name == "restore_message":
        return json.dumps(_dump(await messages.restore_message(email, args["message_id"], db)))
    if name == "list_contacts":
        return json.dumps(_dump(await contacts.list_contacts(email, _int(args, "limit", 100, 1, 500), db)))
    if name == "list_templates":
        agent = await db.scalar(select(Agent.id).where(Agent.email == email))
        if not agent:
            raise ValueError(f"Agent {email} not found")
        rows = (await db.execute(select(EmailTemplate).where(
            EmailTemplate.agent_email == email))).scalars().all()
        return json.dumps([{"id": t.id, "name": t.name, "subject": t.subject} for t in rows])
    if name == "list_suppressions":
        rows = (await db.execute(select(RecipientSuppression).where(
            RecipientSuppression.agent_email == email))).scalars().all()
        return json.dumps([{"id": r.id, "email": r.email, "reason": r.reason} for r in rows])
    if name == "create_agent_suppression":
        req = RecipientSuppressionCreate(email=args["email"], reason=args.get("reason"))
        return json.dumps(_dump(await suppressions.add_suppression(email, req, db)))
    raise ValueError(f"Unknown tool: {name}")
