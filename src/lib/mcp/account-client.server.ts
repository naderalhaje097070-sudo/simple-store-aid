import type { ToolContext } from "@lovable.dev/mcp-js";
import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/integrations/supabase/types";
import { assertCurrentAccountActive } from "../account-state.server";

function denied(text: string) {
  return {
    ok: false as const,
    result: { content: [{ type: "text" as const, text }], isError: true },
  };
}

export async function authorizeMcpTableRead(ctx: ToolContext) {
  if (!ctx.isAuthenticated()) return denied("Not authenticated");

  try {
    const supabase = createClient<Database>(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_PUBLISHABLE_KEY!,
      {
        global: { headers: { Authorization: `Bearer ${ctx.getToken()}` } },
        auth: { persistSession: false, autoRefreshToken: false },
      },
    );
    // Use the same user-scoped client for the live account check and the RLS-protected read.
    await assertCurrentAccountActive(supabase);
    return { ok: true as const, supabase };
  } catch (error) {
    return denied(
      error instanceof Error && error.message === "account_inactive"
        ? "account_inactive"
        : "account_state_unavailable",
    );
  }
}
