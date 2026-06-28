// Extracted verbatim from src/routes/_authenticated/app.tsx (R1) — no body changes.
import * as React from "react";

export function StatusChip({ kind, children, icon }: { kind: "paid" | "partial" | "debt" | "warn" | "info" | "profit"; children: React.ReactNode; icon?: React.ReactNode }) {
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
