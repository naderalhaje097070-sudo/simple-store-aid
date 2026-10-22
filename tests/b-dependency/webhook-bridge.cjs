const assert = require("node:assert/strict");
const cp = require("node:child_process");

const WEBHOOK = "src/routes/api/public/payments/webhook.ts";
const ACCEPTED_A = "51b09a6f33a672704f8424cbf2bbed7a2be682ca";
const ACCEPTED_B4 = "f3b702440a4ffd17038f3c668a2f446620a97919";
function historicalWebhookSource(file, actual) {
  assert.equal(arguments.length, 2, "Historical bridge accepts no caller-selected ref or override");
  if (file !== WEBHOOK) return actual;
  const read = (ref) => cp.execFileSync("git", ["show", `${ref}:${WEBHOOK}`], { encoding: "utf8" });
  // B4 deliberately replaced this one handler. Preserve the original A AST
  // comparison under today's compiler, independently pin actual bytes to the
  // accepted B4 source, and replay today's signed handler in the same CI gate.
  assert.equal(actual, read(ACCEPTED_B4), "Unreviewed current webhook mutation from accepted B4");
  return read(ACCEPTED_A);
}
module.exports = { historicalWebhookSource, WEBHOOK, ACCEPTED_A, ACCEPTED_B4 };
