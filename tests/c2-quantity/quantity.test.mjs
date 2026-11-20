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
const courier = { delivery: "courier", total: 100, items: [] };
for (const [courierState, paid, collectedByCourier, expected] of [
  ["delivered_none", 40, 0, 60],
  ["delivered_none", 100, 0, 0],
  ["delivered_partial", 40, 35, 25],
  ["delivered_partial", 40, 60, 0],
  ["delivered_partial", 40, 70, 0],
  ["delivered_partial", 0, 60, 40],
  ["pending", 0, 0, 0],
  ["returned", 0, 0, 0],
]) {
  const invoice = { ...courier, courierState, paid, collectedByCourier };
  assert.equal(finance.getCustomerDebtForInvoice(invoice), expected);
}
assert.equal(
  finance.canCollectCustomerDebtForInvoice({ ...courier, courierState: "delivered_none", paid: 100 }),
  false,
);
assert.equal(
  finance.getCustomerDebtForInvoice({
    ...courier, total: 0.8, courierState: "delivered_partial", paid: 0.7, collectedByCourier: 0.1,
  }),
  0,
);
assert.equal(finance.getCustomerDebtForInvoice({ ...courier, delivery: "direct", paid: 100 }), 0);
console.log(
  JSON.stringify({
    quantity_cases: observations.length + 7,
    existing_cent_policy_cases: 5,
    customer_debt_cases: 11,
    passed: true,
  }),
);
