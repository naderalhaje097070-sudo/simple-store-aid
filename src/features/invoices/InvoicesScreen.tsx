import { useState } from "react";
import { Info } from "lucide-react";
import type { Invoice } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { Money } from "@/features/shared/Money";
import { TopBar } from "@/features/layout/TopBar";
import { InvoiceRow } from "@/features/home/HomeScreen";
import { DateRangeFilter, useDateRange, inRange } from "@/components/DateRangeFilter";

/* --------------- INVOICES LIST --------------- */
export function InvoicesScreen(p: AppCtx) {
  const [filter, setFilter] = useState<"all" | "paid" | "partial" | "debt">("all");
  const { range, setRange } = useDateRange("today");
  const dated = p.invoices.filter((i: Invoice) => inRange(i.createdAt, range));
  const list = dated.filter((i: Invoice) => filter === "all" ? true : i.status === filter);
  const total = list.reduce((s: number, i: Invoice) => s + i.total, 0);
  return (
    <>
      <TopBar title="الفواتير" onHome={p.goHome} />
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
            <button key={f.id} onClick={() => setFilter(f.id as typeof filter)} className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${filter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border text-foreground"}`}>{f.l}</button>
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
