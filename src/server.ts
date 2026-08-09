import "./lib/error-capture";

import { resolveSupabaseBuildConfig } from "../config/supabase-build-config";
import { consumeLastCapturedError } from "./lib/error-capture";
import { renderErrorPage } from "./lib/error-page";

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
  // server modules that use process.env inherit the same validated target.
  // Never replace the process.env object and never accept conflicting sources.
  hydrateServerProcessEnv(workerEnv);

  // Validate before the generated server entry (auth middleware/admin clients)
  // can execute. Missing intent/config, divergent aliases, and
  // non-production→production targeting all fail closed here.
  resolveSupabaseBuildConfig(process.env);
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
