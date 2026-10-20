// Diagnostic wrapper delegates unchanged. It never reads request/response contents.
const dns = require("node:dns");
const fs = require("node:fs");
const crypto = require("node:crypto");
const safeNames = new Set([
  "localhost",
  "registry.npmjs.org",
  "api.cloudflare.com",
  "cloudflare.com",
  "www.cloudflare.com",
  "dash.cloudflare.com",
  "developers.cloudflare.com",
]);
function note(host) {
  if (typeof host !== "string") return;
  const callers = [
    ...new Error().stack.matchAll(
      /(?:\/tmp\/g01-tools\/node_modules\/)([A-Za-z0-9_@./-]+):(\d+):(\d+)/g,
    ),
  ]
    .slice(0, 6)
    .map((m) => ({
      file: [
        "wrangler/wrangler-dist/cli.js",
        "wrangler/dist/cli.js",
        "miniflare/dist/src/index.js",
        "undici/lib/core/connect.js",
      ].includes(m[1])
        ? m[1]
        : "other_file",
      file_sha256: crypto.createHash("sha256").update(m[1]).digest("hex"),
      line: Number(m[2]),
      column: Number(m[3]),
    }));
  const value = {
    type: "node_dns_lookup",
    pid: process.pid,
    timestamp_ms: Date.now(),
    hostname: safeNames.has(host) ? host : "hashed_hostname",
    hostname_sha256: crypto.createHash("sha256").update(host).digest("hex"),
    callers,
  };
  fs.appendFileSync(process.env.G1_NODE_DNS_LOG, JSON.stringify(value) + "\n", { mode: 0o600 });
}
for (const target of [dns, dns.promises]) {
  const original = target.lookup;
  target.lookup = function (...args) {
    note(args[0]);
    return Reflect.apply(original, this, args);
  };
}
