from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import logging

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.seeds import seed_initial_data
from app.services.ws_manager import ws_manager
from app.routers import agents, messages, reviews, simulator, mcp, stats

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("open_agent_email")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables if not present
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # 2. Seed default data for immediate demo & testing
    async with AsyncSessionLocal() as session:
        await seed_initial_data(session)
    logger.info("Database initialized and demo agents seeded.")

    yield

    # 3. Shutdown
    logger.info("Shutting down database connection...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="The Open-Source Email Gateway & Authenticated Inboxes for AI Agents and Autonomous Systems.",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow Next.js dev server on :3000
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Live Event WebSocket for Dashboard
@app.websocket("/v1/ws/live")
async def live_dashboard_websocket(websocket: WebSocket):
    await ws_manager.connect_broadcast(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        ws_manager.disconnect_broadcast(websocket)
    except Exception:
        ws_manager.disconnect_broadcast(websocket)

# Routers
app.include_router(stats.router)
app.include_router(agents.router)
app.include_router(messages.router)
app.include_router(reviews.router)
app.include_router(simulator.router)
app.include_router(mcp.router)

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "open-agent-email",
        "version": settings.VERSION,
        "shared_domain": settings.SHARED_DOMAIN
    }

@app.get("/")
async def root():
    return {
        "message": "Welcome to Open Agent Email API",
        "docs": "/docs",
        "mcp": "/mcp/info",
        "health": "/health"
    }
