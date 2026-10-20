import { expect, test } from "bun:test";
import { createClient } from "@supabase/supabase-js";
import type { Database } from "../../src/integrations/supabase/types";
import { assertCurrentAccountActive } from "../../src/lib/account-state.server";

function client(fetch: typeof globalThis.fetch) {
  return createClient<Database>("http://127.0.0.1:54321", "oc-app-unit-placeholder", {
    global: { fetch },
    auth: { persistSession: false, autoRefreshToken: false },
  });
}

test("authoritative assertion succeeds with a nullable tenant and one RPC", async () => {
  let calls = 0;
  const supabase = client(async (input, init) => {
    const request = new Request(input, init);
    expect(request.url).toBe("http://127.0.0.1:54321/rest/v1/rpc/current_tenant_id");
    expect(request.method).toBe("POST");
    calls++;
    return Response.json(null);
  });
  await expect(assertCurrentAccountActive(supabase)).resolves.toBeUndefined();
  expect(calls).toBe(1);
});

test("only the exact database lifecycle error is an account denial", async () => {
  for (const [code, message, expected] of [
    ["42501", "account_inactive", "account_inactive"],
    ["42501", "unrelated denial", "account_state_unavailable"],
    ["XX000", "account_inactive", "account_state_unavailable"],
    ["PGRST202", "missing function", "account_state_unavailable"],
  ]) {
    const supabase = client(async () =>
      Response.json({ code, message, details: null, hint: null }, { status: 403 }),
    );
    await expect(assertCurrentAccountActive(supabase)).rejects.toThrow(expected);
  }
});

test("transport rejection cannot permit the operation", async () => {
  const supabase = client(async () => {
    throw new Error("dummy transport failure");
  });
  await expect(assertCurrentAccountActive(supabase)).rejects.toThrow("account_state_unavailable");
});

test("deadline denies even when the transport never settles and aborts it", async () => {
  let signal: AbortSignal | undefined;
  const supabase = client((input, init) => {
    signal = new Request(input, init).signal;
    return new Promise<Response>(() => {});
  });
  const start = performance.now();
  await expect(assertCurrentAccountActive(supabase)).rejects.toThrow("account_state_unavailable");
  expect(signal?.aborted).toBe(true);
  expect(performance.now() - start).toBeGreaterThanOrEqual(2900);
  expect(performance.now() - start).toBeLessThan(4500);
});
