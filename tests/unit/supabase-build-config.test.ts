import { describe, expect, test } from "bun:test";
import {
  APPROVED_PRODUCTION_SUPABASE_TARGET,
  assertSupabaseRuntimeMatchesBuild,
  resolveAndHydrateSupabaseServerConfig,
  resolveSupabaseBuildConfig,
} from "../../config/supabase-build-config";

const isolatedViteConfig = {
  MONGEZZ_DEPLOY_TARGET: "preview",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
  VITE_SUPABASE_PROJECT_ID: "isolated-project",
};

describe("Supabase build configuration", () => {
  test("accepts explicit isolated VITE configuration", () => {
    expect(resolveSupabaseBuildConfig(isolatedViteConfig)).toEqual({
      url: "http://127.0.0.1:54321",
      publishableKey: "isolated-anon-key",
      projectId: "isolated-project",
    });
  });

  test("accepts matching browser and server aliases", () => {
    expect(
      resolveSupabaseBuildConfig({
        ...isolatedViteConfig,
        SUPABASE_URL: "http://127.0.0.1:54321/",
        SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
        SUPABASE_PROJECT_ID: "isolated-project",
      }),
    ).toEqual({
      url: "http://127.0.0.1:54321",
      publishableKey: "isolated-anon-key",
      projectId: "isolated-project",
    });
  });

  test("rejects divergent browser and server aliases", () => {
    expect(() =>
      resolveSupabaseBuildConfig({
        ...isolatedViteConfig,
        SUPABASE_URL: "https://server-project.supabase.co",
      }),
    ).toThrow("VITE_SUPABASE_URL and SUPABASE_URL must target the same project");

    expect(() =>
      resolveSupabaseBuildConfig({
        ...isolatedViteConfig,
        SUPABASE_PUBLISHABLE_KEY: "different-server-key",
      }),
    ).toThrow("VITE_SUPABASE_PUBLISHABLE_KEY and SUPABASE_PUBLISHABLE_KEY must match");

    expect(() =>
      resolveSupabaseBuildConfig({
        ...isolatedViteConfig,
        SUPABASE_PROJECT_ID: "different-server-project",
      }),
    ).toThrow("VITE_SUPABASE_PROJECT_ID and SUPABASE_PROJECT_ID must match");
  });

  test("uses server aliases when VITE aliases are absent", () => {
    expect(
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "staging",
        SUPABASE_URL: "https://staging-project.supabase.co",
        SUPABASE_PUBLISHABLE_KEY: "server-publishable-key",
        SUPABASE_PROJECT_ID: "staging-project",
      }),
    ).toEqual({
      url: "https://staging-project.supabase.co",
      publishableKey: "server-publishable-key",
      projectId: "staging-project",
    });
  });

  test("hydrates missing server aliases only from validated resolved values", () => {
    const env = { ...isolatedViteConfig };

    expect(resolveAndHydrateSupabaseServerConfig(env)).toEqual({
      url: "http://127.0.0.1:54321",
      publishableKey: "isolated-anon-key",
      projectId: "isolated-project",
    });
    expect(env.SUPABASE_URL).toBe("http://127.0.0.1:54321");
    expect(env.SUPABASE_PUBLISHABLE_KEY).toBe("isolated-anon-key");
    expect(env.SUPABASE_PROJECT_ID).toBe("isolated-project");
  });

  test("server alias hydration cannot overwrite divergent explicit aliases", () => {
    const env = {
      ...isolatedViteConfig,
      SUPABASE_URL: "https://different-project.supabase.co",
    };

    expect(() => resolveAndHydrateSupabaseServerConfig(env)).toThrow(
      "VITE_SUPABASE_URL and SUPABASE_URL must target the same project",
    );
    expect(env.SUPABASE_URL).toBe("https://different-project.supabase.co");
  });

  test("runtime identity must match the baked build identity", () => {
    expect(() =>
      assertSupabaseRuntimeMatchesBuild(isolatedViteConfig, {
        MONGEZZ_DEPLOY_TARGET: "preview",
        SUPABASE_URL: "http://127.0.0.1:54321/",
        SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
        SUPABASE_PROJECT_ID: "isolated-project",
      }),
    ).not.toThrow();

    expect(() =>
      assertSupabaseRuntimeMatchesBuild(
        {
          MONGEZZ_DEPLOY_TARGET: "production",
          VITE_SUPABASE_URL: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
          VITE_SUPABASE_PUBLISHABLE_KEY: "production-public-key",
          VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
        },
        isolatedViteConfig,
      ),
    ).toThrow("runtime deployment target does not match baked build target");

    expect(() =>
      assertSupabaseRuntimeMatchesBuild(isolatedViteConfig, {
        MONGEZZ_DEPLOY_TARGET: "preview",
        SUPABASE_URL: "http://127.0.0.1:54323",
        SUPABASE_PUBLISHABLE_KEY: "isolated-anon-key",
        SUPABASE_PROJECT_ID: "isolated-project",
      }),
    ).toThrow("runtime Supabase configuration does not match baked build configuration");
  });

  test("fails closed when deployment target is missing or unsupported", () => {
    expect(() => resolveSupabaseBuildConfig({})).toThrow("MONGEZZ_DEPLOY_TARGET is required");
    expect(() =>
      resolveSupabaseBuildConfig({
        ...isolatedViteConfig,
        MONGEZZ_DEPLOY_TARGET: "qa",
      }),
    ).toThrow("unsupported MONGEZZ_DEPLOY_TARGET");
  });

  test("fails closed when explicit Supabase values are missing or blank", () => {
    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "preview",
        VITE_SUPABASE_URL: " ",
        VITE_SUPABASE_PUBLISHABLE_KEY: "",
        VITE_SUPABASE_PROJECT_ID: "\t",
      }),
    ).toThrow("missing explicit Supabase configuration");
  });

  test("blank VITE aliases do not override usable server aliases", () => {
    expect(
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "preview",
        VITE_SUPABASE_URL: "   ",
        SUPABASE_URL: "https://preview-project.supabase.co",
        VITE_SUPABASE_PUBLISHABLE_KEY: "",
        SUPABASE_PUBLISHABLE_KEY: "server-publishable-key",
        VITE_SUPABASE_PROJECT_ID: "\t",
        SUPABASE_PROJECT_ID: "preview-project",
      }),
    ).toEqual({
      url: "https://preview-project.supabase.co",
      publishableKey: "server-publishable-key",
      projectId: "preview-project",
    });
  });

  test("non-production targets reject the production host or project", () => {
    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "preview",
        VITE_SUPABASE_URL: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
        VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
        VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
      }),
    ).toThrow("cannot use the production Supabase host/project");
  });

  test("terminal DNS dots cannot bypass production isolation", () => {
    const productionUrlWithTerminalDot = APPROVED_PRODUCTION_SUPABASE_TARGET.url.replace(
      ".supabase.co",
      ".supabase.co.",
    );

    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "preview",
        VITE_SUPABASE_URL: productionUrlWithTerminalDot,
        VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
        VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
      }),
    ).toThrow("cannot use the production Supabase host/project");

    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "preview",
        VITE_SUPABASE_URL: productionUrlWithTerminalDot,
        VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
        VITE_SUPABASE_PROJECT_ID: "lookalike-project",
      }),
    ).toThrow("Supabase URL and project ID do not match");
  });

  test("production requires explicit approved host/project and explicit key", () => {
    expect(
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "production",
        VITE_SUPABASE_URL: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
        VITE_SUPABASE_PUBLISHABLE_KEY: "explicit-production-public-key",
        VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
      }),
    ).toEqual({
      url: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
      publishableKey: "explicit-production-public-key",
      projectId: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
    });

    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "production",
        VITE_SUPABASE_URL: "https://staging-project.supabase.co",
        VITE_SUPABASE_PUBLISHABLE_KEY: "public-key-placeholder",
        VITE_SUPABASE_PROJECT_ID: "staging-project",
      }),
    ).toThrow("production target requires the approved production Supabase host/project");
  });

  test("remote Supabase URL and project ID must match", () => {
    expect(() =>
      resolveSupabaseBuildConfig({
        MONGEZZ_DEPLOY_TARGET: "staging",
        VITE_SUPABASE_URL: "https://project-a.supabase.co",
        VITE_SUPABASE_PUBLISHABLE_KEY: "staging-key",
        VITE_SUPABASE_PROJECT_ID: "project-b",
      }),
    ).toThrow("Supabase URL and project ID do not match");
  });
});
