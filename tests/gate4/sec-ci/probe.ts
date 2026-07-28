import { readFileSync } from "node:fs";

const financialPath = ".github/workflows/ephemeral-financial-rules.yml";
const authPath = ".github/workflows/isolated-auth-smoke.yml";

const financial = readFileSync(financialPath, "utf8");
const auth = readFileSync(authPath, "utf8");

function fail(message: string): never {
  console.error(`SEC_CI_G4_BASELINE_FAIL: ${message}`);
  process.exit(1);
}

// True-green baseline: the release-relevant workflow identities must remain stable.
if (!financial.includes("name: Ephemeral Financial Rules")) fail("financial workflow identity changed");
if (!auth.includes("name: Isolated Auth UI Smoke")) fail("auth workflow identity changed");

const gaps: string[] = [];

const usesLegacySetupAction =
  financial.includes("supabase/setup-cli@v1") || auth.includes("supabase/setup-cli@v1");
const usesFloatingLatest = /version:\s*["']?latest["']?/m.test(financial) || /version:\s*["']?latest["']?/m.test(auth);
const postsRawPrLogs =
  financial.includes("gh pr comment") &&
  (financial.includes("/tmp/supabase-start.log") || financial.includes("/tmp/financial-rules.log"));
const grantsCommentWritePermissions =
  /issues:\s*write/m.test(financial) || /pull-requests:\s*write/m.test(financial);

if (usesLegacySetupAction) {
  console.log("SEC_CI_G4_E1_EXPECTED_RED: release workflows still use supabase/setup-cli@v1");
  gaps.push("E1");
}
if (usesFloatingLatest) {
  console.log("SEC_CI_G4_E2_EXPECTED_RED: release workflows still use floating Supabase CLI version latest");
  gaps.push("E2");
}
if (postsRawPrLogs) {
  console.log("SEC_CI_G4_E3_EXPECTED_RED: financial workflow still posts raw log tails into PR comments");
  gaps.push("E3");
}
if (grantsCommentWritePermissions) {
  console.log("SEC_CI_G4_E4_EXPECTED_RED: financial workflow still grants write permissions used only for PR reporting");
  gaps.push("E4");
}

if (gaps.length === 0) {
  console.log("SEC_CI_G4_TARGET_GREEN: deterministic, least-privilege reporting contract detected");
  process.exit(0);
}

const expected = ["E1", "E2", "E3", "E4"];
if (expected.some((id) => !gaps.includes(id))) {
  fail(`partial/unexpected baseline gap set: ${gaps.join(",")}`);
}

// 42 is the controlled expected-red exit. The workflow wrapper must verify the
// exact sentinels before accepting this as Gate-4 evidence.
process.exit(42);
