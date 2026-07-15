export type SupabaseBuildEnvironment = Partial<
  Record<
    | "VITE_SUPABASE_URL"
    | "SUPABASE_URL"
    | "VITE_SUPABASE_PUBLISHABLE_KEY"
    | "SUPABASE_PUBLISHABLE_KEY"
    | "VITE_SUPABASE_PROJECT_ID"
    | "SUPABASE_PROJECT_ID",
    string
  >
>;

export const PRODUCTION_SUPABASE_FALLBACK = Object.freeze({
  url: "https://dahzkekdirrngnkcxinv.supabase.co",
  publishableKey:
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImRhaHprZWtkaXJybmdua2N4aW52Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODI0NzQ5NzksImV4cCI6MjA5ODA1MDk3OX0.9xeU6o1E49rZemO5uwOsnGuYWW1n5MfKJmVlbU6UEvQ",
  projectId: "dahzkekdirrngnkcxinv",
});

function firstNonEmpty(...values: Array<string | undefined>): string | undefined {
  const value = values.find((candidate) => candidate?.trim());
  return value?.trim();
}

export function resolveSupabaseBuildConfig(env: SupabaseBuildEnvironment) {
  return {
    url: firstNonEmpty(env.VITE_SUPABASE_URL, env.SUPABASE_URL) ?? PRODUCTION_SUPABASE_FALLBACK.url,
    publishableKey:
      firstNonEmpty(env.VITE_SUPABASE_PUBLISHABLE_KEY, env.SUPABASE_PUBLISHABLE_KEY) ??
      PRODUCTION_SUPABASE_FALLBACK.publishableKey,
    projectId:
      firstNonEmpty(env.VITE_SUPABASE_PROJECT_ID, env.SUPABASE_PROJECT_ID) ??
      PRODUCTION_SUPABASE_FALLBACK.projectId,
  };
}
