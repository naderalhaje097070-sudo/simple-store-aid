// Runs the exact application definition and locked protocol adapter, without auth stubs.
import { readFileSync } from "node:fs";
const status = JSON.parse(readFileSync(process.env.MCP_TEST_STATUS_FILE, "utf8"));
if (process.env.CI_ISOLATED_SUPABASE !== "1" || status.API_URL !== "http://127.0.0.1:54321") {
  throw new Error("MCP_TEST_UNSAFE_TARGET");
}
process.env.SUPABASE_URL = status.API_URL;
process.env.SUPABASE_PUBLISHABLE_KEY = status.ANON_KEY;
process.env.MONGEZZ_DEPLOY_TARGET = "ci";
process.env.VITE_SUPABASE_URL = status.API_URL;
process.env.VITE_SUPABASE_PUBLISHABLE_KEY = status.ANON_KEY;
process.env.VITE_SUPABASE_PROJECT_ID = "monjez-mcp-ci";
process.env.SUPABASE_PROJECT_ID = "monjez-mcp-ci";
delete process.env.LOVABLE_API_KEY;
delete process.env.SUPABASE_SERVICE_ROLE_KEY;
const sdk = JSON.parse(readFileSync("node_modules/@lovable.dev/mcp-js/package.json", "utf8"));
if (sdk.version !== "0.20.1") throw new Error("MCP_TEST_SDK_VERSION");

// A blocked remote request is a setup failure, never authorization evidence.
const nativeFetch = globalThis.fetch;
const state = { blocked_issuer_requests: 0, blocked_other_requests: 0, sdk_exceptions: 0 };
globalThis.fetch = (input, init) => {
  const url = new URL(input instanceof Request ? input.url : String(input));
  if (url.origin !== status.API_URL) {
    if (url.hostname === "monjez-mcp-ci.supabase.co") state.blocked_issuer_requests++;
    else state.blocked_other_requests++;
    throw new Error("MCP_TEST_REMOTE_NETWORK_BLOCKED");
  }
  const request = new Request(input, init);
  // Never let a redirect escape containment through the native fetch implementation.
  return nativeFetch(request, { redirect: "manual" });
};
const { createMcpProtocolHandler } = await import("@lovable.dev/mcp-js/protocols/mcp");
const { default: definition } = await import("../../src/lib/mcp/index.ts");
const handler = createMcpProtocolHandler(definition);
const server = Bun.serve({
  hostname: "127.0.0.1",
  port: 54325,
  async fetch(request) {
    const path = new URL(request.url).pathname;
    if (path === "/test-health" && request.method === "GET") {
      return Response.json({
        ready: true,
        sdk_version: sdk.version,
        source_definition: "src/lib/mcp/index.ts",
        source_derived_issuer: definition.auth.issuer,
        source_jwks_uri: definition.auth.jwksUri,
        oauth_client_claim_required: definition.auth.requireOAuthClientClaim !== false,
        session_mode: "stateless",
        ...state,
      });
    }
    if (path !== "/mcp") return new Response("", { status: 404 });
    try {
      return await handler(request);
    } catch {
      state.sdk_exceptions++;
      return Response.json({ error: "sdk_exception" }, { status: 500 });
    }
  },
});
process.on("SIGTERM", () => {
  server.stop(true);
  process.exit(0);
});
