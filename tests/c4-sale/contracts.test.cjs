const test = require("node:test");
const assert = require("node:assert/strict");
const { randomUUID } = require("node:crypto");
const { loadApplication, memoryStorage, serialLocks } = require("./loader.cjs");
const actor = randomUUID(),
  tenant = randomUUID(),
  product = randomUUID(),
  order = randomUUID();
const success = () => ({
  data: { success: true, order_id: order, number: 7 },
  error: null,
  status: 200,
});
const input = () => ({
  operationId: randomUUID(),
  items: [{ productId: product, name: "synthetic", qty: 0.25, price: 12.5, cost: 2 }],
  total: 3.13,
  paid: 3.13,
  delivery: "direct",
  method: "cash",
});
function harness(options = {}) {
  const calls = [];
  let user = actor,
    response = async () => success();
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
  const loaded = loadApplication({ ...options, client });
  const api = loaded.load("src/lib/sale-operation.ts"),
    db = loaded.load("src/lib/db.ts");
  return {
    ...loaded,
    api,
    db,
    calls,
    setUser(value) {
      user = value;
    },
    setResponse(value) {
      response = value;
    },
    scope: api.saleScope(options.environment ?? "http://127.0.0.1:54321", tenant, actor),
    send(value) {
      return db.useCreateSale(tenant).mutationFn(value);
    },
  };
}
test("actual hook uses typed idempotent RPC, explicit key, quarter quantity and existing cents", async () => {
  const h = harness(),
    draft = input(),
    result = await h.send(draft);
  assert.equal(result.orderId, order);
  assert.equal(result.number, "7");
  assert.deepEqual(h.calls[0], {
    name: "create_sale_with_items_idempotent",
    request: {
      p_idempotency_key: draft.operationId,
      p_customer_id: null,
      p_delivery: "direct",
      p_courier_id: null,
      p_paid: 3.13,
      p_method: "cash",
      p_items: [{ productId: product, qty: 0.25 }],
      p_courier_state: null,
    },
  });
  assert.equal(h.api.loadSale(h.scope).status, "completed");
  assert(h.events.length >= 2);
});
for (const [paid, state] of [
  [0, "pending"],
  [1, "delivered_partial"],
  [3.13, "delivered_full"],
])
  test("actual courier wire preserves " + state, async () => {
    const h = harness();
    await h.send({
      ...input(),
      delivery: "courier",
      courierId: randomUUID(),
      customerId: randomUUID(),
      paid,
    });
    assert.equal(h.calls[0].request.p_courier_state, state);
  });
test("lost reply survives 31 minutes, years and a fresh module context with same exact request/key", async () => {
  let now = 1_000;
  const store = memoryStorage(),
    draft = input();
  const h = harness({ store, now: () => now });
  h.setResponse(async () => {
    throw Error("lost after model commit");
  });
  await assert.rejects(h.send(draft));
  const bytes = [...store.values.values()][0];
  now += 31 * 60 * 1000;
  assert.equal(h.api.loadSale(h.scope).input.operationId, draft.operationId);
  now += 10 * 365 * 24 * 60 * 60 * 1000;
  const reloaded = harness({ store, now: () => now });
  assert.equal([...store.values.values()][0], bytes);
  await reloaded.send(reloaded.api.loadSale(reloaded.scope).input);
  assert.deepEqual(reloaded.calls[0].request, h.calls[0].request);
});
test("second operation cannot replace unresolved slot even with identical products", async () => {
  const h = harness();
  h.setResponse(async () => {
    throw Error("unknown");
  });
  const draft = input();
  await assert.rejects(h.send(draft));
  const raw = [...h.store.values.values()][0];
  await assert.rejects(h.send({ ...draft, operationId: randomUUID() }));
  assert.equal(h.calls.length, 1);
  assert.equal([...h.store.values.values()][0], raw);
});
test("same identity with changed wire is refused before RPC", async () => {
  const h = harness();
  const draft = input();
  await h.send(draft);
  await assert.rejects(h.send({ ...draft, paid: 0, customerId: randomUUID() }));
  assert.equal(h.calls.length, 1);
});
test("new identical logical sale after definitive success gets a new explicit key", async () => {
  const h = harness(),
    draft = input();
  await h.send(draft);
  await h.send({ ...draft, operationId: randomUUID() });
  assert.notEqual(h.calls[0].request.p_idempotency_key, h.calls[1].request.p_idempotency_key);
});
test("a local completion receipt never bypasses actual server replay", async () => {
  const h = harness(),
    draft = input();
  await h.send(draft);
  await h.send(draft);
  assert.equal(h.calls.length, 2);
  assert.deepEqual(h.calls[0], h.calls[1]);
});
for (const data of [
  null,
  {},
  { success: false, order_id: order, number: 7 },
  { success: true, order_id: "wrong", number: 7 },
  { success: true, order_id: order, number: "7" },
  { success: true, order_id: order, number: 1.5 },
])
  test("invalid success retains key: " + JSON.stringify(data), async () => {
    const h = harness(),
      draft = input();
    h.setResponse(async () => ({ data, error: null, status: 200 }));
    await assert.rejects(h.send(draft));
    assert.equal(h.api.loadSale(h.scope).status, "pending");
    h.setResponse(async () => success());
    await h.send(draft);
    assert.equal(h.calls[1].request.p_idempotency_key, draft.operationId);
  });
for (const failure of ["read", "write", "readback"])
  test("storage " + failure + " fails before outbound write", async () => {
    const store = memoryStorage();
    if (failure === "read")
      store.getItem = () => {
        throw Error("blocked");
      };
    if (failure === "write")
      store.setItem = () => {
        throw Error("quota");
      };
    if (failure === "readback") store.setItem = () => {};
    const h = harness({ store });
    await assert.rejects(h.send(input()));
    assert.equal(h.calls.length, 0);
  });
test("missing Web Locks refuses before storage or RPC", async () => {
  const h = harness({ locks: null });
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
  assert.equal(h.store.values.size, 0);
});
test("malformed and wrong-scope records are retained, not overwritten", async () => {
  const h = harness(),
    key = h.api.saleStorageKey(h.scope);
  h.store.setItem(key, "{");
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
  assert.equal(h.store.getItem(key), "{");
});
test("old unscoped candidate key is neither TTL-expired nor reassigned", async () => {
  const h = harness();
  h.session.setItem("mongezz.pending-sale-idempotency.v1", "unresolved-old-data");
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
  assert.equal(h.session.values.size, 1);
});
test("actor, tenant and environment storage keys are distinct", () => {
  const h = harness(),
    scope = h.scope,
    key = h.api.saleStorageKey(scope);
  for (const change of [
    { actorId: randomUUID() },
    { tenantId: randomUUID() },
    { environment: "https://other.example" },
  ])
    assert.notEqual(key, h.api.saleStorageKey({ ...scope, ...change }));
});
test("old actor's captured recovery cannot dispatch under new actor", async () => {
  const h = harness();
  h.setUser(randomUUID());
  await assert.rejects(h.send({ ...input(), expectedActorId: actor }));
  assert.equal(h.calls.length, 0);
});
test("account change after commit keeps old actor pending, without validated success", async () => {
  const h = harness();
  h.setResponse(async () => {
    h.setUser(randomUUID());
    return success();
  });
  await assert.rejects(h.send(input()));
  assert.equal(h.api.loadSale(h.scope).status, "pending");
});
test("unauthenticated actor refuses before financial RPC", async () => {
  const h = harness();
  h.setUser(null);
  await assert.rejects(h.send(input()));
  assert.equal(h.calls.length, 0);
});
test("parallel same-operation callbacks retain one UUID across serialized real callbacks", async () => {
  const h = harness(),
    draft = input();
  await Promise.all([h.send(draft), h.send(draft)]);
  assert.equal(h.calls.length, 2);
  assert.deepEqual(h.calls[0], h.calls[1]);
});
test("parallel pending different operation cannot overwrite after first uncertain response", async () => {
  const store = memoryStorage(),
    locks = serialLocks(),
    a = harness({ store, locks }),
    b = harness({ store, locks });
  a.setResponse(async () => {
    throw Error("unknown");
  });
  const outcomes = await Promise.allSettled([a.send(input()), b.send(input())]);
  assert(outcomes.every((x) => x.status === "rejected"));
  assert.equal(b.calls.length, 0);
});
test("fresh confirmed canonical SQL rollback releases only its own never-uncertain attempt", async () => {
  const h = harness();
  h.setResponse(async () => ({
    data: null,
    status: 400,
    error: { code: "P0001", message: "insufficient_stock: synthetic" },
  }));
  await assert.rejects(h.send(input()));
  assert.equal(h.api.loadSale(h.scope), null);
});
test("a denial after lost reply cannot erase a potentially committed operation", async () => {
  const h = harness(),
    draft = input();
  h.setResponse(async () => {
    throw Error("unknown");
  });
  await assert.rejects(h.send(draft));
  h.setResponse(async () => ({
    data: null,
    status: 400,
    error: { code: "P0001", message: "insufficient_stock" },
  }));
  await assert.rejects(h.send(draft));
  assert.equal(h.api.loadSale(h.scope).status, "pending");
});
test("storage completion failure after server success keeps original identity", async () => {
  const h = harness(),
    draft = input(),
    original = h.store.setItem;
  h.setResponse(async () => {
    h.store.setItem = () => {
      throw Error("quota after commit");
    };
    return success();
  });
  await assert.rejects(h.send(draft));
  h.store.setItem = original;
  assert.equal(h.api.loadSale(h.scope).input.operationId, draft.operationId);
  assert.equal(h.api.loadSale(h.scope).status, "pending");
});
for (const qty of [0, -1, 0.001, NaN, Infinity])
  test("invalid quantity never reaches RPC: " + qty, async () => {
    const h = harness(),
      draft = input();
    draft.items[0].qty = qty;
    await assert.rejects(h.send(draft));
    assert.equal(h.calls.length, 0);
  });
