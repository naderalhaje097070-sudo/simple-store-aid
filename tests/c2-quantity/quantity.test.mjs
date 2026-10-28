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
const selectors = stripTypeScriptTypes(
  fs.readFileSync("src/domain/finance/invoice-selectors.ts", "utf8").replace(/^import[^\n]*\n/, ""),
);
const finance = await import(
  "data:text/javascript;base64," + Buffer.from(code + selectors).toString("base64")
);
assert.equal(finance.getSaleLineTotal({ price: 12.5, qty: 0.25 }), 3.13);
assert.equal(finance.getSaleLineTotal({ price: 0.25, qty: 0.1 }), 0.03);
assert.equal(
  finance.getSaleTotal([
    { price: 0.25, qty: 0.1 },
    { price: 0.25, qty: 0.1 },
  ]),
  0.06,
);
assert.equal(finance.getSaleLineTotal({ price: 0.29, qty: 1 }), 0.29);
assert.equal(finance.getSaleLineTotal({ price: 10.01, qty: 1.5 }), 15.02);
console.log(
  JSON.stringify({
    quantity_cases: observations.length + 7,
    existing_cent_policy_cases: 5,
    passed: true,
  }),
);
