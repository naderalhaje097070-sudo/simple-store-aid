// Extracted from src/routes/_authenticated/app.tsx (R4a — shared infra for moved screens).
// No logic change.

export const fmt = (n: number) =>
  new Intl.NumberFormat("en-US", { maximumFractionDigits: 0 }).format(Math.round(n));

export const Money = ({ v, className = "" }: { v: number; className?: string }) => (
  <span className={className}>
    <span className="num font-semibold">{fmt(v)}</span>{" "}
    <span className="text-xs opacity-70">د.ل</span>
  </span>
);
