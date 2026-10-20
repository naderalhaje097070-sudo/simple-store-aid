export type MongezzDeployTarget = "local" | "ci" | "preview" | "staging" | "production";

export type SupabaseBuildEnvironment = Partial<
  Record<
    | "MONGEZZ_DEPLOY_TARGET"
    | "VITE_SUPABASE_URL"
    | "SUPABASE_URL"
    | "VITE_SUPABASE_PUBLISHABLE_KEY"
    | "SUPABASE_PUBLISHABLE_KEY"
    | "VITE_SUPABASE_PROJECT_ID"
    | "SUPABASE_PROJECT_ID",
    string
  >
>;

export const APPROVED_PRODUCTION_SUPABASE_TARGET = Object.freeze({
  url: "https://dahzkekdirrngnkcxinv.supabase.co",
  projectId: "dahzkekdirrngnkcxinv",
});

const DEPLOY_TARGETS = new Set<MongezzDeployTarget>([
  "local",
  "ci",
  "preview",
  "staging",
  "production",
]);

const LOOPBACK_HOSTS = new Set(["127.0.0.1", "localhost"]);

function firstNonEmpty(...values: Array<string | undefined>): string | undefined {
  const value = values.find((candidate) => candidate?.trim());
  return value?.trim();
}

function configurationError(message: string): never {
  throw new Error(`SEC_ENV_CONFIG_ERROR: ${message}`);
}

function parseTarget(value: string | undefined): MongezzDeployTarget {
  const target = value?.trim() as MongezzDeployTarget | undefined;
  if (!target) {
    configurationError("MONGEZZ_DEPLOY_TARGET is required");
  }
  if (!DEPLOY_TARGETS.has(target)) {
    configurationError(`unsupported MONGEZZ_DEPLOY_TARGET: ${target}`);
  }
  return target;
}

function parseUrl(value: string): URL {
  try {
    const url = new URL(value);
    if (url.protocol !== "http:" && url.protocol !== "https:") {
      configurationError("Supabase URL must use http or https");
    }
    if (url.username || url.password || url.search || url.hash) {
      configurationError("Supabase URL cannot contain credentials, query, or fragment routing");
    }
    if (url.pathname !== "/") {
      configurationError("Supabase URL must target the project root without a path prefix");
    }
    return url;
  } catch (error) {
    if (error instanceof Error && error.message.startsWith("SEC_ENV_CONFIG_ERROR:")) {
      throw error;
    }
    configurationError("Supabase URL is invalid");
  }
}

function normalizedHostname(url: URL): string {
  return url.hostname.replace(/\.+$/, "").toLowerCase();
}

function canonicalUrl(value: string): string {
  const url = parseUrl(value);
  const port = url.port ? `:${url.port}` : "";
  return `${url.protocol}//${normalizedHostname(url)}${port}`;
}

function validateAliasConsistency(env: SupabaseBuildEnvironment): void {
  const viteUrl = firstNonEmpty(env.VITE_SUPABASE_URL);
  const serverUrl = firstNonEmpty(env.SUPABASE_URL);
  if (viteUrl && serverUrl && canonicalUrl(viteUrl) !== canonicalUrl(serverUrl)) {
    configurationError("VITE_SUPABASE_URL and SUPABASE_URL must target the same project");
  }

  const viteKey = firstNonEmpty(env.VITE_SUPABASE_PUBLISHABLE_KEY);
  const serverKey = firstNonEmpty(env.SUPABASE_PUBLISHABLE_KEY);
  if (viteKey && serverKey && viteKey !== serverKey) {
    configurationError("VITE_SUPABASE_PUBLISHABLE_KEY and SUPABASE_PUBLISHABLE_KEY must match");
  }

  const viteProject = firstNonEmpty(env.VITE_SUPABASE_PROJECT_ID);
  const serverProject = firstNonEmpty(env.SUPABASE_PROJECT_ID);
  if (viteProject && serverProject && viteProject !== serverProject) {
    configurationError("VITE_SUPABASE_PROJECT_ID and SUPABASE_PROJECT_ID must match");
  }
}

function validateRemoteProjectPair(url: URL, projectId: string): void {
  const hostname = normalizedHostname(url);
  if (!hostname.endsWith(".supabase.co")) return;

  const urlProjectId = hostname.slice(0, -".supabase.co".length);
  if (!urlProjectId || urlProjectId !== projectId) {
    configurationError("Supabase URL and project ID do not match");
  }
}

function validatePublicKey(key: string): void {
  if (key.startsWith("sb_secret_")) {
    configurationError("public Supabase key cannot be a secret key");
  }
  // Legacy anon keys are JWTs. Decode only to reject privileged or user tokens;
  // this is a build-time exposure guard, not signature/authentication validation.
  if (key.split(".").length === 3) {
    let role: unknown;
    try {
      const payload = key.split(".")[1].replace(/-/g, "+").replace(/_/g, "/");
      const claims: unknown = JSON.parse(atob(payload));
      if (claims && typeof claims === "object" && "role" in claims) role = claims.role;
    } catch {
      configurationError("public Supabase key has an invalid legacy JWT payload");
    }
    if (role !== "anon") {
      configurationError("public Supabase key must use the legacy anon role");
    }
  }
}

function validateTargetEndpoint(target: MongezzDeployTarget, url: URL, projectId: string): void {
  const hostname = normalizedHostname(url);

  if (target === "local" || target === "ci") {
    if (url.protocol !== "http:" || !LOOPBACK_HOSTS.has(hostname)) {
      configurationError(`${target} target requires an http loopback Supabase endpoint`);
    }
    return;
  }

  if (target === "preview" || target === "staging") {
    const expectedHost = `${projectId}.supabase.co`;
    if (url.protocol !== "https:" || hostname !== expectedHost || url.port) {
      configurationError(
        `${target} target requires a dedicated https Supabase project matching the project ID`,
      );
    }
    return;
  }

  const approvedProductionUrl = canonicalUrl(APPROVED_PRODUCTION_SUPABASE_TARGET.url);
  if (
    canonicalUrl(url.toString()) !== approvedProductionUrl ||
    projectId !== APPROVED_PRODUCTION_SUPABASE_TARGET.projectId
  ) {
    configurationError("production target requires the approved production Supabase host/project");
  }
}

export function resolveSupabaseBuildConfig(env: SupabaseBuildEnvironment) {
  const target = parseTarget(firstNonEmpty(env.MONGEZZ_DEPLOY_TARGET));
  validateAliasConsistency(env);

  const urlValue = firstNonEmpty(env.VITE_SUPABASE_URL, env.SUPABASE_URL);
  const publishableKey = firstNonEmpty(
    env.VITE_SUPABASE_PUBLISHABLE_KEY,
    env.SUPABASE_PUBLISHABLE_KEY,
  );
  const projectId = firstNonEmpty(env.VITE_SUPABASE_PROJECT_ID, env.SUPABASE_PROJECT_ID);

  if (!urlValue || !publishableKey || !projectId) {
    const missing = [
      ...(!urlValue ? ["SUPABASE_URL"] : []),
      ...(!publishableKey ? ["SUPABASE_PUBLISHABLE_KEY"] : []),
      ...(!projectId ? ["SUPABASE_PROJECT_ID"] : []),
    ];
    configurationError(`missing explicit Supabase configuration: ${missing.join(", ")}`);
  }

  validatePublicKey(publishableKey);
  const url = parseUrl(urlValue);
  validateRemoteProjectPair(url, projectId);

  const approvedProductionUrl = new URL(APPROVED_PRODUCTION_SUPABASE_TARGET.url);
  const targetsProductionHost =
    normalizedHostname(url) === normalizedHostname(approvedProductionUrl);
  const targetsProductionProject = projectId === APPROVED_PRODUCTION_SUPABASE_TARGET.projectId;

  if (target !== "production" && (targetsProductionHost || targetsProductionProject)) {
    configurationError(`${target} target cannot use the production Supabase host/project`);
  }

  validateTargetEndpoint(target, url, projectId);

  return {
    url: urlValue,
    publishableKey,
    projectId,
  };
}

// Derive OAuth endpoints only after the existing deployment/endpoint contract passes.
// Production must stay on the approved direct Supabase host; local/ci is loopback.
export function resolveSupabaseMcpIssuer(env: SupabaseBuildEnvironment): string {
  const config = resolveSupabaseBuildConfig(env);
  return `${canonicalUrl(config.url)}/auth/v1`;
}

export function assertSupabaseRuntimeMatchesBuild(
  buildEnv: SupabaseBuildEnvironment,
  runtimeEnv: SupabaseBuildEnvironment,
): void {
  const buildTarget = parseTarget(firstNonEmpty(buildEnv.MONGEZZ_DEPLOY_TARGET));
  const runtimeTarget = parseTarget(firstNonEmpty(runtimeEnv.MONGEZZ_DEPLOY_TARGET));
  const build = resolveSupabaseBuildConfig(buildEnv);
  const runtime = resolveSupabaseBuildConfig(runtimeEnv);

  if (buildTarget !== runtimeTarget) {
    configurationError("runtime deployment target does not match baked build target");
  }

  if (
    canonicalUrl(build.url) !== canonicalUrl(runtime.url) ||
    build.publishableKey !== runtime.publishableKey ||
    build.projectId !== runtime.projectId
  ) {
    configurationError("runtime Supabase configuration does not match baked build configuration");
  }
}

export function resolveAndHydrateSupabaseServerConfig(env: SupabaseBuildEnvironment) {
  const resolved = resolveSupabaseBuildConfig(env);

  if (!firstNonEmpty(env.SUPABASE_URL)) {
    env.SUPABASE_URL = resolved.url;
  }
  if (!firstNonEmpty(env.SUPABASE_PUBLISHABLE_KEY)) {
    env.SUPABASE_PUBLISHABLE_KEY = resolved.publishableKey;
  }
  if (!firstNonEmpty(env.SUPABASE_PROJECT_ID)) {
    env.SUPABASE_PROJECT_ID = resolved.projectId;
  }

  return resolved;
}
