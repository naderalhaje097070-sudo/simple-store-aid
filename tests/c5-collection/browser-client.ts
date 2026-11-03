import { createClient } from "@supabase/supabase-js";
import type { Database } from "@/integrations/supabase/types";
declare global {
  interface Window {
    collectionFixture: {
      url: string;
      anon: string;
      tenant: string;
      order: string;
      token: string;
      refresh: string;
    };
    collectionCalls: unknown[];
    collectionDrop: boolean;
    collectionReplies: number[];
  }
}
const config = window.collectionFixture;
if (config.url !== "http://127.0.0.1:54321") throw Error("isolated target required");
window.collectionCalls = [];
window.collectionReplies = [];
window.collectionDrop = true;
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
      const collection = url.pathname === "/rest/v1/rpc/collect_order_debt_idempotent";
      if (collection) window.collectionCalls.push(JSON.parse(String(init?.body)));
      const reply = await fetch(input, { ...init, redirect: "error" });
      if (collection) {
        window.collectionReplies.push(reply.status);
        if (reply.ok && window.collectionDrop) {
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
