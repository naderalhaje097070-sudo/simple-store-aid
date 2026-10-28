import { useEffect, useState } from "react";
import { parseQuantityText, QUANTITY_ERROR } from "@/domain/finance/quantity";

export function QuantityInput({
  value,
  onCommit,
  onInvalidChange,
}: {
  value: number;
  onCommit: (quantity: number) => boolean;
  onInvalidChange: (invalid: boolean) => void;
}) {
  const [draft, setDraft] = useState(String(value));
  const [error, setError] = useState(false);
  useEffect(() => {
    setDraft(String(value));
    setError(false);
  }, [value]);
  const commit = () => {
    const quantity = parseQuantityText(draft);
    if (quantity === null || !onCommit(quantity)) {
      setDraft(String(value));
      setError(true);
      onInvalidChange(true);
      return;
    }
    setError(false);
    onInvalidChange(false);
  };
  return (
    <div className="flex flex-col items-center">
      <input
        aria-label="الكمية"
        aria-invalid={error}
        title={error ? QUANTITY_ERROR : "الكمية (حتى منزلتين عشريتين)"}
        inputMode="decimal"
        value={draft}
        onChange={(event) => {
          setDraft(event.target.value);
          setError(false);
          onInvalidChange(true);
        }}
        onBlur={commit}
        onKeyDown={(event) => {
          if (event.key === "Enter") event.currentTarget.blur();
        }}
        className={`w-16 h-8 rounded border bg-background text-center text-sm font-bold num ${error ? "border-destructive" : "border-border"}`}
      />
      {error && (
        <span role="alert" className="text-[9px] text-destructive">
          كمية غير صالحة
        </span>
      )}
    </div>
  );
}
