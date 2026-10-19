import type { ReactNode } from "react";
import type { FinancialRead } from "./financial-read-state";
import { Money } from "./Money";

type ReadProps = {
  reads: FinancialRead[];
  onRetry: () => Promise<unknown>;
};

export function FinancialReadNotice({ reads, onRetry }: ReadProps) {
  if (reads.every((read) => read.complete)) return null;
  const failed = reads.some((read) => read.phase === "error");
  const cached = reads.some((read) => read.hasData);
  return (
    <div role="status" className="rounded-2xl bg-warn-soft border border-warn/30 p-4 space-y-2">
      <div className="text-sm font-bold">
        {failed
          ? "تعذّر تحميل البيانات المالية"
          : cached
            ? "جارٍ تحديث البيانات المالية"
            : "جارٍ تحميل البيانات المالية"}
      </div>
      <p className="text-xs text-muted-foreground">
        {cached
          ? "المعروض من آخر قراءة متاحة؛ قد يكون قديمًا أو غير مكتمل."
          : "الأرقام غير متاحة الآن؛ عدم توفرها لا يعني أن الرصيد صفر."}
      </p>
      <button onClick={() => void onRetry()} className="text-sm font-bold text-primary underline">
        إعادة تحميل البيانات المالية
      </button>
    </div>
  );
}

export function FinancialReadBoundary({
  reads,
  onRetry,
  onBack,
  children,
}: ReadProps & { onBack: () => void; children: ReactNode }) {
  return (
    <div className="space-y-3">
      <FinancialReadNotice reads={reads} onRetry={onRetry} />
      {reads.every((read) => read.hasData) ? (
        children
      ) : (
        <div className="p-4 space-y-3">
          <p className="text-sm">الملخص المالي غير متاح حتى تكتمل قراءة البيانات المطلوبة.</p>
          <button onClick={onBack} className="text-sm font-bold text-primary underline">
            الرجوع
          </button>
        </div>
      )}
    </div>
  );
}

export function FinancialAmount({
  read,
  value,
  className,
}: {
  read: FinancialRead;
  value: number;
  className?: string;
}) {
  if (!read.hasData) return <span className="text-sm text-muted-foreground">غير متاح</span>;
  return (
    <span title={read.complete ? undefined : "آخر قراءة متاحة — لم يكتمل التحديث"}>
      <Money v={value} className={className} />
    </span>
  );
}
