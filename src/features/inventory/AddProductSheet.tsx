/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect, useRef } from "react";
import { Sheet } from "@/features/shared/Sheet";

export function AddProductSheet({
  onClose,
  onSave,
  existingNames = [] as string[],
  mode = "add",
  initial,
}: {
  onClose: () => void;
  onSave: (d: {
    name: string;
    price: number;
    cost: number;
    stock: number;
    is_discount: boolean;
  }) => void | Promise<void>;
  existingNames?: string[];
  mode?: "add" | "edit";
  initial?: { name: string; price: number; cost: number; stock: number; is_discount: boolean };
}) {
  const nameRef = useRef<HTMLInputElement>(null);
  const [name, setName] = useState(initial?.name ?? "");
  const [price, setPrice] = useState(initial ? String(initial.price) : "");
  const [cost, setCost] = useState(initial ? String(initial.cost ?? "") : "");
  const [stock, setStock] = useState(initial ? String(initial.stock) : "");
  const [isDiscount, setIsDiscount] = useState(initial?.is_discount ?? false);
  const [touched, setTouched] = useState<{
    name?: boolean;
    price?: boolean;
    cost?: boolean;
    stock?: boolean;
  }>(initial ? { name: true, price: true, cost: true, stock: true } : {});
  const [submitting, setSubmitting] = useState(false);

  // Sync form values whenever initial product changes (edit mode switching between products)
  useEffect(() => {
    setName(initial?.name ?? "");
    setPrice(initial ? String(initial.price) : "");
    setCost(initial ? String(initial.cost ?? "") : "");
    setStock(initial ? String(initial.stock) : "");
    setIsDiscount(initial?.is_discount ?? false);
    setTouched(initial ? { name: true, price: true, cost: true, stock: true } : {});
  }, [initial?.name, initial?.price, initial?.cost, initial?.stock, initial?.is_discount]);

  // Auto-focus name field whenever the sheet opens (both add and edit)
  useEffect(() => {
    const id = setTimeout(() => nameRef.current?.focus(), 50);
    return () => clearTimeout(id);
  }, [mode, initial?.name]);

  const trimmedName = name.trim();
  const priceN = Number(price);
  const costN = Number(cost);
  const stockN = Number(stock);

  const errors: { name?: string; price?: string; stock?: string; cost?: string } = {};
  if (!trimmedName) errors.name = "اسم المنتج مطلوب";
  else if (trimmedName.length < 2) errors.name = "الاسم قصير جداً (حرفان على الأقل)";
  else if (trimmedName.length > 60) errors.name = "الاسم طويل (60 حرفاً كحد أقصى)";

  if (price === "") errors.price = "سعر البيع مطلوب";
  else if (!isFinite(priceN) || priceN <= 0) errors.price = "أدخل سعراً أكبر من صفر";

  if (stock === "") errors.stock = "أدخل كمية المخزون (يمكن أن تكون 0)";
  else if (!isFinite(stockN) || stockN < 0) errors.stock = "الكمية غير صحيحة";
  else if (stockN > 100000) errors.stock = "الكمية كبيرة جداً";

  if (cost !== "" && (!isFinite(costN) || costN < 0)) errors.cost = "تكلفة غير صحيحة";
  if (!errors.cost && !errors.price && cost !== "" && costN > priceN && !isDiscount)
    errors.cost = "التكلفة أعلى من سعر البيع — فعّل خيار التخفيض أو صحّح السعر";

  const warnings: { cost?: string; name?: string } = {};
  if (!errors.cost && !errors.price && cost !== "" && costN > priceN && isDiscount)
    warnings.cost = "منتج على تخفيض (التكلفة أعلى من سعر البيع)";
  if (!errors.name && trimmedName && existingNames.includes(trimmedName.toLowerCase()))
    warnings.name = "يوجد منتج بنفس الاسم — تأكد قبل الحفظ";

  const valid = Object.keys(errors).length === 0;

  const handleSave = async () => {
    if (!valid) {
      setTouched({ name: true, price: true, cost: true, stock: true });
      return;
    }
    setSubmitting(true);
    try {
      await onSave({
        name: trimmedName,
        price: priceN,
        cost: costN || 0,
        stock: stockN,
        is_discount: isDiscount,
      });
    } finally {
      setSubmitting(false);
    }
  };

  const showErr = (k: keyof typeof errors) => touched[k as keyof typeof touched] && errors[k];
  const inputCls = (k: keyof typeof errors) =>
    `mt-1 w-full rounded-xl border bg-background px-3 py-3 text-sm ${showErr(k) ? "border-destructive" : "border-border"}`;

  return (
    <Sheet onClose={onClose} title={mode === "edit" ? "تعديل المنتج" : "إضافة منتج"}>
      <div className="space-y-3">
        <div>
          <label className="text-xs font-bold text-muted-foreground">
            اسم المنتج <span className="text-destructive">*</span>
          </label>
          <input
            ref={nameRef}
            value={name}
            onChange={(e) => setName(e.target.value)}
            onBlur={() => setTouched((t) => ({ ...t, name: true }))}
            className={inputCls("name")}
            placeholder="مثال: ماء 1.5 لتر"
            maxLength={60}
          />
          {showErr("name") && <div className="mt-1 text-xs text-destructive">{errors.name}</div>}
          {!showErr("name") && warnings.name && (
            <div className="mt-1 text-xs text-amber-600 dark:text-amber-500">⚠ {warnings.name}</div>
          )}
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>
            <label className="text-xs font-bold text-muted-foreground">
              سعر البيع <span className="text-destructive">*</span>
            </label>
            <input
              value={price}
              onChange={(e) => setPrice(e.target.value.replace(/[^\d.]/g, ""))}
              onBlur={() => setTouched((t) => ({ ...t, price: true }))}
              inputMode="decimal"
              className={`${inputCls("price")} num text-right`}
              placeholder="0"
            />
            {showErr("price") && (
              <div className="mt-1 text-xs text-destructive">{errors.price}</div>
            )}
          </div>
          <div>
            <label className="text-xs font-bold text-muted-foreground">سعر التكلفة</label>
            <input
              value={cost}
              onChange={(e) => setCost(e.target.value.replace(/[^\d.]/g, ""))}
              onBlur={() => setTouched((t) => ({ ...t, cost: true }))}
              inputMode="decimal"
              className={`${inputCls("cost")} num text-right`}
              placeholder="0"
            />
            {showErr("cost") && <div className="mt-1 text-xs text-destructive">{errors.cost}</div>}
            {!showErr("cost") && warnings.cost && (
              <div className="mt-1 text-xs text-amber-600 dark:text-amber-500">
                ⚠ {warnings.cost}
              </div>
            )}
          </div>
        </div>
        <div>
          <label className="text-xs font-bold text-muted-foreground">
            المخزون الحالي <span className="text-destructive">*</span>
          </label>
          <input
            value={stock}
            onChange={(e) => setStock(e.target.value.replace(/\D/g, ""))}
            onBlur={() => setTouched((t) => ({ ...t, stock: true }))}
            inputMode="numeric"
            className={`${inputCls("stock")} num text-right`}
            placeholder="0"
          />
          {showErr("stock") && <div className="mt-1 text-xs text-destructive">{errors.stock}</div>}
        </div>
        <label className="flex items-center gap-2 rounded-xl border border-border bg-card px-3 py-2 cursor-pointer">
          <input
            type="checkbox"
            checked={isDiscount}
            onChange={(e) => setIsDiscount(e.target.checked)}
            className="w-4 h-4 accent-primary"
          />
          <span className="text-xs font-bold">منتج على تخفيض (تكلفة &gt; بيع)</span>
        </label>
        <button
          disabled={submitting}
          onClick={handleSave}
          className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40"
        >
          {submitting ? "جاري الحفظ…" : mode === "edit" ? "حفظ التعديلات" : "حفظ المنتج"}
        </button>
      </div>
    </Sheet>
  );
}
