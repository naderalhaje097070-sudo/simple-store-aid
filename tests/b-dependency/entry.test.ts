import { afterAll, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { pathToFileURL } from "node:url";

// Compile the actual handwritten entry; only the delegated framework handler is
// a bounded stub. This proves placement, not actual OAuth or deployed transport.
const out = mkdtempSync(join(tmpdir(), "monjez-boundary-entry-"));
const fixture = {
  MONGEZZ_DEPLOY_TARGET: "ci",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "boundary-fixture-placeholder",
  VITE_SUPABASE_PROJECT_ID: "boundary-fixture",
};
const saved = { ...process.env };
for (const key of [
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "SUPABASE_PROJECT_ID",
  "SUPABASE_SERVICE_ROLE_KEY",
])
  delete process.env[key];
Object.assign(process.env, fixture);
const result = await Bun.build({
  entrypoints: ["src/server.ts"],
  outdir: out,
  target: "bun",
  define: Object.fromEntries(
    Object.entries(fixture).map(([key, value]) => [
      `__MONGEZZ_BUILD_${key === "MONGEZZ_DEPLOY_TARGET" ? "DEPLOY_TARGET" : key.replace("VITE_", "")}__`,
      JSON.stringify(value),
    ]),
  ),
  plugins: [
    {
      name: "bounded-delegate",
      setup(build) {
        build.onResolve({ filter: /^@tanstack\/react-start\/server-entry$/ }, () => ({
          path: "delegate",
          namespace: "fixture",
        }));
        build.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
          loader: "js",
          contents:
            'export default { async fetch(request) { return new Response(await request.text(), {status:202,headers:{"x-delegated":"yes","x-original":request.headers.get("x-original")??""}}) } };',
        }));
      },
    },
  ],
});
if (!result.success) throw new Error(JSON.stringify(result.logs));
const entry = (await import(pathToFileURL(result.outputs[0].path).href)).default;
afterAll(() => {
  for (const key of Object.keys(process.env)) if (!(key in saved)) delete process.env[key];
  Object.assign(process.env, saved);
  rmSync(out, { recursive: true, force: true });
});

test("actual entry delegates valid MCP bytes and original headers", async () => {
  const body = '{ "method":"tools/list", "params":{} }';
  const response = await entry.fetch(
    new Request("http://127.0.0.1/mcp", {
      method: "POST",
      body,
      headers: { "x-original": "marker" },
    }),
    {},
    {},
  );
  expect(response.status).toBe(202);
  expect(response.headers.get("x-original")).toBe("marker");
  expect(await response.text()).toBe(body);
});

test("actual entry refuses normalized oversized and malformed inputs before delegation", async () => {
  for (const path of ["/mcp", "/MCP/", "/%6dcp", "/%2emcp/invoke-tool/list_products"]) {
    const response = await entry.fetch(
      new Request(`http://127.0.0.1${path}`, { method: "POST", body: " ".repeat(65537) }),
      {},
      {},
    );
    expect(response.status).toBe(413);
    expect(response.headers.has("x-delegated")).toBe(false);
  }
  const response = await entry.fetch(
    new Request("http://127.0.0.1/mcp", { method: "POST", body: "private-input" }),
    {},
    {},
  );
  expect(response.status).toBe(400);
  expect(response.headers.has("x-delegated")).toBe(false);
});

test("non-MCP body handling still belongs to the original delegated entry", async () => {
  const response = await entry.fetch(
    new Request("http://127.0.0.1/unchanged", { method: "POST", body: "not-json" }),
    {},
    {},
  );
  expect(response.status).toBe(202);
  expect(await response.text()).toBe("not-json");
});
