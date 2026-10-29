// Actual adapter with a configured first-decode router; synthetic files and loopback.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const http = require("node:http");
const { once } = require("node:events");
const { createRequire } = require("node:module");
const { spawnSync } = require("node:child_process");
const r = createRequire(
  path.resolve(process.env.DEPENDENCY_TEST_ROOT || process.cwd(), "package.json"),
);
const { Hono } = r("hono");
const dir = process.env.ADAPTER_FIXTURE_DIR;
const fixture = (name) =>
  path.join(
    dir,
    "dist",
    name + (fs.existsSync(path.join(dir, "dist", name + ".cjs")) ? ".cjs" : ".js"),
  );
const adapter = dir ? require(fixture("index")) : r("@hono/node-server");
const { serveStatic } = dir
  ? require(fixture("serve-static"))
  : r("@hono/node-server/serve-static");
const baseline = process.argv.includes("--baseline");
const checks = [];
const check = (name, pass) => {
  assert.ok(pass, name);
  checks.push({ name, passed: true });
};
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), "monjez-decoding-"));
fs.mkdirSync(path.join(tmp, "admin"));
for (const name of ["secret.txt", "secret%.txt"])
  fs.writeFileSync(path.join(tmp, "admin", name), "synthetic-protected-marker");
fs.writeFileSync(path.join(tmp, "public.txt"), "synthetic-public-marker");
// Current default Hono has further decoder defenses; this is component proof.
const app = new Hono({
  getPath(request) {
    const p = new URL(request.url).pathname;
    try {
      return decodeURI(p);
    } catch {
      return p;
    }
  },
});
let guards = 0;
app.use("/admin/*", async (c, next) => {
  guards++;
  if (c.req.header("authorization") !== "Bearer local-fixture") return c.text("denied", 401);
  await next();
});
app.use("*", serveStatic({ root: tmp }));
const server = adapter.createAdaptorServer({ fetch: app.fetch, hostname: "127.0.0.1" });
const request = (p, headers = {}) =>
  new Promise((resolve, reject) => {
    const req = http.request(
      { hostname: "127.0.0.1", port: server.address().port, path: p, headers, agent: false },
      (res) => {
        let body = "";
        res.on("data", (d) => (body += d));
        res.on("end", () => resolve({ status: res.statusCode, body }));
      },
    );
    req.setTimeout(3000, () => req.destroy(Error("local timeout")));
    req.on("error", reject);
    req.end();
  });
(async () => {
  try {
    server.listen(0, "127.0.0.1");
    await once(server, "listening");
    check(
      "ordinary public file remains readable",
      (await request("/public.txt")).body === "synthetic-public-marker",
    );
    check(
      "ordinary protected prefix refuses anonymous",
      (await request("/admin/secret.txt")).status === 401,
    );
    check(
      "ordinary protected prefix allows authorized",
      (await request("/admin/secret.txt", { authorization: "Bearer local-fixture" })).body ===
        "synthetic-protected-marker",
    );
    const before = guards;
    const response = await request("/%61dmin/secret%.txt");
    const leaked = response.body.includes("synthetic-protected-marker");
    check(
      "configured-router decode boundary matches expected mode",
      baseline ? leaked && guards === before : !leaked,
    );
    const child = spawnSync(
      process.execPath,
      [
        "--max-old-space-size=64",
        path.join(__dirname, "serde-child.cjs"),
        ...(baseline ? ["--baseline"] : []),
      ],
      { env: process.env, encoding: "utf8", timeout: 5000, maxBuffer: 128 * 1024 },
    );
    assert.equal(child.status, 0, child.stderr);
    assert.equal(child.error, undefined);
    console.log(
      JSON.stringify({
        mode: baseline ? "expected-red-old-package" : "patched",
        checks,
        observations: {
          status: response.status,
          protectedMarkerVisible: leaked,
          guardCalls: guards - before,
        },
        serde: JSON.parse(child.stdout),
        router: "explicit first-decode fixture; not application default",
        arbitrary_application_exploit_claim: false,
      }),
    );
  } finally {
    server.closeAllConnections();
    if (server.listening) await new Promise((resolve) => server.close(resolve));
    fs.rmSync(tmp, { recursive: true, force: true });
  }
})().catch((e) => {
  console.error(e);
  process.exitCode = 1;
});
