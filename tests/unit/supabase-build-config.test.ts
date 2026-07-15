import { describe, expect, test } from "bun:test";
import {
  PRODUCTION_SUPABASE_FALLBACK,
  resolveSupabaseBuildConfig,
} from "../../config/supabase-build-config";

describe("Supabase build configuration", () => {
  test("VITE variables override production fallback values", () => {
    const resolved = resolveSupabaseBuildConfig({
      VITE_SUPABASE_URL: "http://127.0.0.1:54321",
      VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
      VITE_SUPABASE_PROJECT_ID: "isolated-project",
    });

    expect(resolved).toEqual({
      url: "http://127.0.0.1:54321",
      publishableKey: "isolated-anon-key",
      projectId: "isolated-project",
    });
  });

  test("server variable aliases are used when VITE variables are absent", () => {
    const resolved = resolveSupabaseBuildConfig({
      SUPABASE_URL: "http://server-supabase.test",
      SUPABASE_PUBLISHABLE_KEY: "server-publishable-key",
      SUPABASE_PROJECT_ID: "server-project",
    });

    expect(resolved).toEqual({
      url: "http://server-supabase.test",
      publishableKey: "server-publishable-key",
      projectId: "server-project",
    });
  });

  test("Lovable preview receives the production public fallback when variables are missing", () => {
    expect(resolveSupabaseBuildConfig({})).toEqual(PRODUCTION_SUPABASE_FALLBACK);
  });

  test("blank environment values do not override usable values", () => {
    const resolved = resolveSupabaseBuildConfig({
      VITE_SUPABASE_URL: "   ",
      SUPABASE_URL: "http://server-supabase.test",
      VITE_SUPABASE_PUBLISHABLE_KEY: "",
      SUPABASE_PUBLISHABLE_KEY: "server-publishable-key",
      VITE_SUPABASE_PROJECT_ID: "\t",
      SUPABASE_PROJECT_ID: "server-project",
    });

    expect(resolved).toEqual({
      url: "http://server-supabase.test",
      publishableKey: "server-publishable-key",
      projectId: "server-project",
    });
  });
});
