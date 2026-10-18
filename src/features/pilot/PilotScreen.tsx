import { Activity, ShieldCheck, AlertTriangle, Bell, CheckCircle2 } from "lucide-react";
import type {
  Product,
  Customer,
  Courier,
  Invoice,
  Payment,
  Expense,
} from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { Money, fmt } from "@/features/shared/Money";
import { tenantTodayKey } from "@/lib/db";
import { getCourierCustodyForInvoice } from "@/domain/finance/invoice-selectors";

export function PilotScreen(p: AppCtx) {
  const products: Product[] = p.products ?? [];
  const customers: Customer[] = p.customers ?? [];
  const couriers: Courier[] = p.couriers ?? [];
  const invoices: Invoice[] = p.invoices ?? [];
  const payments: Payment[] = p.payments ?? [];
  const expenses: Expense[] = p.expenses ?? [];
  const dayCloses: { closedFor: string }[] = p.dayCloses ?? [];
  const role: string | null = p.myRole ?? null;

  if (role !== "owner") {
    return (
      <>
        <TopBar title="صحة النظام" onBack={p.back} onHome={p.goHome} />
        <div className="px-4 pt-6 text-center text-sm text-muted-foreground">
          هذه الصفحة متاحة لصاحب المحل فقط.
        </div>
      </>
    );
  }

  const now = Date.now();
  const DAY = 24 * 60 * 60 * 1000;
  const tenantTz: string = p.tenantTz ?? "Africa/Tripoli";
  const todayKey = tenantTodayKey(tenantTz);
  const isToday = (iso?: string) =>
    !!iso &&
    tenantTodayKey(tenantTz) ===
      new Intl.DateTimeFormat("en-CA", { timeZone: tenantTz }).format(new Date(iso));

  /* ---- broken rules (must be 0) ---- */
  const paidOverTotal = invoices.filter((i) => i.paid > i.total + 0.001).length;
  const collectedOverTotal = invoices.filter(
    (i) => (i.collectedByCourier ?? 0) > i.total + 0.001,
  ).length;
  const negStock = products.filter((p) => p.stock < 0).length;
  const courierMissingId = invoices.filter(
    (i) => i.delivery === "courier" && !i.courierId && i.courierState !== "returned",
  ).length;
  const debtNoCustomer = invoices.filter(
    (i) => i.status !== "paid" && !i.customerId && i.delivery === "direct",
  ).length;
  const brokenTotal =
    paidOverTotal + collectedOverTotal + negStock + courierMissingId + debtNoCustomer;

  /* ---- warnings ---- */
  const lowStock = products.filter((p) => p.stock > 0 && p.stock <= p.lowAt).length;
  const outStock = products.filter((p) => p.stock === 0).length;
  const oldPendingCourier = invoices.filter(
    (i) =>
      i.delivery === "courier" &&
      (i.courierState === "pending" || i.courierState === "delivered_partial") &&
      now - new Date(i.createdAt).getTime() > 7 * DAY,
  ).length;
  const oldDebts = invoices.filter(
    (i) =>
      i.delivery === "direct" &&
      i.courierState !== "returned" &&
      (i.status === "debt" || i.status === "partial") &&
      now - new Date(i.createdAt).getTime() > 30 * DAY,
  ).length;
  const customersNoPhone = customers.filter((c) => !c.phone).length;
  const unsettledCustody = invoices.reduce((s, i) => s + getCourierCustodyForInvoice(i), 0);
  const lastClose = dayCloses[0]?.closedFor ?? null;
  const daysSinceClose = lastClose
    ? Math.floor((new Date(todayKey).getTime() - new Date(lastClose).getTime()) / DAY)
    : null;

  /* ---- usage metrics ---- */
  const activeProducts = products.filter((p) => p.is_active !== false).length;
  const invoicesToday = invoices.filter((i) => isToday(i.createdAt)).length;
  const paymentsToday = payments.filter((pm) => isToday(pm.createdAt));
  const collectedToday = paymentsToday.reduce((s, pm) => s + pm.amount, 0);
  const expensesToday = expenses
    .filter((e) => isToday(e.createdAt))
    .reduce((s, e) => s + e.amount, 0);
  const lifetimeSales = invoices.reduce((s, i) => s + i.total, 0);
  const lifetimeCollected = payments.reduce((s, pm) => s + pm.amount, 0);

  const HealthBadge = ({ ok }: { ok: boolean }) => (
    <span
      className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold ${
        ok ? "bg-success-soft text-success" : "bg-debt-soft text-debt"
      }`}
    >
      {ok ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
      {ok ? "سليم" : "يحتاج مراجعة"}
    </span>
  );

  const Rule = ({
    label,
    value,
    tone = "debt",
  }: {
    label: string;
    value: number;
    tone?: "debt" | "warn" | "info";
  }) => {
    const ok = value === 0;
    const color = ok
      ? "text-success"
      : tone === "warn"
        ? "text-warn"
        : tone === "info"
          ? "text-info"
          : "text-debt";
    return (
      <div className="flex items-center justify-between py-2.5">
        <span className="text-sm flex-1">{label}</span>
        <span className={`num text-base font-bold ${color}`}>{value}</span>
      </div>
    );
  };

  const Metric = ({
    label,
    value,
    suffix,
  }: {
    label: string;
    value: string | number;
    suffix?: string;
  }) => (
    <div className="bg-card border border-border rounded-2xl p-3">
      <div className="text-[11px] text-muted-foreground mb-1">{label}</div>
      <div className="text-lg font-bold">
        <span className="num">{typeof value === "number" ? fmt(value) : value}</span>
        {suffix && <span className="text-[10px] text-muted-foreground mr-1">{suffix}</span>}
      </div>
    </div>
  );

  return (
    <>
      <TopBar title="صحة النظام" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 pb-8 space-y-4">
        {/* Overall health */}
        <div
          className={`rounded-2xl p-4 border-2 ${
            brokenTotal === 0 ? "bg-success-soft border-success/30" : "bg-debt-soft border-debt/40"
          }`}
        >
          <div className="flex items-center gap-2">
            <ShieldCheck
              className={`w-5 h-5 ${brokenTotal === 0 ? "text-success" : "text-debt"}`}
            />
            <div className="text-sm font-bold flex-1">حالة قواعد البيانات المالية</div>
            <HealthBadge ok={brokenTotal === 0} />
          </div>
          <div className="text-[11px] text-muted-foreground mt-2 leading-relaxed">
            {brokenTotal === 0
              ? "كل القواعد المالية الحرجة سليمة. لا توجد أرقام مكسورة في الفواتير أو المخزون."
              : `تم رصد ${fmt(brokenTotal)} حالة تخالف القواعد المالية. راجع التفاصيل أدناه.`}
          </div>
        </div>

        {/* Broken rules */}
        <div className="bg-card border border-border rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <AlertTriangle className="w-4 h-4 text-debt" />
            <div className="text-sm font-bold">قواعد مكسورة (يجب أن تكون صفر)</div>
          </div>
          <div className="divide-y divide-border">
            <Rule label="فواتير مدفوعها أكبر من إجماليها" value={paidOverTotal} />
            <Rule label="فواتير عهدة محصّلها أكبر من الإجمالي" value={collectedOverTotal} />
            <Rule label="منتجات مخزونها سالب" value={negStock} />
            <Rule label="فواتير توصيل بدون مندوب" value={courierMissingId} />
            <Rule label="فواتير دين بدون عميل مرتبط" value={debtNoCustomer} />
          </div>
        </div>

        {/* Warnings */}
        <div className="bg-card border border-border rounded-2xl p-4">
          <div className="flex items-center gap-2 mb-2">
            <Bell className="w-4 h-4 text-warn" />
            <div className="text-sm font-bold">تنبيهات تشغيلية</div>
          </div>
          <div className="divide-y divide-border">
            <Rule label="منتجات نفدت (أوقف عرضها)" value={outStock} tone="debt" />
            <Rule label="منتجات قاربت النفاد" value={lowStock} tone="warn" />
            <Rule label="طلبات مندوب معلّقة أكثر من ٧ أيام" value={oldPendingCourier} tone="warn" />
            <Rule label="ديون أقدم من ٣٠ يوم" value={oldDebts} tone="warn" />
            <Rule label="عملاء بدون رقم هاتف" value={customersNoPhone} tone="info" />
            <div className="flex items-center justify-between py-2.5">
              <span className="text-sm flex-1">عهدة لم تُصفَّ بعد</span>
              <Money
                v={unsettledCustody}
                className={unsettledCustody > 0 ? "text-warn" : "text-success"}
              />
            </div>
            <div className="flex items-center justify-between py-2.5">
              <span className="text-sm flex-1">أيام منذ آخر إغلاق يوم</span>
              <span
                className={`num text-base font-bold ${
                  daysSinceClose === null
                    ? "text-debt"
                    : daysSinceClose === 0
                      ? "text-success"
                      : daysSinceClose <= 2
                        ? "text-warn"
                        : "text-debt"
                }`}
              >
                {daysSinceClose === null ? "—" : fmt(daysSinceClose)}
              </span>
            </div>
          </div>
        </div>

        {/* Usage metrics */}
        <div>
          <div className="flex items-center gap-2 mb-2 px-1">
            <Activity className="w-4 h-4 text-primary" />
            <div className="text-sm font-bold">مقاييس الاستخدام</div>
          </div>
          <div className="grid grid-cols-2 gap-2">
            <Metric label="فواتير اليوم" value={invoicesToday} />
            <Metric label="عمليات تحصيل اليوم" value={paymentsToday.length} />
            <Metric label="محصّل اليوم" value={collectedToday} suffix="د.ل" />
            <Metric label="مصروفات اليوم" value={expensesToday} suffix="د.ل" />
            <Metric label="منتجات نشطة" value={activeProducts} />
            <Metric label="إجمالي المنتجات" value={products.length} />
            <Metric label="عملاء مسجّلون" value={customers.length} />
            <Metric label="مندوبون نشطون" value={couriers.length} />
            <Metric label="إجمالي الفواتير" value={invoices.length} />
            <Metric label="إغلاقات يومية" value={dayCloses.length} />
            <Metric label="مبيعات منذ البداية" value={lifetimeSales} suffix="د.ل" />
            <Metric label="محصّل منذ البداية" value={lifetimeCollected} suffix="د.ل" />
          </div>
        </div>

        <div className="text-[11px] text-muted-foreground text-center pt-2">
          الأرقام مأخوذة مباشرة من قاعدة بيانات محلّك. تُحدَّث فور أي عملية.
        </div>
      </div>
    </>
  );
}
