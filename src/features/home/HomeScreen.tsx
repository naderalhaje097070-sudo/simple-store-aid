import {
  Plus,
  ChevronLeft,
  AlertTriangle,
  Banknote,
  Wallet,
  Truck,
  ArrowDownCircle,
  CheckCircle2,
  Clock,
  LogOut,
} from "lucide-react";
import type { Customer, Invoice, Period } from "@/features/shared/types";
import type { AppCtx, AppAlert } from "@/features/shared/AppContext";
import { Money, fmt } from "@/features/shared/Money";
import { FinancialReadNotice, FinancialAmount } from "@/features/shared/FinancialReadBoundary";
import { EmptyState } from "@/features/shared/EmptyState";
import { StatusChip } from "@/features/shared/StatusChip";

export function HomeScreen(p: AppCtx) {
  const {
    totals,
    alerts,
    period,
    setPeriod,
    invoices,
    go,
    setOpenInvoiceId,
    setQuickExpenseOpen,
    setMoneyDetailsOpen,
    closedToday,
  } = p;

  const signOut = async () => {
    const { supabase } = await import("@/integrations/supabase/client");
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };
  const recent = invoices.slice(-3).reverse();

  // Status: needs attention if there are debt/custody alerts, otherwise ok
  const status: "good" | "ok" | "attention" = alerts.some((a: AppAlert) => a.tone === "debt")
    ? "attention"
    : alerts.length >= 2
      ? "ok"
      : "good";
  const summaryComplete = Object.values(p.financialReads).every((read) => read.complete);
  const statusMeta = !summaryComplete
    ? { l: "الملخص المالي غير مكتمل", color: "text-warn", bg: "bg-warn-soft", emoji: "⚠️" }
    : {
        good: { l: "وضعك اليوم: جيد", color: "text-success", bg: "bg-success-soft", emoji: "👍" },
        ok: { l: "وضعك اليوم: مقبول", color: "text-warn", bg: "bg-warn-soft", emoji: "🟡" },
        attention: {
          l: "وضعك اليوم: يحتاج انتباه",
          color: "text-debt",
          bg: "bg-debt-soft",
          emoji: "⚠️",
        },
      }[status];

  const periodLabel = period === "day" ? "اليوم" : period === "week" ? "هذا الأسبوع" : "هذا الشهر";

  return (
    <>
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <div>
          <div className="text-2xl font-extrabold text-primary leading-none">منجز</div>
          <div className="text-xs text-muted-foreground mt-1">
            بِع بسرعة — واعرف نهاية اليوم فلوسك وين
          </div>
        </div>
        {closedToday && (
          <span className="px-3 py-1 rounded-full bg-success-soft text-success text-[11px] font-bold">
            تم الإقفال
          </span>
        )}
      </div>

      {/* Primary CTA — sales is the main daily action */}
      <div className="px-4 pb-3">
        <button
          onClick={() => go("sale_quick")}
          className="w-full rounded-2xl bg-primary text-primary-foreground p-4 flex items-center gap-3 shadow-md shadow-primary/20 active:scale-[0.99] transition"
        >
          <div className="w-11 h-11 rounded-full bg-primary-foreground/15 flex items-center justify-center">
            <Plus className="w-6 h-6" />
          </div>
          <div className="flex-1 text-right">
            <div className="text-base font-extrabold">فاتورة جديدة</div>
            <div className="text-[11px] opacity-90">ابدأ البيع — أسرع طريق</div>
          </div>
          <ChevronLeft className="w-5 h-5 opacity-90" />
        </button>
      </div>

      {/* Period switcher */}
      <div className="px-4 pb-3 flex gap-2">
        {[
          { id: "day", l: "اليوم" },
          { id: "week", l: "الأسبوع" },
          { id: "month", l: "الشهر" },
        ].map((x) => (
          <button
            key={x.id}
            onClick={() => setPeriod(x.id as Period)}
            className={`px-4 py-1.5 rounded-full text-xs font-bold ${period === x.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}
          >
            {x.l}
          </button>
        ))}
      </div>

      <div className="px-4 pb-3">
        <FinancialReadNotice
          reads={Object.values(p.financialReads)}
          onRetry={p.retryFinancialReads}
        />
      </div>
      {/* Status / answer card — 3 separated numbers: collected / customer debts / courier custody */}
      <div className="px-4">
        <div className={`rounded-2xl ${statusMeta.bg} p-5 border border-border/50`}>
          <div className={`text-sm font-bold ${statusMeta.color} flex items-center gap-2`}>
            <span>{statusMeta.emoji}</span>
            <span>{statusMeta.l}</span>
            <span className="text-[10px] font-normal text-muted-foreground mr-auto">
              {periodLabel}
            </span>
          </div>
          <div className="mt-4 space-y-3 lg:space-y-0 lg:grid lg:grid-cols-3 lg:gap-3">
            <div className="rounded-xl bg-card/60 p-3">
              <div className="text-[11px] text-muted-foreground">المحصّل فعليًا</div>
              <FinancialAmount
                read={p.financialReads.payments}
                value={totals.collected}
                className="text-2xl text-success font-bold"
              />
              <div className="text-[10px] text-muted-foreground mt-0.5">دخل جيبك فعلًا</div>
            </div>
            <div className="grid grid-cols-2 gap-3 lg:contents">
              <div className="rounded-xl bg-card/60 p-3">
                <div className="text-[11px] text-muted-foreground">ديون العملاء</div>
                <FinancialAmount
                  read={p.financialReads.invoices}
                  value={totals.customerDebts}
                  className="text-lg text-debt font-bold"
                />
                <div className="text-[10px] text-muted-foreground mt-0.5">لم تدخل بعد</div>
              </div>
              <div className="rounded-xl bg-card/60 p-3">
                <div className="text-[11px] text-muted-foreground">عهدة المندوب</div>
                <FinancialAmount
                  read={p.financialReads.invoices}
                  value={totals.unsettledCustody}
                  className="text-lg text-warn font-bold"
                />
                <div className="text-[10px] text-muted-foreground mt-0.5">قيد التسوية</div>
              </div>
            </div>
          </div>
          <button
            onClick={() => setMoneyDetailsOpen(true)}
            className="mt-4 w-full text-center text-xs font-bold text-primary py-2 border-t border-border/50"
          >
            عرض حركة اليوم المالية (الكاش، الديون، العهدة)
          </button>
        </div>
      </div>

      {/* Secondary quick actions */}
      <div className="px-4 mt-4">
        <div className="text-xs font-bold text-muted-foreground mb-2">إجراءات سريعة</div>
        <div className="grid grid-cols-3 gap-2.5">
          {[
            {
              l: "تحصيل دين",
              i: Wallet,
              soft: "bg-debt-soft",
              color: "text-debt",
              on: () => go("debts"),
            },
            {
              l: "تسوية مندوب",
              i: Truck,
              soft: "bg-warn-soft",
              color: "text-warn",
              on: () => go("settlements"),
            },
            {
              l: "إضافة مصروف",
              i: ArrowDownCircle,
              soft: "bg-info-soft",
              color: "text-info",
              on: () => setQuickExpenseOpen(true),
            },
          ].map((a, idx) => (
            <button
              key={idx}
              onClick={a.on}
              className={`rounded-2xl ${a.soft} p-3 flex flex-col items-center gap-1.5 active:scale-[0.97] transition`}
            >
              <div
                className={`w-9 h-9 rounded-full bg-card flex items-center justify-center ${a.color}`}
              >
                <a.i className="w-4 h-4" />
              </div>
              <span className={`text-[11px] font-bold ${a.color}`}>{a.l}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Smart alerts */}
      {alerts.length > 0 && (
        <div className="px-4 mt-5">
          <div className="text-xs font-bold text-muted-foreground mb-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5 text-warn" /> يحتاج انتباهك
          </div>
          <div className="rounded-2xl bg-card border border-border divide-y divide-border overflow-hidden">
            {alerts.map((a: AppAlert) => {
              const tone =
                a.tone === "debt" ? "text-debt" : a.tone === "warn" ? "text-warn" : "text-info";
              return (
                <button
                  key={a.id}
                  onClick={a.onClick}
                  className="w-full text-right px-4 py-3 flex items-center gap-3 hover:bg-muted active:bg-muted"
                >
                  <a.icon className={`w-4 h-4 ${tone}`} />
                  <span className="flex-1 text-sm">{a.text}</span>
                  <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                </button>
              );
            })}
          </div>
        </div>
      )}

      {/* Day close — verification step, not a replacement for selling */}
      <div className="px-4 mt-5">
        <button
          onClick={() => go("day_close")}
          className="w-full rounded-2xl bg-card border-2 border-dashed border-primary/40 p-4 flex items-center gap-3 active:scale-[0.99] transition"
        >
          <div className="w-10 h-10 rounded-full bg-primary-soft text-primary flex items-center justify-center">
            <Banknote className="w-5 h-5" />
          </div>
          <div className="flex-1 text-right">
            <div className="text-sm font-bold">إقفال اليوم</div>
            <div className="text-[11px] text-muted-foreground">
              تحقّق نهاية اليوم — تأكيد أن الأرقام صحيحة
            </div>
          </div>
          <ChevronLeft className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      {/* Recent invoices */}
      <div className="px-4 mt-5">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-bold text-muted-foreground">آخر الفواتير</div>
          <button onClick={() => go("invoices")} className="text-xs text-primary font-bold">
            عرض الكل
          </button>
        </div>
        <div className="space-y-2">
          {recent.length === 0 && p.financialReads.invoices.complete && (
            <EmptyState text="ابدأ يومك — لا مبيعات بعد" />
          )}
          {!p.financialReads.invoices.hasData && (
            <div className="text-sm text-muted-foreground">الفواتير غير متاحة الآن</div>
          )}
          {recent.map((inv: Invoice) => (
            <InvoiceRow
              key={inv.id}
              inv={inv}
              customers={p.customers}
              onOpen={(id) => {
                setOpenInvoiceId(id);
                go("invoice_detail");
              }}
            />
          ))}
        </div>
      </div>

      {/* Clear sign-out from the main menu */}
      <div className="px-4 mt-6 mb-6">
        <button
          onClick={signOut}
          className="w-full rounded-2xl border border-destructive/30 bg-destructive/5 p-4 flex items-center gap-3 text-destructive active:scale-[0.99] transition"
        >
          <div className="w-10 h-10 rounded-full bg-destructive/10 flex items-center justify-center">
            <LogOut className="w-5 h-5" />
          </div>
          <div className="flex-1 text-right">
            <div className="text-sm font-bold">تسجيل الخروج</div>
            <div className="text-[11px] opacity-80">اخرج من حسابك بأمان</div>
          </div>
          <ChevronLeft className="w-4 h-4 opacity-70" />
        </button>
      </div>
    </>
  );
}

export function InvoiceRow({
  inv,
  customers,
  onOpen,
}: {
  inv: Invoice;
  customers: Customer[];
  onOpen: (id: string) => void;
}) {
  const cust = customers.find((c) => c.id === inv.customerId);
  const remaining = inv.total - inv.paid;
  return (
    <button
      onClick={() => onOpen(inv.id)}
      className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3 active:scale-[0.99]"
    >
      <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground">
        #{inv.number.slice(-2)}
      </div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm">#{inv.number}</span>
          {inv.status === "paid" && (
            <StatusChip kind="paid" icon={<CheckCircle2 className="w-3 h-3" />}>
              مدفوع
            </StatusChip>
          )}
          {inv.status === "partial" && (
            <StatusChip kind="partial" icon={<Clock className="w-3 h-3" />}>
              جزئي
            </StatusChip>
          )}
          {inv.status === "debt" && (
            <StatusChip kind="debt" icon={<AlertTriangle className="w-3 h-3" />}>
              دين
            </StatusChip>
          )}
        </div>
        <div className="text-xs text-muted-foreground mt-0.5 truncate">
          {inv.status === "paid" && !cust ? "بدون عميل" : (cust?.name ?? "—")} · {inv.time}
          {inv.delivery === "courier" && " · توصيل"}
        </div>
      </div>
      <div className="text-left">
        <Money v={inv.total} className="text-sm" />
        {remaining > 0 && (
          <div className="text-xs text-debt mt-0.5">
            متبقي <span className="num">{fmt(remaining)}</span>
          </div>
        )}
      </div>
    </button>
  );
}
