from sqlalchemy import func, select

from app.database import AsyncSessionLocal
from app.models import Message
from tests.conftest import ADMIN, make_agent, make_key

MSGS = "/v1/agents/a@agents.local/messages"
PAYLOAD = {"recipient": "to@example.com", "subject": "hello", "body_text": "body"}


async def _count():
    async with AsyncSessionLocal() as db:
        return await db.scalar(select(func.count()).select_from(Message))


async def test_idempotency_key_prevents_duplicate_send(client):
    await make_agent(client, "a@agents.local")
    h = {**ADMIN, "Idempotency-Key": "k1"}
    first = await client.post(MSGS, headers=h, json=PAYLOAD)
    second = await client.post(MSGS, headers=h, json=PAYLOAD)
    assert first.status_code == 201 and second.status_code in (200, 201)
    assert first.json()["id"] == second.json()["id"]
    assert await _count() == 1


async def test_idempotency_key_reuse_with_different_body_rejected(client):
    await make_agent(client, "a@agents.local")
    h = {**ADMIN, "Idempotency-Key": "k1"}
    assert (await client.post(MSGS, headers=h, json=PAYLOAD)).status_code == 201
    r = await client.post(MSGS, headers=h, json={**PAYLOAD, "body_text": "different"})
    assert r.status_code == 409
    assert await _count() == 1


async def test_idempotency_keys_are_inbox_scoped(client):
    await make_agent(client, "a@agents.local")
    await make_agent(client, "b@agents.local")
    h = {**ADMIN, "Idempotency-Key": "shared"}
    assert (await client.post(MSGS, headers=h, json=PAYLOAD)).status_code == 201
    assert (await client.post("/v1/agents/b@agents.local/messages", headers=h, json=PAYLOAD)).status_code == 201
    assert await _count() == 2


async def test_forward_replays_idempotently_and_rejects_key_reuse(client):
    await make_agent(client, "a@agents.local")
    original = await client.post(MSGS, headers=ADMIN, json=PAYLOAD)
    assert original.status_code == 201
    url = f"{MSGS}/{original.json()['id']}/forward"
    headers = {**ADMIN, "Idempotency-Key": "forward-1"}
    request = {"recipient": "human@example.com", "note": "Please review"}

    first = await client.post(url, headers=headers, json=request)
    retry = await client.post(url, headers=headers, json=request)
    assert first.status_code == retry.status_code == 201
    assert first.json()["id"] == retry.json()["id"]
    assert await _count() == 2

    changed = await client.post(url, headers=headers, json={**request, "note": "Different context"})
    assert changed.status_code == 409
    assert await _count() == 2


async def test_suppressed_recipient_blocked_before_message_created(client):
    await make_agent(client, "a@agents.local")
    r = await client.post("/v1/agents/a@agents.local/suppressions", headers=ADMIN, json={"email": "To@Example.com"})
    assert r.status_code == 201
    r = await client.post(MSGS, headers=ADMIN, json=PAYLOAD)
    assert r.status_code >= 400 and r.status_code < 500
    assert await _count() == 0


async def test_suppression_is_per_inbox(client):
    await make_agent(client, "a@agents.local")
    await make_agent(client, "b@agents.local")
    await client.post("/v1/agents/a@agents.local/suppressions", headers=ADMIN, json={"email": "to@example.com"})
    assert (await client.post("/v1/agents/b@agents.local/messages", headers=ADMIN, json=PAYLOAD)).status_code == 201


async def test_read_only_key_cannot_send(client):
    await make_agent(client, "a@agents.local")
    ro, _ = await make_key(client, "a@agents.local", "read_only")
    assert (await client.post(MSGS, headers=ro, json=PAYLOAD)).status_code == 403
    assert await _count() == 0
