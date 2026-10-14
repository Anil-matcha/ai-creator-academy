"""Full MCP tool inventory, scope classification, authorization matrix and functional round trips."""

import base64
import datetime
import json

import pytest

from app.database import AsyncSessionLocal
from app.models import Message, MessageAttachment, OutboundJob, WebhookDelivery
from app.routers import mcp_extra
from app.routers.mcp import MCP_TOOLS
from tests.conftest import ADMIN, make_agent, make_key

EXPECTED_TOOLS = sorted("""
approve_review create_agent create_agent_suppression create_api_key create_contact create_template
create_webhook delete_agent delete_agent_suppression delete_api_key delete_contact delete_contact_import
delete_domain delete_message delete_outreach_contact delete_template delete_webhook forward_to_human
get_account_metrics get_agent get_agent_metrics get_attachment get_attachment_data get_contact_consent
get_conversation get_event get_message get_message_lifecycle get_protection get_recent_otp get_template
get_webhook import_contacts list_agents list_api_keys list_contacts list_conversations list_domains
list_events list_messages list_outbox list_outreach_contacts list_reviews list_suppressions list_templates
list_webhook_deliveries list_webhooks preview_template record_contact_consent redeliver_event
register_domain reject_review reply_to_message restore_message retry_outbox_job rotate_webhook_secret
send_message set_outreach_contact test_webhook update_agent update_contact update_message_labels
update_protection update_template update_webhook verify_domain whoami
list_account_suppressions delete_account_suppression export_account list_account_contacts restore_agent
get_review_settings list_starter_templates get_starter_template validate_template copy_starter_template
""".split())

# Written out independently of the implementation so a misclassified tool fails here.
REVIEW_TOOLS = {"list_reviews", "approve_review", "reject_review"}
ADMIN_TOOLS = {
    "list_agents", "create_agent", "get_agent", "update_agent", "delete_agent", "update_protection",
    "list_webhooks", "get_webhook", "create_webhook", "update_webhook", "delete_webhook",
    "rotate_webhook_secret", "test_webhook", "list_webhook_deliveries", "list_events", "get_event",
    "redeliver_event", "list_api_keys", "create_api_key", "delete_api_key", "list_domains",
    "register_domain", "verify_domain", "delete_domain", "get_account_metrics", "list_outbox",
    "retry_outbox_job", "list_account_suppressions", "delete_account_suppression", "export_account",
    "list_account_contacts", "restore_agent", "get_review_settings",
}
INBOX_WRITE_TOOLS = {
    "send_message", "reply_to_message", "forward_to_human", "update_message_labels", "delete_message",
    "restore_message", "create_agent_suppression", "delete_agent_suppression", "create_template",
    "update_template", "delete_template", "create_contact", "update_contact", "delete_contact",
    "import_contacts", "delete_contact_import", "record_contact_consent", "set_outreach_contact",
    "delete_outreach_contact", "copy_starter_template",
}
INBOX_READ_TOOLS = {
    "list_messages", "get_message", "get_recent_otp", "list_conversations", "get_conversation",
    "get_message_lifecycle", "get_agent_metrics", "get_protection", "list_contacts", "list_templates",
    "list_suppressions", "get_attachment", "get_attachment_data", "get_template", "preview_template",
    "get_contact_consent", "list_outreach_contacts",
}
ANY_CREDENTIAL_TOOLS = {"whoami", "list_starter_templates", "get_starter_template", "validate_template"}

DENIAL_MARKERS = ("not authorized", "Administrator token required", "does not permit", "limited to review tools")
A = "a@agents.local"
B = "b@agents.local"


async def rpc(client, headers, name, /, **arguments):
    r = await client.post("/mcp/rpc", headers=headers, json={
        "jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": name, "arguments": arguments}})
    if r.status_code != 200:
        return r.status_code, None
    result = r.json()["result"]
    text = result["content"][0]["text"]
    return result["isError"], (text if result["isError"] else json.loads(text))


async def ok(client, headers, name, /, **arguments):
    err, out = await rpc(client, headers, name, **arguments)
    assert err is False, f"{name} failed: {out}"
    return out


async def fails(client, headers, name, /, contains=None, **arguments):
    err, out = await rpc(client, headers, name, **arguments)
    assert err is True, f"{name} unexpectedly succeeded: {out}"
    if contains:
        assert contains in out, out
    return out


def _is_denial(text):
    return any(marker in text for marker in DENIAL_MARKERS)


# ---------------------------------------------------------------- inventory / classification

def test_exact_tool_inventory():
    names = [t["name"] for t in MCP_TOOLS]
    assert sorted(names) == EXPECTED_TOOLS
    assert len(names) == len(set(names))


def test_every_tool_is_classified_exactly_once():
    groups = [REVIEW_TOOLS, ADMIN_TOOLS, INBOX_WRITE_TOOLS, INBOX_READ_TOOLS, ANY_CREDENTIAL_TOOLS]
    assert sum(len(g) for g in groups) == len(set().union(*groups))
    assert set().union(*groups) == set(EXPECTED_TOOLS)


def test_extension_scope_sets_match_independent_classification():
    assert mcp_extra.EXT_ADMIN == ADMIN_TOOLS & set(mcp_extra.EXT_NAMES) | {"update_protection"}
    assert mcp_extra.EXT_WRITE == INBOX_WRITE_TOOLS & set(mcp_extra.EXT_NAMES)
    assert mcp_extra.EXT_READ == INBOX_READ_TOOLS & set(mcp_extra.EXT_NAMES)


def test_tool_schemas_are_wellformed_and_described():
    for tool in MCP_TOOLS:
        schema = tool["inputSchema"]
        assert schema["type"] == "object" and len(tool["description"]) > 20, tool["name"]
        assert set(schema.get("required", [])) <= set(schema["properties"]), tool["name"]
        if tool["name"] in ADMIN_TOOLS:
            assert tool["description"].startswith("Administrator only"), tool["name"]


# ---------------------------------------------------------------- authorization matrix

def _args_for(name, inbox):
    args = {"agent_email": inbox}
    if name in {"create_agent"}:
        args["email"] = "new@agents.local"
    return args


@pytest.mark.parametrize("name", EXPECTED_TOOLS)
async def test_anonymous_is_rejected(client, name):
    status, _ = await rpc(client, {}, name, agent_email=A)
    assert status == 401


@pytest.mark.parametrize("name", sorted(set(EXPECTED_TOOLS) - ANY_CREDENTIAL_TOOLS - REVIEW_TOOLS))
async def test_reviewer_key_limited_to_review_tools(client, name):
    await make_agent(client, A)
    reviewer, _ = await make_key(client, A, "reviewer")
    text = await fails(client, reviewer, name, **_args_for(name, A))
    assert "limited to review tools" in text


@pytest.mark.parametrize("name", sorted(ADMIN_TOOLS))
@pytest.mark.parametrize("scope", ["read_only", "full_access"])
async def test_inbox_keys_cannot_use_admin_tools(client, name, scope):
    await make_agent(client, A)
    key, _ = await make_key(client, A, scope)
    text = await fails(client, key, name, **_args_for(name, A))
    assert "Administrator token required" in text


@pytest.mark.parametrize("name", sorted(INBOX_WRITE_TOOLS))
async def test_read_only_key_cannot_use_write_tools(client, name):
    await make_agent(client, A)
    key, _ = await make_key(client, A, "read_only")
    text = await fails(client, key, name, **_args_for(name, A))
    assert "does not permit" in text


@pytest.mark.parametrize("name", sorted(INBOX_READ_TOOLS | INBOX_WRITE_TOOLS))
async def test_cross_inbox_access_denied(client, name):
    await make_agent(client, A)
    await make_agent(client, B)
    key, _ = await make_key(client, A, "full_access")
    text = await fails(client, key, name, **_args_for(name, B))
    assert "not authorized for this agent inbox" in text


@pytest.mark.parametrize("name", sorted(INBOX_READ_TOOLS - {"get_recent_otp"}))
async def test_read_only_key_passes_authorization_on_read_tools(client, name):
    await make_agent(client, A)
    key, _ = await make_key(client, A, "read_only")
    err, out = await rpc(client, key, name, **_args_for(name, A))
    assert not (err is True and _is_denial(out)), out


async def test_whoami_available_to_every_credential(client):
    await make_agent(client, A)
    for headers in (ADMIN, (await make_key(client, A, "read_only"))[0], (await make_key(client, A, "reviewer"))[0]):
        assert "scope" in await ok(client, headers, "whoami")


# ---------------------------------------------------------------- functional round trips

async def test_template_lifecycle_and_preview(client):
    await make_agent(client, A)
    created = await ok(client, ADMIN, "create_template", agent_email=A, name="welcome",
                       subject="Hi {{name}}", body_text="Hello {{name}}")
    tid = created["id"]
    assert (await ok(client, ADMIN, "get_template", agent_email=A, template_id=tid))["name"] == "welcome"
    rendered = await ok(client, ADMIN, "preview_template", agent_email=A, template_id=tid, data={"name": "Ada"})
    assert rendered["subject"] == "Hi Ada" and rendered["body_text"] == "Hello Ada"
    adhoc = await ok(client, ADMIN, "preview_template", agent_email=A, subject="S {{x}}", body_text="b", data={"x": 1})
    assert adhoc["subject"] == "S 1"
    updated = await ok(client, ADMIN, "update_template", agent_email=A, template_id=tid, subject="Yo {{name}}")
    assert updated["subject"] == "Yo {{name}}"
    await fails(client, ADMIN, "create_template", agent_email=A, name="welcome", subject="s", body_text="b")  # duplicate
    await ok(client, ADMIN, "delete_template", agent_email=A, template_id=tid)
    await fails(client, ADMIN, "get_template", agent_email=A, template_id=tid)


async def test_template_tools_are_inbox_scoped(client):
    await make_agent(client, A)
    await make_agent(client, B)
    tid = (await ok(client, ADMIN, "create_template", agent_email=A, name="t", subject="s", body_text="b"))["id"]
    key_b, _ = await make_key(client, B, "full_access")
    await fails(client, key_b, "get_template", agent_email=B, template_id=tid)   # id belongs to inbox A
    await fails(client, key_b, "delete_template", agent_email=B, template_id=tid)


async def test_contacts_import_consent_and_outreach(client):
    await make_agent(client, A)
    contact = await ok(client, ADMIN, "create_contact", agent_email=A, email="Pat@Example.com", name="Pat")
    cid = contact["id"]
    assert contact["email"] == "pat@example.com"
    await fails(client, ADMIN, "create_contact", agent_email=A, email="pat@example.com", name="Dup")
    assert (await ok(client, ADMIN, "update_contact", agent_email=A, contact_id=cid, company="Acme"))["company"] == "Acme"

    imported = await ok(client, ADMIN, "import_contacts", agent_email=A,
                        csv="email,name\nnew1@example.com,One\npat@example.com,Pat\nbad,Bad\n")
    assert imported["created"] == 1 and imported["skipped"] == 2
    await fails(client, ADMIN, "delete_contact_import", agent_email=A, batch_id=imported["batch_id"], confirm="no")
    reversed_ = await ok(client, ADMIN, "delete_contact_import", agent_email=A, batch_id=imported["batch_id"], confirm="DELETE")
    assert reversed_["deleted"] == 1
    await fails(client, ADMIN, "import_contacts", agent_email=A, csv="x" * 1_000_001)

    assert (await ok(client, ADMIN, "get_contact_consent", agent_email=A, contact_id=cid))["current"] == "unknown"
    await ok(client, ADMIN, "record_contact_consent", agent_email=A, contact_id=cid, action="granted", source="signup form")
    history = await ok(client, ADMIN, "record_contact_consent", agent_email=A, contact_id=cid, action="revoked", source="reply")
    assert history["current"] == "revoked" and len(history["events"]) == 2
    await fails(client, ADMIN, "record_contact_consent", agent_email=A, contact_id=cid, action="maybe", source="x")

    due = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)).isoformat()
    created = await ok(client, ADMIN, "set_outreach_contact", agent_email=A, contact_id=cid, stage="contacted", next_due_at=due)
    assert created["stage"] == "contacted"
    updated = await ok(client, ADMIN, "set_outreach_contact", agent_email=A, contact_id=cid, stage="waiting")
    assert updated["id"] == created["id"] and updated["stage"] == "waiting"
    assert len(await ok(client, ADMIN, "list_outreach_contacts", agent_email=A)) == 1
    assert await ok(client, ADMIN, "list_outreach_contacts", agent_email=A, due=True) == []
    await ok(client, ADMIN, "delete_outreach_contact", agent_email=A, engagement_id=created["id"])
    assert await ok(client, ADMIN, "list_outreach_contacts", agent_email=A) == []
    await ok(client, ADMIN, "delete_contact", agent_email=A, contact_id=cid)
    await fails(client, ADMIN, "delete_contact", agent_email=A, contact_id=cid)


async def test_contact_ids_do_not_cross_inboxes(client):
    await make_agent(client, A)
    await make_agent(client, B)
    cid = (await ok(client, ADMIN, "create_contact", agent_email=A, email="p@example.com", name="P"))["id"]
    key_b, _ = await make_key(client, B, "full_access")
    await fails(client, key_b, "update_contact", agent_email=B, contact_id=cid, name="Hijack")
    await fails(client, key_b, "get_contact_consent", agent_email=B, contact_id=cid)
    await fails(client, key_b, "record_contact_consent", agent_email=B, contact_id=cid, action="granted", source="x")
    await fails(client, key_b, "set_outreach_contact", agent_email=B, contact_id=cid)


async def test_suppression_create_and_delete(client):
    await make_agent(client, A)
    entry = await ok(client, ADMIN, "create_agent_suppression", agent_email=A, email="no@example.com")
    assert [s["email"] for s in await ok(client, ADMIN, "list_suppressions", agent_email=A)] == ["no@example.com"]
    await ok(client, ADMIN, "delete_agent_suppression", agent_email=A, suppression_id=entry["id"])
    assert await ok(client, ADMIN, "list_suppressions", agent_email=A) == []
    await fails(client, ADMIN, "delete_agent_suppression", agent_email=A, suppression_id=entry["id"])


async def _seed_attachment(inbox, content=b"hello", size=None):
    async with AsyncSessionLocal() as db:
        db.add(Message(id="m1", agent_email=inbox, direction="inbound", sender="x@example.com", recipient=inbox,
                       body_text="b", thread_id="t", rfc_message_id="<m1@x>", status="delivered",
                       created_at=datetime.datetime.utcnow()))
        await db.flush()
        db.add(MessageAttachment(id="att1", message_id="m1", filename="a.txt", content_type="text/plain",
                                 size_bytes=size if size is not None else len(content), content=content))
        await db.commit()


async def test_attachment_metadata_and_data(client):
    await make_agent(client, A)
    await _seed_attachment(A)
    meta = await ok(client, ADMIN, "get_attachment", agent_email=A, message_id="m1")
    assert meta == [{"id": "att1", "filename": "a.txt", "content_type": "text/plain", "size_bytes": 5}]
    assert "content_base64" not in json.dumps(meta)
    data = await ok(client, ADMIN, "get_attachment_data", agent_email=A, message_id="m1", attachment_id="att1")
    assert base64.b64decode(data["content_base64"]) == b"hello"
    await fails(client, ADMIN, "get_attachment_data", agent_email=A, message_id="m1", attachment_id="nope")
    await fails(client, ADMIN, "get_attachment", agent_email=A, message_id="missing")


async def test_attachment_size_cap_and_inbox_scope(client):
    await make_agent(client, A)
    await make_agent(client, B)
    await _seed_attachment(A, size=mcp_extra.MAX_ATTACHMENT_DATA_BYTES + 1)
    await fails(client, ADMIN, "get_attachment_data", agent_email=A, message_id="m1",
                attachment_id="att1", contains="limited to")
    key_b, _ = await make_key(client, B, "read_only")
    await fails(client, key_b, "get_attachment", agent_email=B, message_id="m1")                       # message is A's
    await fails(client, key_b, "get_attachment_data", agent_email=B, message_id="m1", attachment_id="att1")


async def test_webhook_lifecycle_and_secret_shown_once(client):
    await make_agent(client, A)
    created = await ok(client, ADMIN, "create_webhook", agent_email=A, url="https://example.com/hook", events=["email.received"])
    wid, secret = created["id"], created["signing_secret"]
    assert secret.startswith("whsec_")
    for read in (await ok(client, ADMIN, "get_webhook", webhook_id=wid),
                 (await ok(client, ADMIN, "list_webhooks", agent_email=A))[0]):
        assert "signing_secret" not in read and secret not in json.dumps(read)
    assert (await ok(client, ADMIN, "update_webhook", webhook_id=wid, enabled=False))["enabled"] is False
    await fails(client, ADMIN, "test_webhook", webhook_id=wid)                       # disabled endpoints refuse tests
    await ok(client, ADMIN, "update_webhook", webhook_id=wid, enabled=True)
    queued = await ok(client, ADMIN, "test_webhook", webhook_id=wid)
    assert queued["status"] == "pending"
    deliveries = await ok(client, ADMIN, "list_webhook_deliveries", webhook_id=wid)
    assert [d["id"] for d in deliveries] == [queued["delivery_id"]]
    rotated = await ok(client, ADMIN, "rotate_webhook_secret", webhook_id=wid)
    assert rotated["signing_secret"].startswith("whsec_") and rotated["signing_secret"] != secret
    await fails(client, ADMIN, "create_webhook", agent_email=A, url="http://example.com/insecure")
    await fails(client, ADMIN, "create_webhook", agent_email=A, url="https://127.0.0.1/hook")
    await ok(client, ADMIN, "delete_webhook", webhook_id=wid)
    await fails(client, ADMIN, "get_webhook", webhook_id=wid)


async def test_event_tools(client):
    await make_agent(client, A)
    wid = (await ok(client, ADMIN, "create_webhook", agent_email=A, url="https://example.com/hook"))["id"]
    async with AsyncSessionLocal() as db:
        db.add(WebhookDelivery(id="evt_x", endpoint_id=wid, agent_email=A, event_type="email.received",
                               payload={"k": 1}, status="failed", created_at=datetime.datetime.utcnow()))
        await db.commit()
    page = await ok(client, ADMIN, "list_events")
    assert [e["id"] for e in page["items"]] == ["evt_x"]
    assert (await ok(client, ADMIN, "get_event", event_id="evt_x"))["payload"] == {"k": 1}
    assert (await ok(client, ADMIN, "redeliver_event", event_id="evt_x"))["status"] == "pending"
    await fails(client, ADMIN, "redeliver_event", event_id="evt_x")     # already queued
    await fails(client, ADMIN, "get_event", event_id="missing")


async def test_api_key_tools_show_key_once_and_revocation_works(client):
    await make_agent(client, A)
    created = await ok(client, ADMIN, "create_api_key", name="ci", agent_email=A, scope="read_only", expires_in_days=30)
    token = created["key"]
    listed = await ok(client, ADMIN, "list_api_keys")
    assert [k["id"] for k in listed] == [created["id"]]
    assert token not in json.dumps(listed) and "key_hash" not in json.dumps(listed)
    bearer = {"Authorization": f"Bearer {token}"}
    assert (await ok(client, bearer, "whoami"))["scope"] == "read_only"
    await ok(client, ADMIN, "delete_api_key", key_id=created["id"])
    status, _ = await rpc(client, bearer, "whoami")
    assert status == 401
    await fails(client, ADMIN, "create_api_key", name="x", agent_email="ghost@agents.local")
    await fails(client, ADMIN, "create_api_key", name="x", agent_email=A, scope="superuser")


async def test_domain_tools(client):
    created = await ok(client, ADMIN, "register_domain", domain="Mail.Example.com")
    assert created["domain"] == "mail.example.com"
    assert [d["domain"] for d in await ok(client, ADMIN, "list_domains")] == ["mail.example.com"]
    await fails(client, ADMIN, "register_domain", domain="mail.example.com")
    await fails(client, ADMIN, "register_domain", domain="nodots")
    await fails(client, ADMIN, "verify_domain", domain="mail.example.com", contains="not implemented")
    await ok(client, ADMIN, "delete_domain", domain="mail.example.com")
    await fails(client, ADMIN, "delete_domain", domain="mail.example.com")


async def test_agent_admin_tools(client):
    created = await ok(client, ADMIN, "create_agent", email="new@agents.local", display_name="New", hitl_enabled=False)
    assert created["email"] == "new@agents.local" and created["hitl_enabled"] is False
    assert (await ok(client, ADMIN, "get_agent", agent_email="new@agents.local"))["display_name"] == "New"
    updated = await ok(client, ADMIN, "update_agent", agent_email="new@agents.local", display_name="Renamed", hitl_enabled=True)
    assert updated["display_name"] == "Renamed" and updated["hitl_enabled"] is True
    assert "new@agents.local" in [a["email"] for a in await ok(client, ADMIN, "list_agents")]
    soft = await ok(client, ADMIN, "delete_agent", agent_email="new@agents.local")
    assert soft["purged"] is False
    assert "new@agents.local" not in [a["email"] for a in await ok(client, ADMIN, "list_agents")]
    assert (await ok(client, ADMIN, "get_agent", agent_email="new@agents.local"))["email"] == "new@agents.local"  # still stored
    assert (await ok(client, ADMIN, "delete_agent", agent_email="new@agents.local", purge=True))["purged"] is True
    await fails(client, ADMIN, "get_agent", agent_email="new@agents.local")
    await fails(client, ADMIN, "delete_agent", agent_email="new@agents.local", purge="yes")
    await fails(client, ADMIN, "create_agent", email="x@agents.local")          # display_name required


async def test_account_metrics_and_outbox_tools(client):
    await make_agent(client, A)
    assert (await ok(client, ADMIN, "get_account_metrics"))["total_agents"] == 1
    sent = await ok(client, ADMIN, "send_message", agent_email=A, recipient="to@example.com", subject="s", body_text="b")
    await ok(client, ADMIN, "approve_review", review_id=(await ok(client, ADMIN, "list_reviews"))[0]["review_id"])
    jobs = await ok(client, ADMIN, "list_outbox")
    assert [j["message_id"] for j in jobs] == [sent["message_id"]]
    assert await ok(client, ADMIN, "list_outbox", status="failed") == []
    await fails(client, ADMIN, "list_outbox", status="bogus")
    await fails(client, ADMIN, "retry_outbox_job", job_id=jobs[0]["id"])           # only failed/uncertain jobs retry
    await fails(client, ADMIN, "retry_outbox_job", job_id="missing")


async def test_uncertain_outbox_retry_requires_duplicate_risk_confirmation(client):
    await make_agent(client, A)
    await ok(client, ADMIN, "send_message", agent_email=A, recipient="to@example.com", subject="s", body_text="b")
    await ok(client, ADMIN, "approve_review", review_id=(await ok(client, ADMIN, "list_reviews"))[0]["review_id"])
    job_id = (await ok(client, ADMIN, "list_outbox"))[0]["id"]
    from sqlalchemy import update
    async with AsyncSessionLocal() as db:
        await db.execute(update(OutboundJob).where(OutboundJob.id == job_id).values(status="uncertain"))
        await db.commit()
    await fails(client, ADMIN, "retry_outbox_job", job_id=job_id, contains="duplicate")
    retried = await ok(client, ADMIN, "retry_outbox_job", job_id=job_id, confirm_duplicate_risk=True)
    assert retried["status"] == "pending"
    await fails(client, ADMIN, "retry_outbox_job", job_id=job_id, confirm_duplicate_risk="yes")


async def test_argument_validation_errors_are_tool_errors_not_crashes(client):
    await make_agent(client, A)
    await fails(client, ADMIN, "get_template", agent_email=A, contains="Missing required")
    await fails(client, ADMIN, "list_webhooks", limit=0)
    await fails(client, ADMIN, "list_events", limit=1000)
    await fails(client, ADMIN, "list_outreach_contacts", agent_email=A, due="yes")
