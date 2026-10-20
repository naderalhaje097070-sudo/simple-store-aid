// Real installed adapter, native filesystem and loopback only; no application data.
const assert = require("node:assert/strict");
const { test, after } = require("node:test");
const fs = require("node:fs");
const path = require("node:path");
const os = require("node:os");
const http = require("node:http");
const { once } = require("node:events");
const { createRequire } = require("node:module");
const { Hono } = require("hono");

const out = path.resolve("evidence/g0-node-server");
fs.mkdirSync(out, { recursive: true });
const observations = [];
const rootRequire = createRequire(path.resolve("package.json"));
const sdkRequire = createRequire(
  path.resolve("node_modules/@modelcontextprotocol/sdk/package.json"),
);
const adapterPath = sdkRequire.resolve("@hono/node-server");
const adapter = sdkRequire("@hono/node-server");
const { serveStatic } = sdkRequire("@hono/node-server/serve-static");
const manifestPath = path.join(path.dirname(adapterPath), "../package.json");
const manifest = JSON.parse(fs.readFileSync(manifestPath, "utf8"));
if (process.env.REQUIRE_NATIVE_WINDOWS === "1") assert.equal(process.platform, "win32");
const temp = fs.mkdtempSync(path.join(os.tmpdir(), "g0-node-server-"));
const staticRoot = path.join(temp, "static");
fs.mkdirSync(path.join(staticRoot, "admin"), { recursive: true });
fs.writeFileSync(path.join(staticRoot, "public.txt"), "public-marker");
fs.writeFileSync(path.join(staticRoot, "admin/secret.txt"), "protected-marker");
fs.writeFileSync(path.join(temp, "outside.txt"), "outside-marker");
const app = new Hono();
let protectedCalls = 0;
app.use("/admin/*", async (c, next) => {
  protectedCalls++;
  c.header("x-prefix-guard", "ran");
  if (c.req.header("authorization") !== "Bearer local-fixture") return c.text("denied", 401);
  await next();
});
app.post("/echo", async (c) =>
  c.json({ received: await c.req.json() }, 201, { "x-fixture": "echo" }),
);
app.get("/failure", () => {
  throw Error("dummy failure");
});
app.onError((_error, c) => c.text("local-error", 500));
app.use("*", serveStatic({ root: staticRoot }));
const server = adapter.createAdaptorServer({ fetch: app.fetch, hostname: "127.0.0.1" });
const ready = (async () => {
  server.listen(0, "127.0.0.1");
  await once(server, "listening");
})();

async function request(target, urlPath, options = {}) {
  if (!target.listening) throw Error("Fixture server not listening");
  return new Promise((resolve, reject) => {
    const req = http.request(
      {
        hostname: "127.0.0.1",
        port: target.address().port,
        path: urlPath,
        method: options.method || "GET",
        headers: options.headers || {},
        agent: false,
      },
      (res) => {
        const chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () =>
          resolve({
            status: res.statusCode,
            headers: res.headers,
            body: Buffer.concat(chunks).toString("utf8"),
          }),
        );
        res.on("error", reject);
      },
    );
    req.setTimeout(5000, () => req.destroy(Error("Loopback timeout")));
    req.on("error", reject);
    req.end(options.body);
  });
}

test("actual installed adapter resolves identically from SDK and root", () => {
  assert.equal(
    fs.realpathSync(adapterPath),
    fs.realpathSync(rootRequire.resolve("@hono/node-server")),
  );
  assert.equal(typeof adapter.getRequestListener, "function");
  assert.equal(typeof adapter.createAdaptorServer, "function");
  assert.equal(typeof adapter.serve, "function");
  observations.push({
    platform: process.platform,
    node: process.version,
    adapterPath,
    version: manifest.version,
    engines: manifest.engines,
  });
});
test("ordinary public and authorized protected files remain readable", async () => {
  await ready;
  const normal = await request(server, "/public.txt");
  assert.equal(normal.status, 200);
  assert.equal(normal.body, "public-marker");
  const denied = await request(server, "/admin/secret.txt");
  assert.equal(denied.status, 401);
  assert.equal(denied.headers["x-prefix-guard"], "ran");
  assert.equal(denied.body, "denied");
  const allowed = await request(server, "/admin/secret.txt", {
    headers: { authorization: "Bearer local-fixture" },
  });
  assert.equal(allowed.status, 200);
  assert.equal(allowed.body, "protected-marker");
  assert.equal(allowed.headers["x-prefix-guard"], "ran");
});
for (const encoded of ["%5C", "%5c"])
  test(`encoded-backslash-${encoded} must not bypass prefix authorization`, async () => {
    await ready;
    const before = protectedCalls;
    const response = await request(server, `/admin${encoded}secret.txt`);
    observations.push({
      case: encoded,
      platform: process.platform,
      version: manifest.version,
      ...response,
      middlewareCalls: protectedCalls - before,
    });
    assert.equal(
      protectedCalls,
      before,
      "Documented router condition: encoded separator skips prefix middleware",
    );
    assert.equal(response.status, 404);
    assert.equal(response.headers["x-prefix-guard"], undefined);
    assert.ok(!response.body.includes("protected-marker"));
  });
test("traversal repeated separators malformed encoding and missing file are rejected", async () => {
  await ready;
  for (const p of [
    "/admin%5C..%5C..%5Coutside.txt",
    "/admin%5C%5Csecret.txt",
    "/%2e%2e/outside.txt",
    "/missing.txt",
    "/%E0%A4%A",
  ]) {
    const response = await request(server, p);
    assert.equal(response.status, 404, p);
    assert.ok(
      !response.body.includes("protected-marker") && !response.body.includes("outside-marker"),
      p,
    );
  }
});
test("static HEAD and byte-range responses retain their body and header contracts", async () => {
  await ready;
  const head = await request(server, "/public.txt", { method: "HEAD" });
  assert.equal(head.status, 200);
  assert.equal(head.body, "");
  assert.equal(head.headers["content-length"], "13");
  const range = await request(server, "/public.txt", { headers: { range: "bytes=0-5" } });
  assert.equal(range.status, 206);
  assert.equal(range.body, "public");
  assert.equal(range.headers["content-range"], "bytes 0-5/13");
});
test("actual adapter preserves HTTP POST status headers JSON and handled errors", async () => {
  await ready;
  const echoed = await request(server, "/echo", {
    method: "POST",
    headers: { "content-type": "application/json" },
    body: JSON.stringify({ dummy: "local" }),
  });
  assert.equal(echoed.status, 201);
  assert.equal(echoed.headers["x-fixture"], "echo");
  assert.deepEqual(JSON.parse(echoed.body), { received: { dummy: "local" } });
  const error = await request(server, "/failure");
  assert.equal(error.status, 500);
  assert.equal(error.body, "local-error");
  const afterError = await request(server, "/public.txt");
  assert.equal(afterError.status, 200);
});
test("locked SDK Node transport uses real adapter for initialize list invoke and errors", async () => {
  const { McpServer } = sdkRequire("@modelcontextprotocol/sdk/server/mcp.js");
  const { StreamableHTTPServerTransport } = sdkRequire(
    "@modelcontextprotocol/sdk/server/streamableHttp.js",
  );
  const { z } = sdkRequire("zod");
  let calls = 0;
  const pairs = [];
  const unexpected = [];
  const sdkServer = http.createServer((req, res) => {
    // SDK1.31.0 stateless transports are single-request objects, as its example shows.
    const mcp = new McpServer({ name: "local-adapter-fixture", version: "1.0.0" });
    mcp.registerTool("echo", { inputSchema: { value: z.string() } }, async ({ value }) => {
      calls++;
      return { content: [{ type: "text", text: value }] };
    });
    const transport = new StreamableHTTPServerTransport({
      sessionIdGenerator: undefined,
      enableJsonResponse: true,
    });
    const pair = { close: () => (pair.closing ||= mcp.close()) };
    pairs.push(pair);
    res.once("close", () => {
      void pair.close().catch((error) => unexpected.push(error.message));
    });
    void (async () => {
      await mcp.connect(transport);
      await transport.handleRequest(req, res);
    })().catch((error) => {
      unexpected.push(error.message);
      if (!res.headersSent) res.writeHead(500);
      res.end();
    });
  });
  sdkServer.listen(0, "127.0.0.1");
  await once(sdkServer, "listening");
  const rpc = async (method, params) => {
    const response = await request(sdkServer, "/mcp", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
    });
    observations.push({ sdkMethod: method, ...response });
    return response;
  };
  try {
    const init = await rpc("initialize", {
      protocolVersion: "2025-03-26",
      capabilities: {},
      clientInfo: { name: "local", version: "1" },
    });
    assert.equal(init.status, 200);
    assert.equal(JSON.parse(init.body).result.serverInfo.name, "local-adapter-fixture");
    const listed = await rpc("tools/list", {});
    assert.equal(listed.status, 200);
    assert.equal(JSON.parse(listed.body).result.tools[0].name, "echo");
    const invoked = await rpc("tools/call", { name: "echo", arguments: { value: "dummy-marker" } });
    assert.deepEqual(JSON.parse(invoked.body).result.content, [
      { type: "text", text: "dummy-marker" },
    ]);
    const before = calls;
    const invalid = await rpc("tools/call", { name: "echo", arguments: { value: 42 } });
    const rejected = JSON.parse(invalid.body);
    assert.ok(rejected.error || rejected.result?.isError);
    assert.equal(calls, before);
    const malformed = await request(sdkServer, "/mcp", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        accept: "application/json, text/event-stream",
      },
      body: "{",
    });
    observations.push({ sdkMethod: "malformed-json", ...malformed });
    assert.equal(malformed.status, 400);
    assert.ok(JSON.parse(malformed.body).error);
  } finally {
    sdkServer.closeAllConnections();
    await new Promise((resolve) => sdkServer.close(resolve));
    await Promise.all(pairs.map((pair) => pair.close()));
    assert.deepEqual(unexpected, []);
  }
});
after(async () => {
  await ready;
  server.closeAllConnections();
  await new Promise((resolve) => server.close(resolve));
  fs.rmSync(temp, { recursive: true, force: true });
  fs.writeFileSync(path.join(out, "http-observations.json"), JSON.stringify(observations, null, 2));
});
