import { useState } from "react";
import type { Customer, Invoice } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { EmptyState } from "@/features/shared/EmptyState";
import { FinancialReadNotice, FinancialAmount } from "@/features/shared/FinancialReadBoundary";
import { AddCustomerInline } from "./AddCustomerInline";
import { getCustomerDebtForInvoice } from "@/domain/finance/invoice-selectors";

type Filter = "all" | "debt" | "clear";

export function CustomersScreen(p: AppCtx) {
  const [filter, setFilter] = useState<Filter>("all");
  const [q, setQ] = useState("");
  const debtMap = new Map<string, number>();
  p.invoices.forEach((i: Invoice) => {
    if (!i.customerId) return;
    const debt = getCustomerDebtForInvoice(i);
    if (debt > 0) debtMap.set(i.customerId, (debtMap.get(i.customerId) ?? 0) + debt);
  });
  const activeFilter = p.financialReads.invoices.complete ? filter : "all";
  const list = p.customers.filter((c: Customer) => {
    if (q && !c.name.includes(q) && !(c.phone ?? "").includes(q)) return false;
    const has = !!debtMap.get(c.id);
    if (activeFilter === "debt") return has;
    if (activeFilter === "clear") return !has;
    return true;
  });
  return (
    <>
      <TopBar title="العملاء" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <FinancialReadNotice reads={[p.financialReads.invoices]} onRetry={p.retryFinancialReads} />
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="ابحث بالاسم أو الرقم"
          className="w-full rounded-xl border border-border bg-card px-3 py-2.5 text-sm"
        />
        <div className="flex gap-2 overflow-x-auto">
          {[
            { id: "all", l: "الكل" },
            { id: "debt", l: "عليه دين" },
            { id: "clear", l: "لا دين" },
          ].map((f) => (
            <button
              key={f.id}
              disabled={f.id !== "all" && !p.financialReads.invoices.complete}
              onClick={() => setFilter(f.id as Filter)}
              className={`px-4 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${activeFilter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}
            >
              {f.l}
            </button>
          ))}
        </div>
        {list.length === 0 && (
          <EmptyState text={q ? "لا عميل بهذا الاسم" : "لا عملاء بهذا التصنيف"} />
        )}
        <div className="grid grid-cols-1 gap-2 lg:grid-cols-2 xl:grid-cols-3">
          {list.map((c: Customer) => (
            <div
              key={c.id}
              className="rounded-2xl bg-card border border-border p-3 flex items-center gap-3 hover:border-primary/30 transition"
            >
              <div className="w-10 h-10 rounded-full bg-primary-soft text-primary flex items-center justify-center font-bold">
                {c.name[0]}
              </div>
              <div className="flex-1 min-w-0">
                <div className="font-bold text-sm truncate">{c.name}</div>
                <div className="text-xs text-muted-foreground truncate">
                  {c.phone ?? "بدون رقم"}
                </div>
              </div>
              {debtMap.get(c.id) ? (
                <FinancialAmount
                  read={p.financialReads.invoices}
                  value={debtMap.get(c.id)!}
                  className="text-debt font-bold text-sm"
                />
              ) : !p.financialReads.invoices.complete ? (
                <span className="text-[11px] text-muted-foreground">الرصيد غير مؤكد</span>
              ) : (
                <span className="text-[11px] text-success">لا دين</span>
              )}
            </div>
          ))}
        </div>
        <AddCustomerInline
          addCustomerAsync={p.addCustomerAsync}
          customers={p.customers}
          showToast={p.showToast}
        />
      </div>
    </>
  );
}
