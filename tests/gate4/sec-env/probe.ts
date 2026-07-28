import { resolveSupabaseBuildConfig } from "../../../config/supabase-build-config";

const PROD_URL = "https://dahzkekdirrngnkcxinv.supabase.co";
const PROD_PROJECT = "dahzkekdirrngnkcxinv";

function fail(message: string): never {
  console.error(`SEC_ENV_G4_BASELINE_FAIL: ${message}`);
  process.exit(1);
}

function resolvesWithoutThrow(env: Record<string, string>): boolean {
  try {
    resolveSupabaseBuildConfig(env as any);
    return true;
  } catch {
    return false;
  }
}

// True-green compatibility baseline 1: explicit preview/local target works.
const preview = resolveSupabaseBuildConfig({
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
  VITE_SUPABASE_PROJECT_ID: "isolated-project",
} as any);
if (preview.url !== "http://127.0.0.1:54321" || preview.projectId !== "isolated-project") {
  fail("explicit isolated preview configuration no longer resolves correctly");
}

// True-green compatibility baseline 2: explicit production intent plus explicit
// production values remains a valid deploy contract. This prevents a future
// implementation from solving isolation by blocking production entirely.
const production = resolveSupabaseBuildConfig({
  MONGEZZ_DEPLOY_TARGET: "production",
  VITE_SUPABASE_URL: PROD_URL,
  VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
  VITE_SUPABASE_PROJECT_ID: PROD_PROJECT,
} as any);
if (production.url !== PROD_URL || production.projectId !== PROD_PROJECT) {
  fail("explicit production intent/configuration no longer resolves correctly");
}

const gaps: string[] = [];

if (resolvesWithoutThrow({ MONGEZZ_DEPLOY_TARGET: "preview" })) {
  console.log("SEC_ENV_G4_E1_EXPECTED_RED: preview with missing Supabase config does not fail closed");
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
  console.log("SEC_ENV_G4_E2_EXPECTED_RED: preview can resolve the known production Supabase target");
  gaps.push("E2");
}

if (resolvesWithoutThrow({ MONGEZZ_DEPLOY_TARGET: "production" })) {
  console.log("SEC_ENV_G4_E3_EXPECTED_RED: production intent can succeed without explicit Supabase configuration");
  gaps.push("E3");
}

if (gaps.length === 0) {
  console.log("SEC_ENV_G4_TARGET_GREEN: explicit deployment contract fails closed and isolates non-production");
  process.exit(0);
}

const expected = ["E1", "E2", "E3"];
if (expected.some((id) => !gaps.includes(id))) {
  fail(`partial/unexpected environment gap set: ${gaps.join(",")}`);
}

process.exit(42);
