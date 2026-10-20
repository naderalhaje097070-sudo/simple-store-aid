import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

// Execute the real server wrapper with a stub application entry. No database,
// browser, or production request is made by this integration probe.
const fixture = {
  MONGEZZ_DEPLOY_TARGET: "ci",
  VITE_SUPABASE_URL: "http://127.0.0.1:54321",
  VITE_SUPABASE_PUBLISHABLE_KEY: "sb_publishable_offline_fixture",
  VITE_SUPABASE_PROJECT_ID: "offline-fixture",
};
const defines = {
  __MONGEZZ_BUILD_DEPLOY_TARGET__: fixture.MONGEZZ_DEPLOY_TARGET,
  __MONGEZZ_BUILD_SUPABASE_URL__: fixture.VITE_SUPABASE_URL,
  __MONGEZZ_BUILD_SUPABASE_PUBLISHABLE_KEY__: fixture.VITE_SUPABASE_PUBLISHABLE_KEY,
  __MONGEZZ_BUILD_SUPABASE_PROJECT_ID__: fixture.VITE_SUPABASE_PROJECT_ID,
};
const directory = await mkdtemp(join(tmpdir(), "mongezz-server-boundary-"));
const snapshot = { ...process.env };
const keys = [
  ...Object.keys(fixture),
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "SUPABASE_PROJECT_ID",
  "SUPABASE_SERVICE_ROLE_KEY",
];
const originalError = console.error;
try {
  const build = await Bun.build({
    entrypoints: ["src/server.ts"],
    target: "bun",
    define: Object.fromEntries(
      Object.entries(defines).map(([key, value]) => [key, JSON.stringify(value)]),
    ),
    plugins: [
      {
        name: "offline-app-entry",
        setup(builder) {
          builder.onResolve({ filter: /^@tanstack\/react-start\/server-entry$/ }, () => ({
            path: "app-entry",
            namespace: "offline",
          }));
          builder.onLoad({ filter: /.*/, namespace: "offline" }, () => ({
            contents: 'export default { fetch() { return new Response("OFFLINE_APP_ENTRY"); } };',
            loader: "js",
          }));
        },
      },
    ],
  });
  if (!build.success) throw new Error("offline server wrapper build failed");
  const path = join(directory, "server.mjs");
  await Bun.write(path, build.outputs[0]);
  const server = (await import(path)).default;
  console.error = () => {}; // Expected rejection errors; never print runtime values.
  const cases: Array<[string, Record<string, string>, Record<string, string>, number]> = [
    ["missing runtime", {}, {}, 500],
    ["matching runtime", fixture, {}, 200],
    ["different deployment target", { ...fixture, MONGEZZ_DEPLOY_TARGET: "local" }, {}, 500],
    [
      "different public key",
      { ...fixture, VITE_SUPABASE_PUBLISHABLE_KEY: "different-fixture" },
      {},
      500,
    ],
    ["conflicting aliases", { ...fixture, SUPABASE_URL: "http://127.0.0.1:9999" }, {}, 500],
    ["matching worker bindings", {}, fixture, 200],
    ["conflicting worker binding", fixture, { VITE_SUPABASE_PROJECT_ID: "other-fixture" }, 500],
    [
      "remote runtime endpoint",
      { ...fixture, VITE_SUPABASE_URL: "https://forbidden.supabase.co" },
      {},
      500,
    ],
  ];
  for (const [name, environment, bindings, expected] of cases) {
    for (const key of keys) delete process.env[key];
    Object.assign(process.env, environment);
    const response = await server.fetch(new Request("http://localhost:8080/"), bindings, {});
    const body = await response.text();
    if (response.status !== expected || (expected === 200) !== (body === "OFFLINE_APP_ENTRY")) {
      throw new Error(`server boundary failed: ${name}`);
    }
  }
  console.error = originalError;
  console.log(
    `SEC_ENV_SERVER_BOUNDARY_GREEN: ${cases.length} actual wrapper scenarios, stub app entry, no network/database`,
  );
} finally {
  console.error = originalError;
  for (const key of keys) {
    if (snapshot[key] === undefined) delete process.env[key];
    else process.env[key] = snapshot[key];
  }
  await rm(directory, { recursive: true, force: true });
}
