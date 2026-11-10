import { useEffect, useRef, useState } from "react";
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
  // Once the person has typed, an external value update must not overwrite the
  // typed text before it is committed; the committed value re-syncs on blur.
  const editing = useRef(false);
  useEffect(() => {
    if (editing.current) return;
    setDraft(String(value));
    setError(false);
  }, [value]);
  // Commit what is on screen now, not a draft captured by an earlier render.
  const commit = (text: string) => {
    editing.current = false;
    const quantity = parseQuantityText(text);
    if (quantity === null || !onCommit(quantity)) {
      setDraft(String(value));
      setError(true);
      onInvalidChange(true);
      return;
    }
    setDraft(String(quantity));
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
          editing.current = true;
          setDraft(event.target.value);
          setError(false);
          onInvalidChange(true);
        }}
        onBlur={(event) => commit(event.currentTarget.value)}
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
