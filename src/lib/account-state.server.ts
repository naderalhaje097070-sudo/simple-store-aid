import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database } from "@/integrations/supabase/types";

const VERIFICATION_TIMEOUT_MS = 3000;

export async function assertCurrentAccountActive(
  supabase: SupabaseClient<Database>,
): Promise<void> {
  const controller = new AbortController();
  let timer: ReturnType<typeof setTimeout> | undefined;
  let result: { error: { code: string; message: string } | null };
  try {
    result = await Promise.race([
      // This RPC asserts live activity before returning a nullable tenant. Its
      // value is deliberately unused: price lookup does not require a store.
      supabase.rpc("current_tenant_id").abortSignal(controller.signal),
      new Promise<never>((_resolve, reject) => {
        timer = setTimeout(() => {
          controller.abort();
          reject(new Error("account_state_unavailable"));
        }, VERIFICATION_TIMEOUT_MS);
      }),
    ]);
  } catch {
    throw new Error("account_state_unavailable");
  } finally {
    if (timer !== undefined) clearTimeout(timer);
  }

  if (result.error) {
    if (result.error.code === "42501" && result.error.message === "account_inactive") {
      throw new Error("account_inactive");
    }
    throw new Error("account_state_unavailable");
  }
}
