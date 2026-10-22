const fs = require("node:fs");
const assert = require("node:assert/strict");
const cp = require("node:child_process");
const { test } = require("node:test");
const { historicalWebhookSource, WEBHOOK, ACCEPTED_A } = require("./webhook-bridge.cjs");

test("bridge keeps the accepted A comparison and independently pins current B4 bytes", () => {
  const actual = fs.readFileSync(WEBHOOK, "utf8");
  assert.equal(
    historicalWebhookSource(WEBHOOK, actual),
    cp.execFileSync("git", ["show", `${ACCEPTED_A}:${WEBHOOK}`], { encoding: "utf8" }),
  );
});
test("changed current B4 handler cannot be hidden by the historical A comparison", () => {
  assert.throws(
    () => historicalWebhookSource(WEBHOOK, fs.readFileSync(WEBHOOK, "utf8") + "\n// unreviewed\n"),
    /Unreviewed current webhook mutation/,
  );
});
test("every other path retains current source without a replacement", () => {
  assert.equal(historicalWebhookSource("src/unreviewed.ts", "current-source"), "current-source");
});
test("caller-selected references and overrides are rejected", () => {
  assert.throws(
    () => historicalWebhookSource(WEBHOOK, "anything", "HEAD"),
    /no caller-selected ref/,
  );
});
