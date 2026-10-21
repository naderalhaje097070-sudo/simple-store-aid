const { test } = require("node:test");
const assert = require("node:assert/strict");
const { load, request } = require("./webhook_invoke.cjs");
Object.assign(process.env, {
  PADDLE_SANDBOX_API_KEY: "synthetic",
  PADDLE_LIVE_API_KEY: "synthetic",
  LOVABLE_API_KEY: "synthetic",
  PAYMENTS_LIVE_WEBHOOK_SECRET: "app02-live-test-secret",
  PAYMENTS_SANDBOX_WEBHOOK_SECRET: "app02-sandbox-test-secret",
});
const { verifyWebhook } = load("src/lib/paddle.server.ts");
const { createSubscriptionWebhookHandler, subscriptionWrite } = load(
  "src/lib/subscription-webhook.server.ts",
);
const spec = {
  event: "evt_" + "a".repeat(26),
  sub: "sub_" + "a".repeat(26),
  tenant: "11111111-1111-1111-1111-111111111111",
  user: "22222222-2222-2222-2222-222222222222",
};
function handler(persist, verify = verifyWebhook) {
  const logs = [];
  return {
    logs,
    handle: createSubscriptionWebhookHandler({ verify, persist, report: (r) => logs.push(r) }),
  };
}
test("real SDK retains microsecond order and canonical persistence fields", async () => {
  const at = "2026-02-01T00:00:00.123456Z";
  const event = await verifyWebhook(request({ ...spec, at }), "sandbox");
  const write = subscriptionWrite(event, "sandbox");
  assert.equal(write.p_occurred_at, at);
  assert.equal(write.p_subscription.created_at, "2026-01-01T00:00:00Z");
  assert.equal(write.p_subscription.product_id, "synthetic-plan");
  assert.equal("notification_id" in write, false);
});
for (const status of [
  "applied",
  "duplicate",
  "stale",
  "unchanged",
  "legacy_repaired",
  "non_current",
]) {
  test("acknowledges only durable outcome " + status, async () => {
    let calls = 0;
    const { handle } = handler(async (write, signal) => {
      calls++;
      assert.equal(signal.aborted, false);
      assert.equal(write.p_event_id, spec.event);
      return { data: { status }, error: null };
    });
    const response = await handle(request(spec));
    assert.equal(response.status, 200);
    assert.deepEqual(await response.json(), { received: true });
    assert.equal(calls, 1);
  });
}
for (const [name, result] of Object.entries({
  database_error: {
    data: { status: "applied" },
    error: { code: "23505", message: "sensitive-db-details" },
  },
  null_data: { data: null, error: null },
  zero_rows: { data: [], error: null },
  unknown_status: { data: { status: "ok" }, error: null },
})) {
  test("fails closed on " + name, async () => {
    const { handle, logs } = handler(async () => result);
    const response = await handle(request(spec));
    assert.equal(response.status, 503);
    assert.deepEqual(logs, ["persistence_failed"]);
    assert.equal((await response.text()).includes("sensitive"), false);
  });
}
test("transport rejection is retryable without raw error logging", async () => {
  const { handle, logs } = handler(async () => {
    throw new Error("sensitive-db-details");
  });
  assert.equal((await handle(request(spec))).status, 503);
  assert.deepEqual(logs, ["persistence_failed"]);
});
test("invalid environments never reach verification or persistence", async () => {
  let calls = 0;
  const { handle } = handler(
    async () => {
      calls++;
    },
    async () => {
      calls++;
    },
  );
  assert.equal((await handle(request({ ...spec, env: "production" }))).status, 400);
  assert.equal(calls, 0);
});
test("wrong live secret never persists", async () => {
  let calls = 0;
  const { handle, logs } = handler(async () => {
    calls++;
  });
  assert.equal((await handle(request({ ...spec, env: "live", wrongSecret: true }))).status, 400);
  assert.equal(calls, 0);
  assert.deepEqual(logs, ["verification_failed"]);
});
for (const [name, extra] of Object.entries({
  missing_mapping: { noMetadata: true },
  missing_items: { noItems: true },
  unsupported_precision: { at: "2026-02-01T00:00:00.1234567Z" },
  invalid_calendar: { at: "2026-02-30T00:00:00Z" },
  inconsistent_canceled: { type: "subscription.canceled", status: "active" },
})) {
  test("rejects signed invalid payload " + name, async () => {
    let calls = 0;
    const { handle, logs } = handler(async () => {
      calls++;
    });
    assert.equal((await handle(request({ ...spec, ...extra }))).status, 422);
    assert.equal(calls, 0);
    assert.deepEqual(logs, ["payload_invalid"]);
  });
}
test("verified unsupported notification is explicitly ignored without persistence", async () => {
  let calls = 0;
  const { handle } = handler(
    async () => {
      calls++;
    },
    async () => ({ eventType: "synthetic.unhandled" }),
  );
  const response = await handle(request(spec));
  assert.deepEqual(await response.json(), { received: true, ignored: true });
  assert.equal(calls, 0);
});
test("deadline returns retryable response and aborts, without claiming rollback", async () => {
  let signal;
  const start = Date.now();
  const { handle, logs } = handler(async (_, s) => {
    signal = s;
    return new Promise(() => {});
  });
  assert.equal((await handle(request(spec))).status, 503);
  assert.equal(signal.aborted, true);
  assert.ok(Date.now() - start >= 3400 && Date.now() - start < 4800);
  assert.deepEqual(logs, ["persistence_failed"]);
});
