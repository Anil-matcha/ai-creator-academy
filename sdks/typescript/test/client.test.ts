import assert from "node:assert/strict";
import { test } from "node:test";
import { AgentEmailClient, AgentEmailError, attachmentFromBytes, paginate, type FetchLike } from "../src/index.js";

interface Call { url: URL; method: string; headers: Record<string, string>; body: string | undefined }

function mock(...responses: Array<{ status?: number; json?: unknown; text?: string }>) {
  const calls: Call[] = [];
  const queue = [...responses];
  const fetch: FetchLike = async (input, init) => {
    calls.push({ url: new URL(input), method: String(init?.method), headers: init?.headers as Record<string, string>, body: init?.body as string | undefined });
    const next = queue.length > 1 ? queue.shift()! : queue[0] ?? { status: 200, json: {} };
    const status = next.status ?? 200;
    const body = status === 204 ? null : next.text ?? JSON.stringify(next.json ?? {});
    return new Response(body, { status });
  };
  const client = new AgentEmailClient({ baseUrl: "http://api.test/", apiKey: "secret-key", fetch });
  return { client, calls };
}

const INBOX = "a@agents.local";
const base = `/v1/agents/${encodeURIComponent(INBOX)}`;

test("sends bearer auth, trims base URL and encodes path segments", async () => {
  const { client, calls } = mock({ json: [] });
  await client.messages.list("we ird@x.com/../y", { limit: 5, label: "vip", trashed: true });
  const call = calls[0]!;
  assert.equal(call.headers.Authorization, "Bearer secret-key");
  assert.equal(call.url.pathname, "/v1/agents/we%20ird%40x.com%2F..%2Fy/messages");
  assert.equal(call.url.searchParams.get("label"), "vip");
  assert.equal(call.url.searchParams.get("trashed"), "true");
  assert.equal(call.url.searchParams.get("limit"), "5");
});

test("undefined query params are omitted", async () => {
  const { client, calls } = mock({ json: { found: false } });
  await client.messages.otp(INBOX, { sinceSeconds: 60 });
  assert.equal(calls[0]!.url.searchParams.get("since_seconds"), "60");
  assert.equal(calls[0]!.url.searchParams.has("wait_seconds"), false);
});

test("send passes Idempotency-Key and serialises Date schedule as scheduled_at", async () => {
  const { client, calls } = mock({ status: 201, json: { id: "m1", status: "scheduled" } });
  const when = new Date("2030-01-01T00:00:00Z");
  const message = await client.messages.send(INBOX, { recipient: "x@example.com", subject: "s", body_text: "b", send_at: when }, { idempotencyKey: "k-1" });
  assert.equal(message.id, "m1");
  const call = calls[0]!;
  assert.equal(call.method, "POST");
  assert.equal(call.url.pathname, `${base}/messages`);
  assert.equal(call.headers["Idempotency-Key"], "k-1");
  assert.equal(JSON.parse(call.body!).scheduled_at, "2030-01-01T00:00:00.000Z");
  assert.equal(JSON.parse(call.body!).send_at, undefined);
});

test("send rejects timezone-naive scheduled_at strings", async () => {
  const { client } = mock();
  assert.throws(() => client.messages.send(INBOX, {
    recipient: "x@example.com", subject: "s", body_text: "b", scheduled_at: "2030-01-01T00:00:00",
  }), /timezone offset/);
});

test("no Idempotency-Key header unless requested", async () => {
  const { client, calls } = mock({ status: 201, json: {} });
  await client.messages.reply(INBOX, "m1", { body_text: "hi" });
  assert.equal("Idempotency-Key" in calls[0]!.headers, false);
  assert.equal(calls[0]!.url.pathname, `${base}/messages/m1/reply`);
});

test("labels, trash, restore, lifecycle, forward hit the right routes", async () => {
  const { client, calls } = mock({ json: {} });
  await client.messages.setLabels(INBOX, "m1", ["vip"]);
  await client.messages.trash(INBOX, "m1");
  await client.messages.restore(INBOX, "m1");
  await client.messages.lifecycle(INBOX, "m1");
  await client.messages.forward(INBOX, "m1", "boss@example.com", "fyi");
  assert.deepEqual(calls.map((c) => `${c.method} ${c.url.pathname.replace(base, "")}`), [
    "PATCH /messages/m1", "DELETE /messages/m1", "POST /messages/m1/restore", "GET /messages/m1/lifecycle", "POST /messages/m1/forward",
  ]);
  assert.deepEqual(JSON.parse(calls[0]!.body!), { labels: ["vip"] });
});

test("204 responses resolve to undefined", async () => {
  const { client } = mock({ status: 204 });
  assert.equal(await client.contacts.delete(INBOX, "c1"), undefined);
});

test("errors carry status and detail but never the token", async () => {
  const { client } = mock({ status: 403, json: { detail: "Token does not permit sending messages" } });
  await assert.rejects(client.messages.send(INBOX, { recipient: "x@example.com", subject: "s", body_text: "b" }), (err: unknown) => {
    assert.ok(err instanceof AgentEmailError);
    assert.equal(err.status, 403);
    assert.equal(err.detail, "Token does not permit sending messages");
    assert.ok(!err.message.includes("secret-key"));
    return true;
  });
});

test("validation errors keep structured detail", async () => {
  const detail = [{ loc: ["body", "email"], msg: "bad" }];
  const { client } = mock({ status: 422, json: { detail } });
  await assert.rejects(client.contacts.create(INBOX, { email: "x", name: "n" }), (err: unknown) => {
    assert.deepEqual((err as AgentEmailError).detail, detail);
    return true;
  });
});

test("transport failures become AgentEmailError without a status", async () => {
  const client = new AgentEmailClient({ baseUrl: "http://api.test", apiKey: "k", fetch: async () => { throw new Error("ECONNREFUSED"); } });
  await assert.rejects(client.info(), (err: unknown) => err instanceof AgentEmailError && err.status === undefined && /ECONNREFUSED/.test(err.message));
});

test("redirects are refused so credentials are not forwarded", async () => {
  const { client } = mock({ status: 302, text: "" });
  await assert.rejects(client.whoami(), (err: unknown) => err instanceof AgentEmailError && err.status === 302);
});

test("constructor validates inputs", () => {
  assert.throws(() => new AgentEmailClient({ baseUrl: "ftp://x", apiKey: "k" }), TypeError);
  assert.throws(() => new AgentEmailClient({ baseUrl: "http://x", apiKey: "" }), TypeError);
});

test("paginate follows cursors until exhausted", async () => {
  const { client, calls } = mock(
    { json: { items: [{ id: "1" }, { id: "2" }], next_cursor: "c1" } },
    { json: { items: [{ id: "3" }], next_cursor: null } },
  );
  const ids: string[] = [];
  for await (const m of client.messages.iterate(INBOX, { read_status: "unread", limit: 2 })) ids.push(m.id);
  assert.deepEqual(ids, ["1", "2", "3"]);
  assert.equal(calls.length, 2);
  assert.equal(calls[0]!.url.searchParams.has("cursor"), false);
  assert.equal(calls[1]!.url.searchParams.get("cursor"), "c1");
  assert.equal(calls[1]!.url.searchParams.get("read_status"), "unread");
});

test("paginate helper handles an empty first page", async () => {
  const items: number[] = [];
  for await (const x of paginate<number>(async () => ({ items: [], next_cursor: null }))) items.push(x);
  assert.deepEqual(items, []);
});

test("outbox, events and webhook delivery iterators page correctly", async () => {
  const page = (id: string, next: string | null) => ({ json: { items: [{ id }], next_cursor: next } });
  for (const run of [
    (c: AgentEmailClient) => c.outbox.iterate({ status: "failed" }),
    (c: AgentEmailClient) => c.events.iterate({ agent_email: INBOX }),
    (c: AgentEmailClient) => c.webhooks.iterateDeliveries({ endpoint_id: "w1" }),
  ]) {
    const { client, calls } = mock(page("a", "n"), page("b", null));
    const seen: string[] = [];
    for await (const item of run(client)) seen.push((item as { id: string }).id);
    assert.deepEqual(seen, ["a", "b"]);
    assert.equal(calls[1]!.url.searchParams.get("cursor"), "n");
  }
});

test("event iterator keeps time filters on every page", async () => {
  const { client, calls } = mock({ json: { items: [], next_cursor: null } });
  for await (const _ of client.events.iterate({ since: "2026-01-01T00:00:00Z", until: "2026-01-02T00:00:00Z" })) { /* exhausted */ }
  assert.equal(calls[0]!.url.searchParams.get("since"), "2026-01-01T00:00:00Z");
  assert.equal(calls[0]!.url.searchParams.get("until"), "2026-01-02T00:00:00Z");
});

test("contact CSV import sends raw text/csv and reverse requires confirm", async () => {
  const { client, calls } = mock({ json: {} });
  await client.contacts.importCsv(INBOX, "email,name\na@b.com,A\n");
  await client.contacts.reverseImport(INBOX, "batch 1");
  assert.equal(calls[0]!.headers["Content-Type"], "text/csv; charset=utf-8");
  assert.equal(calls[0]!.body, "email,name\na@b.com,A\n");
  assert.equal(calls[1]!.method, "DELETE");
  assert.equal(calls[1]!.url.searchParams.get("confirm"), "DELETE");
  assert.ok(calls[1]!.url.pathname.endsWith("/imports/batch%201"));
});

test("review decisions include the action the server requires", async () => {
  const { client, calls } = mock({ json: {} });
  await client.reviews.approve("rev_1", "ok");
  await client.reviews.reject("rev_1");
  assert.deepEqual(JSON.parse(calls[0]!.body!), { action: "approve", notes: "ok" });
  assert.equal(JSON.parse(calls[1]!.body!).action, "reject");
  assert.equal(calls[1]!.url.pathname, "/v1/reviews/rev_1/reject");
});

test("outbox retry passes duplicate-risk confirmation", async () => {
  const { client, calls } = mock({ json: {} });
  await client.outbox.retry("job1", { confirmDuplicateRisk: true });
  assert.equal(calls[0]!.url.searchParams.get("confirm_duplicate_risk"), "true");
});

test("webhooks, events, keys, domains, protection, metrics routes", async () => {
  const { client, calls } = mock({ json: {} });
  await client.webhooks.create({ agent_email: INBOX, url: "https://x.example/hook" });
  await client.webhooks.rotateSecret("w1");
  await client.webhooks.test("w1");
  await client.webhooks.replay("d1");
  await client.events.redeliver("e1");
  await client.apiKeys.create({ name: "n", agent_email: INBOX, scope: "reviewer" });
  await client.apiKeys.revoke("k1");
  await client.domains.verify("mail.example.com");
  await client.agents.setProtection(INBOX, { threat_sensitivity: "high", hitl_enabled: true });
  await client.agents.metrics(INBOX);
  await client.conversations.get(INBOX, "th_1");
  await client.suppressions.add(INBOX, "x@example.com", "bounced");
  await client.templates.previewSaved(INBOX, "t1", { name: "A" });
  await client.engagements.create(INBOX, { contact_id: "c1", next_due_at: new Date("2030-01-01T00:00:00Z") });
  assert.deepEqual(calls.map((c) => `${c.method} ${c.url.pathname}`), [
    "POST /v1/webhooks", "POST /v1/webhooks/w1/rotate-secret", "POST /v1/webhooks/w1/test",
    "POST /v1/webhooks/deliveries/d1/replay", "POST /v1/events/e1/redeliver", "POST /v1/api-keys",
    "DELETE /v1/api-keys/k1", "POST /v1/domains/mail.example.com/verify", `PUT ${base}/protection`,
    `GET ${base}/metrics`, `GET ${base}/conversations/th_1`, `POST ${base}/suppressions`,
    `POST ${base}/templates/t1/preview`, `POST ${base}/engagements`,
  ]);
  assert.equal(JSON.parse(calls[13]!.body!).next_due_at, "2030-01-01T00:00:00.000Z");
});

test("attachment helper base64-encodes bytes", () => {
  assert.deepEqual(attachmentFromBytes("a.txt", new TextEncoder().encode("hi"), "text/plain"), {
    filename: "a.txt", content_type: "text/plain", content_base64: "aGk=",
  });
});

test("downloadAttachment returns bytes and surfaces failures", async () => {
  const ok = new AgentEmailClient({ baseUrl: "http://x", apiKey: "k", fetch: async () => new Response(new Uint8Array([1, 2, 3])) });
  assert.deepEqual([...(await ok.messages.downloadAttachment(INBOX, "m", "a"))], [1, 2, 3]);
  const bad = new AgentEmailClient({ baseUrl: "http://x", apiKey: "k", fetch: async () => new Response("no", { status: 404 }) });
  await assert.rejects(bad.messages.downloadAttachment(INBOX, "m", "a"), (e: unknown) => (e as AgentEmailError).status === 404);
});
