import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import { getPaddleEnvironment } from "@/lib/paddle";
import { usePaddleCheckout } from "@/hooks/usePaddleCheckout";
import { useTenantId, useTenant } from "@/lib/db";
import { PaymentTestModeBanner } from "@/components/PaymentTestModeBanner";
import { ArrowRight, CheckCircle2, Sparkles, Crown, Calendar } from "lucide-react";

export const Route = createFileRoute("/_authenticated/billing")({
  head: () => ({
    meta: [
      { title: "الاشتراك والباقات — منجز" },
      { name: "description", content: "اختر باقة منجز المناسبة لمحلك واشترك بأمان." },
    ],
  }),
  component: BillingPage,
});

type Plan = {
  priceId: string;
  productId: string;
  name: string;
  price: string;
  cycle: string;
  features: string[];
  highlight?: boolean;
  badge?: string;
  icon: React.ReactNode;
};

const PLANS: Plan[] = [
  {
    priceId: "mongezz_starter_monthly",
    productId: "mongezz_starter",
    name: "Starter",
    price: "$9",
    cycle: "شهرياً",
    icon: <Sparkles className="w-5 h-5" />,
    features: [
      "فرع واحد",
      "حتى 500 فاتورة شهرياً",
      "إدارة العملاء والمنتجات",
      "تقارير يومية أساسية",
    ],
  },
  {
    priceId: "mongezz_pro_monthly",
    productId: "mongezz_pro",
    name: "Pro",
    price: "$19",
    cycle: "شهرياً",
    highlight: true,
    badge: "الأكثر شعبية",
    icon: <Crown className="w-5 h-5" />,
    features: [
      "فروع غير محدودة",
      "فواتير غير محدودة",
      "إدارة المناديب والعهدة",
      "تقارير مالية متقدمة",
      "تصدير فواتير PDF",
    ],
  },
  {
    priceId: "mongezz_pro_yearly",
    productId: "mongezz_pro",
    name: "Pro سنوي",
    price: "$190",
    cycle: "سنوياً",
    badge: "وفّر شهرين",
    icon: <Calendar className="w-5 h-5" />,
    features: [
      "كل مميزات Pro",
      "دفعة واحدة سنوياً",
      "خصم ما يعادل شهرين",
      "أولوية في الدعم",
    ],
  },
];

function BillingPage() {
  const tenantId = useTenantId();
  const { data: tenant } = useTenant(tenantId);
  const env = getPaddleEnvironment();
  const { openCheckout, loading } = usePaddleCheckout();
  const [email, setEmail] = useState<string | undefined>();
  const [userId, setUserId] = useState<string | undefined>();
  const [success, setSuccess] = useState(false);

  useEffect(() => {
    supabase.auth.getUser().then(({ data }) => {
      setEmail(data.user?.email ?? undefined);
      setUserId(data.user?.id);
    });
    const url = new URL(window.location.href);
    if (url.searchParams.get("checkout") === "success") setSuccess(true);
  }, []);

  const sub = useQuery({
    queryKey: ["subscription", tenantId, env],
    enabled: !!tenantId,
    queryFn: async () => {
      const { data, error } = await supabase
        .from("subscriptions")
        .select("*")
        .eq("tenant_id", tenantId!)
        .eq("environment", env)
        .order("created_at", { ascending: false })
        .limit(1)
        .maybeSingle();
      if (error) throw error;
      return data;
    },
  });

  const trialEndsAt = (tenant as any)?.trial_ends_at as string | undefined;
  const subStatus = sub.data?.status as string | undefined;
  const isActive = subStatus === "active" || subStatus === "trialing";

  const handleSubscribe = (plan: Plan) => {
    if (!userId || !tenantId) return;
    openCheckout({
      priceId: plan.priceId,
      customerEmail: email,
      customData: { userId, tenantId },
    });
  };

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground">
      <PaymentTestModeBanner />

      <header className="border-b border-border bg-card">
        <div className="max-w-5xl mx-auto px-4 py-4 flex items-center gap-3">
          <Link to="/app" className="rounded-lg p-2 hover:bg-accent">
            <ArrowRight className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-lg font-bold">الاشتراك والباقات</h1>
            <p className="text-xs text-muted-foreground">اختر الباقة المناسبة لمحلك</p>
          </div>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-6 space-y-6">
        {success && (
          <div className="rounded-2xl border border-green-500/40 bg-green-500/10 p-4 flex items-center gap-3">
            <CheckCircle2 className="w-6 h-6 text-green-600 shrink-0" />
            <div>
              <div className="font-bold text-sm">تم الاشتراك بنجاح!</div>
              <div className="text-xs text-muted-foreground mt-1">
                قد تستغرق العملية بضع ثوانٍ لتظهر هنا. حدّث الصفحة بعد لحظات.
              </div>
            </div>
          </div>
        )}

        {/* Current status */}
        <section className="rounded-2xl border border-border bg-card p-5">
          <div className="text-sm text-muted-foreground mb-2">حالة الاشتراك الحالية</div>
          {isActive && sub.data ? (
            <div>
              <div className="text-xl font-bold flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-green-600" />
                مشترك في {labelFor(sub.data.product_id as string)}
              </div>
              <div className="text-xs text-muted-foreground mt-2">
                {sub.data.current_period_end &&
                  `يتجدد في ${new Date(sub.data.current_period_end as string).toLocaleDateString("ar-LY")}`}
                {sub.data.cancel_at_period_end && " — سيتم الإلغاء عند نهاية الفترة"}
              </div>
            </div>
          ) : trialEndsAt && new Date(trialEndsAt) > new Date() ? (
            <div>
              <div className="text-xl font-bold">في الفترة التجريبية المجانية</div>
              <div className="text-xs text-muted-foreground mt-2">
                تنتهي التجربة في {new Date(trialEndsAt).toLocaleDateString("ar-LY")} — اشترك قبلها لتستمر بدون انقطاع.
              </div>
            </div>
          ) : (
            <div>
              <div className="text-xl font-bold text-orange-600">انتهت التجربة المجانية</div>
              <div className="text-xs text-muted-foreground mt-2">
                اختر باقة لمتابعة استخدام منجز.
              </div>
            </div>
          )}
        </section>

        {/* Plans */}
        <section className="grid gap-4 md:grid-cols-3">
          {PLANS.map((plan) => (
            <div
              key={plan.priceId}
              className={`rounded-2xl border p-5 flex flex-col ${
                plan.highlight
                  ? "border-primary bg-primary/5 shadow-lg"
                  : "border-border bg-card"
              }`}
            >
              {plan.badge && (
                <div className="self-start text-[10px] font-bold bg-primary text-primary-foreground rounded-full px-2 py-0.5 mb-2">
                  {plan.badge}
                </div>
              )}
              <div className="flex items-center gap-2 text-sm font-bold mb-1">
                {plan.icon}
                {plan.name}
              </div>
              <div className="flex items-baseline gap-1 mt-2">
                <span className="text-3xl font-bold">{plan.price}</span>
                <span className="text-xs text-muted-foreground">/ {plan.cycle}</span>
              </div>
              <ul className="mt-4 space-y-2 text-sm flex-1">
                {plan.features.map((f) => (
                  <li key={f} className="flex items-start gap-2">
                    <CheckCircle2 className="w-4 h-4 text-green-600 shrink-0 mt-0.5" />
                    <span>{f}</span>
                  </li>
                ))}
              </ul>
              <button
                onClick={() => handleSubscribe(plan)}
                disabled={loading || !userId}
                className={`mt-5 w-full rounded-xl py-3 text-sm font-bold transition ${
                  plan.highlight
                    ? "bg-primary text-primary-foreground hover:opacity-90"
                    : "bg-foreground/90 text-background hover:opacity-90"
                } disabled:opacity-50`}
              >
                {loading ? "جارٍ الفتح..." : isActive ? "تغيير إلى هذه الباقة" : "اشترك الآن"}
              </button>
            </div>
          ))}
        </section>

        <p className="text-center text-xs text-muted-foreground">
          الدفع آمن ومُدار من شريكنا المالي. يمكنك الإلغاء في أي وقت.
        </p>
      </main>
    </div>
  );
}

function labelFor(productId: string): string {
  if (productId === "mongezz_pro") return "باقة Pro";
  if (productId === "mongezz_starter") return "باقة Starter";
  return productId;
}
