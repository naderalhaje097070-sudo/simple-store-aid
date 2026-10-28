import assert from "node:assert/strict";
import fs from "node:fs";
import { stripTypeScriptTypes } from "node:module";
const code = stripTypeScriptTypes(fs.readFileSync("src/domain/finance/quantity.ts", "utf8"));
const q = await import("data:text/javascript;base64," + Buffer.from(code).toString("base64"));
const observations = [];
for (const [text, expected] of [
  ["0.25", 0.25],
  ["1.50", 1.5],
  [".01", 0.01],
  ["0", 0],
  ["0.001", null],
  ["1.999", null],
  ["NaN", null],
  ["Infinity", null],
  ["-1", null],
  ["", null],
  ["1e2", null],
]) {
  assert.equal(q.parseQuantityText(text), expected);
  observations.push(text);
}
assert.equal(q.stepQuantity(0.25, 1), 1.25);
assert.equal(q.stepQuantity(0.25, -1), 0);
assert.equal(q.stepQuantity(0.29, 1), 1.29);
assert.equal(q.isQuantity(0), false);
assert.equal(q.isQuantity(0, true), true);
assert.equal(q.isQuantity(0.001), false);
assert.equal(q.sumQuantities([0.1, 0.2, 0.29]), 0.59);
console.log(JSON.stringify({ quantity_cases: observations.length + 7, passed: true }));
