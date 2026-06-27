import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/_authenticated/platform-admin")({
  component: PlatformAdminPage,
});

type TabKey = "overview" | "tenants" | "financial" | "system" | "dayclose" | "custody" | "alerts" | "security" | "audit";

const TABS: { key: TabKey; label: string }[] = [
  { key: "overview", label: "نظرة عامة" },
  { key: "tenants", label: "المتاجر" },
  { key: "financial", label: "الصحة المالية" },
  { key: "system", label: "صحة النظام" },
  { key: "dayclose", label: "إغلاق اليوم" },
  { key: "custody", label: "عهدة المناديب" },
  { key: "alerts", label: "التنبيهات" },
  { key: "security", label: "فحوص الأمان" },
  { key: "audit", label: "سجل التدقيق" },
];

function PlatformAdminPage() {
  const [checking, setChecking] = useState(true);
  const [allowed, setAllowed] = useState(false);
  const [tab, setTab] = useState<TabKey>("overview");

  useEffect(() => {
    (async () => {
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { data, error } = await (supabase.rpc as any)("is_platform_admin");
      setAllowed(!error && data === true);
      setChecking(false);
    })();
  }, []);

  if (checking) {
    return <Centered>جاري التحقق…</Centered>;
  }
  if (!allowed) {
    return <Forbidden />;
  }

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground">
      <header className="border-b bg-card">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold">لوحة مشرف منصة منجز</h1>
            <p className="text-xs text-muted-foreground">داخلي — للقراءة فقط</p>
          </div>
          <span className="text-xs px-2 py-1 rounded bg-primary/10 text-primary">Platform Admin</span>
        </div>
        <nav className="max-w-7xl mx-auto px-4 flex gap-1 overflow-x-auto">
          {TABS.map((t) => (
            <button
              key={t.key}
              onClick={() => setTab(t.key)}
              className={`px-3 py-2 text-sm whitespace-nowrap border-b-2 ${
                tab === t.key
                  ? "border-primary text-primary font-semibold"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              {t.label}
            </button>
          ))}
        </nav>
      </header>
      <main className="max-w-7xl mx-auto p-4">
        {tab === "overview" && <OverviewTab />}
        {tab === "tenants" && <TenantsTab />}
        {tab === "financial" && <FinancialTab />}
        {tab === "system" && <SystemTab />}
        {tab === "dayclose" && <DayCloseTab />}
        {tab === "custody" && <CustodyTab />}
        {tab === "alerts" && <AlertsTab />}
        {tab === "security" && <SecurityTab />}
        {tab === "audit" && <AuditTab />}
      </main>
    </div>
  );
}

function Centered({ children }: { children: React.ReactNode }) {
  return (
    <div dir="rtl" className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
      {children}
    </div>
  );
}

function Forbidden() {
  return (
    <div dir="rtl" className="min-h-screen flex flex-col items-center justify-center gap-3 p-6 text-center">
      <div className="text-5xl">🔒</div>
      <h1 className="text-xl font-bold">ممنوع</h1>
      <p className="text-sm text-muted-foreground max-w-sm">
        هذه الصفحة مخصصة لمشغّل منصة منجز فقط.
      </p>
      <a href="/app" className="text-sm text-primary hover:underline mt-2">العودة للتطبيق</a>
    </div>
  );
}

// ────────────────────── helpers ──────────────────────
function StatusBadge({ status }: { status: string }) {
  const map: Record<string, string> = {
    Healthy: "bg-emerald-100 text-emerald-800",
    Matches: "bg-emerald-100 text-emerald-800",
    Passed: "bg-emerald-100 text-emerald-800",
    Warning: "bg-amber-100 text-amber-800",
    Mismatch: "bg-amber-100 text-amber-800",
    Critical: "bg-red-100 text-red-800",
  };
  const label: Record<string, string> = {
    Healthy: "سليم",
    Matches: "مطابق",
    Passed: "ناجح",
    Warning: "تحذير",
    Mismatch: "غير مطابق",
    Critical: "حرج",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-medium ${map[status] ?? "bg-muted text-muted-foreground"}`}>
      {label[status] ?? status}
    </span>
  );
}

const fmt = (n: number | string | null | undefined) => {
  const v = Number(n ?? 0);
  return v.toLocaleString("en-US", { maximumFractionDigits: 2 });
};
const dl = (n: number | string | null | undefined) => `${fmt(n)} د.ل`;
const short = (s: string | null | undefined, n = 8) => (s ? s.slice(0, n) : "—");
const dt = (s: string | null | undefined) =>
  s ? new Date(s).toLocaleString("ar-LY", { dateStyle: "short", timeStyle: "short" }) : "—";

function Card({ title, value, hint, tone = "neutral" }: { title: string; value: React.ReactNode; hint?: string; tone?: "neutral" | "warn" | "crit" | "ok" }) {
  const tones: Record<string, string> = {
    neutral: "bg-card",
    warn: "bg-amber-50 border-amber-200",
    crit: "bg-red-50 border-red-200",
    ok: "bg-emerald-50 border-emerald-200",
  };
  return (
    <div className={`rounded-lg border p-3 ${tones[tone]}`}>
      <div className="text-xs text-muted-foreground">{title}</div>
      <div className="text-lg font-bold mt-1">{value}</div>
      {hint && <div className="text-[10px] text-muted-foreground mt-1">{hint}</div>}
    </div>
  );
}

function useRpc<T = unknown>(fn: string, args?: Record<string, unknown>) {
  const [data, setData] = useState<T | null>(null);
  const [err, setErr] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    let active = true;
    (async () => {
      setLoading(true);
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const { data: d, error } = await (supabase.rpc as any)(fn, args ?? {});
      if (!active) return;
      if (error) setErr(error.message);
      else setData(d as T);
      setLoading(false);
    })();
    return () => { active = false; };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [fn, JSON.stringify(args ?? {})]);
  return { data, err, loading };
}

// ────────────────────── tabs ──────────────────────
type Overview = {
  total_tenants: number; active_tenants: number; total_products: number; total_customers: number;
  total_orders: number; total_payments: number; open_customer_debts: number;
  unsettled_courier_custody: number; expenses_today: number; day_close_count_today: number;
  critical_alerts: number;
};

function OverviewTab() {
  const { data, err, loading } = useRpc<Overview>("get_platform_admin_overview");
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  if (!data) return null;
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <Card title="إجمالي المتاجر" value={fmt(data.total_tenants)} />
      <Card title="متاجر نشطة (30 يوم)" value={fmt(data.active_tenants)} />
      <Card title="إجمالي المنتجات" value={fmt(data.total_products)} />
      <Card title="إجمالي العملاء" value={fmt(data.total_customers)} />
      <Card title="إجمالي الفواتير" value={fmt(data.total_orders)} />
      <Card title="إجمالي المدفوعات" value={fmt(data.total_payments)} />
      <Card title="ديون مفتوحة" value={dl(data.open_customer_debts)} tone="warn" />
      <Card title="عهدة مناديب غير مسوّاة" value={dl(data.unsettled_courier_custody)} tone="warn" />
      <Card title="مصاريف اليوم" value={dl(data.expenses_today)} />
      <Card title="إغلاقات يوم اليوم" value={fmt(data.day_close_count_today)} />
      <Card title="تنبيهات حرجة" value={fmt(data.critical_alerts)} tone={data.critical_alerts > 0 ? "crit" : "ok"} />
    </div>
  );
}

type TenantRow = {
  tenant_id: string; tenant_name: string; owner_user_id: string; created_at: string;
  products_count: number; customers_count: number; orders_count: number;
  total_sales: number; total_collected: number; open_debts: number;
  unsettled_custody: number; last_activity: string | null; health: string;
};

function TenantsTab() {
  const { data, err, loading } = useRpc<TenantRow[]>("get_platform_tenants_health");
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  const rows = data ?? [];
  if (rows.length === 0) return <p className="text-sm text-muted-foreground">لا توجد متاجر بعد.</p>;
  return (
    <div className="overflow-x-auto border rounded-lg bg-card">
      <table className="w-full text-xs">
        <thead className="bg-muted/50">
          <tr className="text-right">
            <th className="p-2">المتجر</th>
            <th className="p-2">معرف</th>
            <th className="p-2">المالك</th>
            <th className="p-2">منتجات</th>
            <th className="p-2">عملاء</th>
            <th className="p-2">فواتير</th>
            <th className="p-2">مبيعات</th>
            <th className="p-2">محصّل</th>
            <th className="p-2">ديون</th>
            <th className="p-2">عهدة</th>
            <th className="p-2">آخر نشاط</th>
            <th className="p-2">الحالة</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.tenant_id} className="border-t">
              <td className="p-2 font-medium">{r.tenant_name}</td>
              <td className="p-2 font-mono">{short(r.tenant_id)}</td>
              <td className="p-2 font-mono">{short(r.owner_user_id)}</td>
              <td className="p-2">{fmt(r.products_count)}</td>
              <td className="p-2">{fmt(r.customers_count)}</td>
              <td className="p-2">{fmt(r.orders_count)}</td>
              <td className="p-2">{dl(r.total_sales)}</td>
              <td className="p-2">{dl(r.total_collected)}</td>
              <td className="p-2">{dl(r.open_debts)}</td>
              <td className="p-2">{dl(r.unsettled_custody)}</td>
              <td className="p-2">{dt(r.last_activity)}</td>
              <td className="p-2"><StatusBadge status={r.health} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type CheckRow = { check_key: string; explanation_ar: string; status: string; affected_count: number };

function FinancialTab() {
  const { data, err, loading } = useRpc<CheckRow[]>("get_platform_financial_health");
  const [openKey, setOpenKey] = useState<string | null>(null);
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  const rows = data ?? [];
  return (
    <div className="space-y-2">
      {rows.map((r) => (
        <div key={r.check_key} className="border rounded-lg bg-card">
          <div className="p-3 flex items-center justify-between gap-2">
            <div className="flex-1">
              <div className="text-sm font-medium">{r.explanation_ar}</div>
              <div className="text-[10px] text-muted-foreground font-mono mt-0.5">{r.check_key}</div>
            </div>
            <div className="text-sm font-bold tabular-nums">{fmt(r.affected_count)}</div>
            <StatusBadge status={r.status} />
            {r.affected_count > 0 && (
              <button
                onClick={() => setOpenKey(openKey === r.check_key ? null : r.check_key)}
                className="text-xs text-primary hover:underline"
              >
                {openKey === r.check_key ? "إخفاء" : "عرض الصفوف"}
              </button>
            )}
          </div>
          {openKey === r.check_key && <AffectedRows checkKey={r.check_key} />}
        </div>
      ))}
    </div>
  );
}

function AffectedRows({ checkKey }: { checkKey: string }) {
  const { data, err, loading } = useRpc<Record<string, unknown>[]>(
    "get_platform_financial_health_rows",
    { p_check_key: checkKey, p_limit: 50 }
  );
  if (loading) return <div className="p-3 text-xs text-muted-foreground">جاري التحميل…</div>;
  if (err) return <div className="p-3 text-xs text-red-600">خطأ: {err}</div>;
  const rows = data ?? [];
  if (rows.length === 0) return <div className="p-3 text-xs text-muted-foreground">لا توجد بيانات.</div>;
  const cols = Object.keys(rows[0]);
  return (
    <div className="border-t overflow-x-auto bg-muted/20">
      <table className="w-full text-[11px]">
        <thead>
          <tr>{cols.map((c) => <th key={c} className="p-2 text-right font-medium">{c}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t">
              {cols.map((c) => <td key={c} className="p-2 font-mono">{String(r[c] ?? "—")}</td>)}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type SystemHealth = {
  rls: { table: string; rls_enabled: boolean; status: string }[];
  rpcs: { rpc: string; exists: boolean; anon_can_execute: boolean; public_can_execute: boolean; status: string }[];
  grant_issues: { rpc: string; issue: string }[];
};

function SystemTab() {
  const { data, err, loading } = useRpc<SystemHealth>("get_platform_system_health");
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  if (!data) return null;
  return (
    <div className="grid md:grid-cols-2 gap-4">
      <section className="border rounded-lg bg-card p-3">
        <h3 className="font-semibold mb-2 text-sm">RLS على الجداول الحساسة</h3>
        <table className="w-full text-xs">
          <tbody>
            {data.rls.map((r) => (
              <tr key={r.table} className="border-t">
                <td className="p-2 font-mono">{r.table}</td>
                <td className="p-2">{r.rls_enabled ? "مفعّل" : "معطّل"}</td>
                <td className="p-2 text-left"><StatusBadge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="border rounded-lg bg-card p-3">
        <h3 className="font-semibold mb-2 text-sm">الوظائف المالية (RPC)</h3>
        <table className="w-full text-xs">
          <tbody>
            {data.rpcs.map((r) => (
              <tr key={r.rpc} className="border-t">
                <td className="p-2 font-mono">{r.rpc}</td>
                <td className="p-2">{r.exists ? "موجودة" : "مفقودة"}</td>
                <td className="p-2 text-[10px] text-muted-foreground">
                  {r.anon_can_execute ? "anon ⚠" : ""}{r.public_can_execute ? " PUBLIC ⚠" : ""}
                </td>
                <td className="p-2 text-left"><StatusBadge status={r.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
      <section className="md:col-span-2 border rounded-lg bg-card p-3">
        <h3 className="font-semibold mb-2 text-sm">مشاكل صلاحيات</h3>
        {data.grant_issues.length === 0 ? (
          <p className="text-xs text-emerald-700">لا توجد مشاكل صلاحيات.</p>
        ) : (
          <ul className="text-xs space-y-1">
            {data.grant_issues.map((g, i) => (
              <li key={i} className="font-mono">{g.rpc} → {g.issue}</li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}

type DayCloseRow = {
  id: string; tenant_id: string; tenant_name: string; closed_for: string;
  sales: number; collected: number; expenses: number; customer_debts: number;
  unsettled_custody: number; realized_profit: number; created_at: string;
  sales_diff: number; collected_diff: number; expenses_diff: number; status: string;
};

function DayCloseTab() {
  const { data, err, loading } = useRpc<DayCloseRow[]>("get_platform_day_close_health", { p_limit: 50 });
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  const rows = data ?? [];
  if (rows.length === 0) return <p className="text-sm text-muted-foreground">لا توجد إغلاقات يوم بعد.</p>;
  return (
    <div className="overflow-x-auto border rounded-lg bg-card">
      <table className="w-full text-xs">
        <thead className="bg-muted/50">
          <tr className="text-right">
            <th className="p-2">المتجر</th>
            <th className="p-2">التاريخ</th>
            <th className="p-2">مبيعات</th>
            <th className="p-2">محصّل</th>
            <th className="p-2">مصاريف</th>
            <th className="p-2">ديون</th>
            <th className="p-2">عهدة</th>
            <th className="p-2">ربح محقق</th>
            <th className="p-2">Δ مبيعات</th>
            <th className="p-2">Δ محصّل</th>
            <th className="p-2">Δ مصاريف</th>
            <th className="p-2">الحالة</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id} className="border-t">
              <td className="p-2">{r.tenant_name ?? short(r.tenant_id)}</td>
              <td className="p-2">{r.closed_for}</td>
              <td className="p-2">{dl(r.sales)}</td>
              <td className="p-2">{dl(r.collected)}</td>
              <td className="p-2">{dl(r.expenses)}</td>
              <td className="p-2">{dl(r.customer_debts)}</td>
              <td className="p-2">{dl(r.unsettled_custody)}</td>
              <td className="p-2">{dl(r.realized_profit)}</td>
              <td className={`p-2 ${Math.abs(r.sales_diff) > 0.01 ? "text-red-600" : ""}`}>{dl(r.sales_diff)}</td>
              <td className={`p-2 ${Math.abs(r.collected_diff) > 0.01 ? "text-red-600" : ""}`}>{dl(r.collected_diff)}</td>
              <td className={`p-2 ${Math.abs(r.expenses_diff) > 0.01 ? "text-red-600" : ""}`}>{dl(r.expenses_diff)}</td>
              <td className="p-2"><StatusBadge status={r.status} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

type CustodyRow = {
  tenant_id: string; tenant_name: string; courier_id: string; courier_name: string;
  unsettled_amount: number; orders_count: number; oldest_age_days: number; risk: string;
};

function CustodyTab() {
  const { data, err, loading } = useRpc<CustodyRow[]>("get_platform_courier_custody_health");
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  const rows = data ?? [];
  if (rows.length === 0) return <p className="text-sm text-emerald-700">لا توجد عهدة معلقة.</p>;
  return (
    <div className="overflow-x-auto border rounded-lg bg-card">
      <table className="w-full text-xs">
        <thead className="bg-muted/50">
          <tr className="text-right">
            <th className="p-2">المتجر</th>
            <th className="p-2">المندوب</th>
            <th className="p-2">المبلغ غير المسوّى</th>
            <th className="p-2">عدد الفواتير</th>
            <th className="p-2">أقدم عهدة (يوم)</th>
            <th className="p-2">الخطورة</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="border-t">
              <td className="p-2">{r.tenant_name ?? short(r.tenant_id)}</td>
              <td className="p-2">{r.courier_name ?? short(r.courier_id)}</td>
              <td className="p-2 font-semibold">{dl(r.unsettled_amount)}</td>
              <td className="p-2">{fmt(r.orders_count)}</td>
              <td className="p-2">{fmt(r.oldest_age_days)}</td>
              <td className="p-2"><StatusBadge status={r.risk} /></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AlertsTab() {
  const overview = useRpc<Overview>("get_platform_admin_overview");
  const checks = useRpc<CheckRow[]>("get_platform_financial_health");
  const sys = useRpc<SystemHealth>("get_platform_system_health");
  const custody = useRpc<CustodyRow[]>("get_platform_courier_custody_health");

  if (overview.loading || checks.loading || sys.loading || custody.loading)
    return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;

  type Alert = { level: "Critical" | "High" | "Medium" | "Low"; text: string };
  const alerts: Alert[] = [];

  (checks.data ?? []).forEach((c) => {
    if (c.status === "Critical") alerts.push({ level: "Critical", text: `${c.explanation_ar} (${c.affected_count})` });
    else if (c.status === "Warning") alerts.push({ level: "Medium", text: `${c.explanation_ar} (${c.affected_count})` });
  });
  (sys.data?.rls ?? []).forEach((r) => {
    if (!r.rls_enabled) alerts.push({ level: "High", text: `RLS معطّل على ${r.table}` });
  });
  (sys.data?.rpcs ?? []).forEach((r) => {
    if (!r.exists) alerts.push({ level: "Critical", text: `وظيفة مالية مفقودة: ${r.rpc}` });
    if (r.anon_can_execute) alerts.push({ level: "High", text: `anon يمكنه تنفيذ ${r.rpc}` });
    if (r.public_can_execute) alerts.push({ level: "High", text: `PUBLIC يمكنه تنفيذ ${r.rpc}` });
  });
  (custody.data ?? []).forEach((c) => {
    if (c.oldest_age_days > 7) alerts.push({ level: "Medium", text: `عهدة قديمة (${c.oldest_age_days} يوم) عند ${c.courier_name ?? short(c.courier_id)}` });
    else if (c.oldest_age_days > 3) alerts.push({ level: "Low", text: `عهدة (${c.oldest_age_days} يوم) عند ${c.courier_name ?? short(c.courier_id)}` });
  });

  const order: Record<Alert["level"], number> = { Critical: 0, High: 1, Medium: 2, Low: 3 };
  alerts.sort((a, b) => order[a.level] - order[b.level]);

  if (alerts.length === 0) return <p className="text-sm text-emerald-700">لا توجد تنبيهات. النظام سليم.</p>;

  const tone: Record<Alert["level"], string> = {
    Critical: "bg-red-50 border-red-200 text-red-900",
    High: "bg-orange-50 border-orange-200 text-orange-900",
    Medium: "bg-amber-50 border-amber-200 text-amber-900",
    Low: "bg-sky-50 border-sky-200 text-sky-900",
  };
  const labelAr: Record<Alert["level"], string> = {
    Critical: "حرج", High: "مرتفع", Medium: "متوسط", Low: "منخفض",
  };
  return (
    <div className="space-y-2">
      {alerts.map((a, i) => (
        <div key={i} className={`border rounded-lg p-3 text-sm flex items-center justify-between ${tone[a.level]}`}>
          <span>{a.text}</span>
          <span className="text-xs font-bold">{labelAr[a.level]}</span>
        </div>
      ))}
    </div>
  );
}

type AuditRow = {
  id: string;
  user_id: string;
  user_email: string | null;
  action: string;
  details: Record<string, unknown> | null;
  created_at: string;
};

const ACTION_LABELS: Record<string, string> = {
  view_overview: "فتح نظرة عامة",
  view_tenants: "عرض المتاجر",
  view_financial_health: "عرض الصحة المالية",
  view_financial_health_rows: "عرض صفوف فحص مالي",
  view_system_health: "عرض صحة النظام",
  view_day_close_health: "عرض إغلاق اليوم",
  view_courier_custody_health: "عرض عهدة المناديب",
};

function AuditTab() {
  const [limit, setLimit] = useState(100);
  const { data, err, loading } = useRpc<AuditRow[]>("get_platform_admin_audit_log", { p_limit: limit, p_offset: 0 });
  if (loading) return <p className="text-sm text-muted-foreground">جاري التحميل…</p>;
  if (err) return <p className="text-sm text-red-600">خطأ: {err}</p>;
  const rows = data ?? [];
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between gap-2">
        <p className="text-xs text-muted-foreground">
          سجل كل عملية وصول للوحة مشرف المنصة (المستخدم، الإجراء، الوقت).
        </p>
        <select
          value={limit}
          onChange={(e) => setLimit(Number(e.target.value))}
          className="text-xs border rounded px-2 py-1 bg-card"
        >
          <option value={50}>آخر 50</option>
          <option value={100}>آخر 100</option>
          <option value={250}>آخر 250</option>
          <option value={500}>آخر 500</option>
        </select>
      </div>
      {rows.length === 0 ? (
        <p className="text-sm text-muted-foreground">لا توجد سجلات بعد.</p>
      ) : (
        <div className="overflow-x-auto border rounded-lg bg-card">
          <table className="w-full text-xs">
            <thead className="bg-muted/50">
              <tr className="text-right">
                <th className="p-2">الوقت</th>
                <th className="p-2">المشرف</th>
                <th className="p-2">معرف المستخدم</th>
                <th className="p-2">الإجراء</th>
                <th className="p-2">التفاصيل</th>
              </tr>
            </thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.id} className="border-t align-top">
                  <td className="p-2 whitespace-nowrap">{dt(r.created_at)}</td>
                  <td className="p-2">{r.user_email ?? "—"}</td>
                  <td className="p-2 font-mono">{short(r.user_id)}</td>
                  <td className="p-2">
                    <span className="px-2 py-0.5 rounded bg-primary/10 text-primary text-[11px]">
                      {ACTION_LABELS[r.action] ?? r.action}
                    </span>
                    <div className="text-[10px] text-muted-foreground font-mono mt-0.5">{r.action}</div>
                  </td>
                  <td className="p-2 font-mono text-[10px] text-muted-foreground max-w-[280px] truncate">
                    {r.details && Object.keys(r.details).length > 0 ? JSON.stringify(r.details) : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
