import json
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Agent, Message, ReviewItem
from app.services.email_service import EmailService
from app.services.hitl_service import HitlService
from app.security import Principal, get_principal

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
                "status": {"type": "string", "enum": ["delivered", "pending_review", "rejected", "blocked"]}
            },
            "required": ["agent_email"]
        }
    },
    {
        "name": "get_message",
        "description": "Fetch full email body, RFC headers, and SPF/DKIM verification details",
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
        "name": "send_message",
        "description": "Send a new outbound email from the agent's email address",
        "inputSchema": {
            "type": "object",
            "properties": {
                "agent_email": {"type": "string"},
                "recipient": {"type": "string"},
                "subject": {"type": "string"},
                "body_text": {"type": "string"}
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
                "body_text": {"type": "string"}
            },
            "required": ["agent_email", "message_id", "body_text"]
        }
    },
    {
        "name": "list_reviews",
        "description": "List items in the Human-in-the-Loop review queue held for threat or approval review",
        "inputSchema": {
            "type": "object",
            "properties": {
                "status": {"type": "string", "enum": ["pending", "approved", "rejected"], "default": "pending"}
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
    admin_tools = {"list_agents", "list_reviews", "approve_review", "reject_review"}
    write_tools = {"send_message", "reply_to_message"}
    if name in admin_tools and not principal.is_admin:
        raise PermissionError("Administrator token required")
    if name in write_tools and not principal.is_admin and principal.scope != "full_access":
        raise PermissionError("Token does not permit sending messages")
    if name in {"list_messages", "get_message", *write_tools} and not principal.is_admin:
        if args.get("agent_email") != principal.agent_email:
            raise PermissionError("Token is not authorized for this agent inbox")
    if name == "list_agents":
        res = await db.execute(select(Agent))
        agents = res.scalars().all()
        return json.dumps([{"email": a.email, "display_name": a.display_name, "status": a.status} for a in agents], indent=2)

    elif name == "list_messages":
        email = args["agent_email"]
        q = select(Message).where(Message.agent_email == email)
        if "direction" in args:
            q = q.where(Message.direction == args["direction"])
        if "status" in args:
            q = q.where(Message.status == args["status"])
        msgs = (await db.execute(q.order_by(Message.created_at.desc()).limit(20))).scalars().all()
        return json.dumps([{
            "id": m.id,
            "direction": m.direction,
            "sender": m.sender,
            "recipient": m.recipient,
            "subject": m.subject,
            "status": m.status,
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
            "spf": msg.spf_status,
            "dkim": msg.dkim_status,
            "dmarc": msg.dmarc_status,
            "threat_score": msg.threat_score
        }, indent=2)

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
            body_text=args["body_text"]
        )
        return json.dumps({"status": "sent", "message_id": msg.id, "rfc_id": msg.rfc_message_id})

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
        reply_msg = await EmailService.send_outbound(
            db=db,
            agent=ag,
            recipient=reply_recipient,
            subject=subj,
            body_text=args["body_text"],
            thread_id=orig.thread_id,
            in_reply_to=orig.rfc_message_id
        )
        return json.dumps({"status": "replied", "message_id": reply_msg.id, "thread_id": reply_msg.thread_id})

    elif name == "list_reviews":
        status_filter = args.get("status", "pending")
        res = await db.execute(
            select(ReviewItem).options(selectinload(ReviewItem.message)).where(ReviewItem.status == status_filter)
        )
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
        rev = await HitlService.resolve_review(db, args["review_id"], "approve", args.get("notes", "Approved via MCP"))
        return json.dumps({"status": "approved", "review_id": rev.id, "message_id": rev.message_id})

    elif name == "reject_review":
        rev = await HitlService.resolve_review(db, args["review_id"], "reject", args.get("notes", "Rejected via MCP"))
        return json.dumps({"status": "rejected", "review_id": rev.id, "message_id": rev.message_id})

    raise ValueError(f"Unknown tool: {name}")
