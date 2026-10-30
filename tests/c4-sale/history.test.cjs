const test = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const cp = require("node:child_process");
const { historicalC4Source, BASE, FILES } = require("./history.cjs");
for (const file of FILES)
  test("C4 history rejects actual source mutation: " + file, () => {
    const actual = fs.readFileSync(file, "utf8");
    assert.equal(
      historicalC4Source(file, actual),
      cp.execFileSync("git", ["show", `${BASE}:${file}`], { encoding: "utf8" }),
    );
    assert.throws(() => historicalC4Source(file, actual + "\n// altered"), /Unreviewed/);
    assert.throws(() => historicalC4Source(file, actual, BASE), /no caller-selected/);
  });
