const assert = require("node:assert/strict");
const cp = require("node:child_process");

const BEFORE = "5601d634390711393d3c64a103876e5adef5ab5e";
const AFTER = "3726567d06d2ca21c5fb0d724571bf126c74be7c";
const FILES = new Set(["src/lib/db.ts", "src/routes/_authenticated/app.tsx"]);
function historicalQuantitySource(file, actual) {
  assert.equal(arguments.length, 2, "Quantity bridge accepts no caller-selected ref or override");
  if (!FILES.has(file)) return actual;
  const read = (ref) => cp.execFileSync("git", ["show", `${ref}:${file}`], { encoding: "utf8" });
  // C2 deliberately changed quantity validation and the two cart components.
  // Pin every current byte before comparing the previous AST under today's
  // compiler. The runtime gate separately executes the current sale callback;
  // stored quantity and cart acceptance remain in the source-bound C2 packet.
  assert.equal(actual, read(AFTER), "Unreviewed current module mutation from tested C2");
  return read(BEFORE);
}
module.exports = { historicalQuantitySource, BEFORE, AFTER, FILES };
