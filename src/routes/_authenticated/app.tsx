import { createFileRoute, useRouter } from "@tanstack/react-router";
import { useMemo, useState, useEffect, useRef } from "react";
import {
  Home, ReceiptText, Plus, Boxes, Store, Bell, Menu,
  Search, X, Minus, ChevronLeft, AlertTriangle, CheckCircle2,
  Wallet, Banknote, Truck, Users, Settings as SettingsIcon,
  TrendingUp, Phone, MessageCircle, Trash2, ArrowLeft, Info,
  Clock, PackageX, ArrowDownCircle, ArrowUpCircle, CircleDollarSign,
  Activity, ShieldCheck, FileDown, Printer, Crown,
} from "lucide-react";
import { downloadInvoicePdf, printInvoice, ensureFont as ensureInvoiceFont, type InvoicePdfData } from "@/lib/invoice-pdf";
import {
  useTenantId, useProducts, useCustomers, useAddCustomer, useAddProduct, useUpdateProductActive, useUpdateProduct, useDeleteProduct,
  useCouriers, useAddCourier, useInvoices, usePayments, useExpenses,
  useAddExpense, useCreateSale, useDeleteInvoice, useCollectDebt, useSettleCourier, useUpdateCourierState,
  useDayCloses, useCloseDay, useTenant, useUpdateTenantName, useUpdateTenantBusinessType, useMyRole,
  tenantTodayKey,
} from "@/lib/db";
import { BUSINESS_TYPES, businessTypeLabel } from "@/lib/business-types";
import { DateRangeFilter, useDateRange, inRange } from "@/components/DateRangeFilter";
import {
  getCourierCustodyForInvoice,
  getCustomerDebtForInvoice,
  getInvoiceItemCost,
  getInvoiceItemMargin,
  getInvoiceRemainingAmount,
  getPendingCourierValueForInvoice,
} from "@/domain/finance/invoice-selectors";

function AppErrorBoundary({ error, reset }: { error: Error; reset: () => void }) {
  const router = useRouter();
  console.error("[Mongezz /app error]", error);
  return (
    <div dir="rtl" className="min-h-screen flex items-center justify-center bg-background text-foreground p-6">
      <div className="max-w-sm w-full bg-card border border-border rounded-2xl p-5 text-center space-y-3">
        <div className="text-2xl">⚠️</div>
        <div className="font-bold text-base">حدث خطأ غير متوقع</div>
        <div className="text-xs text-muted-foreground">حدِّث الصفحة أو اضغط إعادة المحاولة.</div>
        <button
          onClick={() => { router.invalidate(); reset(); }}
          className="w-full rounded-xl bg-primary text-primary-foreground py-3 text-sm font-bold"
        >إعادة المحاولة</button>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/_authenticated/app")({
  head: () => ({
    meta: [
      { title: "منجز — دفتر المحل الذكي" },
      { name: "description", content: "تطبيق منجز لإدارة المحل الصغير: مبيعات، ديون، عهدة المندوب، ومصروفات بلغة بسيطة." },
    ],
  }),
  component: MongezzApp,
  errorComponent: AppErrorBoundary,
});

/* Types & shared components moved to src/features/shared/ (R1) */
import type { Product, Customer, Courier, InvoiceItem, Invoice, Expense, Payment, Screen, Period } from "@/features/shared/types";
import { StatusChip } from "@/features/shared/StatusChip";
import { EmptyState } from "@/features/shared/EmptyState";
import { Sheet } from "@/features/shared/Sheet";
import { Toast } from "@/features/shared/Toast";
import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { BottomNav } from "@/features/layout/BottomNav";
import { DesktopSidebar } from "@/features/layout/DesktopSidebar";
import { Money, fmt } from "@/features/shared/Money";
import { HomeScreen } from "@/features/home/HomeScreen";
import { InventoryScreen } from "@/features/inventory/InventoryScreen";

import { CustomersScreen } from "@/features/customers/CustomersScreen";
import { SettingsScreen } from "@/features/settings/SettingsScreen";
import { ShopHubScreen } from "@/features/shop/ShopHubScreen";
import { ProfitScreen } from "@/features/reports/ProfitScreen";
import { CollectedScreen } from "@/features/reports/CollectedScreen";
import { PilotScreen } from "@/features/pilot/PilotScreen";
import { CouriersScreen } from "@/features/couriers/CouriersScreen";
import { InvoiceDetailScreen } from "@/features/invoices/InvoiceDetailScreen";
import { InvoicesScreen } from "@/features/invoices/InvoicesScreen";


// Phase 3: كل البيانات تأتي من قاعدة بيانات المحل عبر hooks في src/lib/db.ts

/* HELPERS: Money + fmt moved to src/features/shared/Money.tsx (R4a) */

/* ============================== MAIN APP ============================== */


function MongezzApp() {
  const { data: tenantId } = useTenantId();
  const { data: dbProducts } = useProducts(tenantId);
  const { data: dbCustomers } = useCustomers(tenantId);
  const { data: dbCouriers } = useCouriers(tenantId);
  const { data: dbInvoices } = useInvoices(tenantId);
  const { data: dbPayments } = usePayments(tenantId);
  const { data: dbExpenses } = useExpenses(tenantId);
  const addCustomerMut = useAddCustomer(tenantId);
  const addProductMut = useAddProduct(tenantId);
  const toggleActiveMut = useUpdateProductActive(tenantId);
  const updateProductMut = useUpdateProduct(tenantId);
  const deleteProductMut = useDeleteProduct(tenantId);
  const addCourierMut = useAddCourier(tenantId);
  const addExpenseMut = useAddExpense(tenantId);
  const createSaleMut = useCreateSale(tenantId);
  const deleteInvoiceMut = useDeleteInvoice(tenantId);
  const collectDebtMut = useCollectDebt(tenantId);
  const settleCourierMut = useSettleCourier(tenantId);
  const updateCourierStateMut = useUpdateCourierState(tenantId);
  const { data: dbDayCloses } = useDayCloses(tenantId);
  const closeDayMut = useCloseDay(tenantId);
  const { data: myRole } = useMyRole(tenantId);
  const { data: tenantSettings } = useTenant(tenantId);
  const tenantTz = tenantSettings?.timezone ?? "Africa/Tripoli";

  const products = (dbProducts ?? []) as unknown as Product[];
  const customers = (dbCustomers ?? []) as Customer[];
  const couriers = (dbCouriers ?? []) as Courier[];
  const invoices = (dbInvoices ?? []) as unknown as Invoice[];
  const payments = (dbPayments ?? []) as unknown as Payment[];
  const expenses = (dbExpenses ?? []) as Expense[];
  const setCustomers = (_: any) => {};

  const [screen, setScreen] = useState<Screen>("home");
  const [stack, setStack] = useState<Screen[]>([]);
  const [openInvoiceId, setOpenInvoiceId] = useState<string | null>(null);
  const [openCustomerId, setOpenCustomerId] = useState<string | null>(null);
  const [openCourierId, setOpenCourierId] = useState<string | null>(null);
  const [lastCreatedInvoiceId, setLastCreatedInvoiceId] = useState<string | null>(null);
  const [lastSaleSummary, setLastSaleSummary] = useState<{ total: number; paid: number; profit: number; elapsedMs?: number } | null>(null);

  const [period, setPeriod] = useState<Period>("day");
  
  const [quickExpenseOpen, setQuickExpenseOpen] = useState(false);
  const [moneyDetailsOpen, setMoneyDetailsOpen] = useState(false);
  const todayKey = tenantTodayKey(tenantTz);
  const dayCloses = dbDayCloses ?? [];
  const closedToday = dayCloses.some(d => d.closedFor === todayKey);
  const setClosedToday = (_: boolean) => {};
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (t: string) => { setToast(t); setTimeout(() => setToast(null), 2000); };

  const go = (s: Screen) => { setStack(prev => [...prev, screen]); setScreen(s); };
  const back = () => { setStack(prev => { const c = [...prev]; const p = c.pop(); if (p) setScreen(p); return c; }); };

  /* Period window — actual date filtering against DB rows.
     For "day" we use the tenant's timezone so it matches close_day RPC.
     For week/month we still use a rolling window from local midnight, which
     is acceptable for trend cards (not used by close_day). */
  const tzDateKey = (iso?: string) =>
    iso ? new Intl.DateTimeFormat("en-CA", { timeZone: tenantTz }).format(new Date(iso)) : "";
  const periodStart = useMemo(() => {
    const d = new Date();
    if (period === "day") return 0; // unused for day; filtering goes through tzDateKey
    const days = period === "week" ? 7 : 30;
    d.setDate(d.getDate() - days + 1);
    d.setHours(0, 0, 0, 0);
    return d.getTime();
  }, [period]);

  const inPeriod = (iso?: string) => {
    if (!iso) return false;
    if (period === "day") return tzDateKey(iso) === todayKey;
    return new Date(iso).getTime() >= periodStart;
  };


  /* Derived totals — flows filtered by period, stocks reflect current balances */
  const totals = useMemo(() => {
    const invP = invoices.filter(i => inPeriod(i.createdAt));
    const payP = payments.filter(p => inPeriod(p.createdAt));
    const expP = expenses.filter(e => inPeriod(e.createdAt));

    const sales = invP.reduce((s, i) => s + i.total, 0);
    const cogs = invP.reduce((s, i) => s + i.items.reduce((a, it) => a + getInvoiceItemCost(it), 0), 0);
    const expenseTotal = expP.reduce((s, e) => s + e.amount, 0);
    const collected = payP.reduce((s, pm) => s + pm.amount, 0);
    const grossProfit = sales - cogs;
    const netProfit = grossProfit - expenseTotal;
    // Realized profit per-order (matches close_day RPC formula):
    // for each invoice take (price-cost)*qty * min(paid/total, 1)
    const realizedCogs = invP.reduce((s, i) => {
      const ratio = i.total > 0 ? Math.min(1, i.paid / i.total) : 0;
      return s + i.items.reduce((a, it) => a + getInvoiceItemCost(it) * ratio, 0);
    }, 0);
    const realizedRevenue = invP.reduce((s, i) => {
      const ratio = i.total > 0 ? Math.min(1, i.paid / i.total) : 0;
      return s + i.total * ratio;
    }, 0);
    const realizedProfit = realizedRevenue - realizedCogs - expenseTotal;
    const cashToday = collected - expenseTotal;

    // Stocks — current balances across ALL invoices (not period-bound)
    const customerDebts = invoices.reduce((s, i) => s + getCustomerDebtForInvoice(i), 0);

    const unsettledCustody = invoices.reduce((s, i) => s + getCourierCustodyForInvoice(i), 0);

    const inTransit = invoices.reduce((s, i) => s + getPendingCourierValueForInvoice(i), 0);

    const openOnYou = customerDebts + unsettledCustody;

    return { sales, cogs, collected, expenseTotal, grossProfit, netProfit, realizedProfit, realizedCogs, customerDebts, unsettledCustody, inTransit, cashToday, openOnYou };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoices, expenses, payments, periodStart]);

  const scaledTotals = totals; // backward-compat alias; period filtering is now real

  const lowStock = products.filter(p => p.stock > 0 && p.stock <= p.lowAt).length;
  const outStock = products.filter(p => p.stock === 0).length;

  // Smart alerts
  const now = Date.now();
  const THIRTY_DAYS = 30 * 24 * 60 * 60 * 1000;
  const alerts = useMemo(() => {
    const list: { id: string; tone: "warn" | "debt" | "info"; icon: any; text: string; onClick: () => void }[] = [];
    if (lowStock > 0) list.push({ id: "low", tone: "warn", icon: AlertTriangle, text: `${lowStock} منتجات قاربت النفاد`, onClick: () => go("inventory") });
    if (outStock > 0) list.push({ id: "out", tone: "debt", icon: PackageX, text: `${outStock} منتجات نفدت — أوقف عرضها`, onClick: () => go("inventory") });
    if (totals.unsettledCustody > 0 && couriers.length > 0) list.push({ id: "custody", tone: "warn", icon: Truck, text: `عهدة عند المندوب ${fmt(totals.unsettledCustody)} د.ل لم تُصفَّ`, onClick: () => go("settlements") });
    const oldDebts = invoices.filter(i =>
      i.delivery === "direct" &&
      i.courierState !== "returned" &&
      (i.status === "debt" || i.status === "partial") &&
      now - new Date(i.createdAt).getTime() > THIRTY_DAYS
    ).length;
    const allDebts = invoices.filter(i => i.delivery === "direct" && i.courierState !== "returned" && (i.status === "debt" || i.status === "partial")).length;
    if (oldDebts > 0) list.push({ id: "olddebt", tone: "debt", icon: CircleDollarSign, text: `${oldDebts} فواتير دين أقدم من ٣٠ يوم`, onClick: () => go("debts") });
    else if (allDebts > 0) list.push({ id: "debt", tone: "debt", icon: CircleDollarSign, text: `${allDebts} فواتير دين بحاجة تحصيل`, onClick: () => go("debts") });
    const pendingCourier = invoices.filter(i => i.delivery === "courier" && (i.courierState === "pending" || i.courierState === "delivered_partial")).length;
    if (pendingCourier > 0) list.push({ id: "pending", tone: "info", icon: Clock, text: `${pendingCourier} طلبات توصيل غير مكتملة`, onClick: () => go("courier_custody") });
    if (totals.collected > 0 && totals.expenseTotal / totals.collected > 0.3) list.push({ id: "exp", tone: "warn", icon: ArrowDownCircle, text: "مصروفات الفترة مرتفعة نسبيًا", onClick: () => go("expenses") });
    return list;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoices, totals.unsettledCustody, totals.collected, totals.expenseTotal, lowStock, outStock]);


  const ctx: AppCtx = {
    products,
    customers,
    setCustomers,
    couriers,
    invoices,
    expenses,
    payments,
    myRole,
    totals: scaledTotals, rawTotals: totals, lowStock, outStock,
    period, setPeriod, alerts, closedToday, setClosedToday, dayCloses,
    tenantId, tenantTz, tenantSettings,
    closeDayAsync: (input: Parameters<ReturnType<typeof useCloseDay>["mutateAsync"]>[0]) => closeDayMut.mutateAsync(input),
    go, back, setOpenInvoiceId, openInvoiceId, setOpenCustomerId, openCustomerId, setOpenCourierId, openCourierId,
    setLastSaleSummary, lastSaleSummary, setScreen,
    goHome: () => { setStack([]); setScreen("home"); },
    lastCreatedInvoiceId, setLastCreatedInvoiceId,
    setQuickExpenseOpen, setMoneyDetailsOpen, showToast,
    addCustomerAsync: (input: { name: string; phone?: string }) => addCustomerMut.mutateAsync(input),
    addProductAsync: (input: { name: string; price: number; cost: number; stock: number; is_discount: boolean }) => addProductMut.mutateAsync(input),
    toggleProductActiveAsync: (input: { id: string; is_active: boolean }) => toggleActiveMut.mutateAsync(input),
    updateProductAsync: (input: { id: string; name: string; price: number; cost: number; stock: number; is_discount: boolean }) => updateProductMut.mutateAsync(input),
    deleteProductAsync: (productId: string) => deleteProductMut.mutateAsync(productId),
    addCourierAsync: (input: { name: string; phone?: string }) => addCourierMut.mutateAsync(input),
    addExpenseAsync: (input: { type: string; amount: number; method: "cash" | "transfer"; note?: string }) => addExpenseMut.mutateAsync(input),
    createSaleAsync: (input: Parameters<ReturnType<typeof useCreateSale>["mutateAsync"]>[0]) => createSaleMut.mutateAsync(input),
    deleteInvoiceAsync: (orderId: string) => deleteInvoiceMut.mutateAsync(orderId),
    collectDebtAsync: (input: { orderId: string; customerId?: string; amount: number; method: "cash" | "transfer" }) => collectDebtMut.mutateAsync(input),
    settleCourierAsync: (input: { courierId: string; orders: { id: string; customerId?: string; collected?: number }[] }) => settleCourierMut.mutateAsync(input),
    updateCourierStateAsync: (input: { orderId: string; state: "delivered_full" | "delivered_partial" | "delivered_none" | "returned" | "pending"; collected?: number }) => updateCourierStateMut.mutateAsync(input),
  };

  const hideNav = ["sale", "sale_quick", "sale_success", "day_close"].includes(screen);

  const screenTitle: Record<string, string> = {
    home: "الرئيسية", invoices: "الفواتير", invoice_detail: "تفاصيل الفاتورة",
    inventory: "المخزون", shop: "المحل", profit: "الربح",
    collected: "المحصّل فعليًا", debts: "الديون", debt_customer: "ديون العميل",
    courier_custody: "عهدة المندوب", settlements: "التسويات", expenses: "المصروفات",
    customers: "العملاء", couriers: "المندوبون", settings: "الإعدادات",
    sale: "فاتورة جديدة", sale_quick: "بيع سريع", sale_success: "تمت العملية",
    day_close: "إقفال اليوم", pilot: "صحة النظام",
  };

  const navTo = (s: Screen) => { setStack([]); setScreen(s); };

  return (
    <div className="min-h-screen bg-background text-foreground" dir="rtl">
      <div className="md:flex md:min-h-screen">
        <DesktopSidebar
          screen={screen}
          setScreen={navTo}
          myRole={myRole ?? undefined}
          onSale={() => go("sale_quick")}
          onDayClose={() => go("day_close")}
          onQuickExpense={() => setQuickExpenseOpen(true)}
        />

        <div className="md:flex-1 md:flex md:flex-col md:min-w-0">
          {/* Desktop header */}
          <div className="hidden md:flex sticky top-0 z-30 bg-background/95 backdrop-blur border-b border-border px-6 py-3 items-center gap-4">
            <h1 className="text-base font-bold text-foreground">منجز · {screenTitle[screen] ?? ""}</h1>
            <div className="flex-1" />
            <button onClick={() => setQuickExpenseOpen(true)} className="text-xs font-bold px-3 py-2 rounded-xl bg-card border border-border hover:bg-muted">+ مصروف</button>
            <button onClick={() => go("sale_quick")} className="text-xs font-bold px-3 py-2 rounded-xl bg-primary text-primary-foreground hover:opacity-90">+ بيع سريع</button>
          </div>

          <div className="mx-auto w-full max-w-md md:max-w-5xl min-h-screen md:min-h-0 bg-background relative pb-24 md:pb-10 shadow-sm md:shadow-none">
            {screen === "home" && <HomeScreen {...ctx} />}
            {screen === "invoices" && <InvoicesScreen {...ctx} />}
            {screen === "invoice_detail" && <InvoiceDetailScreen {...ctx} />}
            {screen === "inventory" && <InventoryScreen {...ctx} />}
            {screen === "shop" && <ShopHubScreen {...ctx} />}
            {screen === "profit" && <ProfitScreen {...ctx} />}
            {screen === "collected" && <CollectedScreen {...ctx} />}
            {screen === "debts" && <DebtsScreen {...ctx} />}
            {screen === "debt_customer" && <DebtCustomerScreen {...ctx} />}
            {screen === "courier_custody" && <CourierCustodyScreen {...ctx} />}
            {screen === "settlements" && <SettlementsScreen {...ctx} />}
            {screen === "expenses" && <ExpensesScreen {...ctx} />}
            {screen === "customers" && <CustomersScreen {...ctx} />}
            {screen === "couriers" && <CouriersScreen {...ctx} />}
            {screen === "settings" && <SettingsScreen {...ctx} />}
            {screen === "sale" && <SaleScreen {...ctx} />}
            {screen === "sale_quick" && <SaleQuickScreen {...ctx} />}
            {screen === "sale_success" && <SaleSuccessScreen {...ctx} />}
            {screen === "day_close" && <DayCloseScreen {...ctx} />}
            {screen === "pilot" && <PilotScreen {...ctx} />}

            {!hideNav && (
              <div className="md:hidden">
                <BottomNav screen={screen} setScreen={navTo} onSale={() => go("sale_quick")} />
              </div>
            )}

            {quickExpenseOpen && (
              <QuickExpenseSheet
                onClose={() => setQuickExpenseOpen(false)}
                onSave={async (amount: number, type: string, method: "cash" | "transfer") => {
                  await addExpenseMut.mutateAsync({ type, amount, method });
                  setQuickExpenseOpen(false);
                  showToast("تم تسجيل المصروف");
                }}
              />
            )}

            {moneyDetailsOpen && <MoneyDetailsSheet totals={scaledTotals} period={period} onClose={() => setMoneyDetailsOpen(false)} onOpenProfit={() => { setMoneyDetailsOpen(false); go("profit"); }} />}

            {toast && <Toast text={toast} kind="success" />}
          </div>
        </div>
      </div>
    </div>
  );
}

/* DesktopSidebar, TopBar, BottomNav: moved to src/features/layout/ (R3) */

/* ============================== SCREENS ============================== */

/* InvoicesScreen: moved to src/features/invoices/InvoicesScreen.tsx (R5b) */
/* InvoiceDetailScreen: moved to src/features/invoices/InvoiceDetailScreen.tsx (R5a) */

/* --------------- INVENTORY --------------- */
/* InventoryScreen + AddProductSheet: moved to src/features/inventory/ (R4a) */

/* EmptyState: moved to src/features/shared/EmptyState.tsx (R1) */


/* --------------- SHOP HUB --------------- */
/* ShopHubScreen: moved to src/features/shop/ShopHubScreen.tsx (R4b) */


/* ProfitScreen + CollectedScreen: moved to src/features/reports/ (R4b) */


/* --------------- DEBTS --------------- */
function DebtsScreen(p: any) {
  const map = new Map<string, number>();
  p.invoices.forEach((i: Invoice) => {
    const debt = getCustomerDebtForInvoice(i);
    if (debt > 0 && i.customerId) map.set(i.customerId, (map.get(i.customerId) ?? 0) + debt);
  });
  const rows = Array.from(map.entries()).map(([cid, v]) => ({ customer: p.customers.find((c: Customer) => c.id === cid), v }));
  const total = rows.reduce((s, r) => s + r.v, 0);
  return (
    <>
      <TopBar title="الديون" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-debt-soft border border-debt/20 p-4">
          <div className="text-xs text-debt">إجمالي الديون المستحقة</div>
          <Money v={total} className="text-2xl text-debt mt-1" />
        </div>
        {rows.length === 0 && <EmptyState text="لا ديون مستحقة — ممتاز 👍" />}
        <div className="space-y-2">
          {rows.map((r, i) => (
            <button key={i} onClick={() => { p.setOpenCustomerId(r.customer.id); p.go("debt_customer"); }} className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3 active:scale-[0.99]">
              <div className="w-10 h-10 rounded-full bg-debt-soft flex items-center justify-center text-debt font-bold">{r.customer?.name?.[0]}</div>
              <div className="flex-1">
                <div className="font-bold text-sm">{r.customer?.name}</div>
                <div className="text-xs text-muted-foreground">{r.customer?.phone ?? "بدون رقم"}</div>
              </div>
              <Money v={r.v} className="text-debt font-bold" />
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

function DebtCustomerScreen(p: any) {
  const cust: Customer | undefined = p.customers.find((c: Customer) => c.id === p.openCustomerId);
  // Exclude courier orders still pending (not yet delivered) — they aren't customer debt yet.
  const invs = p.invoices.filter((i: Invoice) => i.customerId === cust?.id && getCustomerDebtForInvoice(i) > 0);
  const total = invs.reduce((s: number, i: Invoice) => s + getCustomerDebtForInvoice(i), 0);
  return (
    <>
      <TopBar title={cust?.name ?? "عميل"} onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground">إجمالي المستحق</div>
            <Money v={total} className="text-xl text-debt" />
          </div>
          <div className="flex gap-2">
            <button className="p-2 rounded-full bg-primary-soft text-primary"><Phone className="w-4 h-4" /></button>
            <button className="p-2 rounded-full bg-success-soft text-success"><MessageCircle className="w-4 h-4" /></button>
          </div>
        </div>
        <div className="text-xs font-bold text-muted-foreground">الفواتير المدينة</div>
        {invs.map((inv: Invoice) => (
          <div key={inv.id} className="rounded-2xl bg-card border border-border p-3">
            <div className="flex items-center justify-between">
              <span className="font-bold text-sm">#{inv.number}</span>
              <Money v={inv.total} />
            </div>
            <div className="text-xs text-debt mt-1">متبقي <span className="num">{fmt(getCustomerDebtForInvoice(inv))}</span> د.ل</div>
            <button onClick={() => { p.setOpenInvoiceId(inv.id); p.go("invoice_detail"); }} className="mt-2 w-full rounded-xl bg-primary text-primary-foreground py-2 text-sm font-bold">تحصيل دفعة</button>
          </div>
        ))}
      </div>
    </>
  );
}

/* --------------- COURIER CUSTODY --------------- */
function CourierCustodyScreen(p: any) {
  const [courierId, setCourierId] = useState<string>(p.openCourierId ?? p.couriers[0]?.id ?? "");
  const [markOrder, setMarkOrder] = useState<Invoice | null>(null);
  const [markMode, setMarkMode] = useState<"delivered_full" | "delivered_partial" | "delivered_none" | "returned" | null>(null);
  const [markAmount, setMarkAmount] = useState("");
  if (!p.couriers || p.couriers.length === 0) {
    return (
      <>
        <TopBar title="عهدة المندوب" onBack={p.back} onHome={p.goHome} />
        <div className="px-4 pt-10 text-center space-y-4">
          <div className="text-5xl">🛵</div>
          <div className="font-bold">لا يوجد مندوبون بعد</div>
          <div className="text-xs text-muted-foreground">أضف مندوبًا أولًا لمتابعة طلبات التوصيل والعهدة.</div>
          <button onClick={() => p.go("couriers")} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold text-sm">+ إضافة مندوب</button>
        </div>
      </>
    );
  }
  const list = p.invoices.filter((i: Invoice) => i.delivery === "courier" && i.courierId === courierId);
  const pending = list.filter((i: Invoice) => (i.courierState ?? "pending") === "pending");
  const collected = list.filter((i: Invoice) => i.courierState === "delivered_partial" || i.courierState === "delivered_full");
  const customerDebtOrders = list.filter((i: Invoice) => i.courierState === "delivered_partial" || i.courierState === "delivered_none");

  const pendingV = pending.reduce((s: number, i: Invoice) => s + getPendingCourierValueForInvoice(i), 0);
  const custodyV = collected.reduce((s: number, i: Invoice) => s + getCourierCustodyForInvoice(i), 0);
  const debtV = customerDebtOrders.reduce((s: number, i: Invoice) => s + getCustomerDebtForInvoice(i), 0);

  const goSettlements = () => { p.setOpenCourierId(courierId); p.go("settlements"); };

  const confirmMark = async () => {
    if (!markOrder || !markMode) return;
    const total = markOrder.total;
    const amt = markMode === "delivered_full" ? total : markMode === "delivered_partial" ? Number(markAmount) : 0;
    if (markMode === "delivered_partial" && (!amt || amt <= 0 || amt >= total)) return;
    await p.updateCourierStateAsync({ orderId: markOrder.id, state: markMode, collected: amt });
    setMarkOrder(null); setMarkMode(null); setMarkAmount("");
    p.showToast(
      markMode === "delivered_full" ? "✓ سُلِّمت كاملة — دخلت العهدة" :
      markMode === "delivered_partial" ? "✓ سُلِّمت جزئيًا — الباقي دين على العميل" :
      markMode === "delivered_none" ? "✓ لم تُسلَّم — دين كامل على العميل" :
      "✓ أُرجعت — لا دين ولا عهدة"
    );
  };

  return (
    <>
      <TopBar title="عهدة المندوب" onBack={p.back} onHome={p.goHome} right={<button onClick={goSettlements} className="text-xs font-bold text-primary px-3 py-1.5 rounded-full bg-primary-soft">تسوية</button>} />
      <div className="px-4 pt-3 space-y-3">
        <div className="flex gap-2 overflow-x-auto">
          {p.couriers.map((c: Courier) => (
            <button key={c.id} onClick={() => setCourierId(c.id)} className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${courierId === c.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{c.name}</button>
          ))}
        </div>

        {/* Block 1 */}
        <div className="rounded-2xl bg-warn-soft/40 border border-warn/20 p-4">
          <div className="flex items-center gap-2 text-warn/80 text-xs font-bold"><Clock className="w-4 h-4" />طلبات مع المندوب · قيد التنفيذ</div>
          <Money v={pendingV} className="text-lg mt-1 text-warn/80" />
          <div className="text-[11px] text-muted-foreground mt-1">قيمة متوقعة — غير مؤكدة. لا تدخل في "عند المندوب".</div>
          <div className="mt-2 space-y-1.5">
            {pending.map((i: Invoice) => (
              <div key={i.id} className="bg-card rounded-lg px-3 py-2 space-y-1.5">
                <div className="text-xs flex justify-between">
                  <span>#{i.number} · {p.customers.find((c: Customer) => c.id === i.customerId)?.name}</span>
                  <Money v={i.total} />
                </div>
                <button onClick={() => { setMarkOrder(i); setMarkMode(null); setMarkAmount(""); }} className="w-full text-[11px] font-bold py-1.5 rounded-md bg-primary-soft text-primary">تحديث حالة التسليم ←</button>
              </div>
            ))}
            {pending.length === 0 && <div className="text-xs text-muted-foreground">لا طلبات قيد التنفيذ</div>}
          </div>
        </div>


        {/* Block 2 */}
        <div className="rounded-2xl bg-warn-soft border-2 border-warn/30 p-4">
          <div className="flex items-center gap-2 text-warn text-xs font-bold"><Wallet className="w-4 h-4" />عهدة غير مصفّاة · مال بيد المندوب الآن</div>
          <Money v={custodyV} className="text-2xl mt-1 text-warn" />
          <div className="text-[11px] text-muted-foreground mt-1">قُبض فعلًا ولم يُسلّم لك. هذا فقط ما يظهر في "عند المندوب".</div>
          <div className="mt-2 space-y-1.5">
            {collected.map((i: Invoice) => (
              <div key={i.id} className="text-xs flex justify-between bg-card rounded-lg px-3 py-2">
                <span>#{i.number} · {i.courierState === "delivered_full" ? "كامل" : "جزئي"}</span>
                <Money v={i.collectedByCourier ?? 0} className="text-warn font-bold" />
              </div>
            ))}
          </div>
        </div>

        {/* Block 3 */}
        <div className="rounded-2xl bg-debt-soft border border-debt/20 p-4">
          <div className="flex items-center gap-2 text-debt text-xs font-bold"><CircleDollarSign className="w-4 h-4" />ديون عملاء من طلبات التوصيل</div>
          <Money v={debtV} className="text-lg mt-1 text-debt" />
          <div className="rounded-lg bg-card border border-debt/20 p-2 mt-2 text-[11px] text-muted-foreground flex items-start gap-2">
            <Info className="w-3.5 h-3.5 text-debt shrink-0 mt-0.5" />
            <span>هذه <b>ديون عملاء</b> — ليست عهدة على المندوب. مُحتسبة <b>مرة واحدة</b> ضمن إجمالي الديون.</span>
          </div>
          <button onClick={() => p.go("debts")} className="mt-2 w-full rounded-xl bg-card border border-debt/20 text-debt text-xs font-bold py-2">عرض في الديون ←</button>
          <div className="mt-2 space-y-1.5">
            {customerDebtOrders.map((i: Invoice) => {
              const d = getCustomerDebtForInvoice(i);
              return (
                <div key={i.id} className="text-xs flex justify-between bg-card rounded-lg px-3 py-2">
                  <span>#{i.number} · {p.customers.find((c: Customer) => c.id === i.customerId)?.name}</span>
                  <Money v={d} className="text-debt" />
                </div>
              );
            })}
            {customerDebtOrders.length === 0 && <div className="text-xs text-muted-foreground">لا ديون من التوصيل</div>}
          </div>
        </div>
      </div>

      {markOrder && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-end" onClick={() => setMarkOrder(null)}>
          <div className="w-full bg-card rounded-t-3xl p-4 space-y-3" onClick={e => e.stopPropagation()}>
            <div className="font-bold">تحديث حالة التسليم · #{markOrder.number}</div>
            <div className="text-xs text-muted-foreground">قيمة الطلب: <Money v={markOrder.total} className="num font-bold text-foreground" /></div>
            <div className="grid grid-cols-2 gap-2">
              <button onClick={() => setMarkMode("delivered_full")} className={`py-3 rounded-xl text-sm font-bold ${markMode === "delivered_full" ? "bg-success text-success-foreground" : "bg-muted"}`}>سُلِّمت كاملة</button>
              <button onClick={() => setMarkMode("delivered_partial")} className={`py-3 rounded-xl text-sm font-bold ${markMode === "delivered_partial" ? "bg-warn text-warn-foreground" : "bg-muted"}`}>سُلِّمت جزئيًا</button>
              <button onClick={() => setMarkMode("delivered_none")} className={`py-3 rounded-xl text-sm font-bold ${markMode === "delivered_none" ? "bg-debt text-destructive-foreground" : "bg-muted"}`}>لم تُسلَّم (دين)</button>
              <button onClick={() => setMarkMode("returned")} className={`py-3 rounded-xl text-sm font-bold ${markMode === "returned" ? "bg-foreground text-background" : "bg-muted"}`}>أُرجعت</button>
            </div>
            {markMode === "delivered_partial" && (
              <div className="space-y-1">
                <div className="text-xs text-muted-foreground">المبلغ المقبوض فعلًا</div>
                <input value={markAmount} onChange={e => setMarkAmount(e.target.value)} placeholder="0" inputMode="decimal" className="w-full rounded-xl bg-muted px-3 py-3 text-sm num" />
                <div className="text-[11px] text-muted-foreground">الباقي يصبح دينًا على العميل.</div>
              </div>
            )}
            {markMode && markMode !== "delivered_partial" && (
              <div className="text-[11px] text-muted-foreground rounded-lg bg-muted px-3 py-2">
                {markMode === "delivered_full" && "كامل المبلغ سيدخل عهدة المندوب وينتظر التسوية."}
                {markMode === "delivered_none" && "كامل المبلغ يصبح دينًا على العميل، لا عهدة على المندوب."}
                {markMode === "returned" && "الطلب مُلغى — يُعاد المخزون تلقائيًا. (لا يمكن إرجاع فاتورة حُصِّل منها مبلغ)"}
              </div>
            )}
            <div className="flex gap-2">
              <button onClick={() => setMarkOrder(null)} className="flex-1 rounded-xl bg-muted py-3 text-sm font-bold">إلغاء</button>
              <button
                onClick={confirmMark}
                disabled={!markMode || (markMode === "delivered_partial" && (!Number(markAmount) || Number(markAmount) >= markOrder.total))}
                className="flex-1 rounded-xl bg-primary text-primary-foreground py-3 text-sm font-bold disabled:opacity-40"
              >تأكيد</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

/* --------------- SETTLEMENTS --------------- */
function SettlementsScreen(p: any) {
  const courier = p.couriers.find((c: Courier) => c.id === p.openCourierId) ?? p.couriers[0];
  const collected = courier
    ? p.invoices.filter((i: Invoice) => i.delivery === "courier" && i.courierId === courier.id && (i.courierState === "delivered_partial" || i.courierState === "delivered_full"))
    : [];
  const pending = courier
    ? p.invoices.filter((i: Invoice) => i.delivery === "courier" && i.courierId === courier.id && (i.courierState ?? "pending") === "pending")
    : [];
  const [selected, setSelected] = useState<Set<string>>(new Set(collected.map((i: Invoice) => i.id)));
  const [done, setDone] = useState(false);

  const toggle = (id: string) => setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const net = collected.filter((i: Invoice) => selected.has(i.id)).reduce((s: number, i: Invoice) => s + getCourierCustodyForInvoice(i), 0);

  const [settledAmount, setSettledAmount] = useState(0);

  if (!courier) {
    return (
      <>
        <TopBar title="التسويات" onBack={p.back} onHome={p.goHome} />
        <div className="px-4 pt-10 text-center space-y-4">
          <div className="text-5xl">🧾</div>
          <div className="font-bold">لا يوجد مندوبون لتسويتهم</div>
          <div className="text-xs text-muted-foreground">أضف مندوبًا أولًا، ثم سجّل طلبات توصيل لتظهر هنا.</div>
          <button onClick={() => p.go("couriers")} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold text-sm">+ إضافة مندوب</button>
        </div>
      </>
    );
  }

  const confirm = async () => {
    setSettledAmount(net);
    const settledInvoices = collected.filter((i: Invoice) => selected.has(i.id));
    await p.settleCourierAsync({
      courierId: courier.id,
      orders: settledInvoices.map((i: Invoice) => ({
        id: i.id, customerId: i.customerId, collected: i.collectedByCourier ?? 0,
      })),
    });
    setDone(true);
  };

  if (done) {
    return (
      <>
        <TopBar title="تسوية" onBack={() => { setDone(false); p.back(); }} />
        <div className="p-6 flex flex-col items-center text-center gap-3">
          <div className="w-16 h-16 rounded-full bg-success-soft flex items-center justify-center"><CheckCircle2 className="w-8 h-8 text-success" /></div>
          <div className="text-lg font-bold">✓ تمت التسوية</div>
          <div className="text-sm text-muted-foreground">دخل <Money v={settledAmount} className="text-success font-bold" /> إلى المحصّل فعلًا</div>
          <button onClick={() => { setDone(false); setSettledAmount(0); p.back(); }} className="mt-4 w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">تم</button>
        </div>
      </>
    );
  }

  return (
    <>
      <TopBar title={`تسوية مع ${courier.name}`} onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3 pb-4">
        <div className="text-xs font-bold text-muted-foreground">المبالغ التي قبضها المندوب فعلًا</div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {collected.map((i: Invoice) => (
            <label key={i.id} className="flex items-center gap-3 p-3">
              <input type="checkbox" checked={selected.has(i.id)} onChange={() => toggle(i.id)} className="w-5 h-5 accent-[color:var(--primary)]" />
              <div className="flex-1">
                <div className="text-sm font-bold">#{i.number}</div>
                <div className="text-xs text-muted-foreground">{i.courierState === "delivered_full" ? "كامل" : "جزئي"} · {p.customers.find((c: Customer) => c.id === i.customerId)?.name}</div>
              </div>
              <Money v={i.collectedByCourier ?? 0} className="text-warn font-bold" />
            </label>
          ))}
          {collected.length === 0 && <div className="p-4 text-sm text-muted-foreground text-center">لا عهدة لتسويتها</div>}
        </div>

        <div className="text-xs font-bold text-muted-foreground mt-3">خارج هذه التسوية</div>
        <div className="rounded-2xl bg-muted border border-border p-3 space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground flex items-center gap-2"><Clock className="w-4 h-4" />طلبات قيد التنفيذ</span><span className="num">{pending.length}</span></div>
          <div className="flex justify-between"><span className="text-muted-foreground flex items-center gap-2"><CircleDollarSign className="w-4 h-4" />ديون عملاء من التوصيل</span><span className="text-debt">تبقى على العميل</span></div>
        </div>

        <div className="rounded-2xl bg-primary text-primary-foreground p-4 flex items-center justify-between">
          <div>
            <div className="text-xs opacity-90">صافي ما تستلمه الآن</div>
            <Money v={net} className="text-2xl mt-1" />
          </div>
          <Banknote className="w-8 h-8 opacity-80" />
        </div>

        <button disabled={net <= 0} onClick={confirm} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">تأكيد التسوية</button>
      </div>
    </>
  );
}

/* --------------- EXPENSES --------------- */
function ExpensesScreen(p: any) {
  const [open, setOpen] = useState(false);
  const [amount, setAmount] = useState("");
  const [type, setType] = useState("");
  const [method, setMethod] = useState<"cash" | "transfer" | "">("");
  const [success, setSuccess] = useState(false);
  const { range, setRange } = useDateRange("today");

  const filtered = (p.expenses as Expense[]).filter(e => inRange(e.createdAt, range));
  const total = filtered.reduce((s: number, e: Expense) => s + e.amount, 0);
  const cashT = filtered.filter(e => e.method === "cash").reduce((s: number, e: Expense) => s + e.amount, 0);
  const transferT = total - cashT;

  const canSave = Number(amount) > 0 && !!method && !!type;
  const save = async () => {
    await p.addExpenseAsync({ type, amount: Number(amount), method: method as "cash" | "transfer" });
    setAmount(""); setType(""); setMethod(""); setOpen(false); setSuccess(true);
    setTimeout(() => setSuccess(false), 1800);
  };

  const types = ["إيجار", "كهرباء", "إنترنت", "تغليف", "نقل", "صيانة", "راتب", "أخرى"];

  return (
    <>
      <TopBar title="المصروفات" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <DateRangeFilter value={range} onChange={setRange} />
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="text-xs text-muted-foreground">إجمالي المصروفات · {range.label}</div>
          <Money v={total} className="text-2xl mt-1" />
          <div className="mt-2 text-xs text-muted-foreground">{filtered.length} عملية · نقدي <span className="num">{fmt(cashT)}</span> · تحويل <span className="num">{fmt(transferT)}</span></div>
        </div>
        <div className="rounded-2xl bg-info-soft border border-info/20 p-3 text-xs text-info flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>المصروفات تنقص <b>الربح التقديري</b> فقط. لا تنقص المحصّل فعلًا.</span>
        </div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {filtered.length === 0 && <div className="p-8 text-center text-sm text-muted-foreground">لا توجد مصروفات في هذا النطاق</div>}
          {filtered.map((e: Expense) => (
            <div key={e.id} className="flex items-center gap-3 p-3">
              <ArrowDownCircle className="w-5 h-5 text-debt" />
              <div className="flex-1">
                <div className="text-sm font-bold">{e.type}</div>
                <div className="text-xs text-muted-foreground">{e.time} · {e.method === "cash" ? "نقدي" : "تحويل"}</div>
              </div>
              <Money v={e.amount} className="text-debt" />
            </div>
          ))}
        </div>
        <button onClick={() => setOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ تسجيل مصروف</button>
      </div>


      {success && <Toast text="تم تسجيل المصروف" />}

      {open && (
        <Sheet onClose={() => setOpen(false)} title="مصروف جديد">
          <div className="space-y-3">
            <div>
              <label className="text-xs font-bold text-muted-foreground">المبلغ</label>
              <input value={amount} onChange={e => setAmount(e.target.value)} inputMode="decimal" placeholder="0" className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right" />
            </div>
            <div>
              <label className="text-xs font-bold text-muted-foreground">النوع</label>
              <div className="mt-1 flex flex-wrap gap-2">
                {types.map(t => (
                  <button key={t} onClick={() => setType(t)} className={`px-3 py-1.5 rounded-full text-xs font-bold ${type === t ? "bg-primary text-primary-foreground" : "bg-muted text-foreground"}`}>{t}</button>
                ))}
              </div>
            </div>
            <div>
              <label className="text-xs font-bold text-muted-foreground">طريقة الدفع</label>
              <div className="mt-1 grid grid-cols-2 gap-2">
                <button onClick={() => setMethod("cash")} className={`py-2 rounded-xl text-sm font-bold ${method === "cash" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>نقدي</button>
                <button onClick={() => setMethod("transfer")} className={`py-2 rounded-xl text-sm font-bold ${method === "transfer" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>تحويل</button>
              </div>
            </div>
            <button disabled={!canSave} onClick={save} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">حفظ</button>
          </div>
        </Sheet>
      )}
    </>
  );
}

/* --------------- CUSTOMERS / COURIERS / SETTINGS --------------- */
/* CustomersScreen + AddCustomerInline: moved to src/features/customers/ (R4a) */

/* SettingsScreen: moved to src/features/settings/SettingsScreen.tsx (R4a) */

/* --------------- SALE --------------- */
type CartItem = { productId: string; qty: number };
function SaleScreen(p: any) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [q, setQ] = useState("");
  const [searchFocused, setSearchFocused] = useState(false);
  const [paySheet, setPaySheet] = useState(false);
  const [overStockMsg, setOverStockMsg] = useState<string | null>(null);

  const subtotal = cart.reduce((s, c) => s + (p.products.find((pr: Product) => pr.id === c.productId)?.price ?? 0) * c.qty, 0);

  const add = (pr: Product) => {
    if (pr.stock === 0) return;
    setCart(c => {
      const ex = c.find(x => x.productId === pr.id);
      if (ex) {
        if (ex.qty + 1 > pr.stock) { setOverStockMsg("المطلوب أكبر من المتوفر"); setTimeout(() => setOverStockMsg(null), 1800); return c; }
        return c.map(x => x.productId === pr.id ? { ...x, qty: x.qty + 1 } : x);
      }
      return [...c, { productId: pr.id, qty: 1 }];
    });
  };
  const setQty = (pid: string, qty: number) => {
    const pr = p.products.find((x: Product) => x.id === pid)!;
    if (qty > pr.stock) { setOverStockMsg("المطلوب أكبر من المتوفر"); setTimeout(() => setOverStockMsg(null), 1800); return; }
    if (qty <= 0) setCart(c => c.filter(x => x.productId !== pid));
    else setCart(c => c.map(x => x.productId === pid ? { ...x, qty } : x));
  };

  const filtered = p.products.filter((pr: Product) => !q || pr.name.includes(q));

  return (
    <div className="min-h-[100dvh] bg-background flex flex-col">
      {!searchFocused && (
        <TopBar title="فاتورة جديدة" onBack={p.back} onHome={p.goHome} right={
          <button className="px-3 py-1.5 rounded-full bg-muted text-xs font-bold flex items-center gap-1"><Users className="w-3.5 h-3.5" />بدون عميل</button>
        } />
      )}
      <div className={`px-4 pt-3 pb-3 sticky bg-background z-20 ${searchFocused ? "top-0" : "top-[57px]"}`}>
        <div className="relative">
          <Search className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground" />
          <input
            value={q}
            onChange={e => setQ(e.target.value)}
            onFocus={() => setSearchFocused(true)}
            onBlur={() => setSearchFocused(false)}
            placeholder="ابحث عن منتج"
            className="w-full rounded-xl border border-border bg-card pr-9 pl-3 py-3 text-sm"
          />
          {searchFocused && q && (
            <button onMouseDown={(e) => { e.preventDefault(); setQ(""); }} className="absolute left-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-muted">
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          )}
        </div>
      </div>


      <div className={`px-4 flex-1 ${searchFocused ? "pb-80" : "pb-4"}`}>
        {filtered.length === 0 ? (
          <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground col-span-2">
            <PackageX className="w-8 h-8 mx-auto mb-2 opacity-50" />
            لا منتج بهذا الاسم
            {q && <button onClick={() => setQ("")} className="block mx-auto mt-2 text-primary text-xs font-bold">مسح البحث</button>}
          </div>
        ) : (
          <div className="grid grid-cols-2 gap-2">
            {filtered.map((pr: Product) => {
              const out = pr.stock === 0;
              return (
                <button key={pr.id} disabled={out} onClick={() => add(pr)} className={`text-right rounded-2xl border p-3 transition active:scale-[0.97] ${out ? "bg-muted border-border opacity-60" : "bg-card border-border"}`}>
                  <div className="font-bold text-sm leading-tight">{pr.name}</div>
                  <div className="mt-2 flex items-center justify-between">
                    <Money v={pr.price} className="text-sm" />
                    {out ? <StatusChip kind="debt" icon={<PackageX className="w-3 h-3" />}>نفد</StatusChip>
                      : pr.stock <= pr.lowAt ? <StatusChip kind="warn">منخفض <span className="num">{pr.stock}</span></StatusChip>
                        : <span className="text-[11px] text-muted-foreground">متوفر <span className="num">{pr.stock}</span></span>}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {overStockMsg && <Toast text={overStockMsg} kind="warn" />}

      {/* Cart sticky */}
      {cart.length > 0 && (
        <div className="sticky bottom-0 bg-card border-t border-border p-3 mt-4">
          <div className="max-h-40 overflow-y-auto space-y-1.5 mb-2">
            {cart.map(ci => {
              const pr = p.products.find((x: Product) => x.id === ci.productId)!;
              return (
                <div key={ci.productId} className="flex items-center gap-2">
                  <button onClick={() => setQty(ci.productId, 0)} className="p-1 text-debt"><Trash2 className="w-4 h-4" /></button>
                  <div className="flex-1 text-sm">{pr.name}</div>
                  <div className="flex items-center gap-1">
                    <button onClick={() => setQty(ci.productId, ci.qty - 1)} className="w-7 h-7 rounded-full bg-muted flex items-center justify-center"><Minus className="w-3.5 h-3.5" /></button>
                    <span className="w-7 text-center text-sm font-bold num">{ci.qty}</span>
                    <button onClick={() => setQty(ci.productId, ci.qty + 1)} className="w-7 h-7 rounded-full bg-muted flex items-center justify-center"><Plus className="w-3.5 h-3.5" /></button>
                  </div>
                  <Money v={pr.price * ci.qty} className="text-sm w-16 text-left" />
                </div>
              );
            })}
          </div>
          <div className="flex items-center gap-3">
            <div className="flex-1">
              <div className="text-xs text-muted-foreground">الإجمالي</div>
              <Money v={subtotal} className="text-lg" />
            </div>
            <button onClick={() => setPaySheet(true)} className="rounded-2xl bg-primary text-primary-foreground px-6 py-3 font-bold">إتمام البيع</button>
          </div>
        </div>
      )}

      {paySheet && (
        <PaymentSheet
          subtotal={subtotal}
          customers={p.customers}
          addCustomerAsync={p.addCustomerAsync}
          couriers={p.couriers}
          onClose={() => setPaySheet(false)}
          onSave={async (d: { paid: number; customerId?: string; delivery: "direct" | "courier"; courierId?: string; method: "cash" | "transfer" }) => {
            const items: InvoiceItem[] = cart.map(c => {
              const pr = p.products.find((x: Product) => x.id === c.productId)!;
              return { productId: pr.id, name: pr.name, qty: c.qty, price: pr.price, cost: pr.cost };
            });
            const cogs = items.reduce((s, it) => s + it.cost * it.qty, 0);
            const created = await p.createSaleAsync({
              items, total: subtotal, paid: d.paid,
              customerId: d.customerId, delivery: d.delivery, courierId: d.courierId, method: d.method,
            });
            p.setLastSaleSummary({ total: subtotal, paid: d.paid, profit: subtotal - cogs });
            p.setLastCreatedInvoiceId(created.orderId);
            p.setScreen("sale_success");
          }}
        />
      )}
    </div>
  );
}

function PaymentSheet({ subtotal, customers, addCustomerAsync, couriers, onClose, onSave }: any) {
  const [status, setStatus] = useState<"paid" | "partial" | "debt">("paid");
  const [paidStr, setPaidStr] = useState(String(subtotal));
  const [customerId, setCustomerId] = useState<string | undefined>(undefined);
  const [delivery, setDelivery] = useState<"direct" | "courier">("direct");
  const [courierId, setCourierId] = useState<string | undefined>(undefined);
  const [method, setMethod] = useState<"cash" | "transfer">("cash");
  const [pickCustomer, setPickCustomer] = useState(false);
  const [newName, setNewName] = useState("");
  const [newPhone, setNewPhone] = useState("");

  const paid = status === "debt" ? 0 : status === "paid" ? subtotal : Number(paidStr || 0);
  const remaining = subtotal - paid;
  const overpaid = paid > subtotal;
  const needsCustomer = remaining > 0;
  const needsCourier = delivery === "courier";
  const canSave = subtotal > 0 && !overpaid && (!needsCustomer || !!customerId) && (!needsCourier || !!courierId);

  const trimmedName = newName.trim();
  const trimmedPhone = newPhone.trim();
  const dup = (trimmedName || trimmedPhone)
    ? customers.find((c: Customer) =>
        (trimmedName && c.name.trim() === trimmedName) ||
        (trimmedPhone && c.phone && c.phone.trim() === trimmedPhone)
      )
    : undefined;

  return (
    <Sheet onClose={onClose} title="الدفع">
      <div className="space-y-3">
        <div className="rounded-xl bg-muted p-3 flex justify-between"><span className="text-sm text-muted-foreground">الإجمالي</span><Money v={subtotal} className="font-bold" /></div>

        <div>
          <label className="text-xs font-bold text-muted-foreground">حالة الدفع</label>
          <div className="mt-1 grid grid-cols-3 gap-2">
            {[{ id: "paid", l: "مدفوع" }, { id: "partial", l: "جزئياً" }, { id: "debt", l: "دين" }].map(s => (
              <button key={s.id} onClick={() => { setStatus(s.id as any); if (s.id === "paid") setPaidStr(String(subtotal)); if (s.id === "debt") setPaidStr("0"); if (s.id === "partial") setPaidStr(""); }}
                className={`py-2 rounded-xl text-sm font-bold ${status === s.id ? "bg-primary text-primary-foreground" : "bg-muted"}`}>{s.l}</button>
            ))}
          </div>
        </div>

        {status === "partial" && (
          <div>
            <label className="text-xs font-bold text-muted-foreground">{delivery === "courier" ? "قبضه المندوب الآن" : "المدفوع"}</label>
            <input value={paidStr} onChange={e => setPaidStr(e.target.value)} inputMode="decimal" className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right" />
          </div>
        )}

        {overpaid && <div className="rounded-xl bg-debt-soft text-debt text-xs p-3 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />المبلغ المدفوع أكبر من الإجمالي</div>}

        {delivery === "courier" && paid > 0 && !overpaid && (
          <div className="rounded-xl bg-warn-soft text-warn text-[11px] p-3 flex items-start gap-2">
            <Info className="w-4 h-4 shrink-0 mt-0.5" />
            <span>هذا المبلغ يُسجَّل <b>عهدة بيد المندوب</b> — لا يدخل صندوق المحل إلا بعد التسوية معه.</span>
          </div>
        )}

        {(status === "partial" || status === "debt") && (
          <div className="rounded-xl bg-debt-soft p-3 flex items-center justify-between">
            <div><div className="text-xs text-debt">المتبقي {delivery === "courier" ? "(على العميل بعد التسوية)" : ""}</div><Money v={Math.max(0, remaining)} className="text-debt font-bold" /></div>
          </div>
        )}

        {/* Delivery */}
        <div>
          <label className="text-xs font-bold text-muted-foreground">التسليم</label>
          <div className="mt-1 grid grid-cols-2 gap-2">
            <button onClick={() => setDelivery("direct")} className={`py-2 rounded-xl text-sm font-bold ${delivery === "direct" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>استلام مباشر</button>
            <button onClick={() => setDelivery("courier")} className={`py-2 rounded-xl text-sm font-bold ${delivery === "courier" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>عبر مندوب</button>
          </div>
          {delivery === "courier" && remaining > 0 && <div className="mt-2 text-[11px] text-warn flex items-center gap-1"><Info className="w-3 h-3" />طلب توصيل بمتبقٍّ — اختر العميل لتسجيل دينه.</div>}
          {delivery === "courier" && remaining === 0 && <div className="mt-2 text-[11px] text-muted-foreground flex items-center gap-1"><Info className="w-3 h-3" />مدفوعة كاملة — العميل اختياري، لكن اختيار مستلم يساعدك في التتبع.</div>}
        </div>

        {/* Customer */}
        <div>
          <label className="text-xs font-bold text-muted-foreground">{needsCustomer ? "العميل (إلزامي)" : "العميل (اختياري)"}</label>
          <button onClick={() => setPickCustomer(true)} className={`mt-1 w-full text-right rounded-xl border px-3 py-3 text-sm ${needsCustomer && !customerId ? "border-debt bg-debt-soft text-debt" : "border-border bg-background"}`}>
            {customerId ? customers.find((c: Customer) => c.id === customerId)?.name : (needsCustomer ? "اختر عميلًا — لا يمكن تسجيل متبقٍّ دون عميل" : "بدون عميل")}
          </button>
          {!needsCustomer && !customerId && (
            <div className="mt-1 rounded-lg bg-success-soft text-success text-[11px] p-2 flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" />مدفوعة كاملة — لا حاجة لاختيار عميل</div>
          )}
        </div>


        {/* Courier */}
        {delivery === "courier" && (
          <div>
            <label className="text-xs font-bold text-muted-foreground">المندوب (إلزامي)</label>
            <div className="mt-1 flex flex-wrap gap-2">
              {couriers.map((c: Courier) => (
                <button key={c.id} onClick={() => setCourierId(c.id)} className={`px-3 py-1.5 rounded-full text-xs font-bold ${courierId === c.id ? "bg-warn text-background" : "bg-muted"}`}>{c.name}</button>
              ))}
            </div>
          </div>
        )}

        {/* Method */}
        <div>
          <label className="text-xs font-bold text-muted-foreground">طريقة الدفع</label>
          <div className="mt-1 grid grid-cols-2 gap-2">
            <button onClick={() => setMethod("cash")} className={`py-2 rounded-xl text-sm font-bold ${method === "cash" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>نقدي</button>
            <button onClick={() => setMethod("transfer")} className={`py-2 rounded-xl text-sm font-bold ${method === "transfer" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>تحويل</button>
          </div>
        </div>

        <button disabled={!canSave} onClick={() => { if (!canSave || overpaid || paid > subtotal) return; onSave({ paid, customerId, delivery, courierId, method }); }} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">حفظ الفاتورة</button>
      </div>

      {pickCustomer && (
        <Sheet onClose={() => setPickCustomer(false)} title="اختر عميلًا">
          <div className="space-y-3">
            <div>
              <input value={newName} onChange={e => setNewName(e.target.value)} placeholder="اسم العميل (إلزامي)" className="w-full rounded-xl border border-border bg-background px-3 py-3 text-sm" />
              <input value={newPhone} onChange={e => setNewPhone(e.target.value)} placeholder="رقم الهاتف (اختياري)" inputMode="tel" className="mt-2 w-full rounded-xl border border-border bg-background px-3 py-3 text-sm num text-right" />
              {dup && <div className="text-[11px] text-warn mt-1">⚠ يوجد عميل بنفس {dup.name.trim() === trimmedName ? "الاسم" : "الرقم"}: {dup.name}</div>}
              {trimmedName && (
                <button onClick={async () => {
                  try {
                    const created = await addCustomerAsync({ name: trimmedName, phone: trimmedPhone || undefined });
                    setCustomerId(created.id); setNewName(""); setNewPhone(""); setPickCustomer(false);
                  } catch (err: any) {
                    console.warn(err?.message);
                  }
                }} className="mt-2 w-full rounded-xl bg-primary text-primary-foreground py-2 text-sm font-bold">إضافة وحفظ</button>
              )}
            </div>
            <div className="text-xs font-bold text-muted-foreground">أو اختر من القائمة</div>
            <div className="space-y-1.5 max-h-60 overflow-y-auto">
              {customers.map((c: Customer) => (
                <button key={c.id} onClick={() => { setCustomerId(c.id); setPickCustomer(false); }} className="w-full text-right rounded-xl bg-muted p-3 text-sm">
                  <div className="font-bold">{c.name}</div>
                  <div className="text-xs text-muted-foreground">{c.phone ?? "بدون رقم"}</div>
                </button>
              ))}
            </div>
          </div>
        </Sheet>
      )}
    </Sheet>
  );
}

function SaleSuccessScreen(p: any) {
  const s = p.lastSaleSummary;
  const [secondsLeft, setSecondsLeft] = useState(5);
  const [undone, setUndone] = useState(false);
  const [undoBusy, setUndoBusy] = useState(false);
  useEffect(() => {
    if (secondsLeft <= 0 || undone) return;
    const t = setTimeout(() => setSecondsLeft(n => n - 1), 1000);
    return () => clearTimeout(t);
  }, [secondsLeft, undone]);
  const undo = async () => {
    if (!p.lastCreatedInvoiceId || undoBusy) return;
    setUndoBusy(true);
    try {
      await p.deleteInvoiceAsync(p.lastCreatedInvoiceId);
      p.setLastCreatedInvoiceId(null);
      setUndone(true);
      setTimeout(() => p.setScreen("home"), 600);
    } catch (e) {
      p.showToast?.(e instanceof Error ? e.message : "تعذّر التراجع عن الفاتورة. حاول مرة أخرى.");
    } finally {
      setUndoBusy(false);
    }
  };
  if (undone) {
    return (
      <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center gap-3">
        <div className="text-lg font-bold">تم التراجع عن الفاتورة</div>
        <div className="text-sm text-muted-foreground">جاري العودة للرئيسية…</div>
      </div>
    );
  }
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center gap-4">
      <div className="w-20 h-20 rounded-full bg-success-soft flex items-center justify-center"><CheckCircle2 className="w-10 h-10 text-success" /></div>
      <div className="text-xl font-bold">تم حفظ الفاتورة</div>
      {s && (
        <div className="text-sm text-muted-foreground">
          الإجمالي <span className="num font-bold text-foreground">{fmt(s.total)}</span> · مدفوع <span className="num font-bold text-success">{fmt(s.paid)}</span>
          <div className="mt-2 inline-flex items-center gap-1 px-3 py-1 rounded-full bg-profit-soft text-profit text-xs"><TrendingUp className="w-3 h-3" />ربح تقديري <span className="num font-bold">{fmt(s.profit)}</span> د.ل</div>
          {typeof s.elapsedMs === "number" && (
            <div className="mt-2 text-[11px] text-muted-foreground">⚡ تمّ خلال <span className="num font-bold text-foreground">{(s.elapsedMs / 1000).toFixed(1)}</span> ثانية</div>
          )}
        </div>
      )}
      {/* Undo only works on deletable (unpaid) orders — the delete RPC rejects paid>0. */}
      {secondsLeft > 0 && p.lastCreatedInvoiceId && s?.paid === 0 && (
        <button disabled={undoBusy} onClick={undo} className="text-xs text-debt font-bold underline disabled:opacity-50">{undoBusy ? "جاري التراجع..." : `تراجع عن هذه الفاتورة (${secondsLeft})`}</button>
      )}
      <div className="w-full max-w-xs space-y-2 mt-2">
        <button onClick={() => p.setScreen("sale_quick")} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">بيع جديد</button>
        <button onClick={() => p.setScreen("home")} className="w-full rounded-2xl bg-card border border-border py-3 font-bold">عودة للرئيسية</button>
      </div>
    </div>
  );
}

/* --------------- SALE QUICK (cash, full-paid, no customer) --------------- */
function SaleQuickScreen(p: any) {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [q, setQ] = useState("");
  const [overStockMsg, setOverStockMsg] = useState<string | null>(null);
  const [bumpMsg, setBumpMsg] = useState<string | null>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const startedAt = useRef<number>(performance.now());
  const lastAddedRef = useRef<string | null>(null);
  const pressTimer = useRef<ReturnType<typeof setTimeout> | null>(null);
  const pressFired = useRef(false);

  useEffect(() => {
    const t = setTimeout(() => inputRef.current?.focus(), 60);
    return () => clearTimeout(t);
  }, []);

  // Recently sold products (from invoices), latest first, unique, in-stock
  const recentProducts: Product[] = useMemo(() => {
    const seen = new Set<string>();
    const out: Product[] = [];
    for (let i = 0; i < p.invoices.length && out.length < 6; i++) {
      for (const it of (p.invoices[i] as Invoice).items) {
        if (seen.has(it.productId)) continue;
        seen.add(it.productId);
        const pr = p.products.find((x: Product) => x.id === it.productId);
        if (pr && pr.stock > 0) out.push(pr);
        if (out.length >= 6) break;
      }
    }
    return out;
  }, [p.invoices, p.products]);

  const subtotal = cart.reduce((s, c) => s + (p.products.find((pr: Product) => pr.id === c.productId)?.price ?? 0) * c.qty, 0);
  const totalQty = cart.reduce((s, c) => s + c.qty, 0);

  const flashOver = (m: string) => { setOverStockMsg(m); setTimeout(() => setOverStockMsg(null), 1500); };
  const flashBump = (m: string) => { setBumpMsg(m); setTimeout(() => setBumpMsg(null), 1200); };

  const addN = (pr: Product, n: number) => {
    if (pr.stock === 0) return;
    setCart(c => {
      const ex = c.find(x => x.productId === pr.id);
      const cur = ex?.qty ?? 0;
      const next = Math.min(cur + n, pr.stock);
      if (next === cur) { flashOver("المطلوب أكبر من المتوفر"); return c; }
      if (next < cur + n) flashOver("توقفنا عند الحد المتوفر");
      lastAddedRef.current = pr.id;
      return ex
        ? c.map(x => x.productId === pr.id ? { ...x, qty: next } : x)
        : [...c, { productId: pr.id, qty: next }];
    });
  };
  const add = (pr: Product) => addN(pr, 1);
  const addFive = (pr: Product) => { addN(pr, 5); flashBump("أُضيف ×5"); };

  const setQty = (pid: string, qty: number) => {
    const pr = p.products.find((x: Product) => x.id === pid)!;
    if (qty > pr.stock) { flashOver("المطلوب أكبر من المتوفر"); return; }
    if (qty <= 0) setCart(c => c.filter(x => x.productId !== pid));
    else setCart(c => c.map(x => x.productId === pid ? { ...x, qty } : x));
  };

  const bumpLast = () => {
    const id = lastAddedRef.current;
    if (!id) return;
    const pr = p.products.find((x: Product) => x.id === id);
    if (pr) addN(pr, 1);
  };

  // Long-press handlers (350ms) → addFive; otherwise normal add on release.
  const onPressStart = (pr: Product) => {
    pressFired.current = false;
    pressTimer.current = setTimeout(() => { pressFired.current = true; addFive(pr); }, 350);
  };
  const onPressEnd = (pr: Product) => {
    if (pressTimer.current) clearTimeout(pressTimer.current);
    if (!pressFired.current) add(pr);
  };
  const onPressCancel = () => { if (pressTimer.current) clearTimeout(pressTimer.current); };

  const filtered = p.products.filter((pr: Product) => !q || pr.name.includes(q));

  const save = async () => {
    if (cart.length === 0 || subtotal <= 0) return;
    const items: InvoiceItem[] = cart.map(c => {
      const pr = p.products.find((x: Product) => x.id === c.productId)!;
      return { productId: pr.id, name: pr.name, qty: c.qty, price: pr.price, cost: pr.cost };
    });
    const cogs = items.reduce((s, it) => s + it.cost * it.qty, 0);
    const created = await p.createSaleAsync({
      items, total: subtotal, paid: subtotal,
      delivery: "direct" as const, method: "cash" as const,
    });
    const elapsedMs = Math.round(performance.now() - startedAt.current);
    p.setLastSaleSummary({ total: subtotal, paid: subtotal, profit: subtotal - cogs, elapsedMs });
    p.setLastCreatedInvoiceId(created.orderId);
    p.setScreen("sale_success");
  };

  return (
    <div className="min-h-[100dvh] bg-background flex flex-col" dir="rtl">
      <TopBar title="بيع سريع" onBack={p.back} onHome={p.goHome} right={
        <span className="px-2 py-1 rounded-full bg-success-soft text-success text-[10px] font-bold">نقدي · كامل</span>
      } />

      <div className="px-4 pt-3 pb-2 sticky top-[57px] bg-background z-20">
        <div className="relative">
          <Search className="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground pointer-events-none" />
          <input
            ref={inputRef}
            value={q}
            onChange={e => setQ(e.target.value)}
            placeholder="ابحث عن منتج"
            dir="rtl"
            inputMode="search"
            autoComplete="off"
            className="w-full rounded-xl border border-border bg-card pr-9 pl-9 py-3 text-[16px] text-right"
          />
          {q && (
            <button onClick={() => { setQ(""); inputRef.current?.focus(); }} className="absolute left-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-muted" aria-label="مسح">
              <X className="w-4 h-4 text-muted-foreground" />
            </button>
          )}
        </div>

        {recentProducts.length > 0 && !q && (
          <div className="mt-2 -mx-4 px-4 flex gap-2 overflow-x-auto no-scrollbar" style={{ scrollbarWidth: "none" }}>
            {recentProducts.map(pr => (
              <button
                key={pr.id}
                onClick={() => add(pr)}
                className="shrink-0 rounded-full bg-primary-soft text-primary px-3 py-2 text-xs font-bold flex items-center gap-1 active:scale-95 transition"
              >
                <Plus className="w-3 h-3" />
                <span className="max-w-[110px] truncate">{pr.name}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="px-4 flex-1 pb-4" style={{ overscrollBehavior: "contain" }}>
        {filtered.length === 0 ? (
          <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">
            <PackageX className="w-8 h-8 mx-auto mb-2 opacity-50" />لا منتج بهذا الاسم
          </div>
        ) : (
          <div className="grid grid-cols-3 gap-2">
            {filtered.map((pr: Product) => {
              const out = pr.stock === 0;
              const inCart = cart.find(c => c.productId === pr.id)?.qty ?? 0;
              return (
                <button
                  key={pr.id}
                  disabled={out}
                  onPointerDown={() => !out && onPressStart(pr)}
                  onPointerUp={() => !out && onPressEnd(pr)}
                  onPointerLeave={onPressCancel}
                  onPointerCancel={onPressCancel}
                  className={`relative text-right rounded-2xl border p-2 min-h-[76px] transition active:scale-[0.96] touch-manipulation select-none ${out ? "bg-muted border-border opacity-60" : inCart > 0 ? "bg-primary-soft border-primary/40" : "bg-card border-border"}`}
                >
                  {inCart > 0 && (
                    <span className="absolute top-1 left-1 min-w-[20px] h-5 px-1 rounded-full bg-primary text-primary-foreground text-[10px] font-bold flex items-center justify-center num">{inCart}</span>
                  )}
                  <div className="font-bold text-[12px] leading-tight line-clamp-2 min-h-[28px]">{pr.name}</div>
                  <div className="mt-1 flex items-center justify-between gap-1">
                    <Money v={pr.price} className="text-[11px]" />
                    {out ? <span className="text-[9px] text-debt font-bold">نفد</span>
                      : pr.stock <= pr.lowAt ? <span className="text-[9px] text-warn font-bold num">{pr.stock}</span>
                        : null}
                  </div>
                </button>
              );
            })}
          </div>
        )}
      </div>

      {overStockMsg && <Toast text={overStockMsg} kind="warn" />}
      {bumpMsg && !overStockMsg && <Toast text={bumpMsg} kind="success" />}

      {cart.length > 0 && (
        <div className="sticky bottom-0 bg-card border-t border-border px-3 pt-2 pb-[max(env(safe-area-inset-bottom),10px)] z-20">
          <div className="max-h-28 overflow-y-auto space-y-1 mb-2">
            {cart.map(ci => {
              const pr = p.products.find((x: Product) => x.id === ci.productId)!;
              return (
                <div key={ci.productId} className="flex items-center gap-2">
                  <button onClick={() => setQty(ci.productId, 0)} className="p-1 text-debt shrink-0" aria-label="حذف"><Trash2 className="w-4 h-4" /></button>
                  <div className="flex-1 text-sm truncate min-w-0">{pr.name}</div>
                  <div className="flex items-center gap-1 shrink-0">
                    <button onClick={() => setQty(ci.productId, ci.qty - 1)} className="w-7 h-7 rounded-full bg-muted flex items-center justify-center" aria-label="نقص"><Minus className="w-3 h-3" /></button>
                    <span className="w-6 text-center text-xs font-bold num">{ci.qty}</span>
                    <button onClick={() => setQty(ci.productId, ci.qty + 1)} className="w-7 h-7 rounded-full bg-muted flex items-center justify-center" aria-label="زيادة"><Plus className="w-3 h-3" /></button>
                  </div>
                  <Money v={pr.price * ci.qty} className="text-xs w-14 text-left shrink-0 num" />
                </div>
              );
            })}
          </div>

          <div className="grid grid-cols-[auto_1fr] items-stretch gap-2">
            <button
              onClick={() => p.setScreen("sale")}
              className="rounded-2xl bg-card border border-border px-3 text-[11px] font-bold text-muted-foreground"
              aria-label="بيع متقدم"
            >متقدّم</button>
            <button
              onClick={save}
              className="rounded-2xl bg-primary text-primary-foreground py-3.5 font-bold flex items-center justify-between px-4 active:scale-[0.98] transition min-h-[56px]"
            >
              <span className="text-sm">إصدار الفاتورة</span>
              <span className="flex items-center gap-2 text-[12px] opacity-95">
                <span className="num">{totalQty}</span>
                <span className="opacity-60">قطعة ·</span>
                <span className="num font-extrabold text-base">{fmt(subtotal)}</span>
                <span className="text-[10px] opacity-80">د.ل</span>
              </span>
            </button>
          </div>

          {lastAddedRef.current && (
            <button onClick={bumpLast} className="mt-2 w-full text-[11px] text-primary font-bold py-1 flex items-center justify-center gap-1">
              <Plus className="w-3 h-3" /> تكرار آخر منتج
            </button>
          )}
        </div>
      )}
    </div>
  );
}



/* --------------- DAY CLOSE --------------- */
function DayCloseScreen(p: any) {
  // Day close always reflects TODAY only — independent of dashboard period filter.
  // This matches the close_day RPC which computes today's snapshot server-side.
  const tenantTz: string = p.tenantTz ?? "Africa/Tripoli";
  const t = useMemo(() => {
    const tzKey = (iso?: string) =>
      iso ? new Intl.DateTimeFormat("en-CA", { timeZone: tenantTz }).format(new Date(iso)) : "";
    const todayKey = tenantTodayKey(tenantTz);
    const isToday = (iso?: string) => !!iso && tzKey(iso) === todayKey;
    const invs: Invoice[] = (p.invoices ?? []).filter((i: Invoice) => isToday(i.createdAt));
    const pays: Payment[] = (p.payments ?? []).filter((pm: Payment) => isToday(pm.createdAt));
    const exps: Expense[] = (p.expenses ?? []).filter((e: Expense) => isToday(e.createdAt));

    const sales = invs.reduce((s, i) => s + i.total, 0);
    const collected = pays.reduce((s, pm) => s + pm.amount, 0);
    const expenseTotal = exps.reduce((s, e) => s + e.amount, 0);
    // Mirror close_day RPC: cash-basis profit allocated by today's payments.
    // For each payment today linked to an order, take payment.amount/order.total
    // multiplied by the order's item-margin sum, then subtract today's expenses.
    const invById = new Map<string, Invoice>((p.invoices ?? []).map((i: Invoice) => [i.id, i]));
    const realizedProfit = pays.reduce((s, pm) => {
      if (!pm.invoiceId) return s;
      const inv = invById.get(pm.invoiceId);
      if (!inv || inv.total <= 0) return s;
      const margin = getInvoiceItemMargin(inv);
      return s + (pm.amount / inv.total) * margin;
    }, 0) - expenseTotal;

    // open stocks across ALL invoices (not just today)
    const customerDebts: number = p.rawTotals?.customerDebts ?? p.totals.customerDebts;
    const unsettledCustody: number = p.rawTotals?.unsettledCustody ?? p.totals.unsettledCustody;
    const cashToday = collected - expenseTotal;
    return { sales, collected, expenseTotal, realizedProfit, customerDebts, unsettledCustody, cashToday };
  }, [p.invoices, p.payments, p.expenses, p.rawTotals, p.totals]);
  const Row = ({ label, v, color, hint }: { label: string; v: number; color?: string; hint?: string }) => (
    <div className="flex items-start justify-between py-3">
      <div>
        <div className="text-sm font-medium">{label}</div>
        {hint && <div className="text-[11px] text-muted-foreground mt-0.5">{hint}</div>}
      </div>
      <Money v={v} className={`text-base font-bold ${color ?? ""}`} />
    </div>
  );
  return (
    <div className="min-h-[100dvh] bg-background">
      <TopBar title="إقفال اليوم" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3 pb-32">
        <div className="rounded-2xl bg-primary-soft border border-primary/20 p-4 text-xs text-primary flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>ملخص نهاية اليوم. الأرقام مأخوذة من نفس النموذج المالي — بدون أي تأثير على البيانات.</span>
        </div>

        <div className="rounded-2xl bg-card border border-border px-4 divide-y divide-border">
          <Row label="دخل فعلًا اليوم" v={t.collected} color="text-success" hint="مجموع المقبوض من بيع وتحصيل وتسوية" />
          <Row label="مصروفات اليوم" v={t.expenseTotal} color="text-debt" hint="نقل، إنترنت، إلخ" />
          <Row label="ديون لم تُحصّل" v={t.customerDebts} color="text-debt" hint="على العملاء" />
          <Row label="عند المندوب (لم تُسوَّ)" v={t.unsettledCustody} color="text-warn" hint="عهدة جاهزة للتسوية" />
        </div>

        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="text-xs font-bold text-muted-foreground mb-2">المخزون</div>
          {p.lowStock + p.outStock === 0 ? (
            <div className="text-sm text-success flex items-center gap-2"><CheckCircle2 className="w-4 h-4" /> لا منتجات تحتاج تجديد</div>
          ) : (
            <div className="space-y-1.5 text-sm">
              {p.lowStock > 0 && <div className="text-warn flex items-center gap-2"><AlertTriangle className="w-4 h-4" /> <span className="num">{p.lowStock}</span> منتجات قاربت النفاد</div>}
              {p.outStock > 0 && <div className="text-debt flex items-center gap-2"><PackageX className="w-4 h-4" /> <span className="num">{p.outStock}</span> منتجات نفدت بالكامل</div>}
            </div>
          )}
        </div>

        <div className="rounded-2xl bg-success-soft border border-success/20 p-4">
          <div className="text-xs text-muted-foreground">صافي الكاش اليوم</div>
          <Money v={t.cashToday} className={`text-3xl mt-1 ${t.cashToday < 0 ? "text-debt" : "text-success"}`} />
          <div className="text-[11px] text-muted-foreground mt-1">المحصّل − المصروفات</div>
        </div>
      </div>

      <div className="px-4 mt-3">
        <div className="rounded-2xl bg-muted/40 border border-border p-3 text-[11px] text-muted-foreground text-center leading-relaxed">
          هذه الشاشة ملخّص يومي فقط — لا تُقفل البيانات ولا تُعدّل أي أرقام مالية.
        </div>
      </div>
      <div className="fixed bottom-0 inset-x-0 z-30">
        <div className="mx-auto max-w-md bg-card border-t border-border p-3 pb-[max(env(safe-area-inset-bottom),12px)]">
          {p.closedToday ? (
            <button onClick={() => p.back()} className="w-full rounded-2xl bg-muted text-foreground py-3 font-bold">
              ✓ تم إقفال اليوم مسبقًا — رجوع
            </button>
          ) : (
            <button
              onClick={async () => {
                try {
                  await p.closeDayAsync({});
                  p.showToast("تم حفظ إقفال اليوم");
                  p.back();
                } catch (e: any) {
                  p.showToast("تعذّر الحفظ");
                }
              }}
              className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold"
            >تثبيت إقفال اليوم</button>
          )}
        </div>
      </div>
    </div>
  );
}

/* --------------- QUICK EXPENSE SHEET --------------- */
function QuickExpenseSheet({ onClose, onSave }: { onClose: () => void; onSave: (amount: number, type: string, method: "cash" | "transfer") => void }) {
  const [amt, setAmt] = useState("");
  const [type, setType] = useState("");
  const [method, setMethod] = useState<"cash" | "transfer">("cash");
  const presets = ["نقل", "إنترنت", "كهرباء", "إيجار", "أجور", "أخرى"];
  const valid = Number(amt) > 0 && type.trim().length > 0;
  return (
    <Sheet onClose={onClose} title="إضافة مصروف سريع">
      <div className="space-y-3">
        <div>
          <label className="text-xs font-bold text-muted-foreground">المبلغ</label>
          <input value={amt} onChange={e => setAmt(e.target.value)} inputMode="decimal" placeholder="0" className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right" />
        </div>
        <div>
          <label className="text-xs font-bold text-muted-foreground">السبب</label>
          <input value={type} onChange={e => setType(e.target.value)} placeholder="مثال: نقل" className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-sm text-right" />
          <div className="mt-2 flex flex-wrap gap-1.5">
            {presets.map(pr => (
              <button key={pr} onClick={() => setType(pr)} className={`px-3 py-1 rounded-full text-xs font-bold ${type === pr ? "bg-primary text-primary-foreground" : "bg-muted"}`}>{pr}</button>
            ))}
          </div>
        </div>
        <div>
          <label className="text-xs font-bold text-muted-foreground">طريقة الدفع</label>
          <div className="mt-1 grid grid-cols-2 gap-2">
            <button onClick={() => setMethod("cash")} className={`py-2 rounded-xl text-sm font-bold ${method === "cash" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>نقدي</button>
            <button onClick={() => setMethod("transfer")} className={`py-2 rounded-xl text-sm font-bold ${method === "transfer" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>تحويل</button>
          </div>
        </div>
        <button disabled={!valid} onClick={() => onSave(Number(amt), type.trim(), method)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">حفظ المصروف</button>
      </div>
    </Sheet>
  );
}

/* --------------- MONEY DETAILS SHEET --------------- */
function MoneyDetailsSheet({ totals, period, onClose, onOpenProfit }: { totals: any; period: Period; onClose: () => void; onOpenProfit: () => void }) {
  const periodLabel = period === "day" ? "اليوم" : period === "week" ? "الأسبوع" : "الشهر";
  const Row = ({ label, v, color, hint }: { label: string; v: number; color?: string; hint?: string }) => (
    <div className="flex items-start justify-between py-2.5">
      <div>
        <div className="text-sm">{label}</div>
        {hint && <div className="text-[11px] text-muted-foreground mt-0.5">{hint}</div>}
      </div>
      <Money v={v} className={color ?? ""} />
    </div>
  );
  return (
    <Sheet onClose={onClose} title={`حركة ${periodLabel} المالية`}>
      <div className="space-y-3">
        <div className="rounded-xl bg-muted p-3 text-[11px] text-muted-foreground">
          الفصل المالي: <b>بعت</b> = قيمة الفواتير. <b>محصّل</b> = ما دخل فعلًا. <b>دين</b> = على العميل. <b>عهدة</b> = عند المندوب.
        </div>

        <div className="rounded-xl bg-card border border-border px-3 divide-y divide-border">
          <Row label="بعت (قيمة الفواتير)" v={totals.sales} hint="شامل الديون — ليس كاش" />
          <Row label="المحصّل فعلًا" v={totals.collected} color="text-success" hint="من بيع + تحصيل + تسوية" />
          <Row label="المصروفات" v={totals.expenseTotal} color="text-debt" />
          <Row label="صافي الكاش" v={totals.cashToday} color={totals.cashToday < 0 ? "text-debt font-bold" : "text-success font-bold"} hint="المحصّل − المصروفات" />
        </div>

        <div className="rounded-xl bg-card border border-border px-3 divide-y divide-border">
          <Row label="ديون على العملاء" v={totals.customerDebts} color="text-debt" />
          <Row label="عند المندوب (غير مصفّاة)" v={totals.unsettledCustody} color="text-warn" />
        </div>

        <button onClick={onOpenProfit} className="w-full rounded-xl bg-card border border-border py-2 text-xs font-bold text-muted-foreground hover:text-primary">
          الربح في شاشة مستقلة ←
        </button>
      </div>
    </Sheet>
  );
}

/* Sheet, Toast: moved to src/features/shared/ (R1) */


/* --------------- PILOT HEALTH DASHBOARD --------------- */
/* PilotScreen: moved to src/features/pilot/PilotScreen.tsx (R4b) */

