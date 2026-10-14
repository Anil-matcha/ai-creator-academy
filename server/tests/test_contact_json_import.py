from tests.conftest import ADMIN, make_agent


async def test_json_import_creates_merges_duplicate_rows_and_suppresses_without_mail(client):
    inbox = "contacts@example.com"
    await make_agent(client, inbox)
    response = await client.post("/v1/contacts/import", headers=ADMIN, json={
        "agent_email": inbox,
        "contacts": [
            {"email": "One@Example.com", "display_name": "First", "metadata": {"tier": "free"}, "stage": "new"},
            {"email": "one@example.com", "display_name": "One", "metadata": {"tier": "paid", "active": True}, "suppressed": True},
        ],
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert (body["created"], body["updated"], body["skipped"], body["failed"]) == (1, 1, 0, 0)
    assert body["results"][0]["status"] == "created"
    assert body["results"][1]["status"] == "updated"
    assert body["results"][1]["suppressed"] is True
    contact = (await client.get(f"/v1/agents/{inbox}/contacts", headers=ADMIN)).json()[0]
    assert contact["name"] == "One"
    assert contact["metadata"] == {"tier": "paid", "active": True}
    engagement = (await client.get(f"/v1/agents/{inbox}/engagements", headers=ADMIN)).json()
    assert len(engagement) == 1 and engagement[0]["stage"] == "new"
    assert (await client.get("/v1/account/suppressions", headers=ADMIN)).json()["items"][0]["email"] == "one@example.com"


async def test_json_import_skip_mode_and_invalid_row_keep_valid_rows(client):
    inbox = "contacts@example.com"
    await make_agent(client, inbox)
    response = await client.post("/v1/contacts/import", headers=ADMIN, json={
        "agent_email": inbox,
        "on_conflict": "skip",
        "contacts": [
            {"email": "new@example.com", "display_name": "New"},
            {"email": "NEW@example.com", "display_name": "Duplicate"},
            {"email": "not-an-email", "display_name": "Invalid"},
            "not-an-object",
            {"email": "last@example.com", "display_name": "Last"},
        ],
    })
    assert response.status_code == 200, response.text
    body = response.json()
    assert (body["created"], body["updated"], body["skipped"], body["failed"]) == (2, 0, 1, 2)
    assert [row["status"] for row in body["results"]] == ["created", "skipped", "failed", "failed", "created"]
    contacts = (await client.get(f"/v1/agents/{inbox}/contacts", headers=ADMIN)).json()
    assert {row["email"] for row in contacts} == {"new@example.com", "last@example.com"}
    assert next(row for row in contacts if row["email"] == "new@example.com")["name"] == "New"


async def test_json_import_is_idempotent_and_replays_original_per_row_result(client):
    inbox = "contacts@example.com"
    await make_agent(client, inbox)
    headers = {**ADMIN, "Idempotency-Key": "json-contact-import-1"}
    payload = {"agent_email": inbox, "contacts": [{"email": "one@example.com"}]}
    first = await client.post("/v1/contacts/import", headers=headers, json=payload)
    replay = await client.post("/v1/contacts/import", headers=headers, json=payload)
    assert first.status_code == replay.status_code == 200
    assert replay.json() == first.json()
    assert len((await client.get(f"/v1/agents/{inbox}/contacts", headers=ADMIN)).json()) == 1
    conflict = await client.post("/v1/contacts/import", headers=headers,
                                 json={"agent_email": inbox, "contacts": [{"email": "two@example.com"}]})
    assert conflict.status_code == 422


async def test_json_import_requires_inbox_owner_and_rejects_nested_metadata(client):
    inbox = "owner@example.com"
    other = "other@example.com"
    await make_agent(client, inbox)
    await make_agent(client, other)
    key_response = await client.post("/v1/api-keys", headers=ADMIN, json={
        "name": "owner", "agent_email": inbox, "scope": "full_access"})
    key = {"Authorization": f"Bearer {key_response.json()['key']}"}
    forbidden = await client.post("/v1/contacts/import", headers=key, json={
        "agent_email": other, "contacts": [{"email": "one@example.com"}]})
    assert forbidden.status_code == 403
    invalid_metadata = await client.post("/v1/contacts/import", headers=ADMIN, json={
        "agent_email": inbox, "contacts": [{"email": "one@example.com", "metadata": {"nested": {"x": 1}}}]})
    assert invalid_metadata.status_code == 200
    assert invalid_metadata.json()["failed"] == 1


async def test_contact_metadata_patch_uses_mapped_json_column(client):
    inbox = "metadata@example.com"
    await make_agent(client, inbox)
    created = await client.post("/v1/contacts", headers=ADMIN, json={
        "agent_email": inbox, "email": "person@example.com", "name": "Person",
    })
    assert created.status_code == 201, created.text
    updated = await client.patch("/v1/contacts/person@example.com?agent_email=metadata%40example.com",
                                 headers=ADMIN, json={"metadata": {"source": "import"}})
    assert updated.status_code == 200, updated.text
    assert updated.json()["metadata"] == {"source": "import"}

