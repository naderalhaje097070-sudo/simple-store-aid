// Actual current hook + locked SDK; loopback-only disposable Auth/RPC transport.
const fs = require("node:fs");
const assert = require("node:assert/strict");
const { createClient } = require("@supabase/supabase-js");
const { loadApplication, memoryStorage, serialLocks } = require("../c4-sale/loader.cjs");
if (process.argv[2] === "--preflight") {
  assert.equal(typeof loadApplication, "function");
  assert.equal(typeof createClient, "function");
  console.log("C5_COLLECTION_NATIVE_IMPORTS_OK");
  process.exit(0);
}
const config = JSON.parse(fs.readFileSync(process.argv[2], "utf8"));
assert.equal(config.url, "http://127.0.0.1:54321");
const requests = [],
  responses = [];
const client = createClient(config.url, config.anon, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: false,
  },
  global: {
    fetch: async (input, init) => {
      const url = new URL(typeof input === "string" ? input : input.url);
      assert.equal(url.origin, config.url);
      assert(
        url.pathname.startsWith("/auth/v1/") ||
          url.pathname === "/rest/v1/rpc/collect_order_debt_idempotent",
      );
      if (url.pathname.startsWith("/rest/")) requests.push(JSON.parse(init.body));
      const result = await fetch(input, { ...init, redirect: "error" });
      if (url.pathname.startsWith("/rest/")) {
        responses.push(result.status);
        if (result.ok && ["lost", "null"].includes(config.mode)) {
          await result.arrayBuffer(); // Commit reply reached transport; UI never receives it.
          if (config.mode === "lost")
            throw new TypeError("synthetic response loss after real RPC reply");
          return new Response("null", {
            status: 200,
            headers: { "content-type": "application/json" },
          });
        }
      }
      return result;
    },
  },
});
async function main() {
  const session = await client.auth.setSession({
    access_token: config.actor.token,
    refresh_token: config.actor.refresh,
  });
  assert.equal(session.error, null);
  const store = memoryStorage();
  if (fs.existsSync(config.storage))
    for (const [key, value] of Object.entries(JSON.parse(fs.readFileSync(config.storage, "utf8"))))
      store.values.set(key, value);
  function persist() {
    fs.writeFileSync(config.storage + ".tmp", JSON.stringify(Object.fromEntries(store.values)), {
      mode: 0o600,
    });
    fs.renameSync(config.storage + ".tmp", config.storage);
  }
  store.setItem = (key, value) => {
    store.values.set(key, value);
    persist();
  };
  store.removeItem = (key) => {
    store.values.delete(key);
    persist();
  };
  const app = loadApplication({
    client,
    store,
    locks: serialLocks(),
    now: () => Date.now() + (config.advanceMs || 0),
  });
  const operations = app.load("src/lib/collection-operation.ts");
  const scope = app
    .load("src/lib/sale-operation.ts")
    .saleScope(config.url, config.actor.tenant, config.actor.uid);
  const before = operations.loadCollection(scope);
  const input = config.recover
    ? { ...before.input, expectedActorId: config.actor.uid }
    : config.input;
  let result,
    failure = false;
  try {
    const run = () =>
      app.load("src/lib/db.ts").useCollectDebt(config.actor.tenant).mutationFn(input);
    result = config.mode === "parallel" ? await Promise.all([run(), run()]) : await run();
  } catch {
    failure = true;
  }
  const after = operations.loadCollection(scope);
  console.log(
    JSON.stringify({
      failure,
      result,
      requests,
      responses,
      state: after?.status ?? null,
      retainedKey: after?.input.operationId ?? null,
      source: process.env.EXPECTED_SOURCE,
      actualSDK: true,
      storageIsSynthetic: true,
      actualLoopbackRPC: true,
    }),
  );
}
main().catch(() => {
  console.error("C5_COLLECTION_NATIVE_HOOK_SETUP_FAILED");
  process.exitCode = 1;
});
