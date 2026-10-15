const test = require("node:test");
const assert = require("node:assert/strict");
const { once } = require("node:events");
const { request } = require("node:http");
const { createRequire } = require("node:module");
const qs = require("qs");
const express = require("express");
const bodyParser = require("body-parser");

// The same contracts run unchanged against the old and generated patched graphs.
// Small public synthetic inputs only; no application tools or project data.
for (const [name, input] of [
  ["indexed", "tags[0]=red&tags[1]=blue"],
  ["brackets", "tags[]=red&tags[]=blue"],
]) {
  test(`ordinary array: ${name}`, () => {
    assert.deepEqual(qs.parse(input), { tags: ["red", "blue"] });
  });
}

test("ordinary repeated keys remain arrays", () => {
  assert.deepEqual(qs.parse("tag=red&tag=blue"), { tag: ["red", "blue"] });
});

test("ordinary nested values retain their structure", () => {
  assert.deepEqual(qs.parse("filter[city]=Tripoli&filter[flags][active]=true"), {
    filter: { city: "Tripoli", flags: { active: "true" } },
  });
});

const limits = { comma: true, arrayLimit: 3, throwOnLimitExceeded: true };
for (const [name, input, expected] of [
  ["flat", "a=1,2,3", ["1", "2", "3"]],
  ["bracket", "a[]=1,2,3", [["1", "2", "3"]]],
]) {
  test(`comma group at configured limit: ${name}`, () => {
    assert.deepEqual(qs.parse(input, limits), { a: expected });
  });
}

test("flat comma group over configured limit is rejected", () => {
  assert.throws(() => qs.parse("a=1,2,3,4", limits), RangeError);
});

test("GHSA-x5fp-wj9c-mxmx: bracket comma group cannot bypass strict limit", () => {
  assert.throws(() => qs.parse("a[]=1,2,3,4", limits), RangeError);
});

for (const option of ["plainObjects", "allowPrototypes"]) {
  test(`GHSA-4mjr-xmp4-gh2g: parse/stringify preserves data with ${option}`, () => {
    const encoded = "x%5Bconstructor%5D%5BisBuffer%5D=y";
    const parsed = qs.parse(encoded, { [option]: true });
    assert.equal(parsed.x.constructor.isBuffer, "y");
    assert.equal(Object.hasOwn(parsed.x, "constructor"), true);
    const serialized = qs.stringify(parsed);
    assert.equal(serialized, encoded);
    assert.equal(qs.parse(serialized, { [option]: true }).x.constructor.isBuffer, "y");
    assert.equal(Object.hasOwn(Object.prototype, "isBuffer"), false);
  });
}

test("ordinary parse/stringify handles arrays, nested booleans and empty values", () => {
  const encoded = qs.stringify({ ids: [1, 2], filter: { active: true }, empty: null });
  assert.equal(encoded, "ids%5B0%5D=1&ids%5B1%5D=2&filter%5Bactive%5D=true&empty=");
  assert.deepEqual(qs.parse(encoded), {
    ids: ["1", "2"],
    filter: { active: "true" },
    empty: "",
  });
});

test("ordinary Buffer values still serialize", () => {
  assert.equal(qs.stringify({ blob: Buffer.from("ok") }), "blob=ok");
});

test("locked Express and body-parser resolve the actual tested qs copy", () => {
  const fromExpress = createRequire(require.resolve("express"));
  const fromBodyParser = createRequire(fromExpress.resolve("body-parser"));
  assert.equal(require("express/package.json").version, "5.2.1");
  assert.equal(fromExpress("body-parser/package.json").version, "2.3.0");
  assert.equal(fromExpress("qs"), qs);
  assert.equal(fromBodyParser("qs"), qs);
});

async function withServer(app, run) {
  const server = app.listen(0, "127.0.0.1");
  await once(server, "listening");
  try {
    await run(server);
  } finally {
    await new Promise((resolve, reject) => server.close((error) => (error ? reject(error) : resolve())));
  }
}

function localRequest(server, method, path, body = "") {
  return new Promise((resolve, reject) => {
    const req = request(
      {
        hostname: "127.0.0.1",
        port: server.address().port,
        method,
        path,
        agent: false,
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
          "Content-Length": Buffer.byteLength(body),
        },
      },
      (res) => {
        let data = "";
        res.setEncoding("utf8");
        res.on("data", (chunk) => (data += chunk));
        res.on("error", reject);
        res.on("end", () => resolve({ status: res.statusCode, body: data }));
      },
    );
    req.on("error", reject);
    req.setTimeout(2000, () => req.destroy(new Error("Loopback fixture timeout")));
    req.end(body);
  });
}

test("locked Express extended query parser handles arrays and nested values", async () => {
  const app = express();
  app.set("query parser", "extended");
  app.get("/query", (req, res) => res.json(req.query));
  await withServer(app, async (server) => {
    const response = await localRequest(server, "GET", "/query?ids[]=1&ids[]=2&filter[city]=Tripoli");
    assert.equal(response.status, 200);
    assert.deepEqual(JSON.parse(response.body), {
      ids: ["1", "2"],
      filter: { city: "Tripoli" },
    });
  });
});

test("locked body-parser extended form parser preserves nested arrays", async () => {
  const app = express();
  app.post("/form", bodyParser.urlencoded({ extended: true, parameterLimit: 20, depth: 5 }), (req, res) =>
    res.json(req.body),
  );
  await withServer(app, async (server) => {
    const response = await localRequest(server, "POST", "/form", "ids[]=1&ids[]=2&filter[city]=Tripoli");
    assert.equal(response.status, 200);
    assert.deepEqual(JSON.parse(response.body), {
      ids: ["1", "2"],
      filter: { city: "Tripoli" },
    });
  });
});
