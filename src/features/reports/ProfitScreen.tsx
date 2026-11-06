import { TrendingUp, Info } from "lucide-react";
import { TopBar } from "@/features/layout/TopBar";
import { Money, fmt } from "@/features/shared/Money";
import type { AppCtx } from "@/features/shared/AppContext";

export function ProfitScreen(p: AppCtx) {
  const {
    sales,
    cogs,
    grossProfit,
    expenseTotal,
    netProfit,
    collected,
    realizedCogs,
    realizedRevenue,
    realizedProfit,
    customerDebts,
    unsettledCustody,
  } = p.totals;
  const Row = ({
    label,
    v,
    op,
    color,
  }: {
    label: string;
    v: number;
    op?: string;
    color?: string;
  }) => (
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
      <TopBar title="الربح" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        {/* Realized profit — primary */}
        <div className="rounded-2xl bg-profit-soft border-2 border-profit/30 p-4">
          <div className="flex items-center gap-2 text-profit text-xs font-bold">
            <TrendingUp className="w-4 h-4" /> صافي ربح تقديري بعد المصروفات
          </div>
          <Money v={realizedProfit} className="text-2xl text-profit mt-1" />
          <div className="text-[11px] text-muted-foreground mt-1 leading-relaxed">
            تقدير بحسب نسبة الدفع لفواتير الفترة، بعد المصروفات. يختلف أساسه الزمني عن ملخص التحصيل
            في إقفال اليوم.
          </div>
          <div className="mt-3 pt-3 border-t border-profit/20 space-y-1.5 text-xs">
            <div className="flex justify-between">
              <span className="text-muted-foreground">الإيراد المقدّر بحسب نسبة الدفع</span>
              <Money v={realizedRevenue} />
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">− تكلفة البضاعة المخصّصة للتقدير</span>
              <Money v={realizedCogs} />
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">− مصروفات</span>
              <Money v={expenseTotal} />
            </div>
          </div>
          <div className="flex justify-between mt-3 text-xs text-muted-foreground">
            <span>المحصّل الفعلي في الفترة — بيان نقدي مستقل</span>
            <Money v={collected} />
          </div>
        </div>

        {/* Expected profit — secondary */}
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="flex items-center gap-2 text-muted-foreground text-xs font-bold">
            <Info className="w-4 h-4" /> ربح متوقع لو حُصِّلت كل الديون
          </div>
          <Money v={netProfit} className="text-lg mt-1" />
          <div className="mt-3 divide-y divide-border">
            <Row label="المبيعات" v={sales} />
            <Row label="تكلفة البضاعة المباعة" v={cogs} op="−" />
            <Row label="الربح الإجمالي" v={grossProfit} op="=" color="text-profit font-bold" />
            <Row label="المصروفات" v={expenseTotal} op="−" />
            <Row label="صافي الربح المتوقع" v={netProfit} op="=" color="text-profit font-bold" />
          </div>
        </div>

        <div className="rounded-2xl bg-warn-soft border border-warn/20 p-3 text-xs text-warn flex gap-2">
          <Info className="w-4 h-4 shrink-0 mt-0.5" />
          <span>
            ديون العملاء <span className="num">{fmt(customerDebts)}</span> وعهدة المندوب{" "}
            <span className="num">{fmt(unsettledCustody)}</span> د.ل أرصدة مستقلة، ولا تمثل الفرق
            بين رقمي الربح.
          </span>
        </div>
      </div>
    </>
  );
}
