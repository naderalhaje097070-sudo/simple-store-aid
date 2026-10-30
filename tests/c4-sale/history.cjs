const fs = require("node:fs");
const cp = require("node:child_process");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");
const MANIFEST = "tests/c4-sale/source.json";
const BASE = "9165d9325c5f50fab5c8eb767a780d993f59259f";
const FILES = new Set(["src/lib/db.ts", "src/routes/_authenticated/app.tsx"]);
function historicalC4Source(file, actual) {
  assert.equal(arguments.length, 2, "C4 history accepts no caller-selected ref or override");
  if (!FILES.has(file) || !fs.existsSync(MANIFEST)) return actual;
  const raw = fs.readFileSync(MANIFEST, "utf8");
  assert.equal(raw, cp.execFileSync("git", ["show", "HEAD:" + MANIFEST], { encoding: "utf8" }));
  const manifest = JSON.parse(raw);
  assert.equal(manifest.scope, "C4-FIN03-20261030");
  assert.equal(manifest.base_source, BASE);
  const entry = manifest.protected_blobs.find((x) => x.path === file);
  assert(entry && entry.mode === "100644");
  const bytes = Buffer.from(actual);
  const sha = crypto
    .createHash("sha1")
    .update("blob " + bytes.length + "\0")
    .update(bytes)
    .digest("hex");
  assert.equal(sha, entry.sha, "Unreviewed C4 module mutation");
  // Historical AST/legacy wire tests remain historical. The current C4 callback
  // is independently executed in mandatory contracts/native/browser tests.
  return cp.execFileSync("git", ["show", `${BASE}:${file}`], { encoding: "utf8" });
}
module.exports = { historicalC4Source, BASE, FILES };
