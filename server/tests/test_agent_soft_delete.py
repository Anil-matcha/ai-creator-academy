from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models import Agent, Contact
from tests.conftest import ADMIN, make_agent, make_key


async def test_delete_is_soft_and_restorable(client):
    await make_agent(client, "a@agents.local")
    assert (await client.delete("/v1/agents/a@agents.local", headers=ADMIN)).status_code == 204
    assert (await client.get("/v1/agents", headers=ADMIN)).json() == []
    listed = (await client.get("/v1/agents?include_deleted=true", headers=ADMIN)).json()
    assert [a["email"] for a in listed] == ["a@agents.local"] and listed[0]["deleted_at"]
    # deleting again is idempotent and keeps the first timestamp
    first = listed[0]["deleted_at"]
    assert (await client.delete("/v1/agents/a@agents.local", headers=ADMIN)).status_code == 204
    assert (await client.get("/v1/agents?include_deleted=true", headers=ADMIN)).json()[0]["deleted_at"] == first
    restored = await client.post("/v1/agents/a@agents.local/restore", headers=ADMIN)
    assert restored.status_code == 200 and restored.json()["deleted_at"] is None
    assert len((await client.get("/v1/agents", headers=ADMIN)).json()) == 1


async def test_purge_hard_deletes(client):
    await make_agent(client, "a@agents.local")
    assert (await client.delete("/v1/agents/a@agents.local?purge=true", headers=ADMIN)).status_code == 204
    assert (await client.get("/v1/agents?include_deleted=true", headers=ADMIN)).json() == []
    assert (await client.post("/v1/agents/a@agents.local/restore", headers=ADMIN)).status_code == 404


async def test_soft_delete_keeps_data_and_blocks_recreate(client):
    await make_agent(client, "a@agents.local")
    await client.post("/v1/agents/a@agents.local/contacts", headers=ADMIN, json={"email": "p@example.com", "name": "P"})
    await client.delete("/v1/agents/a@agents.local", headers=ADMIN)
    async with AsyncSessionLocal() as db:
        assert (await db.scalar(select(Contact.id))) is not None
    r = await client.post("/v1/agents", headers=ADMIN, json={"email": "a@agents.local", "display_name": "x"})
    assert r.status_code == 400


async def test_agent_key_cannot_delete_or_restore(client):
    await make_agent(client, "a@agents.local")
    key, _ = await make_key(client, "a@agents.local", "full_access")
    assert (await client.delete("/v1/agents/a@agents.local", headers=key)).status_code == 403
    assert (await client.post("/v1/agents/a@agents.local/restore", headers=key)).status_code == 403


async def test_smtp_recipient_lookup_excludes_deleted_agent(client):
    """The RCPT and ingest lookups in the SMTP receiver must not match a soft-deleted inbox."""
    import inspect
    import smtp_receiver
    assert inspect.getsource(smtp_receiver).count("Agent.deleted_at.is_(None)") >= 2
    await make_agent(client, "a@agents.local")
    await client.delete("/v1/agents/a@agents.local", headers=ADMIN)
    async with AsyncSessionLocal() as db:
        found = await db.scalar(select(Agent).where(Agent.email == "a@agents.local", Agent.status == "active",
                                                    Agent.deleted_at.is_(None)))
        assert found is None
