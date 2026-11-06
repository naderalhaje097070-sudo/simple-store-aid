import type { Database } from "../integrations/supabase/types";

type ReportRow = Database["public"]["Views"]["day_close_profit_report"]["Row"];

export type DBDayClose = {
  id: string;
  closedFor: string;
  sales: number;
  collected: number;
  expenses: number;
  /** Legacy recorded margin before expenses. */
  realizedProfit: number;
  realizedMarginBeforeExpenses: number;
  realizedNetProfit: number;
  customerDebts: number;
  unsettledCustody: number;
  note?: string;
  createdAt: string;
};

function requiredNumber(value: number | null): number {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    throw new Error("تعذّر قراءة قيمة مالية مطلوبة في إقفال اليوم.");
  }
  return value;
}

function requiredText(value: string | null): string {
  if (typeof value !== "string" || !value) {
    throw new Error("تعذّر قراءة سجل إقفال اليوم.");
  }
  return value;
}

// The database derives net. Do not recalculate it or turn absent values into zero.
export function decodeDayCloseReport(row: ReportRow): DBDayClose {
  return {
    id: requiredText(row.id),
    closedFor: requiredText(row.closed_for),
    sales: requiredNumber(row.sales),
    collected: requiredNumber(row.collected),
    expenses: requiredNumber(row.expenses),
    realizedProfit: requiredNumber(row.realized_profit),
    realizedMarginBeforeExpenses: requiredNumber(row.realized_margin_before_expenses),
    realizedNetProfit: requiredNumber(row.realized_net_profit),
    customerDebts: requiredNumber(row.customer_debts),
    unsettledCustody: requiredNumber(row.unsettled_custody),
    note: row.note ?? undefined,
    createdAt: requiredText(row.created_at),
  };
}

export function decodeDayCloseReports(rows: ReportRow[] | null): DBDayClose[] {
  if (!Array.isArray(rows)) {
    throw new Error("تعذّر قراءة سجلات إقفال اليوم.");
  }
  return rows.map(decodeDayCloseReport);
}
