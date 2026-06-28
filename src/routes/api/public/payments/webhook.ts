import { createFileRoute } from "@tanstack/react-router";
import { createClient, type SupabaseClient } from "@supabase/supabase-js";
import { verifyWebhook, EventName, type PaddleEnv } from "@/lib/paddle.server";

let _supabase: SupabaseClient | null = null;
function getSupabase(): SupabaseClient {
  if (!_supabase) {
    _supabase = createClient(
      process.env.SUPABASE_URL!,
      process.env.SUPABASE_SERVICE_ROLE_KEY!,
    );
  }
  return _supabase;
}

async function verifyTenantOwnership(
  supabase: SupabaseClient,
  tenantId: string,
  userId: string,
): Promise<boolean> {
  const { data, error } = await supabase
    .from("tenants")
    .select("id, owner_user_id")
    .eq("id", tenantId)
    .maybeSingle();
  if (error || !data || data.owner_user_id !== userId) {
    console.error("Invalid Paddle tenant/user mapping", {
      tenantId,
      userId,
      foundOwner: data?.owner_user_id ?? null,
      error: error?.message ?? null,
    });
    return false;
  }
  return true;
}

async function handleSubscriptionCreated(data: any, env: PaddleEnv) {
  const { id, customerId, items, status, currentBillingPeriod, customData } = data;
  const userId = customData?.userId;
  const tenantId = customData?.tenantId;
  if (!userId || !tenantId) {
    console.error("Missing userId/tenantId in customData", { userId, tenantId });
    return;
  }
  const item = items?.[0];
  const priceId = item?.price?.importMeta?.externalId;
  const productId = item?.product?.importMeta?.externalId;
  if (!priceId || !productId) {
    console.warn("Skipping subscription: missing importMeta.externalId", {
      rawPriceId: item?.price?.id,
      rawProductId: item?.product?.id,
    });
    return;
  }

  const supabase = getSupabase();
  if (!(await verifyTenantOwnership(supabase, tenantId, userId))) return;


  await supabase.from("subscriptions").upsert(
    {
      tenant_id: tenantId,
      user_id: userId,
      paddle_subscription_id: id,
      paddle_customer_id: customerId,
      product_id: productId,
      price_id: priceId,
      status,
      current_period_start: currentBillingPeriod?.startsAt,
      current_period_end: currentBillingPeriod?.endsAt,
      environment: env,
      updated_at: new Date().toISOString(),
    },
    { onConflict: "paddle_subscription_id" },
  );

  await supabase
    .from("tenants")
    .update({
      subscription_status: status,
      subscription_plan: productId,
      paddle_customer_id: customerId,
      paddle_subscription_id: id,
    })
    .eq("id", tenantId);
}

async function handleSubscriptionUpdated(data: any, env: PaddleEnv) {
  const { id, status, currentBillingPeriod, scheduledChange } = data;
  const supabase = getSupabase();
  await supabase
    .from("subscriptions")
    .update({
      status,
      current_period_start: currentBillingPeriod?.startsAt,
      current_period_end: currentBillingPeriod?.endsAt,
      cancel_at_period_end: scheduledChange?.action === "cancel",
      updated_at: new Date().toISOString(),
    })
    .eq("paddle_subscription_id", id)
    .eq("environment", env);

  await supabase
    .from("tenants")
    .update({ subscription_status: status })
    .eq("paddle_subscription_id", id);
}

async function handleSubscriptionCanceled(data: any, env: PaddleEnv) {
  const supabase = getSupabase();
  await supabase
    .from("subscriptions")
    .update({ status: "canceled", updated_at: new Date().toISOString() })
    .eq("paddle_subscription_id", data.id)
    .eq("environment", env);

  await supabase
    .from("tenants")
    .update({ subscription_status: "canceled" })
    .eq("paddle_subscription_id", data.id);
}

async function handleWebhook(req: Request, env: PaddleEnv) {
  const event = await verifyWebhook(req, env);
  switch (event.eventType) {
    case EventName.SubscriptionCreated:
      await handleSubscriptionCreated(event.data, env);
      break;
    case EventName.SubscriptionUpdated:
      await handleSubscriptionUpdated(event.data, env);
      break;
    case EventName.SubscriptionCanceled:
      await handleSubscriptionCanceled(event.data, env);
      break;
    default:
      console.log("Unhandled event:", event.eventType);
  }
}

export const Route = createFileRoute("/api/public/payments/webhook")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const url = new URL(request.url);
        const env = (url.searchParams.get("env") || "sandbox") as PaddleEnv;
        try {
          await handleWebhook(request, env);
          return Response.json({ received: true });
        } catch (e) {
          console.error("Webhook error:", e);
          return new Response("Webhook error", { status: 400 });
        }
      },
    },
  },
});
