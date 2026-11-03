const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const cp = require("node:child_process");
const { historicalCollectionSource, COLLECTION_BASE, COLLECTION_FILES } = require("./history.cjs");
for (const file of COLLECTION_FILES)
  test("collection delta pins current and historical bytes: " + file, () => {
    const actual = fs.readFileSync(file, "utf8");
    assert.equal(
      historicalCollectionSource(file, actual),
      cp.execFileSync("git", ["show", `${COLLECTION_BASE}:${file}`], { encoding: "utf8" }),
    );
    assert.throws(() => historicalCollectionSource(file, actual + "\n// drift"), /Unreviewed/);
    assert.throws(
      () => historicalCollectionSource(file, actual, COLLECTION_BASE),
      /no caller-selected/,
    );
  });
test("unrelated module has no historical substitution", () =>
  assert.equal(historicalCollectionSource("other.ts", "actual"), "actual"));
