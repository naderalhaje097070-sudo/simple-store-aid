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
  return Object.fromEntries(
    Object.entries(process.env).filter(
      (entry): entry is [string, string] =>
        typeof entry[1] === "string" &&
        ![
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
        ].includes(entry[0]),
    ),
  );
}

function rapidClickPreflight(env: Record<string, string>) {
  const run = Bun.spawnSync(["python3", "tests/e2e/rapid-click-sale.py", "--preflight-only"], {
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

const safeRapidEnvFile = "/tmp/sec-env-rapid-safe.env";
const prodRapidEnvFile = "/tmp/sec-env-rapid-production.env";
await Bun.write(
  safeRapidEnvFile,
  "VITE_SUPABASE_URL=http://127.0.0.1:54321\nVITE_SUPABASE_PUBLISHABLE_KEY=isolated-anon-key\n",
);
await Bun.write(
  prodRapidEnvFile,
  `VITE_SUPABASE_URL=${PROD_URL}\nVITE_SUPABASE_PUBLISHABLE_KEY=production-public-key\n`,
);

const rapidCommon = {
  ...childBaseEnv(),
  MONGEZZ_DEPLOY_TARGET: "ci",
  PGHOST: "127.0.0.1",
  PGPORT: "54322",
  PGUSER: "postgres",
  PGDATABASE: "postgres",
};

const missingMarker = rapidClickPreflight({
  ...rapidCommon,
  MONGEZZ_E2E_ENV_FILE: safeRapidEnvFile,
});
const productionTarget = rapidClickPreflight({
  ...rapidCommon,
  MONGEZZ_E2E_WRITE_TEST: "1",
  MONGEZZ_E2E_ENV_FILE: prodRapidEnvFile,
});
const hostaddrBypass = rapidClickPreflight({
  ...rapidCommon,
  MONGEZZ_E2E_WRITE_TEST: "1",
  MONGEZZ_E2E_ENV_FILE: safeRapidEnvFile,
  PGHOSTADDR: "203.0.113.10",
});
const serviceBypass = rapidClickPreflight({
  ...rapidCommon,
  MONGEZZ_E2E_WRITE_TEST: "1",
  MONGEZZ_E2E_ENV_FILE: safeRapidEnvFile,
  PGSERVICE: "unsafe-service",
});
const safeTarget = rapidClickPreflight({
  ...rapidCommon,
  MONGEZZ_E2E_WRITE_TEST: "1",
  MONGEZZ_E2E_ENV_FILE: safeRapidEnvFile,
});

const rapidSource = await Bun.file("tests/e2e/rapid-click-sale.py").text();
const psqlNoRcCalls = rapidSource.match(/subprocess\.run\(\["psql", "-X"/g)?.length ?? 0;
const startupFilesDisabled = psqlNoRcCalls >= 2;

const missingMarkerBlocked =
  missingMarker.exitCode !== 0 && missingMarker.output.includes("SEC_ENV_RAPID_CLICK_BLOCKED");
const productionBlocked =
  productionTarget.exitCode !== 0 &&
  productionTarget.output.includes("SEC_ENV_RAPID_CLICK_BLOCKED");
const hostaddrBlocked =
  hostaddrBypass.exitCode !== 0 && hostaddrBypass.output.includes("SEC_ENV_RAPID_CLICK_BLOCKED");
const serviceBlocked =
  serviceBypass.exitCode !== 0 && serviceBypass.output.includes("SEC_ENV_RAPID_CLICK_BLOCKED");
const safeAccepted =
  safeTarget.exitCode === 0 && safeTarget.output.includes("SEC_ENV_RAPID_CLICK_PREFLIGHT_OK");

if (
  !missingMarkerBlocked ||
  !productionBlocked ||
  !hostaddrBlocked ||
  !serviceBlocked ||
  !startupFilesDisabled
) {
  console.log(
    "SEC_ENV_G4_E7_EXPECTED_RED: rapid-click write harness does not fail closed before production-capable I/O",
  );
  gaps.push("E7");
}
if (!safeAccepted) {
  fail("rapid-click isolated preflight rejected the approved CI loopback target");
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
