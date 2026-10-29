// Safe synthetic serializer boundaries. No injected code or unbounded loop executes.
const assert = require("node:assert/strict");
const path = require("node:path");
const { createRequire } = require("node:module");
const r = createRequire(
  path.resolve(process.env.DEPENDENCY_TEST_ROOT || process.cwd(), "package.json"),
);
const s = process.env.SEROVAL_FIXTURE_FILE
  ? require(process.env.SEROVAL_FIXTURE_FILE)
  : r("seroval");
const baseline = process.argv.includes("--baseline");
const checks = [];
const check = (name, pass) => {
  assert.ok(pass, name);
  checks.push({ name, passed: true });
};
const cycle = { marker: "local" };
cycle.self = cycle;
const value = {
  cycle,
  date: new Date("2026-01-01T00:00:00Z"),
  map: new Map([["a", 1]]),
  set: new Set([1, 2]),
  big: 123n,
  bytes: new Uint8Array([1, 2, 3]),
  regexp: /(?<group>a)(?<=a)/g,
};
const out = s.fromJSON(s.toJSON(value));
check(
  "ordinary cyclic/date/map/set/bigint/typed/regexp roundtrip",
  out.cycle.self === out.cycle &&
    out.date.toISOString() === value.date.toISOString() &&
    out.map.get("a") === 1 &&
    out.set.size === 2 &&
    out.big === 123n &&
    out.bytes.join() === "1,2,3" &&
    out.regexp.source === value.regexp.source,
);
const bytes = new Uint8Array([1, 2]);
Object.defineProperty(bytes, "constructor", { value: { name: "UNTRUSTED_CONSTRUCTOR" } });
const constructorWritten = s.serialize(bytes).includes("UNTRUSTED_CONSTRUCTOR");
check(
  "typed array own-constructor boundary matches expected mode",
  constructorWritten === baseline,
);
const rawLessThan = s.serialize(new RegExp("<script", "g")).includes("<script");
check("RegExp raw less-than boundary matches expected mode", rawLessThan === baseline);
const rejectedNodes = {};
for (const [name, node] of [
  ["array-list", { t: 9, i: 0, a: { length: 0 } }],
  ["sequence-index", { t: 35, i: 0, a: [], s: -1, l: 99 }],
]) {
  let rejected = false;
  try {
    s.fromJSON({ t: node, m: [], f: 127 });
  } catch (e) {
    assert.ok(
      e instanceof s.SerovalDeserializationError || e instanceof s.SerovalMalformedNodeError,
    );
    rejected = true;
  }
  rejectedNodes[name] = rejected;
  check(name + " rejection matches expected mode", rejected === !baseline);
}
let calls = 0;
const plugin = {
  tag: "local-fixture",
  deserialize: () => ({
    on() {
      calls++;
    },
  }),
};
const node = {
  t: 30,
  a: [
    { t: 31, i: 7, a: [] },
    { t: 25, i: 7, c: "local-fixture", s: null },
  ],
};
let rejected = false;
try {
  const factory = s.fromJSON({ t: node, m: [], f: 127 }, { plugins: [plugin] });
  if (typeof factory === "function") factory();
} catch (e) {
  assert.ok(e instanceof s.SerovalDeserializationError || e instanceof s.SerovalMalformedNodeError);
  rejected = true;
}
check(
  "reused stream id boundary matches expected mode",
  baseline ? calls === 1 && !rejected : calls === 0 && rejected,
);
console.log(
  JSON.stringify({
    mode: baseline ? "expected-red-old-package" : "patched",
    checks,
    observations: {
      constructorWritten,
      rawLessThan,
      rejectedNodes,
      pluginOnCalls: calls,
      pluginSourceRejected: rejected,
    },
    arbitrary_output_evaluated: false,
    unbounded_loop_executed: false,
  }),
);
