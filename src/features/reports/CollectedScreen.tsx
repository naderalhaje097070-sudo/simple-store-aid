/* eslint-disable @typescript-eslint/no-explicit-any */
import { Info, ArrowUpCircle } from "lucide-react";
import type { Customer, Courier, Payment } from "@/features/shared/types";
import { TopBar } from "@/features/layout/TopBar";
import { Money } from "@/features/shared/Money";
import { DateRangeFilter, useDateRange, inRange } from "@/components/DateRangeFilter";

export function CollectedScreen(p: any) {
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
      <TopBar title="المحصّل فعليًا" onBack={p.back} onHome={p.goHome} />
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
