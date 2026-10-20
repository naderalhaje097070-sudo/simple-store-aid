const fs = require("node:fs");
const vm = require("node:vm");
const assert = require("node:assert/strict");
const root = "/workspace/scratch/a14f76980432";
let source = fs.readFileSync(
  root + "/node-server-candidate/tests/unit/dependency-security.test.ts",
  "utf8",
);
source = source
  .replace('import { describe, expect, test } from "bun:test";', "")
  .replace('import { readFileSync } from "node:fs";', "")
  .replace('new URL("../../bun.lock", import.meta.url)', '"/virtual/bun.lock"')
  .replace("minimum!", "minimum");
const original = fs.readFileSync(root + "/ns-preparation/bun.lock", "utf8");
const cases = {
  patched: original,
  newerStable1x: original.replaceAll("@hono/node-server@1.19.15", "@hono/node-server@1.19.17"),
  nestedSafe: original.replace(
    '"packages": {',
    '"packages": {\n "fixture/node-server": ["@hono/node-server@1.19.15", "", {}],',
  ),
  old: original.replaceAll("@hono/node-server@1.19.15", "@hono/node-server@1.19.14"),
  prerelease: original.replaceAll("@hono/node-server@1.19.15", "@hono/node-server@1.19.15-rc.1"),
  major2: original.replaceAll("@hono/node-server@1.19.15", "@hono/node-server@2.0.5"),
  nestedOld: original.replace(
    '"packages": {',
    '"packages": {\n "fixture/node-server": ["@hono/node-server@1.19.14", "", {}],',
  ),
  missing: original.replaceAll("@hono/node-server@1.19.15", "fixture@1.19.15"),
  honoOld: original.replaceAll("hono@4.13.7", "hono@4.13.6"),
  qsOld: original.replaceAll("qs@6.16.0", "qs@6.15.3"),
  dompurifyOld: original.replaceAll("dompurify@3.4.16", "dompurify@3.4.15"),
  babelOld: original.replaceAll("@babel/core@7.29.7", "@babel/core@7.29.0"),
};
const rows = [];
for (const [name, lock] of Object.entries(cases)) {
  const passed = [],
    failed = [];
  const context = {
    readFileSync: () => lock,
    describe: (_, fn) => fn(),
    test: (title, fn) => {
      try {
        fn();
        passed.push(title);
      } catch (error) {
        failed.push({ title, error: error.message });
      }
    },
    expect: (actual) => ({
      toBeGreaterThan: (minimum) => assert(actual > minimum),
      toMatch: (pattern) => assert.match(actual, pattern),
      toEqual: (expected) =>
        assert.deepEqual(JSON.parse(JSON.stringify(actual)), JSON.parse(JSON.stringify(expected))),
    }),
  };
  vm.runInNewContext(source, context, {
    filename: "dependency-security.test.ts [Node assertion adapter]",
  });
  const expectedPass = ["patched", "newerStable1x", "nestedSafe"].includes(name);
  assert.equal(failed.length === 0, expectedPass, JSON.stringify({ name, failed }));
  if (!expectedPass) assert.equal(failed.length, 1, JSON.stringify({ name, failed }));
  rows.push({ case: name, passed: passed.length, failed });
}
fs.writeFileSync(
  root + "/ns-review-guard-replay.json",
  JSON.stringify(
    {
      method:
        "Existing test source in Node VM; imports, lock read and TS non-null syntax adapted; actual Bun and installed adapter NOT executed",
      cases: rows,
    },
    null,
    2,
  ) + "\n",
);
console.log(
  JSON.stringify(
    rows.map((r) => ({ case: r.case, pass: r.passed, fail: r.failed.length })),
    null,
    2,
  ),
);
