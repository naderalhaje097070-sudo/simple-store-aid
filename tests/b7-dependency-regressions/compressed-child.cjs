// Child process has no uncaught-error hook: a decompressor crash must kill it.
const assert = require("node:assert/strict");
const http = require("node:http");
const zlib = require("node:zlib");
const crypto = require("node:crypto");
const bodyParser = require(process.argv[2]);
const result = {
  delayedDeflate: false,
  gzip: false,
  charset: false,
  healthy: false,
  rawConsumer: false,
};
const hardTimeout = setTimeout(() => {
  console.error("bounded child timeout");
  process.exit(2);
}, 6000);
async function scenario(mode) {
  let client;
  const parser = bodyParser.json(mode === "charset" ? { verify() {} } : {});
  const trailing = Buffer.alloc(mode === "delayed" ? 1024 : 100 * 1024, 0x58);
  const first = Buffer.concat([
    mode === "delayed" ? zlib.deflateSync('{"a":1}') : zlib.gzipSync('{"a":1}'),
    Buffer.from([0]),
  ]);
  const expectedHash = crypto.createHash("sha256").update(first).update(trailing).digest("hex");
  const server = http.createServer((req, res) => {
    if (req.url === "/health") {
      res.end("healthy");
      return;
    }
    const hash = crypto.createHash("sha256");
    req.pipe(hash);
    parser(req, res, (error) => {
      if (error) {
        res.statusCode = error.status || 500;
        res.end(error.type);
        return;
      }
      if (mode === "delayed") {
        hash.once("finish", () => {
          res.setHeader("x-raw-hash", hash.read().toString("hex"));
          res.end(JSON.stringify(req.body));
        });
        client.end(trailing);
      } else {
        res.end(JSON.stringify(req.body));
      }
    });
  });
  await new Promise((resolve) => server.listen(0, "127.0.0.1", resolve));
  const port = server.address().port;
  try {
    const response = await new Promise((resolve, reject) => {
      client = http.request(
        {
          host: "127.0.0.1",
          port,
          method: "POST",
          path: "/",
          agent: false,
          headers: {
            "content-type":
              mode === "charset" ? "application/json; charset=utf-999" : "application/json",
            "content-encoding": mode === "delayed" ? "deflate" : "gzip",
            "content-length": first.length + trailing.length,
          },
        },
        (res) => {
          let text = "";
          res.setEncoding("utf8");
          res.on("data", (chunk) => {
            text += chunk;
          });
          res.on("end", () => resolve({ status: res.statusCode, headers: res.headers, text }));
        },
      );
      client.on("error", reject);
      client.setTimeout(2000, () => client.destroy(new Error("request stalled")));
      if (mode === "delayed") client.write(first);
      else client.end(Buffer.concat([first, trailing]));
    });
    assert.equal(response.status, mode === "charset" ? 415 : 200);
    if (mode !== "charset") assert.equal(response.text, '{"a":1}');
    if (mode === "delayed") {
      assert.equal(response.headers["x-raw-hash"], expectedHash);
      result.rawConsumer = true;
    }
    // Give any late unhandled decoder error time to reach the native event loop.
    await new Promise((resolve) => setTimeout(resolve, 100));
    const health = await new Promise((resolve, reject) => {
      http
        .get({ host: "127.0.0.1", port, path: "/health", agent: false }, (res) => {
          let text = "";
          res.on("data", (chunk) => {
            text += chunk;
          });
          res.on("end", () => resolve(text));
        })
        .on("error", reject);
    });
    assert.equal(health, "healthy");
    result.healthy = true;
    result[mode === "delayed" ? "delayedDeflate" : mode] = true;
  } finally {
    server.closeAllConnections();
    await new Promise((resolve) => server.close(resolve));
  }
}
(async () => {
  for (const mode of ["delayed", "gzip", "charset"]) await scenario(mode);
  clearTimeout(hardTimeout);
  console.log(JSON.stringify(result));
})().catch((error) => {
  console.error(error);
  process.exit(1);
});
