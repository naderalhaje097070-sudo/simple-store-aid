import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/integrations/supabase/types";
type Call = {
  rpc: string;
  payload: Record<string, unknown>;
  status: number | null;
  result?: Record<string, unknown>;
};
declare global {
  interface Window {
    journeyFixture: {
      url: string;
      anon: string;
      token: string;
      refresh: string;
    };
    journeyCalls: Call[];
    journeyDrop: Record<string, number>;
    journeyReady: boolean;
  }
}
const config = window.journeyFixture;
if (config.url !== "http://127.0.0.1:54321") throw Error("isolated target required");
window.journeyCalls = [];
window.journeyDrop = {};
window.journeyReady = false;
export const supabase = createClient<Database>(config.url, config.anon, {
  auth: {
    persistSession: false,
    autoRefreshToken: false,
    detectSessionInUrl: false,
  },
  global: {
    fetch: async (input, init) => {
      const url = new URL(
        typeof input === "string" ? input : input instanceof URL ? input.href : input.url,
      );
      if (url.origin !== config.url) throw Error("external target forbidden");
      const rpc = url.pathname.startsWith("/rest/v1/rpc/") ? url.pathname.split("/").at(-1)! : null;
      const call: Call | undefined = rpc
        ? { rpc, payload: JSON.parse(String(init?.body)), status: null }
        : undefined;
      if (call) window.journeyCalls.push(call);
      const reply = await fetch(input, { ...init, redirect: "error" });
      if (call) {
        call.status = reply.status;
        call.result = await reply.clone().json();
        if (reply.ok && (window.journeyDrop[call.rpc] ?? 0) > 0) {
          window.journeyDrop[call.rpc]--;
          await reply.arrayBuffer();
          throw new TypeError("synthetic hidden committed reply");
        }
      }
      return reply;
    },
  },
});
export const ready = supabase.auth.setSession({
  access_token: config.token,
  refresh_token: config.refresh,
});
