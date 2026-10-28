import { createFileRoute } from "@tanstack/react-router";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { verifyWebhook } from "@/lib/paddle.server";
import { createSubscriptionWebhookHandler } from "@/lib/subscription-webhook.server";

let supabase: SupabaseClient | null = null;
function getSupabase(): SupabaseClient {
  if (!supabase) {
    supabase = createClient(process.env.SUPABASE_URL!, process.env.SUPABASE_SERVICE_ROLE_KEY!, {
      auth: { persistSession: false, autoRefreshToken: false },
    });
  }
  return supabase;
}

const handleWebhook = createSubscriptionWebhookHandler({
  verify: verifyWebhook,
  persist: async (write, signal) =>
    getSupabase().rpc("apply_subscription_webhook", write).abortSignal(signal),
  report: (reason) => console.error("Payment webhook rejected", { reason }),
});

export const Route = createFileRoute("/api/public/payments/webhook")({
  server: {
    handlers: {
      POST: ({ request }) => handleWebhook(request),
    },
  },
});
