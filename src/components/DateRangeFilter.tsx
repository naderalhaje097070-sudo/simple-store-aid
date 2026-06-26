import { useMemo, useState } from "react";
import { Calendar, X } from "lucide-react";

export type DateRange = { start: number; end: number; label: string; key: string };

type PresetKey = "today" | "yesterday" | "7d" | "30d" | "month" | "all" | "custom";

const startOfDay = (d: Date) => { const x = new Date(d); x.setHours(0, 0, 0, 0); return x.getTime(); };
const endOfDay = (d: Date) => { const x = new Date(d); x.setHours(23, 59, 59, 999); return x.getTime(); };

export function buildRange(key: PresetKey, custom?: { from: string; to: string }): DateRange {
  const now = new Date();
  if (key === "today") return { key, label: "اليوم", start: startOfDay(now), end: endOfDay(now) };
  if (key === "yesterday") {
    const y = new Date(); y.setDate(y.getDate() - 1);
    return { key, label: "أمس", start: startOfDay(y), end: endOfDay(y) };
  }
  if (key === "7d") {
    const s = new Date(); s.setDate(s.getDate() - 6);
    return { key, label: "آخر ٧ أيام", start: startOfDay(s), end: endOfDay(now) };
  }
  if (key === "30d") {
    const s = new Date(); s.setDate(s.getDate() - 29);
    return { key, label: "آخر ٣٠ يوم", start: startOfDay(s), end: endOfDay(now) };
  }
  if (key === "month") {
    const s = new Date(now.getFullYear(), now.getMonth(), 1);
    return { key, label: "هذا الشهر", start: startOfDay(s), end: endOfDay(now) };
  }
  if (key === "all") return { key, label: "كل الفترات", start: 0, end: Number.MAX_SAFE_INTEGER };
  // custom
  const f = custom?.from ? new Date(custom.from) : now;
  const t = custom?.to ? new Date(custom.to) : now;
  return { key, label: `${custom?.from ?? ""} → ${custom?.to ?? ""}`, start: startOfDay(f), end: endOfDay(t) };
}

export function useDateRange(initial: PresetKey = "today") {
  const [range, setRange] = useState<DateRange>(() => buildRange(initial));
  return { range, setRange };
}

export function inRange(iso: string | undefined, r: DateRange) {
  if (!iso) return false;
  const t = new Date(iso).getTime();
  return t >= r.start && t <= r.end;
}

const PRESETS: { key: PresetKey; label: string }[] = [
  { key: "today", label: "اليوم" },
  { key: "yesterday", label: "أمس" },
  { key: "7d", label: "٧ أيام" },
  { key: "30d", label: "٣٠ يوم" },
  { key: "month", label: "الشهر" },
  { key: "all", label: "الكل" },
];

export function DateRangeFilter({ value, onChange }: { value: DateRange; onChange: (r: DateRange) => void }) {
  const [customOpen, setCustomOpen] = useState(false);
  const [from, setFrom] = useState("");
  const [to, setTo] = useState("");
  const error = useMemo(() => {
    if (!from || !to) return null;
    return new Date(from).getTime() > new Date(to).getTime() ? "تاريخ البداية بعد النهاية" : null;
  }, [from, to]);

  const apply = () => {
    if (!from || !to || error) return;
    onChange(buildRange("custom", { from, to }));
    setCustomOpen(false);
  };

  return (
    <div className="space-y-2">
      <div className="flex gap-2 overflow-x-auto pb-1">
        {PRESETS.map(p => (
          <button
            key={p.key}
            onClick={() => onChange(buildRange(p.key))}
            className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap ${
              value.key === p.key ? "bg-primary text-primary-foreground" : "bg-card border border-border text-foreground"
            }`}
          >
            {p.label}
          </button>
        ))}
        <button
          onClick={() => setCustomOpen(true)}
          className={`px-3 py-1.5 rounded-full text-xs font-bold whitespace-nowrap inline-flex items-center gap-1 ${
            value.key === "custom" ? "bg-primary text-primary-foreground" : "bg-card border border-border text-foreground"
          }`}
        >
          <Calendar className="w-3 h-3" /> نطاق مخصّص
        </button>
      </div>
      {value.key === "custom" && (
        <div className="text-[11px] text-muted-foreground">المدى المختار: <span className="num">{value.label}</span></div>
      )}

      {customOpen && (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40" onClick={() => setCustomOpen(false)}>
          <div onClick={e => e.stopPropagation()} className="w-full max-w-md bg-card rounded-t-3xl p-4 pb-6" dir="rtl">
            <div className="flex items-center justify-between mb-3">
              <h3 className="font-bold">اختيار نطاق التاريخ</h3>
              <button onClick={() => setCustomOpen(false)} className="p-2 rounded-full hover:bg-muted"><X className="w-5 h-5" /></button>
            </div>
            <div className="space-y-3">
              <div>
                <label className="text-xs font-bold text-muted-foreground">من تاريخ</label>
                <input type="date" value={from} onChange={e => setFrom(e.target.value)} className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num" />
              </div>
              <div>
                <label className="text-xs font-bold text-muted-foreground">إلى تاريخ</label>
                <input type="date" value={to} onChange={e => setTo(e.target.value)} className="mt-1 w-full rounded-xl border border-border bg-background px-3 py-3 text-base num" />
              </div>
              {error && <div className="text-xs text-debt">{error}</div>}
              <button
                disabled={!from || !to || !!error}
                onClick={apply}
                className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40"
              >تطبيق</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
