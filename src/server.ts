import "./lib/error-capture";

import {
  assertSupabaseRuntimeMatchesBuild,
  resolveAndHydrateSupabaseServerConfig,
} from "../config/supabase-build-config";
import { consumeLastCapturedError } from "./lib/error-capture";
import { renderErrorPage } from "./lib/error-page";

declare const __MONGEZZ_BUILD_DEPLOY_TARGET__: string;
declare const __MONGEZZ_BUILD_SUPABASE_URL__: string;
declare const __MONGEZZ_BUILD_SUPABASE_PUBLISHABLE_KEY__: string;
declare const __MONGEZZ_BUILD_SUPABASE_PROJECT_ID__: string;

type ServerEntry = {
  fetch: (request: Request, env: unknown, ctx: unknown) => Promise<Response> | Response;
};

const SERVER_ENV_KEYS = [
  "MONGEZZ_DEPLOY_TARGET",
  "VITE_SUPABASE_URL",
  "VITE_SUPABASE_PUBLISHABLE_KEY",
  "VITE_SUPABASE_PROJECT_ID",
  "SUPABASE_URL",
  "SUPABASE_PUBLISHABLE_KEY",
  "SUPABASE_PROJECT_ID",
  "SUPABASE_SERVICE_ROLE_KEY",
] as const;

const BAKED_BUILD_ENV = Object.freeze({
  MONGEZZ_DEPLOY_TARGET: __MONGEZZ_BUILD_DEPLOY_TARGET__,
  VITE_SUPABASE_URL: __MONGEZZ_BUILD_SUPABASE_URL__,
  VITE_SUPABASE_PUBLISHABLE_KEY: __MONGEZZ_BUILD_SUPABASE_PUBLISHABLE_KEY__,
  VITE_SUPABASE_PROJECT_ID: __MONGEZZ_BUILD_SUPABASE_PROJECT_ID__,
});

let serverEntryPromise: Promise<ServerEntry> | undefined;

function hydrateServerProcessEnv(workerEnv: unknown): void {
  if (!workerEnv || typeof workerEnv !== "object") return;
  const bindings = workerEnv as Record<string, unknown>;

  for (const key of SERVER_ENV_KEYS) {
    const bindingValue = bindings[key];
    if (typeof bindingValue !== "string") continue;

    const incoming = bindingValue.trim();
    if (!incoming) continue;

    const existing = process.env[key]?.trim();
    if (existing && existing !== incoming) {
      throw new Error(`SEC_ENV_BINDING_CONFLICT: ${key} differs between runtime sources`);
    }

    process.env[key] = incoming;
  }
}

function verifyServerEnvironment(workerEnv: unknown): void {
  // Cloudflare exposes configured values as Worker bindings. Copy only the
  // allowlisted Supabase/deployment strings into process.env so generated
  // server modules inherit the same runtime source without accepting conflicts.
  hydrateServerProcessEnv(workerEnv);

  // A promoted bundle must run against exactly the public environment identity
  // it was built with. This prevents a production browser/server bundle from
  // being started under preview/staging bindings (or the inverse).
  assertSupabaseRuntimeMatchesBuild(BAKED_BUILD_ENV, process.env);

  // Generated server modules read SUPABASE_* aliases directly. Only after the
  // runtime matches the baked build identity may missing server aliases be
  // materialized from the already-validated public values.
  resolveAndHydrateSupabaseServerConfig(process.env);
}

async function getServerEntry(): Promise<ServerEntry> {
  if (!serverEntryPromise) {
    serverEntryPromise = import("@tanstack/react-start/server-entry").then(
      (m) => (m.default ?? m) as ServerEntry,
    );
  }
  return serverEntryPromise;
}

// h3 swallows in-handler throws into a normal 500 Response with body
// {"unhandled":true,"message":"HTTPError"} — try/catch alone never fires for those.
async function normalizeCatastrophicSsrResponse(response: Response): Promise<Response> {
  if (response.status < 500) return response;
  const contentType = response.headers.get("content-type") ?? "";
  if (!contentType.includes("application/json")) return response;

  const body = await response.clone().text();
  if (!body.includes('"unhandled":true') || !body.includes('"message":"HTTPError"')) {
    return response;
  }

  console.error(consumeLastCapturedError() ?? new Error(`h3 swallowed SSR error: ${body}`));
  return new Response(renderErrorPage(), {
    status: 500,
    headers: { "content-type": "text/html; charset=utf-8" },
  });
}

export default {
  async fetch(request: Request, env: unknown, ctx: unknown) {
    try {
      verifyServerEnvironment(env);
      const handler = await getServerEntry();
      const response = await handler.fetch(request, env, ctx);
      return await normalizeCatastrophicSsrResponse(response);
    } catch (error) {
      console.error(error);
      return new Response(renderErrorPage(), {
        status: 500,
        headers: { "content-type": "text/html; charset=utf-8" },
      });
    }
  },
};
