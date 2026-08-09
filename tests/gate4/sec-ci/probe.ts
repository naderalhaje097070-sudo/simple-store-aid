import { readFileSync } from "node:fs";

const financialPath = ".github/workflows/ephemeral-financial-rules.yml";
const authPath = ".github/workflows/isolated-auth-smoke.yml";

const financial = readFileSync(financialPath, "utf8");
const auth = readFileSync(authPath, "utf8");

function fail(message: string): never {
  console.error(`SEC_CI_G4_BASELINE_FAIL: ${message}`);
  process.exit(1);
}

function setupCliVersion(source: string): string | null {
  const match = source.match(
    /uses:\s*supabase\/setup-cli@v2[\s\S]{0,180}?version:\s*["']?([^\s"']+)/m,
  );

  return match?.[1] ?? null;
}

// True-green baseline: release-relevant workflow identities must remain stable.
if (!financial.includes("name: Ephemeral Financial Rules")) {
  fail("financial workflow identity changed");
}

if (!auth.includes("name: Isolated Auth UI Smoke")) {
  fail("auth workflow identity changed");
}

const financialVersion = setupCliVersion(financial);
const authVersion = setupCliVersion(auth);
const exactSemver = /^\d+\.\d+\.\d+$/;
const gaps: string[] = [];

const bothUseMaintainedAction =
  financial.includes("uses: supabase/setup-cli@v2") && auth.includes("uses: supabase/setup-cli@v2");

const bothUseOneExactVersion =
  financialVersion !== null &&
  authVersion !== null &&
  exactSemver.test(financialVersion) &&
  exactSemver.test(authVersion) &&
  financialVersion === authVersion;

const postsRawPrLogs =
  financial.includes("gh pr comment") &&
  (financial.includes("/tmp/supabase-start.log") || financial.includes("/tmp/financial-rules.log"));

const grantsCommentWritePermissions =
  /issues:\s*write/m.test(financial) || /pull-requests:\s*write/m.test(financial);

if (!bothUseMaintainedAction) {
  console.log("SEC_CI_G4_E1_EXPECTED_RED: release workflows are not both on supabase/setup-cli@v2");
  gaps.push("E1");
}

if (!bothUseOneExactVersion) {
  console.log(
    "SEC_CI_G4_E2_EXPECTED_RED: release workflows do not share one exact semver Supabase CLI pin",
  );
  gaps.push("E2");
}

if (postsRawPrLogs) {
  console.log(
    "SEC_CI_G4_E3_EXPECTED_RED: financial workflow still posts raw log tails into PR comments",
  );
  gaps.push("E3");
}

if (grantsCommentWritePermissions) {
  console.log(
    "SEC_CI_G4_E4_EXPECTED_RED: financial workflow still grants issue or PR write permissions",
  );
  gaps.push("E4");
}

if (gaps.length === 0) {
  console.log(
    `SEC_CI_G4_TARGET_GREEN: setup-cli@v2 pinned to ${financialVersion}; reporting is least-privilege`,
  );
  process.exit(0);
}

const expected = ["E1", "E2", "E3", "E4"];
if (expected.some((id) => !gaps.includes(id))) {
  fail(`partial/unexpected baseline gap set: ${gaps.join(",")}`);
}

// 42 is controlled expected-red. The workflow wrapper verifies every exact
// sentinel so runtime/parse failures cannot masquerade as Gate evidence.
process.exit(42);
