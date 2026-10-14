import pytest

from tests.conftest import ADMIN, make_agent, make_key

A, B = "a@agents.local", "b@agents.local"


async def _suppress(client, inbox, address):
    r = await client.post(f"/v1/agents/{inbox}/suppressions", headers=ADMIN, json={"email": address, "reason": "bounced"})
    assert r.status_code == 201, r.text


async def _contact(client, inbox, address, name="P"):
    r = await client.post(f"/v1/agents/{inbox}/contacts", headers=ADMIN, json={"email": address, "name": name})
    assert r.status_code == 201, r.text
    return r.json()["id"]


@pytest.mark.parametrize("method,path", [
    ("GET", "/v1/account/suppressions"), ("DELETE", "/v1/account/suppressions/x@example.com"),
    ("GET", "/v1/account/export"), ("GET", "/v1/contacts"), ("GET", "/v1/contacts/x@example.com"),
    ("PATCH", "/v1/contacts/x@example.com"), ("DELETE", "/v1/contacts/x@example.com"),
])
async def test_account_routes_are_admin_only(client, method, path):
    await make_agent(client, A)
    key, _ = await make_key(client, A, "full_access")
    assert (await client.request(method, path)).status_code == 401
    assert (await client.request(method, path, headers=key, json={} if method == "PATCH" else None)).status_code == 403


async def test_account_suppressions_aggregate_and_remove(client):
    await make_agent(client, A)
    await make_agent(client, B)
    await _suppress(client, A, "bad@example.com")
    await _suppress(client, B, "bad@example.com")
    await _suppress(client, B, "other@example.com")
    items = (await client.get("/v1/account/suppressions", headers=ADMIN)).json()["items"]
    assert len(items) == 3
    only = (await client.get("/v1/account/suppressions?address=BAD@example.com", headers=ADMIN)).json()["items"]
    assert sorted(i["agent_email"] for i in only) == [A, B]
    r = await client.delete("/v1/account/suppressions/Bad@Example.com", headers=ADMIN)
    assert r.status_code == 200 and r.json()["removed"] == 2
    assert [i["email"] for i in (await client.get("/v1/account/suppressions", headers=ADMIN)).json()["items"]] == ["other@example.com"]
    assert (await client.delete("/v1/account/suppressions/bad@example.com", headers=ADMIN)).status_code == 404


async def test_cross_inbox_contacts(client):
    await make_agent(client, A)
    await make_agent(client, B)
    await _contact(client, A, "p@example.com", "Pat A")
    await _contact(client, B, "p@example.com", "Pat B")
    await _contact(client, B, "q@example.com", "Quinn")
    assert len((await client.get("/v1/contacts", headers=ADMIN)).json()["items"]) == 3
    assert len((await client.get(f"/v1/contacts?agent_email={B}", headers=ADMIN)).json()["items"]) == 2
    assert [c["email"] for c in (await client.get("/v1/contacts?q=quin", headers=ADMIN)).json()["items"]] == ["q@example.com"]
    assert len((await client.get("/v1/contacts/p@example.com", headers=ADMIN)).json()["items"]) == 2
    assert len((await client.get(f"/v1/contacts/p@example.com?agent_email={A}", headers=ADMIN)).json()["items"]) == 1
    assert (await client.get("/v1/contacts/none@example.com", headers=ADMIN)).status_code == 404


async def test_account_contact_write_requires_disambiguation(client):
    await make_agent(client, A)
    await make_agent(client, B)
    await _contact(client, A, "p@example.com", "Pat A")
    await _contact(client, B, "p@example.com", "Pat B")
    assert (await client.patch("/v1/contacts/p@example.com", headers=ADMIN, json={"name": "New"})).status_code == 409
    assert (await client.delete("/v1/contacts/p@example.com", headers=ADMIN)).status_code == 409
    r = await client.patch(f"/v1/contacts/p@example.com?agent_email={A}", headers=ADMIN, json={"name": "New"})
    assert r.status_code == 200 and r.json()["name"] == "New"
    # the other inbox's row is untouched
    other = (await client.get(f"/v1/contacts/p@example.com?agent_email={B}", headers=ADMIN)).json()["items"][0]
    assert other["name"] == "Pat B"
    assert (await client.delete(f"/v1/contacts/p@example.com?agent_email={A}", headers=ADMIN)).status_code == 204
    # now unambiguous
    assert (await client.delete("/v1/contacts/p@example.com", headers=ADMIN)).status_code == 204
    assert (await client.get("/v1/contacts/p@example.com", headers=ADMIN)).status_code == 404


async def test_account_contact_create_and_duplicates(client):
    await make_agent(client, A)
    body = {"agent_email": A, "email": "New@Example.com", "name": "New"}
    r = await client.post("/v1/contacts", headers=ADMIN, json=body)
    assert r.status_code == 201 and r.json()["email"] == "new@example.com" and r.json()["agent_email"] == A
    assert (await client.post("/v1/contacts", headers=ADMIN, json=body)).status_code == 409
    assert (await client.post("/v1/contacts", headers=ADMIN, json={**body, "agent_email": "missing@agents.local"})).status_code == 404
    # a rename cannot collide with an existing contact in the same inbox
    await client.post("/v1/contacts", headers=ADMIN, json={**body, "email": "other@example.com"})
    clash = await client.patch(f"/v1/contacts/other@example.com?agent_email={A}", headers=ADMIN, json={"email": "new@example.com"})
    assert clash.status_code == 409


async def test_export_contents_exclude_secrets(client):
    await make_agent(client, A)
    await _contact(client, A, "p@example.com")
    await _suppress(client, A, "bad@example.com")
    await client.post(f"/v1/agents/{A}/templates", headers=ADMIN, json={"name": "t", "subject": "s", "body_text": "b"})
    hook = await client.post("/v1/webhooks", headers=ADMIN, json={
        "agent_email": A, "url": "https://example.com/hook?token=SECRETTOKEN", "events": ["*"]})
    assert hook.status_code == 201, hook.text
    secret = hook.json().get("signing_secret") or hook.json().get("secret")
    await make_key(client, A, "full_access")
    r = await client.get("/v1/account/export", headers=ADMIN)
    assert r.status_code == 200
    body = r.json()
    assert body["truncated"] is False and body["truncated_collections"] == []
    assert body["counts"] == {"agents": 1, "contacts": 1, "templates": 1, "suppressions": 1, "webhook_endpoints": 1}
    text = r.text
    assert "SECRETTOKEN" not in text and "key_hash" not in text and "oae_" not in text
    if secret:
        assert secret not in text
    assert "signing_secret" not in text and "password" not in text


async def test_export_is_bounded_and_flags_truncation(client):
    await make_agent(client, A)
    for i in range(3):
        await _contact(client, A, f"p{i}@example.com")
    body = (await client.get("/v1/account/export?limit_per_collection=2", headers=ADMIN)).json()
    assert body["truncated"] is True and body["truncated_collections"] == ["contacts"]
    assert len(body["contacts"]) == 2 and body["counts"]["contacts"] == 2
    assert (await client.get("/v1/account/export?limit_per_collection=0", headers=ADMIN)).status_code == 422
    assert (await client.get("/v1/account/export?limit_per_collection=999999", headers=ADMIN)).status_code == 422


async def test_export_includes_soft_deleted_agents(client):
    await make_agent(client, A)
    await client.delete(f"/v1/agents/{A}", headers=ADMIN)
    agents = (await client.get("/v1/account/export", headers=ADMIN)).json()["agents"]
    assert agents[0]["email"] == A and agents[0]["deleted_at"]
