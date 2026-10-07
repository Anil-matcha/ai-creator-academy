import uuid
import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models import Agent
from app.schemas import AgentCreate, AgentUpdate, AgentResponse
from app.services.ws_manager import ws_manager

router = APIRouter(prefix="/v1/agents", tags=["Agents"])

@router.get("", response_model=List[AgentResponse])
async def list_agents(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Agent).order_by(Agent.created_at.desc()))
    return result.scalars().all()

@router.post("", response_model=AgentResponse, status_code=201)
async def create_agent(agent_in: AgentCreate, db: AsyncSession = Depends(get_db)):
    # Check if email taken
    res = await db.execute(select(Agent).where(Agent.email == agent_in.email))
    if res.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Agent with this email already exists")

    agent_id = f"ag_{uuid.uuid4().hex[:10]}"
    agent = Agent(
        id=agent_id,
        email=agent_in.email,
        display_name=agent_in.display_name,
        description=agent_in.description or "",
        threat_sensitivity=agent_in.threat_sensitivity,
        hitl_enabled=agent_in.hitl_enabled,
        auto_reply_enabled=agent_in.auto_reply_enabled,
        auto_reply_prompt=agent_in.auto_reply_prompt or "You are an autonomous AI assistant.",
        status="active",
        created_at=datetime.datetime.utcnow(),
        updated_at=datetime.datetime.utcnow()
    )
    db.add(agent)
    await db.commit()
    await db.refresh(agent)
    return agent

@router.get("/{email}", response_model=AgentResponse)
async def get_agent(email: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Agent).where(Agent.email == email))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent

@router.patch("/{email}", response_model=AgentResponse)
async def update_agent(email: str, update_in: AgentUpdate, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Agent).where(Agent.email == email))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")

    update_data = update_in.model_dump(exclude_unset=True)
    for field, val in update_data.items():
        setattr(agent, field, val)
    agent.updated_at = datetime.datetime.utcnow()

    await db.commit()
    await db.refresh(agent)
    return agent

@router.delete("/{email}", status_code=204)
async def delete_agent(email: str, db: AsyncSession = Depends(get_db)):
    res = await db.execute(select(Agent).where(Agent.email == email))
    agent = res.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    await db.delete(agent)
    await db.commit()
    return None

@router.websocket("/{email}/ws")
async def agent_websocket_endpoint(websocket: WebSocket, email: str):
    """
    Real-time inbound message push stream for an agent.
    Agents connect without needing public URLs or ngrok tunnels.
    """
    await ws_manager.connect_agent(email, websocket)
    try:
        while True:
            # Keep-alive ping/pong
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect_agent(email, websocket)
    except Exception:
        ws_manager.disconnect_agent(email, websocket)
