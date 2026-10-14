import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Agent, Message, ReviewItem
from app.services.email_service import EmailService
from app.services.attachment_utils import decode_attachment_inputs
from app.services.hitl_service import HitlService
from app.services.otp_finder import find_recent_otp
from app.security import Principal, get_principal
from app.schemas import normalize_send_at
from app.routers.mcp_extra import EXT_ADMIN, EXT_NAMES, EXT_READ, EXT_TOOLS, EXT_WRITE, run_ext_tool

router = APIRouter(prefix="/mcp", tags=["Model Context Protocol (MCP)"])

MCP_TOOLS = [
    {
        "name": "list_agents",
        "description": "Lists all AI agent email inboxes configured in Open Agent Email",
        "inputSchema": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "list_messages",
        "description": "List emails received or sent by a specific agent inbox",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string", "description": "Agent email address"},
                "direction": {"type": "string", "enum": ["inbound", "outbound"], "description": "Optional filter"},
                "status": {"type": "string", "enum": ["delivered", "accepted_by_relay", "sending", "delivery_unknown", "pending_review", "rejected", "blocked", "failed"]},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}
            },
            "required": ["agent_email"]
        }
    },
    {
        "name": "get_message",
        "description": "Fetch full email body, RFC headers, and SPF/DKIM/DMARC authentication evidence",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "message_id": {"type": "string"}
            },
            "required": ["agent_email", "message_id"]
        }
    },
    {
        "name": "get_recent_otp",
        "description": "Find a recent verification code in delivered inbound mail for one agent inbox; returns only the code and minimal message metadata.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "since_seconds": {"type": "integer", "minimum": 1, "maximum": 86400, "default": 600},
                "wait_seconds": {"type": "number", "minimum": 0, "maximum": 10, "default": 0}
            },
            "required": ["agent_email"]
        }
    },
    {
        "name": "send_message",
        "description": "Send a new outbound email from the agent's email address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body_text": {"type": "string"},
                "attachments": {"type": "array", "items": {"type": "object", "properties": {
                    "filename": {"type": "string", "maxLength": 255},
                    "content_type": {"type": "string", "maxLength": 255},
                    "content_base64": {"type": "string"}
                }, "required": ["filename", "content_base64"]}},
                "idempotency_key": {"type": "string", "maxLength": 128, "description": "Optional retry key; reuse only for the same request"}
            },
            "required": ["agent_email", "recipient", "subject", "body_text"]
        }
    },
    {
        "name": "reply_to_message",
        "description": "Reply in-thread to an email, preserving RFC Message-ID and In-Reply-To headers",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "message_id": {"type": "string"},
                "body_text": {"type": "string"},
                "attachments": {"type": "array", "items": {"type": "object", "properties": {
                    "filename": {"type": "string", "maxLength": 255},
                    "content_type": {"type": "string", "maxLength": 255},
                    "content_base64": {"type": "string"}
                }, "required": ["filename", "content_base64"]}},
                "idempotency_key": {"type": "string", "maxLength": 128, "description": "Optional retry key; reuse only for the same request"}
            },
            "required": ["agent_email", "message_id", "body_text"]
        }
    },
    {
        "name": "forward_to_human",
        "description": "Hand an email conversation to a human teammate by forwarding the original message with optional context. Outbound approval rules still apply.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "message_id": {"type": "string"},
                "recipient": {"type": "string", "description": "Human teammate email address"},
                "note": {"type": "string", "description": "Optional context for the human"}
            },
            "required": ["agent_email", "message_id", "recipient"]
        }
    },
    {
        "name": "list_reviews",
        "description": "List items in the Human-in-the-Loop review queue held for threat or approval review",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "approved", "rejected"], "default": "pending"},
                "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 50}
            }
        }
    },
    {
        "name": "approve_review",
        "description": "Approve a message held in the HITL review queue, releasing it for agent processing",
        "inputSchema": {
            "type": "object",
            "properties": {
                "review_id": {"type": "string"},
                "notes": {"type": "string"}
            },
            "required": ["review_id"]
        }
    },
    {
        "name": "reject_review",
        "description": "Reject a suspicious message held in the HITL review queue",
        "inputSchema": {
            "type": "object",
            "properties": {
                "review_id": {"type": "string"},
                "notes": {"type": "string"}
            },
            "required": ["review_id"]
        }
    }
]

SEND_AT_PROP = {"type": "string", "format": "date-time", "description": "Defer submission until this UTC time (at most 90 days ahead)"}
for _tool_def in MCP_TOOLS:
    if _tool_def["name"] in {"send_message", "reply_to_message"}:
        _tool_def["inputSchema"]["properties"]["send_at"] = SEND_AT_PROP
MCP_TOOLS.extend(EXT_TOOLS)


def _parse_send_at(value):
    if value is None:
        return None
    from datetime import datetime
    try:
        return normalize_send_at(datetime.fromisoformat(str(value).replace("Z", "+00:00")))
    except ValueError as exc:
        raise ValueError(f"send_at: {exc}") from exc


@router.get("")
@router.get("/info")
async def mcp_info(principal: Principal = Depends(get_principal)):
    """
    Returns server metadata and ready-to-paste configurations for Cursor and Claude Code.
    """
    return {
        "name": "open-agent-email-mcp",
        "version": "1.0.0",
        "protocol": "mcp-streamable-http",
        "endpoints": {
            "rpc": "http://127.0.0.1:8000/mcp/rpc",
            "tools": "http://127.0.0.1:8000/mcp/tools"
        },
        "cursor_config": {
            "mcpServers": {
                "open-agent-email": {
                    "url": "http://127.0.0.1:8000/mcp/rpc"
                }
            }
        },
        "tools_count": len(MCP_TOOLS)
    }

@router.get("/tools")
async def get_tools(principal: Principal = Depends(get_principal)):
    return {"tools": MCP_TOOLS}

@router.post("/rpc")
async def mcp_rpc_handler(request: Request, db: AsyncSession = Depends(get_db), principal: Principal = Depends(get_principal)):
    """
    Handles standard JSON-RPC 2.0 requests from MCP hosts (Cursor, Claude, etc.).
    """
    body = await request.json()
    req_id = body.get("id")
    method = body.get("method")
    params = body.get("params", {})

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {"listChanged": True}
                },
                "serverInfo": {
                    "name": "open-agent-email",
                    "version": "1.0.0"
                }
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": MCP_TOOLS}
        }

    if method == "tools/call":
        tool_name = params.get("name")
        args = params.get("arguments", {})

        try:
            res_text = await execute_mcp_tool(db, tool_name, args, principal)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": res_text}],
                    "isError": False
                }
            }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": f"Error executing {tool_name}: {str(e)}"}],
                    "isError": True
                }
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method {method} not found"}
    }

async def execute_mcp_tool(db: AsyncSession, name: str, args: dict, principal: Principal) -> str:
    admin_tools = {"list_agents"} | EXT_ADMIN
    review_tools = {"list_reviews", "approve_review", "reject_review"}
    write_tools = {"send_message", "reply_to_message", "forward_to_human"} | EXT_WRITE
    if not principal.is_admin and principal.scope == "reviewer" and name not in review_tools | {"whoami"}:
        raise PermissionError("Reviewer credentials are limited to review tools")
    if name in admin_tools and not principal.is_admin:
        raise PermissionError("Administrator token required")
    if name in review_tools and not principal.is_admin and principal.scope != "reviewer":
        raise PermissionError("Reviewer credential required")
    if name in write_tools and not principal.is_admin and principal.scope != "full_access":
        raise PermissionError("Token does not permit sending messages")
    if name in {"list_messages", "get_message", "get_recent_otp", *write_tools, *EXT_READ} and not principal.is_admin:
        if args.get("agent_email") != principal.agent_email:
            raise PermissionError("Token is not authorized for this agent inbox")
    if name == "list_agents":
        res = await db.execute(select(Agent))
        agents = res.scalars().all()
        return json.dumps([{"email": a.email, "display_name": a.display_name, "status": a.status} for a in agents], indent=2)

    elif name == "list_messages":
        email = args["agent_email"]
        limit = args.get("limit", 20)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100")
        q = select(Message).where(Message.agent_email == email)
        if "direction" in args:
            q = q.where(Message.direction == args["direction"])
        if "status" in args:
            q = q.where(Message.status == args["status"])
        msgs = (await db.execute(q.order_by(Message.created_at.desc()).limit(limit))).scalars().all()
        return json.dumps([{
            "id": m.id,
            "direction": m.direction,
            "sender": m.sender,
            "recipient": m.recipient,
            "subject": m.subject,
            "status": m.status,
            "provider_delivery_status": m.provider_delivery_status,
            "threat_score": m.threat_score,
            "created_at": m.created_at.isoformat()
        } for m in msgs], indent=2)

    elif name == "get_message":
        query = select(Message).where(Message.id == args["message_id"])
        if not principal.is_admin:
            query = query.where(Message.agent_email == principal.agent_email)
        res = await db.execute(query)
        msg = res.scalar_one_or_none()
        if not msg:
            raise ValueError(f"Message {args['message_id']} not found")
        return json.dumps({
            "id": msg.id,
            "sender": msg.sender,
            "subject": msg.subject,
            "body_text": msg.body_text,
            "status": msg.status,
            "provider_delivery_status": msg.provider_delivery_status,
            "provider_delivery_error": msg.provider_delivery_error,
            "raw_message_id": msg.raw_message_id,
            "in_reply_to": msg.in_reply_to,
            "references": msg.references,
            "spf": msg.spf_status,
            "dkim": msg.dkim_status,
            "dmarc": msg.dmarc_status,
            "auth_evidence": msg.auth_evidence,
            "threat_score": msg.threat_score
        }, indent=2)

    elif name == "get_recent_otp":
        since_seconds = args.get("since_seconds", 600)
        wait_seconds = args.get("wait_seconds", 0)
        if isinstance(since_seconds, bool) or not isinstance(since_seconds, int) or not 1 <= since_seconds <= 86400:
            raise ValueError("since_seconds must be an integer between 1 and 86400")
        if isinstance(wait_seconds, bool) or not isinstance(wait_seconds, (int, float)) or not 0 <= wait_seconds <= 10:
            raise ValueError("wait_seconds must be a number between 0 and 10")
        match = await find_recent_otp(
            db,
            args["agent_email"],
            since_seconds=since_seconds,
            wait_seconds=float(wait_seconds),
        )
        return json.dumps(match or {"found": False})

    elif name == "send_message":
        res = await db.execute(select(Agent).where(Agent.email == args["agent_email"]))
        ag = res.scalar_one_or_none()
        if not ag:
            raise ValueError(f"Agent {args['agent_email']} not found")
        msg = await EmailService.send_outbound(
            db=db,
            agent=ag,
            recipient=args["recipient"],
            subject=args["subject"],
            body_text=args["body_text"],
            attachments=decode_attachment_inputs(args.get("attachments")),
            idempotency_key=args.get("idempotency_key"),
            send_at=_parse_send_at(args.get("send_at")),
        )
        return json.dumps({
            "status": msg.status,
            "scheduled_for": msg.scheduled_for.isoformat() if msg.scheduled_for else None,
            "message_id": msg.id,
            "rfc_id": msg.rfc_message_id,
            "delivery_error": msg.delivery_error,
        })

    elif name == "reply_to_message":
        res = await db.execute(select(Agent).where(Agent.email == args["agent_email"]))
        ag = res.scalar_one_or_none()
        if not ag:
            raise ValueError(f"Agent {args['agent_email']} not found")
        m_res = await db.execute(select(Message).where(Message.id == args["message_id"], Message.agent_email == args["agent_email"]))
        orig = m_res.scalar_one_or_none()
        if not orig:
            raise ValueError(f"Message {args['message_id']} not found")
        
        reply_recipient = orig.sender if orig.direction == "inbound" else orig.recipient
        subj = f"Re: {orig.subject}" if not orig.subject.lower().startswith("re:") else orig.subject
        in_reply_to, references = EmailService.reply_headers(orig)
        reply_msg = await EmailService.send_outbound(
            db=db,
            agent=ag,
            recipient=reply_recipient,
            subject=subj,
            body_text=args["body_text"],
            attachments=decode_attachment_inputs(args.get("attachments")),
            thread_id=orig.thread_id,
            in_reply_to=in_reply_to,
            references=references,
            idempotency_key=args.get("idempotency_key"),
            send_at=_parse_send_at(args.get("send_at")),
        )
        return json.dumps({
            "status": reply_msg.status,
            "message_id": reply_msg.id,
            "thread_id": reply_msg.thread_id,
            "delivery_error": reply_msg.delivery_error,
        })

    elif name == "forward_to_human":
        original_res = await db.execute(
            select(Message).where(
                Message.id == args["message_id"],
                Message.agent_email == args["agent_email"],
            )
        )
        original = original_res.scalar_one_or_none()
        if not original:
            raise ValueError(f"Message {args['message_id']} not found")
        agent_res = await db.execute(select(Agent).where(Agent.email == args["agent_email"]))
        agent = agent_res.scalar_one_or_none()
        if not agent:
            raise ValueError(f"Agent {args['agent_email']} not found")
        forwarded = await EmailService.forward_to_human(
            db=db,
            agent=agent,
            original=original,
            recipient=args["recipient"],
            note=args.get("note"),
        )
        return json.dumps({
            "status": forwarded.status,
            "message_id": forwarded.id,
            "recipient": forwarded.recipient,
            "delivery_error": forwarded.delivery_error,
        })

    elif name == "list_reviews":
        status_filter = args.get("status", "pending")
        if not isinstance(status_filter, str) or status_filter not in {"pending", "approved", "rejected"}:
            raise ValueError("status must be one of: pending, approved, rejected")
        limit = args.get("limit", 50)
        if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 100:
            raise ValueError("limit must be an integer between 1 and 100")
        query = select(ReviewItem).options(selectinload(ReviewItem.message)).where(ReviewItem.status == status_filter)
        if not principal.is_admin:
            query = query.where(ReviewItem.agent_email == principal.agent_email)
        res = await db.execute(query.order_by(ReviewItem.created_at.desc()).limit(limit))
        reviews = res.scalars().all()
        return json.dumps([{
            "review_id": r.id,
            "message_id": r.message_id,
            "agent_email": r.agent_email,
            "reason": r.reason,
            "threat_score": r.threat_score,
            "status": r.status
        } for r in reviews], indent=2)

    elif name == "approve_review":
        if not principal.is_admin:
            agent_email = await db.scalar(select(ReviewItem.agent_email).where(ReviewItem.id == args["review_id"]))
            if agent_email != principal.agent_email:
                raise PermissionError("Review item is outside this reviewer's inbox scope")
        rev = await HitlService.resolve_review(
            db, args["review_id"], "approve", args.get("notes", "Approved via MCP"), principal.principal_id
        )
        return json.dumps({"status": "approved", "review_id": rev.id, "message_id": rev.message_id})

    elif name == "reject_review":
        if not principal.is_admin:
            agent_email = await db.scalar(select(ReviewItem.agent_email).where(ReviewItem.id == args["review_id"]))
            if agent_email != principal.agent_email:
                raise PermissionError("Review item is outside this reviewer's inbox scope")
        rev = await HitlService.resolve_review(
            db, args["review_id"], "reject", args.get("notes", "Rejected via MCP"), principal.principal_id
        )
        return json.dumps({"status": "rejected", "review_id": rev.id, "message_id": rev.message_id})

    elif name in EXT_NAMES:
        return await run_ext_tool(db, name, args, principal)

    raise ValueError(f"Unknown tool: {name}")
