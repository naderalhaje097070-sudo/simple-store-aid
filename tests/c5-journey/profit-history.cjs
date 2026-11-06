// Peel only the exact owner-adopted C5 profit-contract delta off the current
// source so earlier C2/C4/collection history bridges keep comparing their own
// reviewed bytes. Any byte not recorded in profit-source.json is rejected.
const fs = require("node:fs");
const cp = require("node:child_process");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");

const BASE = "f2967cfbc0cf46fb09a5f4fc0c454f38f3f51a66";
const MANIFEST = "tests/c5-journey/profit-source.json";
const FILES = new Set(["src/lib/db.ts", "src/routes/_authenticated/app.tsx"]);

function blob(text) {
  const bytes = Buffer.from(text);
  return crypto
    .createHash("sha1")
    .update("blob " + bytes.length + "\0")
    .update(bytes)
    .digest("hex");
}

function historicalProfitSource(file, actual) {
  assert.equal(arguments.length, 2, "Profit history accepts no caller-selected ref or override");
  if (!FILES.has(file)) return actual;
  const raw = fs.readFileSync(MANIFEST, "utf8");
  assert.equal(raw, cp.execFileSync("git", ["show", "HEAD:" + MANIFEST], { encoding: "utf8" }));
  const m = JSON.parse(raw);
  assert.equal(m.scope, "C5-PROFIT-CONTRACT-IMPLEMENT-01");
  assert.equal(m.repository, "naderalhaje097070-sudo/simple-store-aid");
  assert.equal(m.base_source, BASE);
  const prior = cp.execFileSync("git", ["show", `${BASE}:${file}`], { encoding: "utf8" });
  assert.equal(m.changes[file].before, blob(prior), "Unreviewed profit provenance");
  assert.equal(blob(actual), m.changes[file].after, "Unreviewed profit module mutation");
  return prior;
}

module.exports = { historicalProfitSource, PROFIT_BASE: BASE, PROFIT_FILES: FILES };
