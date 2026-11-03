const test = require("node:test");
const assert = require("node:assert/strict");
const { randomUUID } = require("node:crypto");
const { loadApplication, memoryStorage, serialLocks } = require("../c4-sale/loader.cjs");
const actor = randomUUID(),
  tenant = randomUUID(),
  order = randomUUID();
const input = () => ({
  operationId: randomUUID(),
  expectedActorId: actor,
  orderId: order,
  amount: 20,
  method: "cash",
});
const success = () => ({
  status: 200,
  error: null,
  data: { success: true, new_paid: 20, status: "partial" },
});
function harness(options = {}) {
  let user = actor,
    response = async () => success();
  const calls = [];
  const client = {
    auth: {
      async getUser() {
        return { data: { user: user ? { id: user } : null }, error: null };
      },
    },
    rpc(name, request) {
      calls.push({ name, request: JSON.parse(JSON.stringify(request)) });
      return {
        abortSignal(signal) {
          assert(signal instanceof AbortSignal);
          return response(request);
        },
      };
    },
  };
  const app = loadApplication({ ...options, client });
  const api = app.load("src/lib/collection-operation.ts");
  const scope = app
    .load("src/lib/sale-operation.ts")
    .saleScope(options.environment ?? "http://127.0.0.1:54321", tenant, actor);
  const hook = app.load("src/lib/db.ts").useCollectDebt(tenant);
  return {
    ...app,
    api,
    scope,
    calls,
    hook,
    send: (x) => hook.mutationFn(x),
    setUser: (x) => (user = x),
    setResponse: (x) => (response = x),
  };
}
test("actual collection hook sends explicit keyed wire and invalidates authoritative queries", async () => {
  const h = harness(),
    d = input();
  await h.send(d);
  assert.deepEqual(h.calls, [
    {
      name: "collect_order_debt_idempotent",
      request: {
        p_idempotency_key: d.operationId,
        p_order_id: order,
        p_amount: 20,
        p_method: "cash",
      },
    },
  ]);
  assert.equal(h.api.loadCollection(h.scope).status, "completed");
  h.hook.onSuccess();
  assert.deepEqual(JSON.parse(JSON.stringify(h.invalidations)), [
    { queryKey: ["invoices", tenant] },
    { queryKey: ["payments", tenant] },
  ]);
});
test("hidden success persists exact UUID and payload through reload and years", async () => {
  const store = memoryStorage(),
    d = input(),
    h = harness({ store });
  h.setResponse(async () => {
    throw Error("hidden commit");
  });
  await assert.rejects(h.send(d));
  const raw = [...store.values.values()][0],
    r = harness({ store, now: () => Date.now() + 1e12 });
  assert.equal([...store.values.values()][0], raw);
  await r.send(r.api.loadCollection(r.scope).input);
  assert.deepEqual(r.calls[0], h.calls[0]);
});
test("unknown blocks new UUID even for identical amount", async () => {
  const h = harness();
  h.setResponse(async () => {
    throw Error("unknown");
  });
  await assert.rejects(h.send(input()));
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 1);
});
test("a new intentional equal payment gets a distinct key", async () => {
  const h = harness();
  await h.send(input());
  await h.send(input());
  assert.notEqual(h.calls[0].request.p_idempotency_key, h.calls[1].request.p_idempotency_key);
});
for (const change of [{ amount: 21 }, { method: "transfer" }, { orderId: randomUUID() }])
  test("same UUID payload conflict " + JSON.stringify(change), async () => {
    const h = harness(),
      d = input();
    await h.send(d);
    await assert.rejects(h.send({ ...d, ...change }));
    assert.equal(h.calls.length, 1);
  });
test("completed local receipt always reaches real server replay", async () => {
  const h = harness(),
    d = input();
  await h.send(d);
  await h.send(d);
  assert.deepEqual(h.calls[0], h.calls[1]);
});
test("parallel tabs share browser lock and preserve one unresolved operation", async () => {
  const store = memoryStorage(),
    locks = serialLocks(),
    a = harness({ store, locks }),
    b = harness({ store, locks }),
    d = input();
  a.setResponse(async () => {
    throw Error("lost");
  });
  const outcomes = await Promise.allSettled([a.send(d), b.send(input())]);
  assert(outcomes.every((x) => x.status === "rejected"));
  assert.equal(a.calls.length, 1);
  assert.equal(b.calls.length, 0);
  await b.send(b.api.loadCollection(b.scope).input);
  assert.deepEqual(a.calls[0], b.calls[0]);
});
test("caller mutation while waiting for lock cannot change persisted payload", async () => {
  const h = harness(),
    d = input(),
    p = h.send(d);
  d.amount = 99;
  await p;
  assert.equal(h.calls[0].request.p_amount, 20);
});
for (const data of [
  null,
  {},
  { success: false },
  { success: true, new_paid: "20", status: "partial" },
  { success: true, new_paid: 20, status: "unknown" },
])
  test("invalid reply retains identity " + JSON.stringify(data), async () => {
    const h = harness(),
      d = input();
    h.setResponse(async () => ({ status: 200, error: null, data }));
    await assert.rejects(h.send(d));
    assert.equal(h.api.loadCollection(h.scope).status, "pending");
  });
test("fresh known SQL rollback releases only a never-uncertain slot", async () => {
  const h = harness();
  h.setResponse(async () => ({
    status: 400,
    error: { code: "P0001", message: "amount_exceeds_remaining" },
    data: null,
  }));
  await assert.rejects(h.send(input()));
  assert.equal(h.api.loadCollection(h.scope), null);
});
test("denial after unknown cannot erase a possibly committed operation", async () => {
  const h = harness(),
    d = input();
  h.setResponse(async () => {
    throw Error("lost");
  });
  await assert.rejects(h.send(d));
  h.setResponse(async () => ({
    status: 400,
    error: { code: "P0001", message: "amount_exceeds_remaining" },
    data: null,
  }));
  await assert.rejects(h.send(d));
  assert.equal(h.api.loadCollection(h.scope).input.operationId, d.operationId);
});
for (const user of [null, randomUUID()])
  test("actor mismatch before sending " + user, async () => {
    const h = harness();
    h.setUser(user);
    await assert.rejects(h.send(input()));
    assert.equal(h.calls.length, 0);
  });
test("actor change after reply leaves operation pending in original scope", async () => {
  const h = harness();
  h.setResponse(async () => {
    h.setUser(randomUUID());
    return success();
  });
  await assert.rejects(h.send(input()));
  assert.equal(h.api.loadCollection(h.scope).status, "pending");
});
test("environment tenant actor storage namespaces do not collide", () => {
  const h = harness(),
    k = h.api.collectionKey(h.scope);
  for (const s of [
    { ...h.scope, environment: "http://127.0.0.1:54323" },
    { ...h.scope, tenantId: randomUUID() },
    { ...h.scope, actorId: randomUUID() },
  ])
    assert.notEqual(k, h.api.collectionKey(s));
});
test("storage failure sends no financial request", async () => {
  const store = memoryStorage();
  store.setItem = () => {
    throw Error("blocked");
  };
  const h = harness({ store });
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
});
test("missing locks fails closed", async () => {
  const h = harness({ locks: null });
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
});
test("malformed durable state is not silently overwritten", async () => {
  const h = harness();
  h.store.setItem(h.api.collectionKey(h.scope), "{}");
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
});
for (const amount of [NaN, Infinity, 0, -1])
  test("invalid amount sends nothing " + amount, async () => {
    const h = harness();
    await assert.rejects(h.send({ ...input(), amount }));
    assert.equal(h.calls.length, 0);
  });
