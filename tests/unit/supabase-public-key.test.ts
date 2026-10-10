import { describe, expect, test } from "bun:test";
import { resolveSupabaseBuildConfig } from "../../config/supabase-build-config";

const env = {
  MONGEZZ_DEPLOY_TARGET: "ci",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PROJECT_ID: "isolated-fixture",
};
const jwt = (role: string) =>
  `${btoa('{"alg":"HS256","typ":"JWT"}')}.${btoa(JSON.stringify({ role }))}.fixture`;

describe("public Supabase configuration rejects privileged credentials", () => {
  for (const key of ["sb_secret_offline_fixture", jwt("service_role"), jwt("authenticated")]) {
    test(`rejects privileged key format ${key.startsWith("sb_secret_") ? "secret" : "JWT"}`, () => {
      expect(() =>
        resolveSupabaseBuildConfig({ ...env, VITE_SUPABASE_PUBLISHABLE_KEY: key }),
      ).toThrow("public Supabase key");
    });
  }
  test("accepts legacy anon and publishable fixtures", () => {
    for (const key of [jwt("anon"), "sb_publishable_offline_fixture"]) {
      expect(
        resolveSupabaseBuildConfig({ ...env, VITE_SUPABASE_PUBLISHABLE_KEY: key }).publishableKey,
      ).toBe(key);
    }
  });
});
