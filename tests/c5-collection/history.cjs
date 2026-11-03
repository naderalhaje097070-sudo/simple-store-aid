// Preserve historical C2/C4 AST comparisons while admitting only the exact
// owner-authorized collection delta. Current callbacks/native/browser tests
// execute the current source separately; this function is never an app loader.
const fs = require("node:fs");
const cp = require("node:child_process");
const crypto = require("node:crypto");
const assert = require("node:assert/strict");
const c4 = require("../c4-sale/history.cjs");
const BASE = "570ec47e4fe78ab25dc7e653a0a84cdc9a5d8644";
const MANIFEST = "tests/c5-collection/source.json";
const FILES = new Set([
  "src/lib/db.ts",
  "src/routes/_authenticated/app.tsx",
  "src/features/invoices/InvoiceDetailScreen.tsx",
]);
function blob(text) {
  const bytes = Buffer.from(text);
  return crypto
    .createHash("sha1")
    .update("blob " + bytes.length + "\0")
    .update(bytes)
    .digest("hex");
}
function historicalCollectionSource(file, actual) {
  assert.equal(
    arguments.length,
    2,
    "Collection history accepts no caller-selected ref or override",
  );
  if (!FILES.has(file)) return actual;
  const raw = fs.readFileSync(MANIFEST, "utf8");
  assert.equal(raw, cp.execFileSync("git", ["show", "HEAD:" + MANIFEST], { encoding: "utf8" }));
  const m = JSON.parse(raw);
  assert.equal(m.scope, "C5-COLLECTION-RETRY-01");
  assert.equal(m.repository, "naderalhaje097070-sudo/simple-store-aid");
  assert.equal(m.base_source, BASE);
  const prior = cp.execFileSync("git", ["show", `${BASE}:${file}`], { encoding: "utf8" });
  assert.equal(m.changes[file].before, blob(prior), "Unreviewed collection provenance");
  assert.equal(blob(actual), m.changes[file].after, "Unreviewed collection module mutation");
  return prior;
}
function historicalC4Source(file, actual) {
  assert.equal(arguments.length, 2, "Collection bridge accepts no caller-selected ref or override");
  return c4.historicalC4Source(file, historicalCollectionSource(file, actual));
}
module.exports = {
  historicalCollectionSource,
  historicalC4Source,
  BASE: c4.BASE,
  FILES: c4.FILES,
  COLLECTION_BASE: BASE,
  COLLECTION_FILES: FILES,
};
