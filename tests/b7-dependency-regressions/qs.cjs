const assert = require("node:assert/strict");
const path = require("node:path");
const { createRequire } = require("node:module");
const load = createRequire(path.join(process.env.DEPENDENCY_TEST_ROOT || process.cwd(), "package.json"));
const sdk = createRequire(load.resolve("@modelcontextprotocol/sdk/package.json"));
const express = createRequire(sdk.resolve("express/package.json"));
const qs = express("qs");
const baseline = process.argv.includes("--baseline");
const inputs = [
  JSON.parse('{"a":[{"toString":"x"}]}'),
  qs.parse("a[0][toString]=x", { allowPrototypes: true }),
  qs.parse("a[0][toString]=x", { plainObjects: true }),
  { a: [[{ toString: "x" }]] },
];
let observed = 0;
for (const input of inputs) {
  const before = JSON.stringify(input);
  for (const encodeValuesOnly of [false, true]) {
    const stringify = () => qs.stringify(input, { arrayFormat: "comma", encodeValuesOnly });
    if (baseline) assert.throws(stringify, /Cannot convert object to primitive value/);
    else assert.match(decodeURIComponent(stringify()), /\[object Object\]/);
    observed++;
  }
  assert.equal(JSON.stringify(input), before);
}
assert.equal(qs.stringify({ a: ["x", "y"] }, { arrayFormat: "comma" }), "a=x%2Cy");
assert.equal(qs.stringify({ a: [{ toString: () => "z" }] }, { arrayFormat: "comma" }), "a=z");
assert.equal(Object.prototype.polluted, undefined);
console.log(JSON.stringify({ mode: baseline ? "exact-vulnerable-baseline" : "patched", ok: true, hostileCases: observed, normalComma: true, callableToString: true, inputsUnchanged: true }));
