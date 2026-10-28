/* Actual route + locked SDK signature verification. Synthetic input only; never prints credentials. */
const fs = require("node:fs");
const path = require("node:path");
const vm = require("node:vm");
const crypto = require("node:crypto");
const cp = require("node:child_process");
const ts = require("typescript");
const root = path.resolve(__dirname, "../..");
const cache = new Map();
let post;
function load(name, baseline = false) {
  if (cache.has(name)) return cache.get(name);
  const file = path.join(root, name);
  const source = baseline
    ? cp.execFileSync("git", ["show", "dc0ced4fcf20947ccaa603a3e4b5cc16f5b8f0a0:" + name], {
        cwd: root,
        encoding: "utf8",
      })
    : fs.readFileSync(file, "utf8");
  const output = ts.transpileModule(source, {
    compilerOptions: { module: ts.ModuleKind.CommonJS, target: ts.ScriptTarget.ES2022 },
  }).outputText;
  const module = { exports: {} };
  cache.set(name, module.exports);
  const customRequire = (id) => {
    if (id === "@tanstack/react-router")
      return {
        createFileRoute: () => (config) => {
          post = config.server.handlers.POST;
          return {};
        },
      };
    if (id.startsWith("@/")) return load("src/" + id.slice(2) + ".ts");
    return require(id);
  };
  // Fixed reason logging is counted, never exported as raw SDK/DB exception text.
  vm.runInNewContext(
    "(function(require,module,exports,process,console,Request,Response,URL,AbortController,setTimeout,clearTimeout){" +
      output +
      "\n})",
    {},
    { filename: file },
  )(
    customRequire,
    module,
    module.exports,
    process,
    { error: () => {}, log: () => {} },
    Request,
    Response,
    URL,
    AbortController,
    setTimeout,
    clearTimeout,
  );
  return module.exports;
}
function fixture(spec) {
  const created = spec.created || "2026-01-01T00:00:00Z";
  const product = {
    id: "pro_" + "p".repeat(26),
    name: "Synthetic",
    tax_category: "standard",
    status: "active",
    created_at: created,
    updated_at: created,
    import_meta: { external_id: spec.product || "synthetic-plan", imported_from: "fixture" },
  };
  const price = {
    id: "pri_" + "p".repeat(26),
    product_id: product.id,
    description: "Synthetic",
    type: "standard",
    billing_cycle: { interval: "month", frequency: 1 },
    tax_mode: "account_setting",
    unit_price: { amount: "100", currency_code: "USD" },
    quantity: { minimum: 1, maximum: 1 },
    status: "active",
    created_at: created,
    updated_at: created,
    import_meta: { external_id: spec.price || "synthetic-price", imported_from: "fixture" },
  };
  const event = {
    event_id: spec.event,
    event_type: spec.type || "subscription.created",
    notification_id: spec.notification || "ntf_" + "n".repeat(26),
    occurred_at: spec.at || "2026-02-01T00:00:00Z",
    data: {
      id: spec.sub,
      status: spec.status || "active",
      customer_id: spec.customer || "ctm_" + "c".repeat(26),
      address_id: "add_" + "a".repeat(26),
      currency_code: "USD",
      created_at: created,
      updated_at: spec.at || "2026-02-01T00:00:00Z",
      collection_mode: "automatic",
      billing_cycle: { interval: "month", frequency: 1 },
      current_billing_period: spec.noPeriod
        ? null
        : { starts_at: "2026-01-01T00:00:00Z", ends_at: "2026-03-01T00:00:00Z" },
      scheduled_change: spec.cancel
        ? { action: "cancel", effective_at: "2026-03-01T00:00:00Z", resume_at: null }
        : null,
      items: spec.noItems
        ? []
        : [
            {
              status: "active",
              quantity: 1,
              recurring: true,
              created_at: created,
              updated_at: created,
              product,
              price,
            },
          ],
      custom_data: spec.noMetadata ? null : { tenantId: spec.tenant, userId: spec.user },
    },
  };
  return event;
}
function request(spec) {
  const body = JSON.stringify(fixture(spec));
  const stamp = String(Math.floor(Date.now() / 1000));
  const secret = spec.wrongSecret
    ? "incorrect-test-secret"
    : spec.env === "live"
      ? "app02-live-test-secret"
      : "app02-sandbox-test-secret";
  const signature = crypto
    .createHmac("sha256", secret)
    .update(stamp + ":" + body)
    .digest("hex");
  return new Request(
    "http://localhost/api/public/payments/webhook" +
      (spec.env === undefined ? "" : "?env=" + encodeURIComponent(spec.env)),
    { method: "POST", body, headers: { "paddle-signature": "ts=" + stamp + ";h1=" + signature } },
  );
}
module.exports = { load, fixture, request };
if (require.main === module) {
  (async () => {
    const input = JSON.parse(fs.readFileSync(0, "utf8"));
    if (input.statusFile) {
      const status = JSON.parse(fs.readFileSync(input.statusFile, "utf8"));
      if (status.API_URL !== "http://127.0.0.1:54321") throw new Error("loopback_required");
      process.env.SUPABASE_URL = status.API_URL;
      process.env.SUPABASE_SERVICE_ROLE_KEY = status.SERVICE_ROLE_KEY;
    }
    Object.assign(process.env, {
      PADDLE_SANDBOX_API_KEY: "synthetic",
      PADDLE_LIVE_API_KEY: "synthetic",
      LOVABLE_API_KEY: "synthetic",
      PAYMENTS_LIVE_WEBHOOK_SECRET: "app02-live-test-secret",
      PAYMENTS_SANDBOX_WEBHOOK_SECRET: "app02-sandbox-test-secret",
    });
    load("src/routes/api/public/payments/webhook.ts", input.baseline === true);
    const results = await Promise.all(
      input.events.map(async (spec) => {
        const response = await post({ request: request(spec) });
        return {
          status: response.status,
          acknowledged: response.status === 200 && (await response.json()).received === true,
        };
      }),
    );
    // All handler responses are resolved. Flush the safe summary, then close test-only keepalive handles.
    process.stdout.write(JSON.stringify(results) + "\n", () => process.exit(0));
  })().catch(() => {
    process.stderr.write("APP02_INVOCATION_FAILED\n");
    process.exitCode = 2;
  });
}
