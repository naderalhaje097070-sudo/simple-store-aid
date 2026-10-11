import { expect, test } from "bun:test";
import {
  APPROVED_PRODUCTION_SUPABASE_TARGET,
  resolveSupabaseMcpIssuer,
  type SupabaseBuildEnvironment,
} from "../../config/supabase-build-config";

const local: SupabaseBuildEnvironment = {
  MONGEZZ_DEPLOY_TARGET: "ci",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "issuer-contract-placeholder",
  VITE_SUPABASE_PROJECT_ID: "monjez-mcp-ci",
};

function actualDefinition(config: SupabaseBuildEnvironment) {
  // A fresh process prevents other unit tests or ambient deployment values from
  // replacing this explicit test environment. No auth or tool implementation stub.
  const env = { ...process.env };
  for (const name of [
    "MONGEZZ_DEPLOY_TARGET",
    "VITE_SUPABASE_URL",
    "SUPABASE_URL",
    "VITE_SUPABASE_PUBLISHABLE_KEY",
    "SUPABASE_PUBLISHABLE_KEY",
    "VITE_SUPABASE_PROJECT_ID",
    "SUPABASE_PROJECT_ID",
    "LOVABLE_API_KEY",
  ])
    delete env[name];
  Object.assign(env, config);
  return Bun.spawnSync({
    cmd: [
      process.execPath,
      "--eval",
      'const { default: mcp } = await import("./src/lib/mcp/index.ts"); console.log(JSON.stringify(mcp.auth));',
    ],
    env,
  });
}

test("actual MCP definition uses the approved local issuer", () => {
  const result = actualDefinition(local);
  expect(result.exitCode).toBe(0);
  const auth = JSON.parse(new TextDecoder().decode(result.stdout));
  // Retains the original red assertion on actual application configuration.
  expect(auth).toMatchObject({
    type: "oauth",
    issuer: "http://127.0.0.1:54321/auth/v1",
  });
  expect(auth.jwksUri).toBe(
    "http://127.0.0.1:54321/auth/v1/.well-known/jwks.json",
  );
  expect(auth.acceptedAudiences).toEqual(["authenticated"]);
  expect(auth.requireOAuthClientClaim).not.toBe(false);
});

test("actual MCP import fails closed without explicit environment configuration", () => {
  const result = actualDefinition({});
  expect(result.exitCode).not.toBe(0);
  expect(new TextDecoder().decode(result.stderr)).toContain(
    "SEC_ENV_CONFIG_ERROR",
  );
});

test("issuer resolution validates local and ci endpoints before canonicalizing", () => {
  for (const target of ["local", "ci"]) {
    expect(
      resolveSupabaseMcpIssuer({
        ...local,
        MONGEZZ_DEPLOY_TARGET: target,
        VITE_SUPABASE_URL: "http://LOCALHOST:54321/",
      }),
    ).toBe("http://localhost:54321/auth/v1");
  }
});

test("remote environments retain direct Supabase project endpoints", () => {
  for (const target of ["preview", "staging"]) {
    expect(
      resolveSupabaseMcpIssuer({
        ...local,
        MONGEZZ_DEPLOY_TARGET: target,
        VITE_SUPABASE_URL: "https://isolated-project.supabase.co/",
        VITE_SUPABASE_PROJECT_ID: "isolated-project",
      }),
    ).toBe("https://isolated-project.supabase.co/auth/v1");
  }
  expect(
    resolveSupabaseMcpIssuer({
      ...local,
      MONGEZZ_DEPLOY_TARGET: "production",
      VITE_SUPABASE_URL: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
      VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
    }),
  ).toBe(APPROVED_PRODUCTION_SUPABASE_TARGET.url + "/auth/v1");
});

test("issuer cannot bypass the existing endpoint, alias or public key contract", () => {
  const invalid: SupabaseBuildEnvironment[] = [
    { ...local, VITE_SUPABASE_URL: undefined },
    { ...local, VITE_SUPABASE_PUBLISHABLE_KEY: undefined },
    { ...local, VITE_SUPABASE_PROJECT_ID: undefined },
    { ...local, MONGEZZ_DEPLOY_TARGET: undefined },
    { ...local, SUPABASE_URL: "https://foreign.supabase.co" },
    { ...local, SUPABASE_PROJECT_ID: "foreign" },
    { ...local, SUPABASE_PUBLISHABLE_KEY: "different-public-key" },
    { ...local, VITE_SUPABASE_PUBLISHABLE_KEY: "sb_secret_forbidden" },
    { ...local, VITE_SUPABASE_URL: "http://127.0.0.1:54321/proxy" },
    { ...local, VITE_SUPABASE_URL: "http://127.0.0.1:54321/?project=x" },
    {
      ...local,
      VITE_SUPABASE_URL: "https://foreign.supabase.co",
      VITE_SUPABASE_PROJECT_ID: "foreign",
    },
    {
      ...local,
      MONGEZZ_DEPLOY_TARGET: "production",
      VITE_SUPABASE_URL: "https://proxy.example.com",
      VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
    },
    {
      ...local,
      VITE_SUPABASE_URL: APPROVED_PRODUCTION_SUPABASE_TARGET.url,
      VITE_SUPABASE_PROJECT_ID: APPROVED_PRODUCTION_SUPABASE_TARGET.projectId,
    },
  ];
  for (const config of invalid)
    expect(() => resolveSupabaseMcpIssuer(config)).toThrow(
      "SEC_ENV_CONFIG_ERROR",
    );
});
