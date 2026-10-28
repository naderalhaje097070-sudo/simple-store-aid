// Node --import preload: containment only; never imports an MCP handler or changes routing.
import { createServer } from "node:http";
import { writeFileSync, renameSync, existsSync } from "node:fs";

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
  "LOVABLE_API_KEY",
  "SUPABASE_SERVICE_ROLE_KEY",
]) {
  if (process.env[name]) throw new Error("ROUTE_UNSAFE_ENVIRONMENT");
}
const nativeFetch = globalThis.fetch;
const state = {
  pid: process.pid,
  uid: process.getuid(),
  guard_ready: false,
  redirect_manual: false,
  native_redirect_rejected: false,
  external_blocked: 0,
  downstream: {},
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
  if (url.origin !== "http://127.0.0.1:54321") {
    state.external_blocked++;
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
