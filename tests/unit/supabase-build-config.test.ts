import { describe, expect, test } from "bun:test";
import {
  APPROVED_PRODUCTION_SUPABASE_TARGET,
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

  test("VITE aliases take precedence over server aliases", () => {
    const resolved = resolveSupabaseBuildConfig({
      ...isolatedViteConfig,
      SUPABASE_URL: "http://server-supabase.test",
      SUPABASE_PUBLISHABLE_KEY: "server-key",
      SUPABASE_PROJECT_ID: "server-project",
    });

    expect(resolved).toEqual({
      url: "http://127.0.0.1:54321",
      publishableKey: "isolated-anon-key",
      projectId: "isolated-project",
    });
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
