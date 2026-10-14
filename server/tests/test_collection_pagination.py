from tests.conftest import ADMIN, make_agent

A = "a@agents.local"


async def test_engagement_pages_follow_stable_order_and_bind_due_filter(client):
    await make_agent(client, A)
    ids = []
    for address in ("one@example.com", "two@example.com"):
        contact = await client.post(f"/v1/agents/{A}/contacts", headers=ADMIN,
                                    json={"email": address, "name": address})
        assert contact.status_code == 201
        engagement = await client.post(f"/v1/agents/{A}/engagements", headers=ADMIN,
                                       json={"contact_id": contact.json()["id"]})
        assert engagement.status_code == 201
        ids.append(engagement.json()["id"])
    first = await client.get(f"/v1/agents/{A}/engagements/page?limit=1", headers=ADMIN)
    assert first.status_code == 200 and len(first.json()["items"]) == 1 and first.json()["next_cursor"]
    second = await client.get(f"/v1/agents/{A}/engagements/page?limit=1&cursor=" + first.json()["next_cursor"], headers=ADMIN)
    assert len(second.json()["items"]) == 1 and second.json()["next_cursor"] is None
    assert (await client.get(f"/v1/agents/{A}/engagements/page?due=true&cursor=" + first.json()["next_cursor"], headers=ADMIN)).status_code == 400
