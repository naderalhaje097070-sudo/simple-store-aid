import { readdir } from "node:fs/promises";
import {
  APPROVED_PRODUCTION_SUPABASE_TARGET,
  assertSupabaseRuntimeMatchesBuild,
  resolveAndHydrateSupabaseServerConfig,
  resolveSupabaseBuildConfig,
  type SupabaseBuildEnvironment,
} from "../../../config/supabase-build-config";

const PROD_URL = APPROVED_PRODUCTION_SUPABASE_TARGET.url;
const PROD_PROJECT = APPROVED_PRODUCTION_SUPABASE_TARGET.projectId;

function fail(message: string): never {
  console.error(`SEC_ENV_G4_BASELINE_FAIL: ${message}`);
  process.exit(1);
}

function resolve(env: Record<string, string>) {
  return resolveSupabaseBuildConfig(env as SupabaseBuildEnvironment);
}

function resolvesWithoutThrow(env: Record<string, string>): boolean {
  try {
    resolve(env);
    return true;
  } catch {
    return false;
  }
}

function childBaseEnv(): Record<string, string> {
  const excluded = new Set([
    "VITE_SUPABASE_URL",
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    "MONGEZZ_E2E_WRITE_TEST",
    "MONGEZZ_DEPLOY_TARGET",
    "MONGEZZ_E2E_ENV_FILE",
    "PGHOST",
    "PGHOSTADDR",
    "PGPORT",
    "PGUSER",
    "PGDATABASE",
    "PGSERVICE",
    "PGSERVICEFILE",
    "PSQLRC",
  ]);

  return Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] => typeof entry[1] === "string" && !excluded.has(entry[0]),
    ),
  );
}

type PreflightResult = {
  exitCode: number;
  output: string;
};

function pythonPreflight(script: string, env: Record<string, string>): PreflightResult {
  const run = Bun.spawnSync(["python3", script, "--preflight-only"], {
    env,
    stdout: "pipe",
    stderr: "pipe",
  });
  const decode = (value: Uint8Array) => new TextDecoder().decode(value);
  return {
    exitCode: run.exitCode,
    output: `${decode(run.stdout)}\n${decode(run.stderr)}`,
  };
}

function preflightBlocked(result: PreflightResult): boolean {
  return (
    result.exitCode !== 0 &&
    (result.output.includes("SEC_ENV_RAPID_CLICK_BLOCKED") ||
      result.output.includes("SEC_ENV_WRITE_HARNESS_BLOCKED"))
  );
}

function preflightAccepted(result: PreflightResult): boolean {
  return (
    result.exitCode === 0 &&
    (result.output.includes("SEC_ENV_RAPID_CLICK_PREFLIGHT_OK") ||
      result.output.includes("SEC_ENV_WRITE_HARNESS_PREFLIGHT_OK"))
  );
}

const preview = resolve({
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: "https://preview-project.supabase.co",
  VITE_SUPABASE_PUBLISHABLE_KEY: "preview-public-key",
  VITE_SUPABASE_PROJECT_ID: "preview-project",
});

if (
  preview.url !== "https://preview-project.supabase.co" ||
  preview.projectId !== "preview-project"
) {
  fail("explicit dedicated preview configuration no longer resolves correctly");
}

const production = resolve({
  MONGEZZ_DEPLOY_TARGET: "production",
  VITE_SUPABASE_URL: PROD_URL,
  VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
  VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
});

if (production.url !== PROD_URL || production.projectId !== PROD_PROJECT) {
  fail("explicit production intent/configuration no longer resolves correctly");
}

const gaps: string[] = [];

if (resolvesWithoutThrow({ MONGEZZ_DEPLOY_TARGET: "preview" })) {
  console.log(
    "SEC_ENV_G4_E1_EXPECTED_RED: preview with missing Supabase config does not fail closed",
  );
  gaps.push("E1");
}

if (
  resolvesWithoutThrow({
    MONGEZZ_DEPLOY_TARGET: "preview",
    VITE_SUPABASE_URL: PROD_URL,
    VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
    VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
  })
) {
  console.log(
    "SEC_ENV_G4_E2_EXPECTED_RED: preview can resolve the known production Supabase target",
  );
  gaps.push("E2");
}

if (resolvesWithoutThrow({ MONGEZZ_DEPLOY_TARGET: "production" })) {
  console.log(
    "SEC_ENV_G4_E3_EXPECTED_RED: production intent can succeed without explicit Supabase configuration",
  );
  gaps.push("E3");
}

const productionUrlWithTerminalDot = PROD_URL.replace(".supabase.co", ".supabase.co.");
const terminalDotBypass = resolvesWithoutThrow({
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: productionUrlWithTerminalDot,
  VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
  VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
});
const queryRoutingBypass = resolvesWithoutThrow({
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: "https://preview-project.supabase.co?project=prod",
  VITE_SUPABASE_PUBLISHABLE_KEY: "preview-public-key",
  VITE_SUPABASE_PROJECT_ID: "preview-project",
});
const gatewayRoutingBypass = resolvesWithoutThrow({
  MONGEZZ_DEPLOY_TARGET: "staging",
  VITE_SUPABASE_URL: "https://gateway.example",
  VITE_SUPABASE_PUBLISHABLE_KEY: "staging-public-key",
  VITE_SUPABASE_PROJECT_ID: "staging-project",
});

if (terminalDotBypass || queryRoutingBypass || gatewayRoutingBypass) {
  console.log(
    "SEC_ENV_G4_E4_EXPECTED_RED: endpoint normalization or routing can bypass target isolation",
  );
  gaps.push("E4");
}

const serverAliasEnv: SupabaseBuildEnvironment = {
  MONGEZZ_DEPLOY_TARGET: "ci",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
  VITE_SUPABASE_PROJECT_ID: "isolated-project",
};
resolveAndHydrateSupabaseServerConfig(serverAliasEnv);
if (
  serverAliasEnv.SUPABASE_URL !== serverAliasEnv.VITE_SUPABASE_URL ||
  serverAliasEnv.SUPABASE_PUBLISHABLE_KEY !== serverAliasEnv.VITE_SUPABASE_PUBLISHABLE_KEY ||
  serverAliasEnv.SUPABASE_PROJECT_ID !== serverAliasEnv.VITE_SUPABASE_PROJECT_ID
) {
  console.log(
    "SEC_ENV_G4_E5_EXPECTED_RED: validated VITE-only runtime does not materialize required server aliases",
  );
  gaps.push("E5");
}

try {
  assertSupabaseRuntimeMatchesBuild(
    {
      MONGEZZ_DEPLOY_TARGET: "production",
      VITE_SUPABASE_URL: PROD_URL,
      VITE_SUPABASE_PUBLISHABLE_KEY: "production-public-key",
      VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
    },
    {
      MONGEZZ_DEPLOY_TARGET: "ci",
      VITE_SUPABASE_URL: "http://127.0.0.1:54321",
      VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
      VITE_SUPABASE_PROJECT_ID: "isolated-project",
    },
  );
  console.log(
    "SEC_ENV_G4_E6_EXPECTED_RED: runtime environment can diverge from the baked build identity",
  );
  gaps.push("E6");
} catch {
  // Expected target-green behavior.
}

// E7 — inventory and fail-closed containment of every checked-in E2E harness.
const e2eEntries = await readdir("tests/e2e", { withFileTypes: true });
const actualPythonHarnesses = e2eEntries
  .filter((entry) => entry.isFile() && entry.name.endsWith(".py"))
  .map((entry) => entry.name)
  .sort();
const classifiedPythonHarnesses = [
  "isolated-auth-smoke.py", // read-only
  "rapid-click-sale.py", // destructive; legacy in-file guard
  "sale-dashboard-close.py", // destructive; shared guard
  "write_harness_guard.py", // safety infrastructure
].sort();
const inventoryMatches =
  actualPythonHarnesses.length === classifiedPythonHarnesses.length &&
  actualPythonHarnesses.every((name, index) => name === classifiedPythonHarnesses[index]);

const safeEnvFile = "/tmp/sec-env-e2e-safe.env";
const prodEnvFile = "/tmp/sec-env-e2e-production.env";
await Bun.write(
  safeEnvFile,
  "VITE_SUPABASE_URL=http://127.0.0.1:54321\nVITE_SUPABASE_PUBLISHABLE_KEY=isolated-anon-key\n",
);
await Bun.write(
  prodEnvFile,
  `VITE_SUPABASE_URL=${PROD_URL}\nVITE_SUPABASE_PUBLISHABLE_KEY=production-public-key\n`,
);

const safeCommon = {
  ...childBaseEnv(),
  MONGEZZ_DEPLOY_TARGET: "ci",
  PGHOST: "127.0.0.1",
  PGPORT: "54322",
  PGUSER: "postgres",
  PGDATABASE: "postgres",
};

const destructiveHarnesses = ["tests/e2e/rapid-click-sale.py", "tests/e2e/sale-dashboard-close.py"];

let allDestructiveHarnessesContained = inventoryMatches;
for (const script of destructiveHarnesses) {
  const missingMarker = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_E2E_ENV_FILE: safeEnvFile,
  });
  const productionTarget = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_DEPLOY_TARGET: "production",
    MONGEZZ_E2E_WRITE_TEST: "1",
    MONGEZZ_E2E_ENV_FILE: safeEnvFile,
  });
  const productionEndpoint = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_E2E_WRITE_TEST: "1",
    MONGEZZ_E2E_ENV_FILE: prodEnvFile,
  });
  const hostaddrBypass = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_E2E_WRITE_TEST: "1",
    MONGEZZ_E2E_ENV_FILE: safeEnvFile,
    PGHOSTADDR: "203.0.113.10",
  });
  const serviceBypass = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_E2E_WRITE_TEST: "1",
    MONGEZZ_E2E_ENV_FILE: safeEnvFile,
    PGSERVICE: "unsafe-service",
  });
  const safeTarget = pythonPreflight(script, {
    ...safeCommon,
    MONGEZZ_E2E_WRITE_TEST: "1",
    MONGEZZ_E2E_ENV_FILE: safeEnvFile,
  });

  if (
    !preflightBlocked(missingMarker) ||
    !preflightBlocked(productionTarget) ||
    !preflightBlocked(productionEndpoint) ||
    !preflightBlocked(hostaddrBypass) ||
    !preflightBlocked(serviceBypass) ||
    !preflightAccepted(safeTarget)
  ) {
    allDestructiveHarnessesContained = false;
  }
}

const rapidSource = await Bun.file("tests/e2e/rapid-click-sale.py").text();
const saleCloseSource = await Bun.file("tests/e2e/sale-dashboard-close.py").text();
const sharedGuardSource = await Bun.file("tests/e2e/write_harness_guard.py").text();
const runnerSource = await Bun.file("tests/e2e/run.sh").text();
const readOnlySmokeSource = await Bun.file("tests/e2e/isolated-auth-smoke.py").text();

const rapidPreflightBeforeNetwork =
  rapidSource.indexOf("require_explicit_write_intent()") >= 0 &&
  rapidSource.indexOf("require_explicit_write_intent()") < rapidSource.indexOf("import requests");
const saleCloseUsesSharedGuard =
  saleCloseSource.includes("from write_harness_guard import") &&
  saleCloseSource.indexOf("WRITE_CONFIG = require_write_harness()") >= 0 &&
  saleCloseSource.indexOf("WRITE_CONFIG = require_write_harness()") <
    saleCloseSource.indexOf("import requests");
const sharedGuardPinsPsqlRouting =
  sharedGuardSource.includes('"psql",') &&
  sharedGuardSource.includes('"-X",') &&
  sharedGuardSource.includes('"-h",') &&
  sharedGuardSource.includes('"-p",') &&
  sharedGuardSource.includes('"-U",') &&
  sharedGuardSource.includes('"-d",') &&
  sharedGuardSource.includes("env=_psql_env(config)");
const rapidPsqlStartupDisabled =
  (rapidSource.match(/subprocess\.run\(\["psql", "-X"/g)?.length ?? 0) >= 2;
const runnerPreflight = 'python3 "$HERE/sale-dashboard-close.py" --preflight-only';
const runnerChecksPreflightBeforeServer =
  runnerSource.includes(runnerPreflight) &&
  runnerSource.indexOf(runnerPreflight) < runnerSource.indexOf("curl -sf");
const readOnlySmokeStaysIsolated =
  readOnlySmokeSource.includes('CI_ISOLATED_SUPABASE") != "1"') &&
  !readOnlySmokeSource.includes("psql") &&
  !readOnlySmokeSource.includes("requests.post");

if (
  !allDestructiveHarnessesContained ||
  !rapidPreflightBeforeNetwork ||
  !saleCloseUsesSharedGuard ||
  !sharedGuardPinsPsqlRouting ||
  !rapidPsqlStartupDisabled ||
  !runnerChecksPreflightBeforeServer ||
  !readOnlySmokeStaysIsolated
) {
  console.log(
    "SEC_ENV_G4_E7_EXPECTED_RED: checked-in E2E inventory contains an unclassified or non-contained write-capable path",
  );
  gaps.push("E7");
}

if (gaps.length === 0) {
  console.log(
    "SEC_ENV_G4_TARGET_GREEN: explicit deployment contract fails closed and isolates non-production",
  );
  process.exit(0);
}

const expected = ["E1", "E2", "E3", "E4", "E5", "E6", "E7"];
if (expected.some((id) => !gaps.includes(id))) {
  fail(`partial/unexpected environment gap set: ${gaps.join(",")}`);
}

process.exit(42);
