import { createFileRoute } from "@tanstack/react-router";
import { useMemo, useState } from "react";
import {
  Home, ReceiptText, Plus, Boxes, Store, Bell, Menu,
  Search, X, Minus, ChevronLeft, AlertTriangle, CheckCircle2,
  Wallet, Banknote, Truck, Users, Settings as SettingsIcon,
  TrendingUp, Phone, MessageCircle, Trash2, ArrowLeft, Info,
  Clock, PackageX, ArrowDownCircle, ArrowUpCircle, CircleDollarSign,
} from "lucide-react";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "منجز — دفتر المحل الذكي" },
      { name: "description", content: "تطبيق منجز لإدارة المحل الصغير: مبيعات، ديون، عهدة المندوب، ومصروفات بلغة بسيطة." },
    ],
  }),
  component: MongezzApp,
});

/* ============================== MOCK DATA ============================== */

type Product = { id: string; name: string; price: number; cost: number; stock: number; lowAt: number };
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
  collectedByCourier?: number; // amount currently in courier custody from this order, unsettled
  time: string;
};
type Expense = { id: string; type: string; amount: number; method: "cash" | "transfer"; time: string; note?: string };
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
};

const seedProducts: Product[] = [
  { id: "p1", name: "زيت زيتون 1 لتر", price: 25, cost: 18, stock: 24, lowAt: 5 },
  { id: "p2", name: "أرز بسمتي 5 كغ", price: 60, cost: 48, stock: 3, lowAt: 5 },
  { id: "p3", name: "سكر 1 كغ", price: 4, cost: 3, stock: 0, lowAt: 10 },
  { id: "p4", name: "شاي أحمر 500غ", price: 15, cost: 10, stock: 40, lowAt: 8 },
  { id: "p5", name: "معكرونة 500غ", price: 3, cost: 2, stock: 18, lowAt: 6 },
  { id: "p6", name: "حليب مبخّر", price: 5, cost: 3.5, stock: 30, lowAt: 10 },
];

const seedCustomers: Customer[] = [
  { id: "c1", name: "أحمد علي", phone: "0912345678" },
  { id: "c2", name: "محمود سالم", phone: "0911223344" },
  { id: "c3", name: "سامي عبدالله" },
];

const seedCouriers: Courier[] = [
  { id: "k1", name: "علي", phone: "0918887766" },
  { id: "k2", name: "خالد", phone: "0915556677" },
];

const seedInvoices: Invoice[] = [
  // paid invoice without customer
  { id: "i1", number: "1041", items: [{ productId: "p1", name: "زيت زيتون 1 لتر", qty: 2, price: 25, cost: 18 }], total: 50, paid: 50, status: "paid", delivery: "direct", time: "09:14" },
  // partial invoice with customer
  { id: "i2", number: "1042", items: [{ productId: "p4", name: "شاي أحمر 500غ", qty: 4, price: 15, cost: 10 }], total: 60, paid: 20, customerId: "c1", status: "partial", delivery: "direct", time: "10:30" },
  // debt invoice with customer
  { id: "i3", number: "1043", items: [{ productId: "p2", name: "أرز بسمتي 5 كغ", qty: 1, price: 60, cost: 48 }], total: 60, paid: 0, customerId: "c2", status: "debt", delivery: "direct", time: "11:05" },
  // courier in-transit
  { id: "i4", number: "1044", items: [{ productId: "p1", name: "زيت زيتون 1 لتر", qty: 5, price: 25, cost: 18 }], total: 125, paid: 0, customerId: "c3", delivery: "courier", courierId: "k1", status: "debt", courierState: "pending", time: "11:40" },
  // courier partial collected
  { id: "i5", number: "1045", items: [{ productId: "p2", name: "أرز بسمتي 5 كغ", qty: 1, price: 60, cost: 48 }, { productId: "p6", name: "حليب مبخّر", qty: 8, price: 5, cost: 3.5 }], total: 100, paid: 0, customerId: "c1", delivery: "courier", courierId: "k1", status: "debt", courierState: "delivered_partial", collectedByCourier: 40, time: "12:10" },
  // courier full collected, unsettled
  { id: "i6", number: "1046", items: [{ productId: "p4", name: "شاي أحمر 500غ", qty: 2, price: 15, cost: 10 }, { productId: "p6", name: "حليب مبخّر", qty: 34, price: 5, cost: 3.5 }], total: 200, paid: 0, customerId: "c2", delivery: "courier", courierId: "k1", status: "debt", courierState: "delivered_full", collectedByCourier: 200, time: "12:40" },
];

const seedExpenses: Expense[] = [
  { id: "e1", type: "نقل", amount: 40, method: "cash", time: "08:30" },
  { id: "e2", type: "إنترنت", amount: 20, method: "transfer", time: "09:00" },
];

const seedPayments: Payment[] = [
  // matches i1 — direct full sale, cash
  { id: "pay1", kind: "sale", method: "cash", amount: 50, invoiceId: "i1", invoiceNumber: "1041", time: "09:14" },
  // matches i2 — direct partial sale, transfer
  { id: "pay2", kind: "sale", method: "transfer", amount: 20, invoiceId: "i2", invoiceNumber: "1042", customerId: "c1", time: "10:30" },
];

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
  | "sale" | "sale_success";

function MongezzApp() {
  const [products] = useState<Product[]>(seedProducts);
  const [customers, setCustomers] = useState<Customer[]>(seedCustomers);
  const [couriers] = useState<Courier[]>(seedCouriers);
  const [invoices, setInvoices] = useState<Invoice[]>(seedInvoices);
  const [expenses, setExpenses] = useState<Expense[]>(seedExpenses);
  const [payments, setPayments] = useState<Payment[]>(seedPayments);

  const [screen, setScreen] = useState<Screen>("home");
  const [stack, setStack] = useState<Screen[]>([]);
  const [openInvoiceId, setOpenInvoiceId] = useState<string | null>(null);
  const [openCustomerId, setOpenCustomerId] = useState<string | null>(null);
  const [lastSaleSummary, setLastSaleSummary] = useState<{ total: number; paid: number; profit: number } | null>(null);

  const go = (s: Screen) => { setStack(prev => [...prev, screen]); setScreen(s); };
  const back = () => { setStack(prev => { const c = [...prev]; const p = c.pop(); if (p) setScreen(p); return c; }); };

  /* Derived totals */
  const totals = useMemo(() => {
    const sales = invoices.reduce((s, i) => s + i.total, 0);
    const cogs = invoices.reduce((s, i) => s + i.items.reduce((a, it) => a + it.cost * it.qty, 0), 0);
    // collected: direct paid amounts (delivery=direct paid) + courier settlements (we don't track settled, so just direct)
    const directCollected = invoices.filter(i => i.delivery === "direct").reduce((s, i) => s + i.paid, 0);
    const expenseTotal = expenses.reduce((s, e) => s + e.amount, 0);
    const collected = directCollected; // courier custody enters only after settlement
    const grossProfit = sales - cogs;
    const netProfit = grossProfit - expenseTotal;

    // customer debts: remaining on partial/debt direct invoices + remaining customer debt portion of courier orders (total - collectedByCourier where delivered)
    const directDebt = invoices.filter(i => i.delivery === "direct").reduce((s, i) => s + (i.total - i.paid), 0);
    const courierCustomerDebt = invoices
      .filter(i => i.delivery === "courier")
      .reduce((s, i) => {
        const cs = i.courierState ?? "pending";
        if (cs === "delivered_none") return s + i.total;
        if (cs === "delivered_partial") return s + (i.total - (i.collectedByCourier ?? 0));
        if (cs === "delivered_full" || cs === "returned" || cs === "pending") return s;
        return s;
      }, 0);
    const customerDebts = directDebt + courierCustomerDebt;

    // unsettled courier custody = sum of collectedByCourier for delivered_partial/full
    const unsettledCustody = invoices
      .filter(i => i.delivery === "courier" && (i.courierState === "delivered_partial" || i.courierState === "delivered_full"))
      .reduce((s, i) => s + (i.collectedByCourier ?? 0), 0);

    // in-transit value
    const inTransit = invoices
      .filter(i => i.delivery === "courier" && (i.courierState === "pending" || !i.courierState))
      .reduce((s, i) => s + i.total, 0);

    return { sales, cogs, collected, expenseTotal, grossProfit, netProfit, customerDebts, unsettledCustody, inTransit };
  }, [invoices, expenses]);

  const lowStock = products.filter(p => p.stock > 0 && p.stock <= p.lowAt).length;
  const outStock = products.filter(p => p.stock === 0).length;

  const ctx = {
    products, customers, setCustomers, couriers, invoices, setInvoices, expenses, setExpenses, payments, setPayments,
    totals, lowStock, outStock,
    go, back, setOpenInvoiceId, openInvoiceId, setOpenCustomerId, openCustomerId,
    setLastSaleSummary, lastSaleSummary, setScreen,
  };

  return (
    <div className="min-h-screen bg-background text-foreground" dir="rtl">
      <div className="mx-auto max-w-md min-h-screen bg-background relative pb-24 shadow-sm">
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
        {screen === "sale_success" && <SaleSuccessScreen {...ctx} />}

        {!["sale", "sale_success"].includes(screen) && <BottomNav screen={screen} setScreen={(s) => { setStack([]); setScreen(s); }} onSale={() => go("sale")} />}
      </div>
    </div>
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
  const { totals, lowStock, invoices, go, setOpenInvoiceId } = p;
  const today = invoices.slice(-4).reverse();
  return (
    <>
      <div className="px-4 pt-4 pb-3 flex items-center justify-between">
        <div>
          <div className="text-2xl font-extrabold text-primary leading-none">منجز</div>
          <div className="text-xs text-muted-foreground mt-1">دفتر محلك الذكي</div>
        </div>
        <div className="flex items-center gap-1">
          <button className="p-2 rounded-full hover:bg-muted relative">
            <Bell className="w-5 h-5" />
            {lowStock > 0 && <span className="absolute top-1 left-1 w-2 h-2 bg-debt rounded-full" />}
          </button>
          <button className="p-2 rounded-full hover:bg-muted"><Menu className="w-5 h-5" /></button>
        </div>
      </div>

      {/* Today card */}
      <div className="px-4">
        <div className="rounded-2xl bg-gradient-to-br from-primary to-primary/85 text-primary-foreground p-5 shadow-md">
          <div className="text-sm opacity-90">بطاقة اليوم</div>
          <div className="mt-3 grid grid-cols-2 gap-4">
            <div>
              <div className="text-xs opacity-80">بعت اليوم</div>
              <div className="mt-1"><Money v={totals.sales} className="text-xl" /></div>
            </div>
            <div>
              <div className="text-xs opacity-80">دخل فعلًا</div>
              <div className="mt-1"><Money v={totals.collected} className="text-xl" /></div>
            </div>
          </div>
          <div className="mt-4 pt-3 border-t border-white/20">
            <div className="flex items-center gap-1.5 text-xs opacity-90">
              <TrendingUp className="w-3.5 h-3.5" /> ربح تقديري
            </div>
            <div className="mt-1 flex items-baseline gap-2">
              <Money v={totals.netProfit} className="text-lg" />
              <span className="text-[11px] opacity-80">تقريبًا</span>
            </div>
            <div className="text-[11px] opacity-75 mt-1">قد يشمل فواتير لم تُحصّل بالكامل</div>
          </div>
        </div>
      </div>

      {/* Outside collected */}
      <div className="px-4 mt-5">
        <div className="text-xs font-bold text-muted-foreground mb-2">مستحقات (خارج المحصّل)</div>
        <div className="grid grid-cols-2 gap-3">
          <button onClick={() => go("debts")} className="text-right rounded-2xl bg-card border border-border p-4 active:scale-[0.98] transition">
            <div className="flex items-center gap-2 text-debt"><CircleDollarSign className="w-4 h-4" /><span className="text-xs font-medium">ديون مستحقة</span></div>
            <div className="mt-2"><Money v={totals.customerDebts} className="text-lg text-debt" /></div>
            <div className="text-[11px] text-muted-foreground mt-1">على العملاء</div>
          </button>
          <button onClick={() => go("courier_custody")} className="text-right rounded-2xl bg-card border border-border p-4 active:scale-[0.98] transition">
            <div className="flex items-center gap-2 text-warn"><Truck className="w-4 h-4" /><span className="text-xs font-medium">عند المندوب</span></div>
            <div className="mt-2"><Money v={totals.unsettledCustody} className="text-lg text-warn" /></div>
            <div className="text-[11px] text-muted-foreground mt-1">عهدة غير مصفّاة فقط</div>
          </button>
        </div>
      </div>

      {/* Expenses */}
      <div className="px-4 mt-4">
        <div className="rounded-2xl bg-card border border-border p-4 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground">مصروفات اليوم</div>
            <div className="mt-1 text-sm">صرفت اليوم <Money v={totals.expenseTotal} className="text-base font-bold" /></div>
          </div>
          <button onClick={() => go("expenses")} className="px-3 py-2 rounded-full bg-primary-soft text-primary text-sm font-bold">+ مصروف</button>
        </div>
      </div>

      {/* Alerts */}
      {lowStock > 0 && (
        <div className="px-4 mt-3">
          <button onClick={() => go("inventory")} className="w-full text-right rounded-2xl bg-warn-soft border border-warn/20 p-3 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-warn" />
            <div className="flex-1 text-sm text-warn font-medium">{lowStock} منتجات قاربت النفاد</div>
            <ChevronLeft className="w-4 h-4 text-warn" />
          </button>
        </div>
      )}

      {/* Quick actions */}
      <div className="px-4 mt-4">
        <div className="grid grid-cols-3 gap-2">
          {[
            { l: "فاتورة", i: Plus, on: () => go("sale") },
            { l: "تحصيل دين", i: Wallet, on: () => go("debts") },
            { l: "مصروف", i: ArrowDownCircle, on: () => go("expenses") },
          ].map((a, idx) => (
            <button key={idx} onClick={a.on} className="rounded-2xl bg-card border border-border p-3 flex flex-col items-center gap-1 active:scale-95 transition">
              <a.i className="w-5 h-5 text-primary" />
              <span className="text-xs font-medium">{a.l}</span>
            </button>
          ))}
        </div>
      </div>

      {/* Last invoices */}
      <div className="px-4 mt-5">
        <div className="flex items-center justify-between mb-2">
          <div className="text-xs font-bold text-muted-foreground">آخر الفواتير</div>
          <button onClick={() => go("invoices")} className="text-xs text-primary font-bold">عرض الكل</button>
        </div>
        <div className="space-y-2">
          {today.length === 0 && <div className="rounded-2xl bg-card border border-border p-6 text-center text-sm text-muted-foreground">ابدأ يومك — لا مبيعات بعد</div>}
          {today.map((inv: Invoice) => <InvoiceRow key={inv.id} inv={inv} customers={p.customers} onOpen={(id) => { setOpenInvoiceId(id); go("invoice_detail"); }} />)}
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
  const list = p.invoices.filter((i: Invoice) => filter === "all" ? true : i.status === filter);
  const total = list.reduce((s: number, i: Invoice) => s + i.total, 0);
  return (
    <>
      <TopBar title="الفواتير" />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-3 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground">إجمالي المبيعات (ليس المحصّل)</div>
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
          {list.length === 0 && <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">لا فواتير بهذه الحالة</div>}
          {list.map((inv: Invoice) => <InvoiceRow key={inv.id} inv={inv} customers={p.customers} onOpen={(id) => { p.setOpenInvoiceId(id); p.go("invoice_detail"); }} />)}
        </div>
      </div>
    </>
  );
}

/* --------------- INVOICE DETAIL --------------- */
function InvoiceDetailScreen(p: any) {
  const inv: Invoice | undefined = p.invoices.find((i: Invoice) => i.id === p.openInvoiceId);
  if (!inv) return <><TopBar title="فاتورة" onBack={p.back} /><div className="p-4 text-sm text-muted-foreground">لم يتم العثور على الفاتورة</div></>;
  const cust = p.customers.find((c: Customer) => c.id === inv.customerId);
  const remaining = inv.total - inv.paid;
  const cogs = inv.items.reduce((s, it) => s + it.cost * it.qty, 0);
  const profit = inv.total - cogs;

  const [collectOpen, setCollectOpen] = useState(false);
  const [collectAmt, setCollectAmt] = useState("");
  const [collectMethod, setCollectMethod] = useState<"cash" | "transfer">("cash");

  const submitCollect = () => {
    const a = Number(collectAmt);
    if (!a || a <= 0 || a > remaining) return;
    p.setInvoices((arr: Invoice[]) => arr.map(i => i.id === inv.id ? { ...i, paid: i.paid + a, status: (i.paid + a) >= i.total ? "paid" : "partial" } : i));
    p.setPayments((arr: Payment[]) => [...arr, {
      id: "pay" + Date.now(),
      kind: "debt_collection",
      method: collectMethod,
      amount: a,
      invoiceId: inv.id,
      invoiceNumber: inv.number,
      customerId: inv.customerId,
      time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }),
    }]);
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
          <div className="flex justify-between"><span className="text-muted-foreground">المدفوع</span><Money v={inv.paid} className="text-success" /></div>
          <div className="flex justify-between"><span className="text-muted-foreground">المتبقي</span><Money v={remaining} className={remaining > 0 ? "text-debt" : ""} /></div>
        </div>

        <div className="rounded-2xl bg-profit-soft border border-profit/20 p-4">
          <div className="flex items-center gap-2 text-profit text-xs font-bold"><TrendingUp className="w-4 h-4" /> ربح الفاتورة (تقديري)</div>
          <div className="mt-1"><Money v={profit} className="text-lg text-profit" /></div>
          <div className="text-[11px] text-muted-foreground mt-1">التكلفة وقت البيع: <span className="num">{fmt(cogs)}</span> د.ل</div>
        </div>

        <div className="grid grid-cols-2 gap-2">
          <button disabled={remaining <= 0} onClick={() => setCollectOpen(true)} className="rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40">تحصيل دفعة</button>
          <button className="rounded-2xl bg-card border border-border py-3 font-bold">مشاركة</button>
        </div>
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
  const list = p.products.filter((pr: Product) => filter === "all" ? true : filter === "low" ? (pr.stock > 0 && pr.stock <= pr.lowAt) : pr.stock === 0);
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
          {list.length === 0 && filter !== "out" && <EmptyState text="لا منتجات بهذا التصنيف" />}
          {list.map((pr: Product) => (
            <div key={pr.id} className="rounded-2xl bg-card border border-border p-3 flex items-center justify-between">
              <div>
                <div className="font-bold text-sm">{pr.name}</div>
                <div className="mt-1 flex items-center gap-2">
                  {pr.stock === 0 && <StatusChip kind="debt" icon={<PackageX className="w-3 h-3" />}>نفد</StatusChip>}
                  {pr.stock > 0 && pr.stock <= pr.lowAt && <StatusChip kind="warn" icon={<AlertTriangle className="w-3 h-3" />}>منخفض <span className="num">{pr.stock}</span></StatusChip>}
                  {pr.stock > pr.lowAt && <StatusChip kind="info">متوفر <span className="num">{pr.stock}</span></StatusChip>}
                </div>
              </div>
              <div className="text-left"><Money v={pr.price} className="text-sm" /></div>
            </div>
          ))}
        </div>
        <button className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة منتج</button>
      </div>
    </>
  );
}

function EmptyState({ text }: { text: string }) {
  return <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">{text}</div>;
}

/* --------------- SHOP HUB --------------- */
function ShopHubScreen(p: any) {
  const cards = [
    { id: "collected", l: "المحصّل فعليًا", v: p.totals.collected, color: "text-primary", soft: "bg-primary-soft", Icon: Wallet },
    { id: "profit", l: "ربح تقديري", v: p.totals.netProfit, color: "text-profit", soft: "bg-profit-soft", Icon: TrendingUp, hint: "تقريبًا" },
    { id: "debts", l: "ديون مستحقة", v: p.totals.customerDebts, color: "text-debt", soft: "bg-debt-soft", Icon: CircleDollarSign },
    { id: "courier_custody", l: "عند المندوب", v: p.totals.unsettledCustody, color: "text-warn", soft: "bg-warn-soft", Icon: Truck, hint: "عهدة غير مصفّاة" },
  ];
  const sections = [
    { id: "profit", l: "الربح التقديري", Icon: TrendingUp },
    { id: "collected", l: "المحصّل فعليًا", Icon: Wallet },
    { id: "debts", l: "الديون", Icon: CircleDollarSign },
    { id: "courier_custody", l: "عهدة المندوب", Icon: Truck },
    { id: "settlements", l: "التسويات", Icon: Banknote },
    { id: "expenses", l: "المصروفات", Icon: ArrowDownCircle },
    { id: "customers", l: "العملاء", Icon: Users },
    { id: "couriers", l: "المندوبون", Icon: Truck },
    { id: "settings", l: "الإعدادات", Icon: SettingsIcon },
  ];
  return (
    <>
      <TopBar title="المحل" />
      <div className="px-4 pt-3">
        <div className="flex gap-2 mb-3">
          {["اليوم", "الأسبوع", "الشهر"].map((x, i) => (
            <button key={x} className={`px-4 py-1.5 rounded-full text-xs font-bold ${i === 0 ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{x}</button>
          ))}
        </div>
        <div className="grid grid-cols-2 gap-3">
          {cards.map(c => (
            <button key={c.id} onClick={() => p.go(c.id as Screen)} className={`text-right rounded-2xl ${c.soft} p-4 active:scale-[0.98] transition`}>
              <div className={`flex items-center gap-2 ${c.color} text-xs font-bold`}><c.Icon className="w-4 h-4" />{c.l}</div>
              <div className="mt-2"><Money v={c.v} className={`text-lg ${c.color}`} /></div>
              {c.hint && <div className="text-[11px] text-muted-foreground mt-1">{c.hint}</div>}
            </button>
          ))}
        </div>

        <div className="mt-5 text-xs font-bold text-muted-foreground mb-2">الأقسام</div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border overflow-hidden">
          {sections.map(s => (
            <button key={s.id} onClick={() => p.go(s.id as Screen)} className="w-full flex items-center gap-3 px-4 py-3 text-right hover:bg-muted active:bg-muted">
              <s.Icon className="w-5 h-5 text-primary" />
              <span className="flex-1 text-sm font-medium">{s.l}</span>
              <ChevronLeft className="w-4 h-4 text-muted-foreground" />
            </button>
          ))}
        </div>
      </div>
    </>
  );
}

/* --------------- PROFIT --------------- */
function ProfitScreen(p: any) {
  const { sales, cogs, grossProfit, expenseTotal, netProfit } = p.totals;
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
      <TopBar title="الربح التقديري" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4 divide-y divide-border">
          <Row label="المبيعات" v={sales} />
          <Row label="تكلفة البضاعة المباعة" v={cogs} op="−" />
          <Row label="الربح الإجمالي" v={grossProfit} op="=" color="text-profit font-bold" />
          <Row label="المصروفات" v={expenseTotal} op="−" />
          <Row label="صافي الربح التقديري" v={netProfit} op="=" color="text-profit font-bold text-lg" />
        </div>
        <div className="rounded-2xl bg-warn-soft border border-warn/20 p-3 text-xs text-warn flex gap-2"><Info className="w-4 h-4 shrink-0 mt-0.5" /><span>تقديري — قد يشمل فواتير لم تُحصّل بالكامل. الربح ليس نقدًا بيدك.</span></div>
      </div>
    </>
  );
}

/* --------------- COLLECTED --------------- */
function CollectedScreen(p: any) {
  const payments: Payment[] = p.payments;
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

  const sorted = [...payments].sort((a, b) => (a.time < b.time ? 1 : a.time > b.time ? -1 : 0));

  return (
    <>
      <TopBar title="المحصّل فعليًا" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-primary text-primary-foreground p-5">
          <div className="text-xs opacity-90">المدفوع المحصّل</div>
          <Money v={p.totals.collected} className="text-2xl mt-1" />
          <div className="text-[11px] opacity-80 mt-2">ما دخل فعلًا لجيبك حتى الآن</div>
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
        {Math.abs(sum - p.totals.collected) > 0.5 && (
          <div className="rounded-xl bg-warn-soft text-warn text-[11px] p-2 flex gap-2"><Info className="w-3 h-3 mt-0.5 shrink-0" />فرق بسيط بين المجموع والتفصيل قد يظهر مع بيانات تجريبية.</div>
        )}
        <div className="rounded-2xl bg-info-soft border border-info/20 p-3 text-xs text-info flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>لا يشمل ديون العملاء، ولا عهدة المندوب غير المصفّاة. المصروفات لا تُنقص هذا الرقم.</span>
        </div>
        <div className="text-xs font-bold text-muted-foreground mt-2">الحركة</div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {sorted.length === 0 && <div className="p-4 text-sm text-muted-foreground text-center">لا حركات بعد</div>}
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
  const invs = p.invoices.filter((i: Invoice) => i.customerId === cust?.id && (i.total - i.paid) > 0);
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
  const [courierId, setCourierId] = useState<string>(p.couriers[0]?.id);
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

  return (
    <>
      <TopBar title="عهدة المندوب" onBack={p.back} right={<button onClick={() => p.go("settlements")} className="text-xs font-bold text-primary px-3 py-1.5 rounded-full bg-primary-soft">تسوية</button>} />
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
              <div key={i.id} className="text-xs flex justify-between bg-card rounded-lg px-3 py-2">
                <span>#{i.number} · {p.customers.find((c: Customer) => c.id === i.customerId)?.name}</span>
                <Money v={i.total} />
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
          <div className="text-[11px] text-muted-foreground mt-1">هذه ديون عملاء — ليست عهدة. تظهر أيضًا في إجمالي الديون.</div>
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
    </>
  );
}

/* --------------- SETTLEMENTS --------------- */
function SettlementsScreen(p: any) {
  const courier = p.couriers[0];
  const collected = p.invoices.filter((i: Invoice) => i.delivery === "courier" && i.courierId === courier.id && (i.courierState === "delivered_partial" || i.courierState === "delivered_full"));
  const pending = p.invoices.filter((i: Invoice) => i.delivery === "courier" && i.courierId === courier.id && (i.courierState ?? "pending") === "pending");
  const [selected, setSelected] = useState<Set<string>>(new Set(collected.map((i: Invoice) => i.id)));
  const [done, setDone] = useState(false);

  const toggle = (id: string) => setSelected(s => { const n = new Set(s); n.has(id) ? n.delete(id) : n.add(id); return n; });
  const net = collected.filter((i: Invoice) => selected.has(i.id)).reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);

  const [settledAmount, setSettledAmount] = useState(0);
  const confirm = () => {
    setSettledAmount(net);
    const settledInvoices = collected.filter((i: Invoice) => selected.has(i.id));
    const now = new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });
    p.setInvoices((arr: Invoice[]) => arr.map(i => {
      if (selected.has(i.id) && (i.courierState === "delivered_partial" || i.courierState === "delivered_full")) {
        const collectedAmt = i.collectedByCourier ?? 0;
        return { ...i, delivery: "direct" as const, paid: i.paid + collectedAmt, collectedByCourier: 0, status: (i.paid + collectedAmt) >= i.total ? "paid" as const : "partial" as const };
      }
      return i;
    }));
    p.setPayments((arr: Payment[]) => [
      ...arr,
      ...settledInvoices.map((i: Invoice, idx: number) => ({
        id: "pay" + Date.now() + "_" + idx,
        kind: "settlement" as const,
        method: "settlement" as const,
        amount: i.collectedByCourier ?? 0,
        invoiceId: i.id,
        invoiceNumber: i.number,
        customerId: i.customerId,
        courierId: i.courierId,
        time: now,
      })),
    ]);
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

  const total = p.expenses.reduce((s: number, e: Expense) => s + e.amount, 0);
  const cashT = p.expenses.filter((e: Expense) => e.method === "cash").reduce((s: number, e: Expense) => s + e.amount, 0);
  const transferT = total - cashT;

  const canSave = Number(amount) > 0 && !!method && !!type;
  const save = () => {
    p.setExpenses((arr: Expense[]) => [...arr, { id: "e" + Date.now(), type, amount: Number(amount), method: method as any, time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }) }]);
    setAmount(""); setType(""); setMethod(""); setOpen(false); setSuccess(true);
    setTimeout(() => setSuccess(false), 1800);
  };

  const types = ["إيجار", "كهرباء", "إنترنت", "تغليف", "نقل", "صيانة", "راتب", "أخرى"];

  return (
    <>
      <TopBar title="المصروفات" onBack={p.back} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="text-xs text-muted-foreground">إجمالي المصروفات اليوم</div>
          <Money v={total} className="text-2xl mt-1" />
          <div className="mt-2 text-xs text-muted-foreground">نقدي <span className="num">{fmt(cashT)}</span> · تحويل <span className="num">{fmt(transferT)}</span></div>
        </div>
        <div className="rounded-2xl bg-info-soft border border-info/20 p-3 text-xs text-info flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>المصروفات تنقص <b>الربح التقديري</b> فقط. لا تنقص المحصّل فعلًا.</span>
        </div>
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {p.expenses.map((e: Expense) => (
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
  const debtMap = new Map<string, number>();
  p.invoices.forEach((i: Invoice) => { if (i.customerId && i.total - i.paid > 0 && i.delivery === "direct") debtMap.set(i.customerId, (debtMap.get(i.customerId) ?? 0) + (i.total - i.paid)); });
  return (
    <>
      <TopBar title="العملاء" onBack={p.back} />
      <div className="px-4 pt-3 space-y-2">
        {p.customers.map((c: Customer) => (
          <div key={c.id} className="rounded-2xl bg-card border border-border p-3 flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary-soft text-primary flex items-center justify-center font-bold">{c.name[0]}</div>
            <div className="flex-1">
              <div className="font-bold text-sm">{c.name}</div>
              <div className="text-xs text-muted-foreground">{c.phone ?? "بدون رقم"}</div>
            </div>
            {debtMap.get(c.id) ? <Money v={debtMap.get(c.id)!} className="text-debt font-bold text-sm" /> : <span className="text-[11px] text-success">لا دين</span>}
          </div>
        ))}
        <button className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة عميل</button>
      </div>
    </>
  );
}

function CouriersScreen(p: any) {
  return (
    <>
      <TopBar title="المندوبون" onBack={p.back} />
      <div className="px-4 pt-3 space-y-2">
        {p.couriers.map((c: Courier) => {
          const list = p.invoices.filter((i: Invoice) => i.courierId === c.id);
          const custody = list.filter((i: Invoice) => i.courierState === "delivered_partial" || i.courierState === "delivered_full").reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);
          return (
            <button key={c.id} onClick={() => p.go("courier_custody")} className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3">
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
        <button className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة مندوب</button>
      </div>
    </>
  );
}

function SettingsScreen(p: any) {
  const rows = ["بيانات المحل", "العملة وصيغة الأرقام", "حد التنبيه الافتراضي", "نسخ احتياطي ومزامنة", "تسجيل الخروج"];
  return (
    <>
      <TopBar title="الإعدادات" onBack={p.back} />
      <div className="px-4 pt-3">
        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          {rows.map(r => (
            <div key={r} className="flex items-center gap-3 px-4 py-3">
              <span className="flex-1 text-sm">{r}</span>
              <ChevronLeft className="w-4 h-4 text-muted-foreground" />
            </div>
          ))}
        </div>
        <div className="mt-4 text-[11px] text-muted-foreground text-center">آخر مزامنة منذ 5 دقائق</div>
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


      <div className={`px-4 grid grid-cols-2 gap-2 flex-1 ${searchFocused ? "pb-80" : "pb-4"}`}>
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
          setCustomers={p.setCustomers}
          couriers={p.couriers}
          onClose={() => setPaySheet(false)}
          onSave={(d: { paid: number; customerId?: string; delivery: "direct" | "courier"; courierId?: string; method: "cash" | "transfer" }) => {
            const items: InvoiceItem[] = cart.map(c => {
              const pr = p.products.find((x: Product) => x.id === c.productId)!;
              return { productId: pr.id, name: pr.name, qty: c.qty, price: pr.price, cost: pr.cost };
            });
            const cogs = items.reduce((s, it) => s + it.cost * it.qty, 0);
            const number = String(1040 + p.invoices.length + 1);
            const newInv: Invoice = {
              id: "i" + Date.now(),
              number,
              items,
              total: subtotal,
              paid: d.paid,
              customerId: d.customerId,
              delivery: d.delivery,
              courierId: d.courierId,
              status: d.paid >= subtotal ? "paid" : d.paid > 0 ? "partial" : "debt",
              courierState: d.delivery === "courier" ? "pending" : undefined,
              time: new Date().toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false }),
            };
            p.setInvoices((arr: Invoice[]) => [...arr, newInv]);
            if (d.delivery === "direct" && d.paid > 0) {
              p.setPayments((arr: Payment[]) => [...arr, {
                id: "pay" + Date.now(),
                kind: "sale",
                method: d.method,
                amount: d.paid,
                invoiceId: newInv.id,
                invoiceNumber: newInv.number,
                customerId: d.customerId,
                time: newInv.time,
              }]);
            }
            p.setLastSaleSummary({ total: subtotal, paid: d.paid, profit: subtotal - cogs });
            p.setScreen("sale_success");
          }}
        />
      )}
    </div>
  );
}

function PaymentSheet({ subtotal, customers, setCustomers, couriers, onClose, onSave }: any) {
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
            <label className="text-xs font-bold text-muted-foreground">المدفوع</label>
            <input value={paidStr} onChange={e => setPaidStr(e.target.value)} inputMode="decimal" className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right" />
          </div>
        )}

        {overpaid && <div className="rounded-xl bg-debt-soft text-debt text-xs p-3 flex items-center gap-2"><AlertTriangle className="w-4 h-4" />المبلغ المدفوع أكبر من الإجمالي</div>}

        {(status === "partial" || status === "debt") && (
          <div className="rounded-xl bg-debt-soft p-3 flex items-center justify-between">
            <div><div className="text-xs text-debt">المتبقي</div><Money v={Math.max(0, remaining)} className="text-debt font-bold" /></div>
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
                <button onClick={() => {
                  const id = "c" + Date.now();
                  setCustomers((arr: Customer[]) => [...arr, { id, name: trimmedName, phone: trimmedPhone || undefined }]);
                  setCustomerId(id); setNewName(""); setNewPhone(""); setPickCustomer(false);
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
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-6 text-center gap-4">
      <div className="w-20 h-20 rounded-full bg-success-soft flex items-center justify-center"><CheckCircle2 className="w-10 h-10 text-success" /></div>
      <div className="text-xl font-bold">تم حفظ الفاتورة</div>
      {s && (
        <div className="text-sm text-muted-foreground">
          الإجمالي <span className="num font-bold text-foreground">{fmt(s.total)}</span> · مدفوع <span className="num font-bold text-success">{fmt(s.paid)}</span>
          <div className="mt-2 inline-flex items-center gap-1 px-3 py-1 rounded-full bg-profit-soft text-profit text-xs"><TrendingUp className="w-3 h-3" />ربح تقديري <span className="num font-bold">{fmt(s.profit)}</span> د.ل</div>
        </div>
      )}
      <div className="w-full max-w-xs space-y-2 mt-4">
        <button onClick={() => p.setScreen("sale")} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">فاتورة جديدة</button>
        <button onClick={() => p.setScreen("home")} className="w-full rounded-2xl bg-card border border-border py-3 font-bold">عودة للرئيسية</button>
      </div>
    </div>
  );
}

/* ============================== UTILITIES ============================== */
function Sheet({ children, title, onClose }: { children: React.ReactNode; title: string; onClose: () => void }) {
  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={onClose}>
      <div onClick={e => e.stopPropagation()} className="w-full max-w-md bg-card rounded-t-3xl p-4 pb-6 max-h-[90vh] overflow-y-auto" dir="rtl">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-bold">{title}</h3>
          <button onClick={onClose} className="p-2 rounded-full hover:bg-muted"><X className="w-5 h-5" /></button>
        </div>
        {children}
      </div>
    </div>
  );
}

function Toast({ text, kind = "info" }: { text: string; kind?: "info" | "warn" | "success" }) {
  const colors = { info: "bg-foreground text-background", warn: "bg-warn text-white", success: "bg-success text-white" };
  return (
    <div className="fixed bottom-28 inset-x-0 z-50 flex justify-center pointer-events-none">
      <div className={`px-4 py-2 rounded-full text-sm font-bold shadow-lg ${colors[kind]}`}>{text}</div>
    </div>
  );
}
