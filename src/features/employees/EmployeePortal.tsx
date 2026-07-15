import { useState } from "react";
import { Wallet, PackageCheck, LogOut } from "lucide-react";
import { Money } from "@/features/shared/Money";
import { supabase } from "@/integrations/supabase/client";
import {
  useEmployeeOrderState,
  useEmployeePortal,
  useRequestCustodySettlement,
} from "./employee-db";
import { EmployeeOrderCard } from "./EmployeeOrderCard";

export function EmployeePortal({ tenantId }: { tenantId: string }) {
  const portal = useEmployeePortal(tenantId, true);
  const updateState = useEmployeeOrderState(tenantId);
  const requestSettlement = useRequestCustodySettlement(tenantId);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const run = async (action: () => Promise<unknown>, message: string) => {
    setError(null);
    setSuccess(null);
    try {
      await action();
      setSuccess(message);
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذّر إتمام العملية");
    }
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };

  if (portal.isLoading) {
    return (
      <div
        dir="rtl"
        className="min-h-screen flex items-center justify-center text-sm text-muted-foreground"
      >
        جاري تحميل طلباتك…
      </div>
    );
  }

  if (portal.error || !portal.data) {
    return (
      <div dir="rtl" className="min-h-screen bg-background flex items-center justify-center p-5">
        <div className="w-full max-w-sm rounded-2xl bg-card border border-border p-5 text-center space-y-3">
          <div className="font-bold">تعذّر فتح حساب الموظف</div>
          <div className="text-xs text-destructive">
            {portal.error?.message ?? "الحساب غير مرتبط بمندوب نشط"}
          </div>
          <button onClick={signOut} className="w-full rounded-xl bg-muted py-3 text-sm font-bold">
            تسجيل الخروج
          </button>
        </div>
      </div>
    );
  }

  const data = portal.data;
  const pendingRequest = data.settlementRequests.find((request) => request.status === "pending");

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground pb-8">
      <header className="sticky top-0 z-20 bg-background/95 backdrop-blur border-b border-border px-4 py-3">
        <div className="max-w-xl mx-auto flex items-center gap-3">
          <div className="flex-1">
            <div className="text-xs text-muted-foreground">{data.tenantName}</div>
            <h1 className="font-bold">مرحبًا، {data.courier.name}</h1>
          </div>
          <button
            onClick={signOut}
            className="w-10 h-10 rounded-xl border border-border flex items-center justify-center"
            aria-label="تسجيل الخروج"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </header>

      <main className="max-w-xl mx-auto px-4 pt-4 space-y-4">
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-card border border-border p-4">
            <div className="flex items-center gap-2 text-xs text-muted-foreground">
              <PackageCheck className="w-4 h-4" />
              طلباتي المعلقة
            </div>
            <div className="text-2xl font-extrabold mt-2">{data.pendingOrders}</div>
          </div>
          <div className="rounded-2xl bg-warn-soft border border-warn/20 p-4">
            <div className="flex items-center gap-2 text-xs text-warn">
              <Wallet className="w-4 h-4" />
              عهدتي
            </div>
            <Money v={data.custody} className="text-xl font-extrabold mt-2" />
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4 space-y-2">
          <div className="font-bold text-sm">التسوية</div>
          <p className="text-xs text-muted-foreground">
            التسليم لا يعني التصفية. المبلغ يبقى عهدة حتى يعتمد صاحب المحل التسوية.
          </p>
          <button
            disabled={requestSettlement.isPending || data.custody <= 0 || !!pendingRequest}
            onClick={() => run(() => requestSettlement.mutateAsync(), "تم إرسال طلب التسوية")}
            className="w-full rounded-xl bg-primary text-primary-foreground py-3 text-sm font-bold disabled:opacity-50"
          >
            {pendingRequest ? "طلب التسوية قيد المراجعة" : "إرسال طلب تسوية"}
          </button>
        </div>

        {error && (
          <div className="rounded-xl bg-destructive/10 text-destructive px-3 py-2 text-xs">
            {error}
          </div>
        )}
        {success && (
          <div className="rounded-xl bg-success-soft text-success px-3 py-2 text-xs">{success}</div>
        )}

        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="font-bold">الطلبات المسندة إليّ</h2>
            <button onClick={() => portal.refetch()} className="text-xs text-primary font-bold">
              تحديث
            </button>
          </div>
          {data.orders.length === 0 && (
            <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">
              لا توجد طلبات مسندة إليك الآن.
            </div>
          )}
          {data.orders.map((order) => (
            <EmployeeOrderCard
              key={order.id}
              order={order}
              busy={updateState.isPending}
              onUpdate={(state, collected) =>
                run(
                  () => updateState.mutateAsync({ orderId: order.id, state, collected }),
                  "تم تحديث حالة الطلب",
                )
              }
            />
          ))}
        </section>
      </main>
    </div>
  );
}
