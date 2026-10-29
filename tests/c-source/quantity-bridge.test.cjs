const test = require("node:test");
const assert = require("node:assert/strict");
const cp = require("node:child_process");
const fs = require("node:fs");
const { historicalQuantitySource, BEFORE, AFTER, FILES } = require("./quantity-bridge.cjs");
const read = (ref, file) =>
  cp.execFileSync("git", ["show", `${ref}:${file}`], { encoding: "utf8" });

for (const file of FILES) {
  test(`fixed C2 bridge admits only the tested current bytes: ${file}`, () => {
    const current = fs.readFileSync(file, "utf8");
    assert.equal(current, read(AFTER, file));
    assert.equal(historicalQuantitySource(file, current), read(BEFORE, file));
    assert.throws(() => historicalQuantitySource(file, current + "\n// mutation"), /Unreviewed/);
    assert.throws(() => historicalQuantitySource(file, current, BEFORE), /no caller-selected/);
    const needle = file.endsWith("db.ts") ? "p_paid: input.paid" : "const quantitiesValid =";
    assert.equal(current.split(needle).length - 1, file.endsWith("db.ts") ? 1 : 2);
    assert.throws(
      () =>
        historicalQuantitySource(
          file,
          current.replace(needle, needle + (file.endsWith("db.ts") ? " + 1" : " false &&")),
        ),
      /Unreviewed/,
    );
    assert.throws(() => historicalQuantitySource(file, read(BEFORE, file)), /Unreviewed/);
  });
}
test("unrelated modules retain their actual source", () => {
  assert.equal(historicalQuantitySource("other.ts", "actual"), "actual");
});
