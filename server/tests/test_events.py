import datetime

from app.database import AsyncSessionLocal
from app.models import WebhookDelivery
from tests.conftest import ADMIN, make_agent, make_key


async def _endpoint(client):
    await make_agent(client, "a@agents.local")
    r = await client.post("/v1/webhooks", headers=ADMIN, json={
        "agent_email": "a@agents.local", "url": "https://example.com/hook", "events": ["*"]})
    assert r.status_code == 201, r.text
    return r.json()["id"]


async def _delivery(endpoint_id, status="failed"):
    async with AsyncSessionLocal() as db:
        db.add(WebhookDelivery(id="evt_1", endpoint_id=endpoint_id, agent_email="a@agents.local",
                               event_type="email.received", payload={"x": 1}, status=status,
                               created_at=datetime.datetime.utcnow()))
        await db.commit()


async def test_events_list_get_redeliver(client):
    eid = await _endpoint(client)
    await _delivery(eid)
    page = (await client.get("/v1/events", headers=ADMIN)).json()
    assert [i["id"] for i in page["items"]] == ["evt_1"]
    assert (await client.get("/v1/events?agent_email=other@agents.local", headers=ADMIN)).json()["items"] == []
    assert (await client.get("/v1/events/evt_1", headers=ADMIN)).json()["payload"] == {"x": 1}
    assert (await client.get("/v1/events/missing", headers=ADMIN)).status_code == 404
    r = await client.post("/v1/events/evt_1/redeliver", headers=ADMIN)
    assert r.status_code in (200, 202) and r.json()["status"] == "pending"
    assert (await client.post("/v1/events/evt_1/redeliver", headers=ADMIN)).status_code == 409  # already pending


async def test_events_admin_only(client):
    await make_agent(client, "a@agents.local")
    key, _ = await make_key(client, "a@agents.local", "full_access")
    assert (await client.get("/v1/events", headers=key)).status_code == 403
    assert (await client.get("/v1/events")).status_code == 401


async def test_get_webhook_and_its_deliveries(client):
    eid = await _endpoint(client)
    await _delivery(eid)
    assert (await client.get(f"/v1/webhooks/{eid}", headers=ADMIN)).json()["id"] == eid
    assert (await client.get("/v1/webhooks/nope", headers=ADMIN)).status_code == 404
    assert len((await client.get(f"/v1/webhooks/{eid}/deliveries", headers=ADMIN)).json()) == 1
    # static route still wins over the {endpoint_id} capture
    assert (await client.get("/v1/webhooks/deliveries", headers=ADMIN)).status_code == 200
