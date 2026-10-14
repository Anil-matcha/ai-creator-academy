from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio

from app.config import settings
from app.database import engine, Base, AsyncSessionLocal
from app.services.ws_manager import ws_manager
from app.routers import agents, messages, reviews, domains, settings_router, api_keys, mcp, stats, outbox
from app.security import authenticate_token
from app.rate_limit import ApiRateLimitMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger("open_agent_email")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Startup: Create tables if not present
    logger.info("Initializing database schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        def apply_additive_schema_updates(sync_conn):
            from sqlalchemy import inspect, text
            inspector = inspect(sync_conn)
            timestamp_type = "DATETIME" if sync_conn.dialect.name == "sqlite" else "TIMESTAMP"
            key_columns = {column["name"] for column in inspector.get_columns("api_keys")}
            message_columns = {column["name"] for column in inspector.get_columns("messages")}
            if "agent_email" not in key_columns:
                sync_conn.execute(text("ALTER TABLE api_keys ADD COLUMN agent_email VARCHAR(255)"))
            if "expires_at" not in key_columns:
                sync_conn.execute(text(f"ALTER TABLE api_keys ADD COLUMN expires_at {timestamp_type}"))
            if "delivery_error" not in message_columns:
                sync_conn.execute(text("ALTER TABLE messages ADD COLUMN delivery_error TEXT"))
            review_columns = {column["name"] for column in inspector.get_columns("review_items")}
            if "reviewed_by" not in review_columns:
                sync_conn.execute(text("ALTER TABLE review_items ADD COLUMN reviewed_by VARCHAR(128)"))
            if "raw_message_id" not in message_columns:
                sync_conn.execute(text("ALTER TABLE messages ADD COLUMN raw_message_id VARCHAR(998)"))
            if "idempotency_key" not in message_columns:
                sync_conn.execute(text("ALTER TABLE messages ADD COLUMN idempotency_key VARCHAR(128)"))
            if "request_hash" not in message_columns:
                sync_conn.execute(text("ALTER TABLE messages ADD COLUMN request_hash VARCHAR(64)"))
            if "auth_evidence" not in message_columns:
                sync_conn.execute(text("ALTER TABLE messages ADD COLUMN auth_evidence JSON"))
            outbox_columns = {column["name"] for column in inspector.get_columns("outbound_jobs")}
            if "retried_by" not in outbox_columns:
                sync_conn.execute(text("ALTER TABLE outbound_jobs ADD COLUMN retried_by VARCHAR(128)"))
            if "retried_at" not in outbox_columns:
                sync_conn.execute(text(f"ALTER TABLE outbound_jobs ADD COLUMN retried_at {timestamp_type}"))
            message_indexes = {index["name"] for index in inspector.get_indexes("messages")}
            if "ix_messages_raw_message_id" not in message_indexes:
                sync_conn.execute(text("CREATE INDEX ix_messages_raw_message_id ON messages (raw_message_id)"))
            if "uq_messages_agent_idempotency_key" not in message_indexes:
                sync_conn.execute(text("CREATE UNIQUE INDEX uq_messages_agent_idempotency_key ON messages (agent_email, idempotency_key)"))
        await conn.run_sync(apply_additive_schema_updates)
    logger.info("Database schema ready.")

    from app.services.outbound_worker import run_outbound_worker
    outbound_task = asyncio.create_task(run_outbound_worker(), name="outbound-mail-worker")
    app.state.outbound_worker_task = outbound_task

    # 2. Start inbound SMTP server daemon on port 2525
    smtp_server = None
    try:
        from smtp_receiver import start_smtp_server
        smtp_server = await start_smtp_server()
        logger.info("Inbound SMTP listener active on port 2525.")
    except Exception as e:
        logger.warning(f"Could not bind SMTP port 2525 on startup: {e}")
    app.state.smtp_server = smtp_server

    yield

    # 3. Shutdown
    if smtp_server:
        logger.info("Shutting down inbound SMTP listener...")
        smtp_server.close()
        await smtp_server.wait_closed()

    outbound_task.cancel()
    try:
        await outbound_task
    except asyncio.CancelledError:
        pass

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
# Register rate limiting before CORS so CORS headers are still added to 429 replies.
app.add_middleware(
    ApiRateLimitMiddleware,
    requests=settings.API_RATE_LIMIT_REQUESTS,
    window_seconds=settings.API_RATE_LIMIT_WINDOW_SECONDS,
    max_clients=settings.API_RATE_LIMIT_MAX_CLIENTS,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global Live Event WebSocket for Dashboard
@app.websocket("/v1/ws/live")
async def live_dashboard_websocket(websocket: WebSocket):
    scheme, _, token = websocket.headers.get("authorization", "").partition(" ")
    if scheme.lower() != "bearer":
        token = websocket.query_params.get("api_key", "")
    async with AsyncSessionLocal() as db:
        try:
            principal = await authenticate_token(token, db)
        except Exception:
            await websocket.close(code=1008)
            return
    if not principal.is_admin:
        await websocket.close(code=1008)
        return
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
app.include_router(outbox.router)
app.include_router(agents.router)
app.include_router(messages.router)
app.include_router(reviews.router)
app.include_router(domains.router)
app.include_router(settings_router.router)
app.include_router(api_keys.router)
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


@app.get("/ready")
async def readiness_check():
    from sqlalchemy import func, select, text
    from app.models import OutboundJob

    database_ready = False
    pending_jobs = None
    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
            pending_jobs = await db.scalar(
                select(func.count()).select_from(OutboundJob).where(OutboundJob.status == "pending")
            )
            database_ready = True
    except Exception:
        logger.exception("Readiness check could not access the database")

    smtp_server = getattr(app.state, "smtp_server", None)
    smtp_ready = bool(smtp_server and smtp_server.is_serving())
    worker = getattr(app.state, "outbound_worker_task", None)
    worker_ready = bool(worker and not worker.done())
    ready = database_ready and smtp_ready and worker_ready
    return JSONResponse(
        status_code=200 if ready else 503,
        content={
            "status": "ready" if ready else "not_ready",
            "components": {
                "database": "ready" if database_ready else "unavailable",
                "smtp_listener": "ready" if smtp_ready else "unavailable",
                "outbound_worker": "ready" if worker_ready else "unavailable",
            },
            "outbox_pending": pending_jobs,
        },
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to Open Agent Email API",
        "docs": "/docs",
        "mcp": "/mcp/info",
        "health": "/health"
    }
