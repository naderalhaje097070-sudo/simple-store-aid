// Node --import preload: containment only; never imports an MCP handler or changes routing.
import { createServer } from "node:http";
import { writeFileSync, renameSync, existsSync, readFileSync } from "node:fs";

if (process.env.CI_ISOLATED_SUPABASE !== "1" || process.getuid() === 0) {
  throw new Error("ROUTE_UNSAFE_PROCESS");
}
for (const name of [
  "HTTP_PROXY",
  "HTTPS_PROXY",
  "ALL_PROXY",
  "http_proxy",
  "https_proxy",
  "all_proxy",
  "SUPABASE_SERVICE_ROLE_KEY",
]) {
  if (process.env[name]) throw new Error("ROUTE_UNSAFE_ENVIRONMENT");
}
for (const name of ["LOVABLE_API_KEY", "PADDLE_SANDBOX_API_KEY", "PADDLE_LIVE_API_KEY"]) {
  if (process.env[name] !== "oc-app-dummy") throw new Error("OC_APP_DUMMY_ONLY");
}
const nativeFetch = globalThis.fetch;
const state = {
  pid: process.pid,
  uid: process.getuid(),
  guard_ready: false,
  redirect_manual: false,
  native_redirect_rejected: false,
  external_blocked: 0,
  external_denials: [],
  metrics_stub_calls: 0,
  downstream: {},
  gateway_calls: [],
  injected_faults: [],
  activity_checks: 0,
  runtime_conflict_errors: 0,
};
const statePath = process.env.MCP_ROUTE_STATE;
if (!statePath) throw new Error("ROUTE_STATE_REQUIRED");
function save() {
  writeFileSync(statePath + ".tmp", JSON.stringify(state), { mode: 0o644 });
  renameSync(statePath + ".tmp", statePath);
}
// A disposable local redirect canary tests the native implementation under the
// already-installed UID firewall. It supplies no credentials and is not an app route.
const canary = createServer((_req, res) => {
  res.writeHead(302, { Location: "http://198.51.100.1/route-containment-canary" });
  res.end();
});
await new Promise((resolve) => canary.listen(0, "127.0.0.1", resolve));
const canaryUrl = `http://127.0.0.1:${canary.address().port}/redirect`;
try {
  const manual = await nativeFetch(canaryUrl, {
    redirect: "manual",
    signal: AbortSignal.timeout(3000),
  });
  state.redirect_manual = manual.status === 302;
  await manual.body?.cancel();
  try {
    await nativeFetch(canaryUrl, { redirect: "follow", signal: AbortSignal.timeout(3000) });
  } catch (error) {
    // A timeout cannot prove containment. The firewall must reject the socket.
    state.native_redirect_rejected = error.cause?.code === "ECONNREFUSED";
  }
} finally {
  await new Promise((resolve) => canary.close(resolve));
}
if (!state.redirect_manual || !state.native_redirect_rejected) {
  save();
  throw new Error("ROUTE_FIREWALL_SELFTEST_FAILED");
}
globalThis.fetch = (input, init) => {
  const request = new Request(input, init);
  const url = new URL(request.url);
  // Official wrapper0.20.1 enables metrics when the price fixture's dummy key
  // exists. Intercept only that exact synthetic sink; never send it externally.
  if (
    url.href === "https://api.lovable.dev/v1/app-mcp-usage" &&
    request.method === "POST" &&
    request.headers.get("authorization") === "Bearer oc-app-dummy" &&
    request.headers.get("content-type") === "application/json"
  ) {
    state.metrics_stub_calls++;
    save();
    return Promise.resolve(new Response(null, { status: 204 }));
  }
  if (
    url.origin === "https://connector-gateway.lovable.dev" &&
    url.pathname === "/paddle/prices" &&
    request.method === "GET" &&
    ["oc-app-price", "oc-app-missing", "oc-app-escaped &?"].includes(
      url.searchParams.get("external_id"),
    ) &&
    [...url.searchParams.keys()].join() === "external_id"
  ) {
    state.gateway_calls.push({ path: url.pathname, price: url.searchParams.get("external_id") });
    save();
    return Promise.resolve(
      Response.json({
        data:
          url.searchParams.get("external_id") === "oc-app-missing"
            ? []
            : [{ id: "pri_oc_app_dummy" }],
      }),
    );
  }
  if (
    url.origin === "http://127.0.0.1:54321" &&
    url.pathname === "/rest/v1/rpc/current_tenant_id"
  ) {
    state.activity_checks++;
    save();
    const faultPath = statePath.replace(/\.json$/, ".fault");
    const fault = existsSync(faultPath) ? readFileSync(faultPath, "utf8").trim() : "";
    if (fault) {
      state.injected_faults.push(fault);
      save();
      if (fault === "database")
        return Promise.resolve(
          Response.json({ code: "XX000", message: "dummy database fault" }, { status: 500 }),
        );
      if (fault === "transport") return Promise.reject(new Error("dummy transport fault"));
      if (fault === "timeout")
        return new Promise((resolve, reject) => {
          if (request.signal.aborted) {
            reject(request.signal.reason);
            return;
          }
          request.signal.addEventListener("abort", () => reject(request.signal.reason), {
            once: true,
          });
        });
      throw new Error("OC_APP_UNKNOWN_FAULT");
    }
  }
  if (url.origin !== "http://127.0.0.1:54321") {
    state.external_blocked++;
    // Diagnostic contains destination origin and a fixed path class only.
    // No URL query, credentials, headers, body or caller-provided error text.
    if (state.external_denials.length < 8) {
      const known = [
        "/auth/v1/.well-known/jwks.json",
        "/.well-known/oauth-protected-resource",
        "/mcp",
        "/paddle/prices",
      ];
      state.external_denials.push({
        origin: url.origin.slice(0, 200),
        path_class: known.includes(url.pathname) ? url.pathname : "other",
        method: request.method,
        callers: new Error("B5_BLOCKED_DESTINATION").stack
          .split("\n")
          .slice(1, 5)
          .map((line) => line.slice(0, 400)),
      });
    }
    save();
    throw new Error("ROUTE_EXTERNAL_FETCH_BLOCKED");
  }
  // Only fixed pathname counters reach evidence; queries, headers and bodies never do.
  const key =
    url.pathname === "/auth/v1/.well-known/jwks.json"
      ? "jwks"
      : url.pathname.startsWith("/rest/v1/")
        ? "rest"
        : url.pathname === "/auth/v1/user"
          ? "user"
          : "other_local";
  state.downstream[key] = (state.downstream[key] || 0) + 1;
  save();
  return nativeFetch(request, { redirect: "manual" });
};
const originalError = console.error;
console.error = (...args) => {
  if (
    args.some(
      (value) =>
        value instanceof Error &&
        value.message ===
          "SEC_ENV_CONFIG_ERROR: runtime Supabase configuration does not match baked build configuration",
    )
  ) {
    state.runtime_conflict_errors++;
    save();
  }
  originalError(...args);
};
state.guard_ready = true;
save();
if (process.env.MCP_ROUTE_PREFLIGHT === "1") process.exit(0);
// Parent snapshots firewall counters while preload still holds the real bundle.
// This excludes this process's canary without missing startup/import attempts.
const releasePath = process.env.MCP_ROUTE_RELEASE;
if (!releasePath) throw new Error("ROUTE_RELEASE_REQUIRED");
for (let i = 0; i < 200 && !existsSync(releasePath); i++) {
  await new Promise((resolve) => setTimeout(resolve, 50));
}
if (!existsSync(releasePath)) throw new Error("ROUTE_RELEASE_TIMEOUT");
