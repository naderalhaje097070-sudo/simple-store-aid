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

/* ============================== MOCK DATA ============================== */

type Product = { id: string; name: string; price: number; cost: number; stock: number; lowAt: number; is_discount?: boolean };
type Customer = { id: string; name: string; phone?: string };
type Courier = { id: string; name: string; phone?: string };
type InvoiceItem = { productId: string; name: string; qty: number; price: number; cost: number };
type Invoice = {
  id: string;
  number: string;
  items: InvoiceItem[];
  total: number;
  paid: number;
  customerId?: string;
  delivery: "direct" | "courier";
  courierId?: string;
  status: "paid" | "partial" | "debt";
  courierState?: "pending" | "delivered_none" | "delivered_partial" | "delivered_full" | "returned";
  collectedByCourier?: number;
  time: string;
  createdAt: string;
};
type Expense = { id: string; type: string; amount: number; method: "cash" | "transfer"; time: string; createdAt: string; note?: string };
type Payment = {
  id: string;
  kind: "sale" | "debt_collection" | "settlement";
  method: "cash" | "transfer" | "settlement";
  amount: number;
  invoiceId?: string;
  invoiceNumber?: string;
  customerId?: string;
  courierId?: string;
  time: string;
  createdAt: string;
};

// Phase 3: كل البيانات تأتي من قاعدة بيانات المحل عبر hooks في src/lib/db.ts

/* ============================== HELPERS ============================== */

const fmt = (n: number) => new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(n));
const Money = ({ v, className = "" }: { v: number; className?: string }) => (
  <span className={className}><span className="num font-semibold">{fmt(v)}</span> <span className="text-xs opacity-70">د.ل</span></span>
);

/* ============================== MAIN APP ============================== */

type Screen =
  | "home" | "invoices" | "invoice_detail" | "inventory" | "shop"
  | "profit" | "collected" | "debts" | "debt_customer"
  | "courier_custody" | "settlements" | "expenses" | "customers" | "couriers" | "settings"
  | "sale" | "sale_quick" | "sale_success" | "day_close" | "pilot";

type Period = "day" | "week" | "month";

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
    const cogs = invP.reduce((s, i) => s + i.items.reduce((a, it) => a + it.cost * it.qty, 0), 0);
    const expenseTotal = expP.reduce((s, e) => s + e.amount, 0);
    const collected = payP.reduce((s, pm) => s + pm.amount, 0);
    const grossProfit = sales - cogs;
    const netProfit = grossProfit - expenseTotal;
    // Realized profit per-order (matches close_day RPC formula):
    // for each invoice take (price-cost)*qty * min(paid/total, 1)
    const realizedCogs = invP.reduce((s, i) => {
      const ratio = i.total > 0 ? Math.min(1, i.paid / i.total) : 0;
      return s + i.items.reduce((a, it) => a + it.cost * it.qty * ratio, 0);
    }, 0);
    const realizedRevenue = invP.reduce((s, i) => {
      const ratio = i.total > 0 ? Math.min(1, i.paid / i.total) : 0;
      return s + i.total * ratio;
    }, 0);
    const realizedProfit = realizedRevenue - realizedCogs - expenseTotal;
    const cashToday = collected - expenseTotal;

    // Stocks — current balances across ALL invoices (not period-bound)
    const directDebt = invoices.filter(i => i.delivery === "direct").reduce((s, i) => s + (i.total - i.paid), 0);
    const courierCustomerDebt = invoices
      .filter(i => i.delivery === "courier")
      .reduce((s, i) => {
        const cs = i.courierState ?? "pending";
        if (cs === "delivered_none") return s + i.total;
        if (cs === "delivered_partial") return s + (i.total - (i.collectedByCourier ?? 0));
        return s;
      }, 0);
    const customerDebts = directDebt + courierCustomerDebt;

    const unsettledCustody = invoices
      .filter(i => i.delivery === "courier" && (i.courierState === "delivered_partial" || i.courierState === "delivered_full"))
      .reduce((s, i) => s + (i.collectedByCourier ?? 0), 0);

    const inTransit = invoices
      .filter(i => i.delivery === "courier" && (i.courierState === "pending" || !i.courierState))
      .reduce((s, i) => s + i.total, 0);

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
      (i.status === "debt" || i.status === "partial") &&
      now - new Date(i.createdAt).getTime() > THIRTY_DAYS
    ).length;
    const allDebts = invoices.filter(i => i.delivery === "direct" && (i.status === "debt" || i.status === "partial")).length;
    if (oldDebts > 0) list.push({ id: "olddebt", tone: "debt", icon: CircleDollarSign, text: `${oldDebts} فواتير دين أقدم من ٣٠ يوم`, onClick: () => go("debts") });
    else if (allDebts > 0) list.push({ id: "debt", tone: "debt", icon: CircleDollarSign, text: `${allDebts} فواتير دين بحاجة تحصيل`, onClick: () => go("debts") });
    const pendingCourier = invoices.filter(i => i.delivery === "courier" && (i.courierState === "pending" || i.courierState === "delivered_partial")).length;
    if (pendingCourier > 0) list.push({ id: "pending", tone: "info", icon: Clock, text: `${pendingCourier} طلبات توصيل غير مكتملة`, onClick: () => go("courier_custody") });
    if (totals.collected > 0 && totals.expenseTotal / totals.collected > 0.3) list.push({ id: "exp", tone: "warn", icon: ArrowDownCircle, text: "مصروفات الفترة مرتفعة نسبيًا", onClick: () => go("expenses") });
    return list;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [invoices, totals.unsettledCustody, totals.collected, totals.expenseTotal, lowStock, outStock]);


  const ctx = {
    products, customers, setCustomers, couriers, invoices, expenses, payments, myRole,
    totals: scaledTotals, rawTotals: totals, lowStock, outStock,
    period, setPeriod, alerts, closedToday, setClosedToday, dayCloses,
    tenantId, tenantTz, tenantSettings,
    closeDayAsync: (input: Parameters<ReturnType<typeof useCloseDay>["mutateAsync"]>[0]) => closeDayMut.mutateAsync(input),
    go, back, setOpenInvoiceId, openInvoiceId, setOpenCustomerId, openCustomerId, setOpenCourierId, openCourierId,
    setLastSaleSummary, lastSaleSummary, setScreen,
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

function DesktopSidebar({
  screen, setScreen, myRole, onSale, onDayClose, onQuickExpense,
}: {
  screen: Screen; setScreen: (s: Screen) => void; myRole?: string;
  onSale: () => void; onDayClose: () => void; onQuickExpense: () => void;
}) {
  const Item = ({ id, label, Icon }: { id: Screen; label: string; Icon: typeof Home }) => {
    const active = screen === id;
    return (
      <button
        onClick={() => setScreen(id)}
        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm transition ${
          active ? "bg-primary-soft text-primary font-bold" : "text-muted-foreground hover:bg-muted hover:text-foreground"
        }`}
      >
        <Icon className="w-4 h-4 shrink-0" />
        <span className="flex-1 text-right truncate">{label}</span>
      </button>
    );
  };
  const Group = ({ title, children }: { title: string; children: React.ReactNode }) => (
    <div className="mt-4">
      <div className="px-3 pb-1.5 text-[10px] font-bold text-muted-foreground/70 tracking-wider">{title}</div>
      <div className="space-y-0.5">{children}</div>
    </div>
  );
  return (
    <aside className="hidden md:flex md:flex-col md:w-64 md:shrink-0 md:sticky md:top-0 md:h-screen border-l border-border bg-card">
      <div className="px-5 py-4 border-b border-border">
        <div className="flex items-center gap-2">
          <div className="w-9 h-9 rounded-2xl bg-primary text-primary-foreground grid place-items-center font-black">م</div>
          <div>
            <div className="text-sm font-black leading-tight">منجز</div>
            <div className="text-[10px] text-muted-foreground">دفتر المحل الذكي</div>
          </div>
        </div>
      </div>

      <div className="px-3 py-3 border-b border-border space-y-2">
        <button onClick={onSale} className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-bold hover:opacity-90">
          <Plus className="w-4 h-4" /> بيع سريع
        </button>
        <div className="grid grid-cols-2 gap-2">
          <button onClick={onQuickExpense} className="py-2 rounded-xl bg-muted text-xs font-bold hover:bg-muted/70">+ مصروف</button>
          <button onClick={onDayClose} className="py-2 rounded-xl bg-muted text-xs font-bold hover:bg-muted/70">إقفال اليوم</button>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto px-2 py-3">
        <Group title="اليومي">
          <Item id="home" label="الرئيسية" Icon={Home} />
          <Item id="invoices" label="الفواتير" Icon={ReceiptText} />
          <Item id="collected" label="المحصّل فعليًا" Icon={Wallet} />
          <Item id="profit" label="الربح" Icon={TrendingUp} />
          <Item id="expenses" label="المصروفات" Icon={ArrowDownCircle} />
        </Group>
        <Group title="الديون والعهدة">
          <Item id="debts" label="ديون العملاء" Icon={CircleDollarSign} />
          <Item id="courier_custody" label="عهدة المندوب" Icon={Truck} />
          <Item id="settlements" label="التسويات" Icon={Banknote} />
        </Group>
        <Group title="الإدارة">
          <Item id="inventory" label="المخزون" Icon={Boxes} />
          <Item id="customers" label="العملاء" Icon={Users} />
          <Item id="couriers" label="المندوبون" Icon={Truck} />
          <Item id="shop" label="أقسام المحل" Icon={Store} />
          <Item id="settings" label="الإعدادات" Icon={SettingsIcon} />
          {myRole === "owner" && <Item id="pilot" label="صحة النظام" Icon={Activity} />}
        </Group>
      </nav>

      <div className="px-4 py-3 border-t border-border text-[10px] text-muted-foreground text-center">
        نسخة تجريبية مغلقة
      </div>
    </aside>
  );
}

/* ============================== SHARED UI ============================== */

function TopBar({ title, onBack, right }: { title: string; onBack?: () => void; right?: React.ReactNode }) {
  return (
    <div className="sticky top-0 z-30 bg-background/95 backdrop-blur border-b border-border px-4 py-3 flex items-center gap-3">
      {onBack && (
        <button onClick={onBack} className="p-2 -mr-2 rounded-full hover:bg-muted">
          <ArrowLeft className="w-5 h-5 rotate-180" />
        </button>
      )}
      <h1 className="text-lg font-bold flex-1">{title}</h1>
      {right}
    </div>
  );
}

function StatusChip({ kind, children, icon }: { kind: "paid" | "partial" | "debt" | "warn" | "info" | "profit"; children: React.ReactNode; icon?: React.ReactNode }) {
  const styles: Record<string, string> = {
    paid: "bg-success-soft text-success",
    partial: "bg-warn-soft text-warn",
    debt: "bg-debt-soft text-debt",
    warn: "bg-warn-soft text-warn",
    info: "bg-info-soft text-info",
    profit: "bg-profit-soft text-profit",
  };
  return (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${styles[kind]}`}>
      {icon}{children}
    </span>
  );
}

function BottomNav({ screen, setScreen, onSale }: { screen: Screen; setScreen: (s: Screen) => void; onSale: () => void }) {
  const Tab = ({ id, label, Icon }: { id: Screen; label: string; Icon: typeof Home }) => {
    const active = screen === id;
    return (
      <button onClick={() => setScreen(id)} className="flex-1 flex flex-col items-center gap-1 py-2">
        <Icon className={`w-5 h-5 ${active ? "text-primary" : "text-muted-foreground"}`} />
        <span className={`text-[11px] ${active ? "text-primary font-bold" : "text-muted-foreground"}`}>{label}</span>
      </button>
    );
  };
  return (
    <div className="fixed bottom-0 inset-x-0 z-40 pointer-events-none">
      <div className="mx-auto max-w-md relative">
        <div className="bg-card border-t border-border pointer-events-auto flex items-stretch px-2 pb-[max(env(safe-area-inset-bottom),8px)] pt-1">
          <Tab id="home" label="الرئيسية" Icon={Home} />
          <Tab id="invoices" label="الفواتير" Icon={ReceiptText} />
          <div className="w-16" />
          <Tab id="inventory" label="المخزون" Icon={Boxes} />
          <Tab id="shop" label="المحل" Icon={Store} />
        </div>
        <button
          onClick={onSale}
          className="absolute left-1/2 -translate-x-1/2 -top-6 pointer-events-auto bg-primary text-primary-foreground rounded-full w-16 h-16 shadow-lg shadow-primary/30 flex flex-col items-center justify-center font-bold active:scale-95 transition"
          aria-label="بيع جديد"
        >
          <Plus className="w-6 h-6" />
          <span className="text-[11px] -mt-0.5">بيع</span>
        </button>
      </div>
    </div>
  );
}

/* ============================== SCREENS ============================== */

function HomeScreen(p: any) {
  const { totals, alerts, period, setPeriod, invoices, go, setOpenInvoiceId, setQuickExpenseOpen, setMoneyDetailsOpen, closedToday } = p;
  const recent = invoices.slice(-3).reverse();

  // Status: needs attention if there are debt/custody alerts, otherwise ok
  const status: "good" | "ok" | "attention" =
    alerts.some((a: any) => a.tone === "debt") ? "attention"
      : alerts.length >= 2 ? "ok"
        : "good";
  const statusMeta = {
    good: { l: "وضعك اليوم: جيد", color: "text-success", bg: "bg-success-soft", emoji: "👍" },
    ok: { l: "وضعك اليوم: مقبول", color: "text-warn", bg: "bg-warn-soft", emoji: "🟡" },
    attention: { l: "وضعك اليوم: يحتاج انتباه", color: "text-debt", bg: "bg-debt-soft", emoji: "⚠️" },
  }[status];

  const periodLabel = period === "day" ? "اليوم" : period === "week" ? "هذا الأسبوع" : "هذا الشهر";

  return (
    <>
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <div>
          <div className="text-2xl font-extrabold text-primary leading-none">منجز</div>
          <div className="text-xs text-muted-foreground mt-1">بِع بسرعة — واعرف نهاية اليوم فلوسك وين</div>
        </div>
        {closedToday && <span className="px-3 py-1 rounded-full bg-success-soft text-success text-[11px] font-bold">تم الإقفال</span>}
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
        {[{ id: "day", l: "اليوم" }, { id: "week", l: "الأسبوع" }, { id: "month", l: "الشهر" }].map(x => (
          <button key={x.id} onClick={() => setPeriod(x.id as any)} className={`px-4 py-1.5 rounded-full text-xs font-bold ${period === x.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{x.l}</button>
        ))}
      </div>

      {/* Status / answer card — 3 separated numbers: collected / customer debts / courier custody */}
      <div className="px-4">
        <div className={`rounded-2xl ${statusMeta.bg} p-5 border border-border/50`}>
          <div className={`text-sm font-bold ${statusMeta.color} flex items-center gap-2`}>
            <span>{statusMeta.emoji}</span>
            <span>{statusMeta.l}</span>
            <span className="text-[10px] font-normal text-muted-foreground mr-auto">{periodLabel}</span>
          </div>
          <div className="mt-4 space-y-3">
            <div className="rounded-xl bg-card/60 p-3">
              <div className="text-[11px] text-muted-foreground">المحصّل فعليًا</div>
              <Money v={totals.collected} className="text-2xl text-success font-bold" />
              <div className="text-[10px] text-muted-foreground mt-0.5">دخل جيبك فعلًا</div>
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div className="rounded-xl bg-card/60 p-3">
                <div className="text-[11px] text-muted-foreground">ديون العملاء</div>
                <Money v={totals.customerDebts} className="text-lg text-debt font-bold" />
                <div className="text-[10px] text-muted-foreground mt-0.5">لم تدخل بعد</div>
              </div>
              <div className="rounded-xl bg-card/60 p-3">
                <div className="text-[11px] text-muted-foreground">عهدة المندوب</div>
                <Money v={totals.unsettledCustody} className="text-lg text-warn font-bold" />
                <div className="text-[10px] text-muted-foreground mt-0.5">قيد التسوية</div>
              </div>
            </div>
          </div>
          <button onClick={() => setMoneyDetailsOpen(true)} className="mt-4 w-full text-center text-xs font-bold text-primary py-2 border-t border-border/50">
            عرض التفاصيل المالية (صافي الكاش، الربح…)
          </button>
        </div>
      </div>

      {/* Secondary quick actions */}
      <div className="px-4 mt-4">
        <div className="text-xs font-bold text-muted-foreground mb-2">إجراءات سريعة</div>
        <div className="grid grid-cols-3 gap-2.5">
          {[
            { l: "تحصيل دين", i: Wallet, soft: "bg-debt-soft", color: "text-debt", on: () => go("debts") },
            { l: "تسوية مندوب", i: Truck, soft: "bg-warn-soft", color: "text-warn", on: () => go("settlements") },
            { l: "إضافة مصروف", i: ArrowDownCircle, soft: "bg-info-soft", color: "text-info", on: () => setQuickExpenseOpen(true) },
          ].map((a, idx) => (
            <button key={idx} onClick={a.on} className={`rounded-2xl ${a.soft} p-3 flex flex-col items-center gap-1.5 active:scale-[0.97] transition`}>
              <div className={`w-9 h-9 rounded-full bg-card flex items-center justify-center ${a.color}`}>
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
            {alerts.map((a: any) => {
              const tone = a.tone === "debt" ? "text-debt" : a.tone === "warn" ? "text-warn" : "text-info";
              return (
                <button key={a.id} onClick={a.onClick} className="w-full text-right px-4 py-3 flex items-center gap-3 hover:bg-muted active:bg-muted">
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
        <button onClick={() => go("day_close")} className="w-full rounded-2xl bg-card border-2 border-dashed border-primary/40 p-4 flex items-center gap-3 active:scale-[0.99] transition">
          <div className="w-10 h-10 rounded-full bg-primary-soft text-primary flex items-center justify-center"><Banknote className="w-5 h-5" /></div>
          <div className="flex-1 text-right">
            <div className="text-sm font-bold">إقفال اليوم</div>
            <div className="text-[11px] text-muted-foreground">تحقّق نهاية اليوم — تأكيد أن الأرقام صحيحة</div>
          </div>
          <ChevronLeft className="w-4 h-4 text-muted-foreground" />
        </button>
      </div>

      {/* Recent invoices */}
      <div className="px-4 mt-5">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-bold text-muted-foreground">آخر الفواتير</div>
          <button onClick={() => go("invoices")} className="text-xs text-primary font-bold">عرض الكل</button>
        </div>
        <div className="space-y-2">
          {recent.length === 0 && <EmptyState text="ابدأ يومك — لا مبيعات بعد" />}
          {recent.map((inv: Invoice) => <InvoiceRow key={inv.id} inv={inv} customers={p.customers} onOpen={(id) => { setOpenInvoiceId(id); go("invoice_detail"); }} />)}
        </div>
      </div>
    </>
  );
}

function InvoiceRow({ inv, customers, onOpen }: { inv: Invoice; customers: Customer[]; onOpen: (id: string) => void }) {
  const cust = customers.find(c => c.id === inv.customerId);
  const remaining = inv.total - inv.paid;
  return (
    <button onClick={() => onOpen(inv.id)} className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3 active:scale-[0.99]">
      <div className="w-10 h-10 rounded-full bg-muted flex items-center justify-center text-xs font-bold text-muted-foreground">#{inv.number.slice(-2)}</div>
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2">
          <span className="font-bold text-sm">#{inv.number}</span>
          {inv.status === "paid" && <StatusChip kind="paid" icon={<CheckCircle2 className="w-3 h-3" />}>مدفوع</StatusChip>}
          {inv.status === "partial" && <StatusChip kind="partial" icon={<Clock className="w-3 h-3" />}>جزئي</StatusChip>}
          {inv.status === "debt" && <StatusChip kind="debt" icon={<AlertTriangle className="w-3 h-3" />}>دين</StatusChip>}
        </div>
        <div className="text-xs text-muted-foreground mt-0.5 truncate">
          {inv.status === "paid" && !cust ? "بدون عميل" : cust?.name ?? "—"} · {inv.time}
          {inv.delivery === "courier" && " · توصيل"}
        </div>
      </div>
      <div className="text-left">
        <Money v={inv.total} className="text-sm" />
        {remaining > 0 && <div className="text-xs text-debt mt-0.5">متبقي <span className="num">{fmt(remaining)}</span></div>}
      </div>
    </button>
  );
}

/* --------------- INVOICES LIST --------------- */
function InvoicesScreen(p: any) {
  const [filter, setFilter] = useState<"all" | "paid" | "partial" | "debt">("all");
  const { range, setRange } = useDateRange("today");
  const dated = p.invoices.filter((i: Invoice) => inRange(i.createdAt, range));
  const list = dated.filter((i: Invoice) => filter === "all" ? true : i.status === filter);
  const total = list.reduce((s: number, i: Invoice) => s + i.total, 0);
  return (
    <>
      <TopBar title="الفواتير" />
      <div className="px-4 pt-3 space-y-3">
        <DateRangeFilter value={range} onChange={setRange} />
        <div className="rounded-2xl bg-card border border-border p-3 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground">قيمة الفواتير · {range.label} <span className="text-[10px]">(ليست المحصّل)</span></div>
            <div className="text-[11px] text-muted-foreground mb-1">{list.length} فاتورة · بالـ د.ل</div>
            <Money v={total} className="text-lg" />
          </div>
          <Info className="w-4 h-4 text-muted-foreground" />
        </div>
        <div className="flex gap-2 overflow-x-auto pb-1">
          {[
            { id: "all", l: "الكل" }, { id: "paid", l: "مدفوع" }, { id: "partial", l: "جزئي" }, { id: "debt", l: "دين" },
          ].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id as any)} className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${filter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border text-foreground"}`}>{f.l}</button>
          ))}
        </div>
        <div className="space-y-2">
          {list.length === 0 && <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">لا توجد فواتير في هذا النطاق</div>}
          {list.map((inv: Invoice) => <InvoiceRow key={inv.id} inv={inv} customers={p.customers} onOpen={(id) => { p.setOpenInvoiceId(id); p.go("invoice_detail"); }} />)}
        </div>
      </div>
    </>
  );
}

/* --------------- INVOICE DETAIL --------------- */
function InvoiceDetailScreen(p: any) {
  const { data: tenantId } = useTenantId();
  const { data: tenant } = useTenant(tenantId);
  const inv: Invoice | undefined = p.invoices.find((i: Invoice) => i.id === p.openInvoiceId);
  const [pdfBusy, setPdfBusy] = useState(false);
  useEffect(() => { ensureInvoiceFont(); }, []);
  if (!inv) return <><TopBar title="فاتورة" onBack={p.back} /><div className="p-4 text-sm text-muted-foreground">لم يتم العثور على الفاتورة</div></>;
  const cust = p.customers.find((c: Customer) => c.id === inv.customerId);
  const remaining = inv.total - inv.paid;
  const cogs = inv.items.reduce((s, it) => s + it.cost * it.qty, 0);
  const profit = inv.total - cogs;

  const [collectOpen, setCollectOpen] = useState(false);
  const [collectAmt, setCollectAmt] = useState("");
  const [collectMethod, setCollectMethod] = useState<"cash" | "transfer">("cash");

  const submitCollect = async () => {
    const a = Number(collectAmt);
    if (!a || a <= 0 || a > remaining) return;
    await p.collectDebtAsync({ orderId: inv.id, customerId: inv.customerId, amount: a, method: collectMethod });
    setCollectOpen(false); setCollectAmt(""); setCollectMethod("cash");
  };

  return (
    <>
      <TopBar title={`فاتورة #${inv.number}`} onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-muted-foreground">العميل</div>
              <div className="font-bold mt-0.5">{remaining > 0 ? (cust?.name ?? "—") : (cust?.name ?? "بدون عميل")}</div>
            </div>
            {inv.status === "paid" && <StatusChip kind="paid" icon={<CheckCircle2 className="w-3 h-3" />}>مدفوع</StatusChip>}
            {inv.status === "partial" && <StatusChip kind="partial" icon={<Clock className="w-3 h-3" />}>جزئي</StatusChip>}
            {inv.status === "debt" && <StatusChip kind="debt" icon={<AlertTriangle className="w-3 h-3" />}>دين</StatusChip>}
          </div>
          <div className="text-xs text-muted-foreground mt-2">{inv.time} {inv.delivery === "courier" && "· توصيل عبر مندوب"}</div>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="text-xs font-bold text-muted-foreground mb-2">الأصناف</div>
          <div className="space-y-2">
            {inv.items.map((it, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div>{it.name} <span className="text-muted-foreground">× <span className="num">{it.qty}</span></span></div>
                <Money v={it.qty * it.price} />
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4 space-y-2 text-sm">
          <div className="flex justify-between"><span className="text-muted-foreground">الإجمالي</span><Money v={inv.total} /></div>
          <div className="flex justify-between"><span className="text-muted-foreground">المدفوع للصندوق</span><Money v={inv.paid} className="text-success" /></div>
          {inv.delivery === "courier" && (inv.collectedByCourier ?? 0) > 0 && (
            <div className="flex justify-between"><span className="text-muted-foreground">بيد المندوب (عهدة)</span><Money v={inv.collectedByCourier ?? 0} className="text-warn" /></div>
          )}
          <div className="flex justify-between"><span className="text-muted-foreground">المتبقي على العميل</span><Money v={remaining} className={remaining > 0 ? "text-debt" : ""} /></div>
        </div>

        <div className="rounded-2xl bg-profit-soft border border-profit/20 p-4">
          <div className="flex items-center gap-2 text-profit text-xs font-bold"><TrendingUp className="w-4 h-4" /> ربح الفاتورة (تقديري)</div>
          <div className="mt-1"><Money v={profit} className="text-lg text-profit" /></div>
          <div className="text-[11px] text-muted-foreground mt-1">التكلفة وقت البيع: <span className="num">{fmt(cogs)}</span> د.ل</div>
        </div>

        {/* Payment timeline */}
        {(() => {
          const invPayments = (p.payments as Payment[]).filter(pm => pm.invoiceId === inv.id).sort((a, b) => a.time < b.time ? -1 : 1);
          if (invPayments.length === 0 && remaining === inv.total) return null;
          return (
            <div className="rounded-2xl bg-card border border-border p-4">
              <div className="text-xs font-bold text-muted-foreground mb-2">سجل الدفعات</div>
              <div className="space-y-1.5">
                {invPayments.map(pm => (
                  <div key={pm.id} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">
                      {pm.kind === "sale" ? "بيع" : pm.kind === "debt_collection" ? "تحصيل دفعة" : "تسوية مندوب"}
                      {" · "}{pm.method === "cash" ? "نقدي" : pm.method === "transfer" ? "تحويل" : "تسوية"}
                      {" · "}{pm.time}
                    </span>
                    <Money v={pm.amount} className="text-success font-bold" />
                  </div>
                ))}
                {remaining > 0 && (
                  <div className="flex items-center justify-between text-xs pt-2 border-t border-border mt-2">
                    <span className="text-debt">المتبقي على العميل</span>
                    <Money v={remaining} className="text-debt font-bold" />
                  </div>
                )}
              </div>
            </div>
          );
        })()}

        {(() => {
          const courierName = inv.courierId ? p.couriers.find((c: Courier) => c.id === inv.courierId)?.name : undefined;
          const salePm = (p.payments as Payment[]).find(pm => pm.invoiceId === inv.id && pm.kind === "sale");
          const method = (salePm?.method ?? "cash") as "cash" | "transfer";
          const createdAt = (inv as any).createdAt ? new Date((inv as any).createdAt) : new Date();
          const dateText = createdAt.toLocaleDateString("en-GB");
          const data: InvoicePdfData = {
            shopName: tenant?.name ?? "محلي",
            number: String(inv.number),
            issuedAt: createdAt,
            dateText, timeText: inv.time,
            customerName: cust?.name,
            customerPhone: (cust as any)?.phone,
            courierName,
            delivery: inv.delivery,
            items: inv.items.map(it => ({ name: it.name, qty: it.qty, price: it.price })),
            total: inv.total,
            paid: inv.paid,
            collectedByCourier: inv.collectedByCourier,
            remaining,
            method,
            status: inv.status,
          };
          const handlePdf = async () => {
            setPdfBusy(true);
            try { await downloadInvoicePdf(data); p.showToast?.("تم تحميل الفاتورة"); }
            catch (e) { console.error(e); p.showToast?.("تعذّر إنشاء PDF"); }
            finally { setPdfBusy(false); }
          };
          return (
            <>
              <div className="grid grid-cols-2 gap-2">
                <button disabled={pdfBusy} onClick={handlePdf} className="rounded-2xl bg-card border border-border py-3 font-bold text-sm flex items-center justify-center gap-1.5 disabled:opacity-50">
                  <FileDown className="w-4 h-4" />{pdfBusy ? "..." : "تحميل PDF"}
                </button>
                <button onClick={() => printInvoice(data)} className="rounded-2xl bg-card border border-border py-3 font-bold text-sm flex items-center justify-center gap-1.5">
                  <Printer className="w-4 h-4" />طباعة
                </button>
              </div>
              <button disabled={remaining <= 0} onClick={() => setCollectOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">تحصيل دفعة</button>
            </>
          );
        })()}
      </div>

      {collectOpen && (
        <Sheet onClose={() => setCollectOpen(false)} title="تحصيل دفعة">
          <div className="space-y-3">
            <div className="text-sm text-muted-foreground">المتبقي: <Money v={remaining} className="text-debt" /></div>
            <input value={collectAmt} onChange={e => setCollectAmt(e.target.value)} inputMode="decimal" placeholder="المبلغ" className="w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right" />
            {Number(collectAmt) > remaining && <div className="text-xs text-debt">لا يمكن تحصيل أكثر من المتبقي</div>}
            <div>
              <label className="text-xs font-bold text-muted-foreground">طريقة الدفع</label>
              <div className="mt-1 grid grid-cols-2 gap-2">
                <button onClick={() => setCollectMethod("cash")} className={`py-2 rounded-xl text-sm font-bold ${collectMethod === "cash" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>نقدي</button>
                <button onClick={() => setCollectMethod("transfer")} className={`py-2 rounded-xl text-sm font-bold ${collectMethod === "transfer" ? "bg-primary text-primary-foreground" : "bg-muted"}`}>تحويل</button>
              </div>
            </div>
            <button disabled={!Number(collectAmt) || Number(collectAmt) > remaining} onClick={submitCollect} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">تأكيد التحصيل</button>
          </div>
        </Sheet>
      )}
    </>
  );
}

/* --------------- INVENTORY --------------- */
function InventoryScreen(p: any) {
  const [filter, setFilter] = useState<"all" | "low" | "out">("all");
  const [editing, setEditing] = useState<any>(null);
  const [addOpen, setAddOpen] = useState(false);
  const list = p.products.filter((pr: any) => {
    if (filter === "low") return pr.stock > 0 && pr.stock <= pr.lowAt;
    if (filter === "out") return pr.stock === 0;
    return true;
  });
  return (
    <>
      <TopBar title="المخزون" />
      <div className="px-4 pt-3 space-y-3">
        <div className="flex gap-2">
          {[{ id: "all", l: "الكل" }, { id: "low", l: "منخفض" }, { id: "out", l: "نفد" }].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id as any)} className={`px-4 py-1.5 rounded-full text-xs font-bold ${filter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{f.l}</button>
          ))}
        </div>
        <div className="space-y-2">
          {list.length === 0 && filter === "out" && <EmptyState text="لا منتجات نافدة — جيد 👍" />}
          {list.length === 0 && filter !== "out" && <EmptyState text="لا منتجات بهذا التصنيف — أضف منتجاً جديداً" />}
          {list.map((pr: any) => (
            <div key={pr.id} className={`rounded-2xl border p-3 ${pr.stock === 0 ? "bg-debt-soft/40 border-debt/20" : "bg-card border-border"} ${pr.is_active === false ? "opacity-60" : ""}`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm">{pr.name}</div>
                  <div className="mt-1 flex items-center gap-2">
                    {pr.is_active === false && <StatusChip kind="warn">موقوف</StatusChip>}
                    {pr.is_discount && <StatusChip kind="info">تخفيض</StatusChip>}
                    {pr.stock === 0 && <StatusChip kind="debt" icon={<PackageX className="w-3 h-3" />}>نفد</StatusChip>}
                    {pr.stock > 0 && pr.stock <= pr.lowAt && <StatusChip kind="warn" icon={<AlertTriangle className="w-3 h-3" />}>منخفض <span className="num">{pr.stock}</span></StatusChip>}
                    {pr.stock > pr.lowAt && <StatusChip kind="info">متوفر <span className="num">{pr.stock}</span></StatusChip>}
                  </div>
                </div>
                <div className="text-left"><Money v={pr.price} className="text-sm" /></div>
              </div>
              <div className="mt-2 flex gap-2 flex-wrap">
                <button onClick={() => setEditing(pr)} className="flex-1 rounded-xl bg-card border border-border text-xs font-bold py-2">تعديل</button>
                {pr.stock === 0 && pr.is_active !== false && (
                  <button onClick={async () => { try { await p.toggleProductActiveAsync({ id: pr.id, is_active: false }); p.showToast("تم إيقاف العرض"); } catch (e: any) { p.showToast(e?.message ?? "تعذّر"); } }} className="flex-1 rounded-xl bg-card border border-debt/30 text-debt text-xs font-bold py-2">إيقاف العرض</button>
                )}
                {pr.is_active === false && (
                  <button onClick={async () => { try { await p.toggleProductActiveAsync({ id: pr.id, is_active: true }); p.showToast("تم تفعيل المنتج"); } catch (e: any) { p.showToast(e?.message ?? "تعذّر"); } }} className="flex-1 rounded-xl bg-card border border-border text-xs font-bold py-2">إعادة العرض</button>
                )}
                <button
                  onClick={async () => {
                    if (!window.confirm(`حذف المنتج "${pr.name}"؟\nإذا استُخدم في فواتير سابقة سيتم إيقافه فقط للحفاظ على السجلات.`)) return;
                    try {
                      const r = await p.deleteProductAsync(pr.id);
                      if (r.deleted) p.showToast("تم حذف المنتج");
                      else if (r.archived) p.showToast(`استُخدم في ${r.usedIn} فاتورة — تم إيقافه فقط`);
                    } catch (e: any) { p.showToast(e?.message ?? "تعذّر الحذف"); }
                  }}
                  className="rounded-xl bg-card border border-debt/40 text-debt text-xs font-bold py-2 px-3"
                  aria-label="حذف المنتج"
                >حذف</button>
              </div>
            </div>
          ))}
        </div>
        <button onClick={() => setAddOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة منتج</button>
      </div>

      {addOpen && <AddProductSheet existingNames={(p.products ?? []).map((x: any) => String(x.name || "").trim().toLowerCase())} onClose={() => setAddOpen(false)} onSave={async (data) => {
        try { await p.addProductAsync(data); setAddOpen(false); p.showToast("تمت إضافة المنتج"); }
        catch (e: any) { p.showToast(e?.message ?? "تعذّر الحفظ"); }
      }} />}
      {editing && <AddProductSheet
        mode="edit"
        initial={{ name: editing.name, price: editing.price, cost: editing.cost ?? 0, stock: editing.stock, is_discount: !!editing.is_discount }}
        existingNames={(p.products ?? []).filter((x: any) => x.id !== editing.id).map((x: any) => String(x.name || "").trim().toLowerCase())}
        onClose={() => setEditing(null)}
        onSave={async (data) => {
          try { await p.updateProductAsync({ id: editing.id, ...data }); setEditing(null); p.showToast("تم تحديث المنتج"); }
          catch (e: any) { p.showToast(e?.message ?? "تعذّر الحفظ"); }
        }}
      />}
    </>
  );
}

function AddProductSheet({ onClose, onSave, existingNames = [] as string[], mode = "add", initial }: { onClose: () => void; onSave: (d: { name: string; price: number; cost: number; stock: number; is_discount: boolean }) => void | Promise<void>; existingNames?: string[]; mode?: "add" | "edit"; initial?: { name: string; price: number; cost: number; stock: number; is_discount: boolean } }) {
  const nameRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState(initial?.name ?? "");
  const [price, setPrice] = useState(initial ? String(initial.price) : "");
  const [cost, setCost] = useState(initial ? String(initial.cost ?? "") : "");
  const [stock, setStock] = useState(initial ? String(initial.stock) : "");
  const [isDiscount, setIsDiscount] = useState(initial?.is_discount ?? false);
  const [touched, setTouched] = useState<{ name?: boolean; price?: boolean; cost?: boolean; stock?: boolean }>(initial ? { name: true, price: true, cost: true, stock: true } : {});
  const [submitting, setSubmitting] = useState(false);

  // Sync form values whenever initial product changes (edit mode switching between products)
  useEffect(() => {
    setName(initial?.name ?? "");
    setPrice(initial ? String(initial.price) : "");
    setCost(initial ? String(initial.cost ?? "") : "");
    setStock(initial ? String(initial.stock) : "");
    setIsDiscount(initial?.is_discount ?? false);
    setTouched(initial ? { name: true, price: true, cost: true, stock: true } : {});
  }, [initial?.name, initial?.price, initial?.cost, initial?.stock, initial?.is_discount]);

  // Auto-focus name field whenever the sheet opens (both add and edit)
  useEffect(() => {
    const id = setTimeout(() => nameRef.current?.focus(), 50);
    return () => clearTimeout(id);
  }, [mode, initial?.name]);

  const trimmedName = name.trim();
  const priceN = Number(price);
  const costN = Number(cost);
  const stockN = Number(stock);

  const errors: { name?: string; price?: string; stock?: string; cost?: string } = {};
  if (!trimmedName) errors.name = "اسم المنتج مطلوب";
  else if (trimmedName.length < 2) errors.name = "الاسم قصير جداً (حرفان على الأقل)";
  else if (trimmedName.length > 60) errors.name = "الاسم طويل (60 حرفاً كحد أقصى)";

  if (price === "" ) errors.price = "سعر البيع مطلوب";
  else if (!isFinite(priceN) || priceN <= 0) errors.price = "أدخل سعراً أكبر من صفر";

  if (stock === "") errors.stock = "أدخل كمية المخزون (يمكن أن تكون 0)";
  else if (!isFinite(stockN) || stockN < 0) errors.stock = "الكمية غير صحيحة";
  else if (stockN > 100000) errors.stock = "الكمية كبيرة جداً";

  if (cost !== "" && (!isFinite(costN) || costN < 0)) errors.cost = "تكلفة غير صحيحة";
  if (!errors.cost && !errors.price && cost !== "" && costN > priceN && !isDiscount) errors.cost = "التكلفة أعلى من سعر البيع — فعّل خيار التخفيض أو صحّح السعر";

  const warnings: { cost?: string; name?: string } = {};
  if (!errors.cost && !errors.price && cost !== "" && costN > priceN && isDiscount) warnings.cost = "منتج على تخفيض (التكلفة أعلى من سعر البيع)";
  if (!errors.name && trimmedName && existingNames.includes(trimmedName.toLowerCase())) warnings.name = "يوجد منتج بنفس الاسم — تأكد قبل الحفظ";

  const valid = Object.keys(errors).length === 0;

  const handleSave = async () => {
    if (!valid) {
      setTouched({ name: true, price: true, cost: true, stock: true });
      return;
    }
    setSubmitting(true);
    try {
      await onSave({ name: trimmedName, price: priceN, cost: costN || 0, stock: stockN, is_discount: isDiscount });
    } finally {
      setSubmitting(false);
    }
  };

  const showErr = (k: keyof typeof errors) => touched[k as keyof typeof touched] && errors[k];
  const inputCls = (k: keyof typeof errors) => `mt-1 w-full rounded-xl border bg-background px-3 py-3 text-sm ${showErr(k) ? "border-destructive" : "border-border"}`;

  return (
    <Sheet onClose={onClose} title={mode === "edit" ? "تعديل المنتج" : "إضافة منتج"}>
      <div className="space-y-3">
        <div>
          <label className="text-xs font-bold text-muted-foreground">اسم المنتج <span className="text-destructive">*</span></label>
          <input
            ref={nameRef}
            value={name}
            onChange={e => setName(e.target.value)}
            onBlur={() => setTouched(t => ({ ...t, name: true }))}
            className={inputCls("name")}
            placeholder="مثال: ماء 1.5 لتر"
            maxLength={60}
          />
          {showErr("name") && <div className="mt-1 text-xs text-destructive">{errors.name}</div>}
          {!showErr("name") && warnings.name && <div className="mt-1 text-xs text-amber-600 dark:text-amber-500">⚠ {warnings.name}</div>}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs font-bold text-muted-foreground">سعر البيع <span className="text-destructive">*</span></label>
            <input
              value={price}
              onChange={e => setPrice(e.target.value.replace(/[^\d.]/g, ""))}
              onBlur={() => setTouched(t => ({ ...t, price: true }))}
              inputMode="decimal"
              className={`${inputCls("price")} num text-right`}
              placeholder="0"
            />
            {showErr("price") && <div className="mt-1 text-xs text-destructive">{errors.price}</div>}
          </div>
          <div>
            <label className="text-xs font-bold text-muted-foreground">سعر التكلفة</label>
            <input
              value={cost}
              onChange={e => setCost(e.target.value.replace(/[^\d.]/g, ""))}
              onBlur={() => setTouched(t => ({ ...t, cost: true }))}
              inputMode="decimal"
              className={`${inputCls("cost")} num text-right`}
              placeholder="0"
            />
            {showErr("cost") && <div className="mt-1 text-xs text-destructive">{errors.cost}</div>}
            {!showErr("cost") && warnings.cost && <div className="mt-1 text-xs text-amber-600 dark:text-amber-500">⚠ {warnings.cost}</div>}
          </div>
        </div>
        <div>
          <label className="text-xs font-bold text-muted-foreground">المخزون الحالي <span className="text-destructive">*</span></label>
          <input
            value={stock}
            onChange={e => setStock(e.target.value.replace(/\D/g, ""))}
            onBlur={() => setTouched(t => ({ ...t, stock: true }))}
            inputMode="numeric"
            className={`${inputCls("stock")} num text-right`}
            placeholder="0"
          />
          {showErr("stock") && <div className="mt-1 text-xs text-destructive">{errors.stock}</div>}
        </div>
        <label className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 cursor-pointer">
          <input type="checkbox" checked={isDiscount} onChange={e => setIsDiscount(e.target.checked)} className="w-4 h-4 accent-primary" />
          <span className="text-xs font-bold">منتج على تخفيض (تكلفة &gt; بيع)</span>
        </label>
        <button
          disabled={submitting}
          onClick={handleSave}
          className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40"
        >
          {submitting ? "جاري الحفظ…" : mode === "edit" ? "حفظ التعديلات" : "حفظ المنتج"}
        </button>
      </div>
    </Sheet>
  );
}

/* EmptyState: moved to src/features/shared/EmptyState.tsx (R1) */


/* --------------- SHOP HUB --------------- */
function ShopHubScreen(p: any) {
  const mgmtItems: { id: Screen; l: string; Icon: any; hint?: string }[] = [
    { id: "customers", l: "العملاء", Icon: Users },
    { id: "inventory", l: "المنتجات", Icon: Boxes },
    { id: "couriers", l: "المندوبون", Icon: Truck },
  ];
  if (p.myRole === "owner") {
    mgmtItems.push({ id: "pilot", l: "صحة النظام", Icon: Activity, hint: "أخطاء ومقاييس" });
  }
  mgmtItems.push({ id: "settings", l: "إعدادات المحل", Icon: SettingsIcon });
  const groups: { title: string; items: { id: Screen; l: string; Icon: any; hint?: string }[] }[] = [
    {
      title: "يومي",
      items: [
        { id: "expenses", l: "المصروفات", Icon: ArrowDownCircle },
        { id: "debts", l: "تحصيل دين", Icon: CircleDollarSign, hint: "ديون العملاء" },
        { id: "settlements", l: "تسوية مندوب", Icon: Banknote, hint: "تصفية العهدة" },
        { id: "collected", l: "المحصّل فعليًا", Icon: Wallet },
        { id: "profit", l: "الربح التقديري", Icon: TrendingUp, hint: "قد يشمل ديون" },
      ],
    },
    {
      title: "إدارة",
      items: mgmtItems,
    },
  ];
  return (
    <>
      <TopBar title="أقسام المحل" />
      <div className="px-4 pt-3">
        <div className="text-xs text-muted-foreground mb-3">الأرقام اليومية في «الرئيسية». هنا التنقّل بين أقسام المحل.</div>
        {/* Billing link hidden — Paddle integration kept in repo but not user-facing yet */}
        {groups.map(g => (
          <div key={g.title} className="mb-4">
            <div className="text-xs font-bold text-muted-foreground mb-2 px-1">{g.title}</div>
            <div className="rounded-2xl bg-card border border-border divide-y divide-border overflow-hidden">
              {g.items.map(s => (
                <button key={s.id} onClick={() => p.go(s.id)} className="w-full flex items-center gap-3 px-4 py-3 text-right hover:bg-muted active:bg-muted">
                  <s.Icon className="w-5 h-5 text-primary" />
                  <span className="flex-1 text-sm font-medium">{s.l}</span>
                  {s.hint && <span className="text-[10px] text-muted-foreground">{s.hint}</span>}
                  <ChevronLeft className="w-4 h-4 text-muted-foreground" />
                </button>
              ))}
            </div>
          </div>
        ))}
      </div>
    </>
  );
}

/* --------------- PROFIT --------------- */
function ProfitScreen(p: any) {
  const { sales, cogs, grossProfit, expenseTotal, netProfit, collected, realizedCogs, realizedProfit, customerDebts, unsettledCustody } = p.totals;
  const Row = ({ label, v, op, color }: { label: string; v: number; op?: string; color?: string }) => (
    <div className="flex items-center justify-between py-2">
      <div className="flex items-center gap-2">
        {op && <span className="w-6 text-center text-muted-foreground font-bold">{op}</span>}
        <span className="text-sm">{label}</span>
      </div>
      <Money v={v} className={color ?? ""} />
    </div>
  );
  return (
    <>
      <TopBar title="الربح" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        {/* Realized profit — primary */}
        <div className="rounded-2xl bg-profit-soft border-2 border-profit/30 p-4">
          <div className="flex items-center gap-2 text-profit text-xs font-bold"><TrendingUp className="w-4 h-4" /> ربح تقديري</div>
          <Money v={realizedProfit} className="text-2xl text-profit mt-1" />
          <div className="text-[11px] text-muted-foreground mt-1 leading-relaxed">
            تقدير مبني على نسبة الدفع لفواتير الفترة. الحساب النهائي يُوحَّد لاحقًا على أساس المدفوعات الفعلية.
          </div>
          <div className="mt-3 pt-3 border-t border-profit/20 space-y-1.5 text-xs">
            <div className="flex justify-between"><span className="text-muted-foreground">المحصّل فعليًا</span><Money v={collected} /></div>
            <div className="flex justify-between"><span className="text-muted-foreground">− تكلفة البضاعة المرتبطة بالمحصّل</span><Money v={realizedCogs} /></div>
            <div className="flex justify-between"><span className="text-muted-foreground">− مصروفات</span><Money v={expenseTotal} /></div>
          </div>
        </div>

        {/* Expected profit — secondary */}
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold"><Info className="w-4 h-4" /> ربح متوقع لو حُصِّلت كل الديون</div>
          <Money v={netProfit} className="text-lg mt-1" />
          <div className="mt-3 divide-y divide-border">
            <Row label="المبيعات" v={sales} />
            <Row label="تكلفة البضاعة المباعة" v={cogs} op="−" />
            <Row label="الربح الإجمالي" v={grossProfit} op="=" color="text-profit font-bold" />
            <Row label="المصروفات" v={expenseTotal} op="−" />
            <Row label="صافي الربح المتوقع" v={netProfit} op="=" color="text-profit font-bold" />
          </div>
        </div>

        <div className="rounded-2xl bg-warn-soft border border-warn/20 p-3 text-xs text-warn flex gap-2"><Info className="w-4 h-4 shrink-0 mt-0.5" /><span>الفرق بين الرقمين = ديون <span className="num">{fmt(customerDebts)}</span> + عهدة <span className="num">{fmt(unsettledCustody)}</span> د.ل لم تدخل جيبك بعد.</span></div>
      </div>
    </>
  );
}

/* --------------- COLLECTED --------------- */
function CollectedScreen(p: any) {
  const allPayments: Payment[] = p.payments;
  const { range, setRange } = useDateRange("today");
  const payments = allPayments.filter(pm => inRange(pm.createdAt, range));
  const cash = payments.filter(pm => pm.method === "cash").reduce((s, pm) => s + pm.amount, 0);
  const transfer = payments.filter(pm => pm.method === "transfer").reduce((s, pm) => s + pm.amount, 0);
  const settlement = payments.filter(pm => pm.method === "settlement").reduce((s, pm) => s + pm.amount, 0);
  const sum = cash + transfer + settlement;

  const customerName = (id?: string) => p.customers.find((c: Customer) => c.id === id)?.name;
  const courierName = (id?: string) => p.couriers.find((c: Courier) => c.id === id)?.name;

  const label = (pm: Payment) => {
    if (pm.kind === "sale") return `بيع ${pm.method === "cash" ? "نقدي" : "تحويل"}${pm.invoiceNumber ? " #" + pm.invoiceNumber : ""}`;
    if (pm.kind === "debt_collection") return `تحصيل دين ${pm.method === "cash" ? "نقدي" : "تحويل"}${customerName(pm.customerId) ? " · " + customerName(pm.customerId) : ""}`;
    return `تسوية مندوب${courierName(pm.courierId) ? " · " + courierName(pm.courierId) : ""}${pm.invoiceNumber ? " · #" + pm.invoiceNumber : ""}`;
  };

  const sorted = [...payments].sort((a, b) => (a.createdAt < b.createdAt ? 1 : a.createdAt > b.createdAt ? -1 : 0));

  return (
    <>
      <TopBar title="المحصّل فعليًا" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <DateRangeFilter value={range} onChange={setRange} />
        <div className="rounded-2xl bg-primary text-primary-foreground p-5">
          <div className="text-xs opacity-90">المدفوع المحصّل · {range.label}</div>
          <Money v={sum} className="text-2xl mt-1" />
          <div className="text-[11px] opacity-80 mt-2">ما دخل فعلًا لجيبك في هذا النطاق</div>
        </div>
        <div className="grid grid-cols-2 gap-3">
          <div className="rounded-2xl bg-card border border-border p-4"><div className="text-xs text-muted-foreground">نقدي</div><Money v={cash} className="text-base mt-1" /></div>
          <div className="rounded-2xl bg-card border border-border p-4"><div className="text-xs text-muted-foreground">تحويل</div><Money v={transfer} className="text-base mt-1" /></div>
        </div>
        {settlement > 0 && (
          <div className="rounded-2xl bg-card border border-border p-4 flex items-center justify-between">
            <div>
              <div className="text-xs text-muted-foreground">تسويات مندوب</div>
              <div className="text-[11px] text-muted-foreground">مبالغ سُلّمت لك من المندوب</div>
            </div>
            <Money v={settlement} className="text-base" />
          </div>
        )}
        <div className="rounded-2xl bg-info-soft border border-info/20 p-3 text-xs text-info flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>لا يشمل ديون العملاء، ولا عهدة المندوب غير المصفّاة. المصروفات لا تُنقص هذا الرقم.</span>
        </div>
        <div className="text-xs font-bold text-muted-foreground mt-2">الحركة ({sorted.length})</div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {sorted.length === 0 && <div className="p-4 text-sm text-muted-foreground text-center">لا حركات في هذا النطاق</div>}
          {sorted.map((pm) => (
            <div key={pm.id} className="flex items-center gap-3 p-3">
              <ArrowUpCircle className={`w-5 h-5 ${pm.method === "settlement" ? "text-warn" : "text-success"}`} />
              <div className="flex-1">
                <div className="text-sm">{label(pm)}</div>
                <div className="text-[11px] text-muted-foreground">{pm.time}</div>
              </div>
              <Money v={pm.amount} className={`text-sm ${pm.method === "settlement" ? "text-warn" : "text-success"}`} />
            </div>
          ))}
        </div>
      </div>
    </>
  );
}

/* --------------- DEBTS --------------- */
function DebtsScreen(p: any) {
  const map = new Map<string, number>();
  p.invoices.forEach((i: Invoice) => {
    if (i.delivery === "direct" && i.total - i.paid > 0 && i.customerId) {
      map.set(i.customerId, (map.get(i.customerId) ?? 0) + (i.total - i.paid));
    }
    if (i.delivery === "courier") {
      const cs = i.courierState ?? "pending";
      let debt = 0;
      if (cs === "delivered_none") debt = i.total;
      if (cs === "delivered_partial") debt = i.total - (i.collectedByCourier ?? 0);
      if (debt > 0 && i.customerId) map.set(i.customerId, (map.get(i.customerId) ?? 0) + debt);
    }
  });
  const rows = Array.from(map.entries()).map(([cid, v]) => ({ customer: p.customers.find((c: Customer) => c.id === cid), v }));
  const total = rows.reduce((s, r) => s + r.v, 0);
  return (
    <>
      <TopBar title="الديون" onBack={p.back} />
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
  const invs = p.invoices.filter((i: Invoice) =>
    i.customerId === cust?.id &&
    (i.total - i.paid) > 0 &&
    !(i.delivery === "courier" && (i.courierState ?? "pending") === "pending")
  );
  const total = invs.reduce((s: number, i: Invoice) => s + (i.total - i.paid), 0);
  return (
    <>
      <TopBar title={cust?.name ?? "عميل"} onBack={p.back} />
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
            <div className="text-xs text-debt mt-1">متبقي <span className="num">{fmt(inv.total - inv.paid)}</span> د.ل</div>
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
        <TopBar title="عهدة المندوب" onBack={p.back} />
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

  const pendingV = pending.reduce((s: number, i: Invoice) => s + i.total, 0);
  const custodyV = collected.reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);
  const debtV = customerDebtOrders.reduce((s: number, i: Invoice) => {
    if (i.courierState === "delivered_none") return s + i.total;
    if (i.courierState === "delivered_partial") return s + (i.total - (i.collectedByCourier ?? 0));
    return s;
  }, 0);

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
      <TopBar title="عهدة المندوب" onBack={p.back} right={<button onClick={goSettlements} className="text-xs font-bold text-primary px-3 py-1.5 rounded-full bg-primary-soft">تسوية</button>} />
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
              const d = i.courierState === "delivered_none" ? i.total : (i.total - (i.collectedByCourier ?? 0));
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
  const net = collected.filter((i: Invoice) => selected.has(i.id)).reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);

  const [settledAmount, setSettledAmount] = useState(0);

  if (!courier) {
    return (
      <>
        <TopBar title="التسويات" onBack={p.back} />
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
      <TopBar title={`تسوية مع ${courier.name}`} onBack={p.back} />
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
      <TopBar title="المصروفات" onBack={p.back} />
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
function CustomersScreen(p: any) {
  const [filter, setFilter] = useState<"all" | "debt" | "clear">("all");
  const [q, setQ] = useState("");
  const debtMap = new Map<string, number>();
  p.invoices.forEach((i: Invoice) => {
    if (!i.customerId) return;
    if (i.delivery === "direct" && i.total - i.paid > 0) {
      debtMap.set(i.customerId, (debtMap.get(i.customerId) ?? 0) + (i.total - i.paid));
    }
    if (i.delivery === "courier") {
      const cs = i.courierState ?? "pending";
      let d = 0;
      if (cs === "delivered_none") d = i.total;
      if (cs === "delivered_partial") d = i.total - (i.collectedByCourier ?? 0);
      if (d > 0) debtMap.set(i.customerId, (debtMap.get(i.customerId) ?? 0) + d);
    }
  });
  const list = p.customers.filter((c: Customer) => {
    if (q && !c.name.includes(q) && !(c.phone ?? "").includes(q)) return false;
    const has = !!debtMap.get(c.id);
    if (filter === "debt") return has;
    if (filter === "clear") return !has;
    return true;
  });
  return (
    <>
      <TopBar title="العملاء" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <input value={q} onChange={e => setQ(e.target.value)} placeholder="ابحث بالاسم أو الرقم" className="w-full rounded-xl border border-border bg-card px-3 py-2.5 text-sm" />
        <div className="flex gap-2 overflow-x-auto">
          {[{ id: "all", l: "الكل" }, { id: "debt", l: "عليه دين" }, { id: "clear", l: "لا دين" }].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id as any)} className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${filter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{f.l}</button>
          ))}
        </div>
        {list.length === 0 && <EmptyState text={q ? "لا عميل بهذا الاسم" : "لا عملاء بهذا التصنيف"} />}
        <div className="space-y-2">
          {list.map((c: Customer) => (
            <div key={c.id} className="rounded-2xl bg-card border border-border p-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-primary-soft text-primary flex items-center justify-center font-bold">{c.name[0]}</div>
              <div className="flex-1">
                <div className="font-bold text-sm">{c.name}</div>
                <div className="text-xs text-muted-foreground">{c.phone ?? "بدون رقم"}</div>
              </div>
              {debtMap.get(c.id) ? <Money v={debtMap.get(c.id)!} className="text-debt font-bold text-sm" /> : <span className="text-[11px] text-success">لا دين</span>}
            </div>
          ))}
        </div>
        <AddCustomerInline addCustomerAsync={p.addCustomerAsync} customers={p.customers} showToast={p.showToast} />
      </div>
    </>
  );
}

function AddCustomerInline({ addCustomerAsync, customers, showToast }: { addCustomerAsync: (i: { name: string; phone?: string }) => Promise<any>; customers: Customer[]; showToast: (s: string) => void }) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const trimmedName = name.trim();
  const trimmedPhone = phone.trim();
  const dup = customers.find(c => c.name.trim() === trimmedName || (!!trimmedPhone && (c.phone ?? "").trim() === trimmedPhone));
  const submit = async () => {
    if (!trimmedName) return;
    try {
      await addCustomerAsync({ name: trimmedName, phone: trimmedPhone || undefined });
      setName(""); setPhone(""); setOpen(false);
      showToast("تم إضافة العميل");
    } catch (e: any) {
      showToast(e?.message ?? "تعذّر الإضافة");
    }
  };
  if (!open) {
    return (
      <button onClick={() => setOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة عميل</button>
    );
  }
  return (
    <div className="rounded-2xl bg-card border border-border p-3 space-y-2">
      <div className="font-bold text-sm">إضافة عميل جديد</div>
      <input value={name} onChange={e => setName(e.target.value)} placeholder="اسم العميل (إلزامي)" className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm" />
      <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="رقم الهاتف (اختياري)" inputMode="tel" className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm num text-right" />
      {dup && <div className="text-[11px] text-warn">⚠ يوجد عميل بنفس {dup.name.trim() === trimmedName ? "الاسم" : "الرقم"}: {dup.name}</div>}
      <div className="flex gap-2">
        <button onClick={() => { setOpen(false); setName(""); setPhone(""); }} className="flex-1 rounded-xl bg-muted py-2.5 text-sm font-bold">إلغاء</button>
        <button disabled={!trimmedName} onClick={submit} className="flex-1 rounded-xl bg-primary text-primary-foreground py-2.5 text-sm font-bold disabled:opacity-40">حفظ</button>
      </div>
    </div>
  );
}

function CouriersScreen(p: any) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const submit = async () => {
    if (!name.trim()) return;
    await p.addCourierAsync({ name: name.trim(), phone: phone.trim() || undefined });
    setName(""); setPhone(""); setOpen(false);
    p.showToast("تم إضافة المندوب");
  };
  return (
    <>
      <TopBar title="المندوبون" onBack={p.back} />
      <div className="px-4 pt-3 space-y-2">
        {p.couriers.map((c: Courier) => {
          const list = p.invoices.filter((i: Invoice) => i.courierId === c.id);
          const custody = list.filter((i: Invoice) => i.courierState === "delivered_partial" || i.courierState === "delivered_full").reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);
          return (
            <button key={c.id} onClick={() => { p.setOpenCourierId(c.id); p.go("courier_custody"); }} className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-warn-soft text-warn flex items-center justify-center font-bold">{c.name[0]}</div>
              <div className="flex-1">
                <div className="font-bold text-sm">{c.name}</div>
                <div className="text-xs text-muted-foreground"><span className="num">{list.length}</span> طلب</div>
              </div>
              <div className="text-left">
                <div className="text-[11px] text-muted-foreground">عهدة غير مصفّاة</div>
                <Money v={custody} className="text-warn font-bold text-sm" />
              </div>
            </button>
          );
        })}
        {p.couriers.length === 0 && (
          <div className="rounded-2xl bg-muted/40 border border-border p-6 text-center text-sm text-muted-foreground">
            لا يوجد مندوبون بعد. أضف أول مندوب توصيل.
          </div>
        )}
        <button onClick={() => setOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة مندوب</button>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-end" onClick={() => setOpen(false)}>
          <div className="w-full bg-card rounded-t-3xl p-4 space-y-3" onClick={e => e.stopPropagation()}>
            <div className="font-bold">إضافة مندوب</div>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="اسم المندوب" className="w-full rounded-xl bg-muted px-3 py-3 text-sm" />
            <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="رقم الهاتف (اختياري)" inputMode="tel" className="w-full rounded-xl bg-muted px-3 py-3 text-sm" />
            <div className="flex gap-2">
              <button onClick={() => setOpen(false)} className="flex-1 rounded-xl bg-muted py-3 text-sm font-bold">إلغاء</button>
              <button onClick={submit} disabled={!name.trim()} className="flex-1 rounded-xl bg-primary text-primary-foreground py-3 text-sm font-bold disabled:opacity-40">حفظ</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}

function SettingsScreen(p: any) {
  const { data: tenantId } = useTenantId();
  const { data: tenant } = useTenant(tenantId);
  const { data: role } = useMyRole(tenantId);
  const updateNameMut = useUpdateTenantName(tenantId);
  const updateBizMut = useUpdateTenantBusinessType(tenantId);
  const [name, setName] = useState("");
  const [bizType, setBizType] = useState<string>("");
  const [savedFlash, setSavedFlash] = useState(false);
  const [bizFlash, setBizFlash] = useState(false);
  useEffect(() => { if (tenant?.name) setName(tenant.name); }, [tenant?.name]);
  useEffect(() => { setBizType(tenant?.business_type ?? ""); }, [tenant?.business_type]);

  const signOut = async () => {
    const { supabase } = await import("@/integrations/supabase/client");
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };

  const save = async () => {
    const v = name.trim();
    if (!v || v === tenant?.name) return;
    await updateNameMut.mutateAsync(v);
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 1500);
  };

  const saveBiz = async () => {
    const v = bizType || null;
    if (v === (tenant?.business_type ?? null)) return;
    await updateBizMut.mutateAsync(v);
    setBizFlash(true);
    setTimeout(() => setBizFlash(false), 1500);
  };

  const roleLabel = role === "owner" ? "صاحب المحل" : role === "staff" ? "موظّف" : "—";

  return (
    <>
      <TopBar title="الإعدادات" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4">
          <label className="block text-xs text-muted-foreground mb-1">اسم المحل</label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={60}
            className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
            placeholder="مثال: بقالة الأمين"
          />
          <button
            onClick={save}
            disabled={updateNameMut.isPending || !name.trim() || name.trim() === tenant?.name}
            className="mt-3 w-full h-10 rounded-xl bg-primary text-primary-foreground text-sm font-semibold disabled:opacity-50"
          >
            {updateNameMut.isPending ? "..." : savedFlash ? "تم الحفظ ✓" : "حفظ"}
          </button>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4">
          <label className="block text-xs text-muted-foreground mb-1">نوع النشاط</label>
          <select
            value={bizType}
            onChange={e => setBizType(e.target.value)}
            className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
          >
            <option value="">غير محدد</option>
            {BUSINESS_TYPES.map(b => (
              <option key={b.value} value={b.value}>{b.label}</option>
            ))}
          </select>
          <p className="mt-2 text-[11px] text-muted-foreground">
            للعرض فقط — لا يؤثر على الحسابات أو المنتجات.
          </p>
          <button
            onClick={saveBiz}
            disabled={updateBizMut.isPending || (bizType || null) === (tenant?.business_type ?? null)}
            className="mt-3 w-full h-10 rounded-xl bg-primary text-primary-foreground text-sm font-semibold disabled:opacity-50"
          >
            {updateBizMut.isPending ? "..." : bizFlash ? "تم الحفظ ✓" : "حفظ"}
          </button>
        </div>

        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">دورك في المحل</span>
            <span className="text-sm font-semibold">{roleLabel}</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">نوع النشاط الحالي</span>
            <span className="text-sm font-semibold">{businessTypeLabel(tenant?.business_type)}</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">رقم المحل</span>
            <span className="text-[11px] font-mono text-muted-foreground" dir="ltr">{tenantId?.slice(0, 8) ?? "—"}</span>
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border overflow-hidden">
          <button onClick={signOut} className="w-full flex items-center gap-3 px-4 py-3 text-right text-destructive font-semibold">
            <span className="flex-1">تسجيل الخروج</span>
          </button>
        </div>

        <p className="text-[11px] text-muted-foreground text-center pt-2">منجز — دفتر محلك الذكي</p>
      </div>
    </>
  );
}

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
        <TopBar title="فاتورة جديدة" onBack={p.back} right={
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
  const needsCustomer = remaining > 0 || delivery === "courier";
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
          {delivery === "courier" && <div className="mt-2 text-[11px] text-warn flex items-center gap-1"><Info className="w-3 h-3" />طلبات التوصيل تحتاج اسم العميل أو المستلم</div>}
        </div>

        {/* Customer */}
        <div>
          <label className="text-xs font-bold text-muted-foreground">{needsCustomer ? "العميل (إلزامي)" : "العميل (اختياري)"}</label>
          <button onClick={() => setPickCustomer(true)} className={`mt-1 w-full text-right rounded-xl border px-3 py-3 text-sm ${needsCustomer && !customerId ? "border-debt bg-debt-soft text-debt" : "border-border bg-background"}`}>
            {customerId ? customers.find((c: Customer) => c.id === customerId)?.name : (needsCustomer ? "اختر عميلًا — لا يمكن تسجيل متبقٍّ دون عميل" : "بدون عميل")}
          </button>
          {status === "paid" && delivery === "direct" && !customerId && (
            <div className="mt-1 rounded-lg bg-success-soft text-success text-[11px] p-2 flex items-center gap-1.5"><CheckCircle2 className="w-3.5 h-3.5" />مدفوعة كاملة — لا حاجة لاختيار عميل</div>
          )}
        </div>


        {/* Courier */}
        {delivery === "courier" && (
          <div>
            <label className="text-xs font-bold text-muted-foreground">المندوب (إلزامي)</label>
            <div className="mt-1 flex flex-wrap gap-2">
              {couriers.map((c: Courier) => (
                <button key={c.id} onClick={() => setCourierId(c.id)} className={`px-3 py-1.5 rounded-full text-xs font-bold ${courierId === c.id ? "bg-warn text-white" : "bg-muted"}`}>{c.name}</button>
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
  useEffect(() => {
    if (secondsLeft <= 0 || undone) return;
    const t = setTimeout(() => setSecondsLeft(n => n - 1), 1000);
    return () => clearTimeout(t);
  }, [secondsLeft, undone]);
  const undo = async () => {
    if (!p.lastCreatedInvoiceId) return;
    await p.deleteInvoiceAsync(p.lastCreatedInvoiceId);
    p.setLastCreatedInvoiceId(null);
    setUndone(true);
    setTimeout(() => p.setScreen("home"), 600);
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
      {secondsLeft > 0 && p.lastCreatedInvoiceId && (
        <button onClick={undo} className="text-xs text-debt font-bold underline">تراجع عن هذه الفاتورة ({secondsLeft})</button>
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
    for (let i = p.invoices.length - 1; i >= 0 && out.length < 6; i--) {
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
      <TopBar title="بيع سريع" onBack={p.back} right={
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
      const margin = inv.items.reduce((a, it) => a + (it.price - it.cost) * it.qty, 0);
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
      <TopBar title="إقفال اليوم" onBack={p.back} />
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
    <Sheet onClose={onClose} title={`التفاصيل المالية · ${periodLabel}`}>
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

        <div className="rounded-xl bg-profit-soft border border-profit/20 p-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-profit font-bold">ربح تقديري</div>
              <Money v={totals.realizedProfit} className="text-base text-profit" />
              <div className="text-[10px] text-muted-foreground mt-0.5">يُوحَّد لاحقًا على أساس المدفوعات</div>
            </div>
            <div className="text-left">
              <div className="text-xs text-muted-foreground font-bold">ربح تقديري</div>
              <Money v={totals.netProfit} className="text-base" />
              <div className="text-[10px] text-warn mt-0.5">قد يشمل ديون</div>
            </div>
          </div>
          <button onClick={onOpenProfit} className="mt-3 w-full rounded-xl bg-card border border-border py-2 text-xs font-bold text-primary">رؤية شاشة الربح الكاملة</button>
        </div>
      </div>
    </Sheet>
  );
}

/* Sheet, Toast: moved to src/features/shared/ (R1) */


/* --------------- PILOT HEALTH DASHBOARD --------------- */
function PilotScreen(p: any) {
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
        <TopBar title="صحة النظام" onBack={p.back} />
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
  const isToday = (iso?: string) => !!iso && tenantTodayKey(tenantTz) === new Intl.DateTimeFormat("en-CA", { timeZone: tenantTz }).format(new Date(iso));

  /* ---- broken rules (must be 0) ---- */
  const paidOverTotal = invoices.filter(i => i.paid > i.total + 0.001).length;
  const collectedOverTotal = invoices.filter(i => (i.collectedByCourier ?? 0) > i.total + 0.001).length;
  const negStock = products.filter(p => p.stock < 0).length;
  const courierMissingId = invoices.filter(i => i.delivery === "courier" && !i.courierId && i.courierState !== "returned").length;
  const debtNoCustomer = invoices.filter(i => i.status !== "paid" && !i.customerId && i.delivery === "direct").length;
  const brokenTotal = paidOverTotal + collectedOverTotal + negStock + courierMissingId + debtNoCustomer;

  /* ---- warnings ---- */
  const lowStock = products.filter(p => p.stock > 0 && p.stock <= p.lowAt).length;
  const outStock = products.filter(p => p.stock === 0).length;
  const oldPendingCourier = invoices.filter(i =>
    i.delivery === "courier" &&
    (i.courierState === "pending" || i.courierState === "delivered_partial") &&
    now - new Date(i.createdAt).getTime() > 7 * DAY
  ).length;
  const oldDebts = invoices.filter(i =>
    i.delivery === "direct" && (i.status === "debt" || i.status === "partial") &&
    now - new Date(i.createdAt).getTime() > 30 * DAY
  ).length;
  const customersNoPhone = customers.filter(c => !c.phone).length;
  const unsettledCustody = invoices
    .filter(i => i.delivery === "courier" && (i.courierState === "delivered_partial" || i.courierState === "delivered_full"))
    .reduce((s, i) => s + (i.collectedByCourier ?? 0), 0);
  const lastClose = dayCloses[0]?.closedFor ?? null;
  const daysSinceClose = lastClose
    ? Math.floor((new Date(todayKey).getTime() - new Date(lastClose).getTime()) / DAY)
    : null;

  /* ---- usage metrics ---- */
  const activeProducts = products.filter(p => (p as any).is_active !== false).length;
  const invoicesToday = invoices.filter(i => isToday(i.createdAt)).length;
  const paymentsToday = payments.filter(pm => isToday(pm.createdAt));
  const collectedToday = paymentsToday.reduce((s, pm) => s + pm.amount, 0);
  const expensesToday = expenses.filter(e => isToday(e.createdAt)).reduce((s, e) => s + e.amount, 0);
  const lifetimeSales = invoices.reduce((s, i) => s + i.total, 0);
  const lifetimeCollected = payments.reduce((s, pm) => s + pm.amount, 0);

  const HealthBadge = ({ ok }: { ok: boolean }) => (
    <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[11px] font-bold ${
      ok ? "bg-success-soft text-success" : "bg-debt-soft text-debt"
    }`}>
      {ok ? <CheckCircle2 className="w-3 h-3" /> : <AlertTriangle className="w-3 h-3" />}
      {ok ? "سليم" : "يحتاج مراجعة"}
    </span>
  );

  const Rule = ({ label, value, tone = "debt" }: { label: string; value: number; tone?: "debt" | "warn" | "info" }) => {
    const ok = value === 0;
    const color = ok ? "text-success" : tone === "warn" ? "text-warn" : tone === "info" ? "text-info" : "text-debt";
    return (
      <div className="flex items-center justify-between py-2.5">
        <span className="text-sm flex-1">{label}</span>
        <span className={`num text-base font-bold ${color}`}>{value}</span>
      </div>
    );
  };

  const Metric = ({ label, value, suffix }: { label: string; value: string | number; suffix?: string }) => (
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
      <TopBar title="صحة النظام" onBack={p.back} />
      <div className="px-4 pt-3 pb-8 space-y-4">

        {/* Overall health */}
        <div className={`rounded-2xl p-4 border-2 ${
          brokenTotal === 0 ? "bg-success-soft border-success/30" : "bg-debt-soft border-debt/40"
        }`}>
          <div className="flex items-center gap-2">
            <ShieldCheck className={`w-5 h-5 ${brokenTotal === 0 ? "text-success" : "text-debt"}`} />
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
              <Money v={unsettledCustody} className={unsettledCustody > 0 ? "text-warn" : "text-success"} />
            </div>
            <div className="flex items-center justify-between py-2.5">
              <span className="text-sm flex-1">أيام منذ آخر إغلاق يوم</span>
              <span className={`num text-base font-bold ${
                daysSinceClose === null ? "text-debt" : daysSinceClose === 0 ? "text-success" : daysSinceClose <= 2 ? "text-warn" : "text-debt"
              }`}>
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
