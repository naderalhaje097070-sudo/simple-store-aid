import {
  APPROVED_PRODUCTION_SUPABASE_TARGET,
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

const preview = resolve({
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
  VITE_SUPABASE_PROJECT_ID: "isolated-project",
});

if (preview.url !== "http://127.0.0.1:54321" || preview.projectId !== "isolated-project") {
  fail("explicit isolated preview configuration no longer resolves correctly");
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
if (
  resolvesWithoutThrow({
    MONGEZZ_DEPLOY_TARGET: "preview",
    VITE_SUPABASE_URL: productionUrlWithTerminalDot,
    VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
    VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
  })
) {
  console.log(
    "SEC_ENV_G4_E4_EXPECTED_RED: terminal DNS dot bypasses non-production production-target isolation",
  );
  gaps.push("E4");
}

const serverAliasEnv: SupabaseBuildEnvironment = {
  MONGEZZ_DEPLOY_TARGET: "preview",
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

if (gaps.length === 0) {
  console.log(
    "SEC_ENV_G4_TARGET_GREEN: explicit deployment contract fails closed and isolates non-production",
  );
  process.exit(0);
}

const expected = ["E1", "E2", "E3", "E4", "E5"];
if (expected.some((id) => !gaps.includes(id))) {
  fail(`partial/unexpected environment gap set: ${gaps.join(",")}`);
}

process.exit(42);
