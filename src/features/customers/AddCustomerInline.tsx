/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import type { Customer } from "@/features/shared/types";

export function AddCustomerInline({
  addCustomerAsync,
  customers,
  showToast,
}: {
  addCustomerAsync: (i: { name: string; phone?: string }) => Promise<any>;
  customers: Customer[];
  showToast: (s: string) => void;
}) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const trimmedName = name.trim();
  const trimmedPhone = phone.trim();
  const dup = customers.find(
    (c) =>
      c.name.trim() === trimmedName || (!!trimmedPhone && (c.phone ?? "").trim() === trimmedPhone),
  );
  const submit = async () => {
    if (!trimmedName) return;
    try {
      await addCustomerAsync({ name: trimmedName, phone: trimmedPhone || undefined });
      setName("");
      setPhone("");
      setOpen(false);
      showToast("تم إضافة العميل");
    } catch (e: any) {
      showToast(e?.message ?? "تعذّر الإضافة");
    }
  };
  if (!open) {
    return (
      <button
        onClick={() => setOpen(true)}
        className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold"
      >
        ＋ إضافة عميل
      </button>
    );
  }
  return (
    <div className="rounded-2xl bg-card border border-border p-3 space-y-2">
      <div className="font-bold text-sm">إضافة عميل جديد</div>
      <input
        value={name}
        onChange={(e) => setName(e.target.value)}
        placeholder="اسم العميل (إلزامي)"
        className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm"
      />
      <input
        value={phone}
        onChange={(e) => setPhone(e.target.value)}
        placeholder="رقم الهاتف (اختياري)"
        inputMode="tel"
        className="w-full rounded-xl border border-border bg-background px-3 py-2.5 text-sm num text-right"
      />
      {dup && (
        <div className="text-[11px] text-warn">
          ⚠ يوجد عميل بنفس {dup.name.trim() === trimmedName ? "الاسم" : "الرقم"}: {dup.name}
        </div>
      )}
      <div className="flex gap-2">
        <button
          onClick={() => {
            setOpen(false);
            setName("");
            setPhone("");
          }}
          className="flex-1 rounded-xl bg-muted py-2.5 text-sm font-bold"
        >
          إلغاء
        </button>
        <button
          disabled={!trimmedName}
          onClick={submit}
          className="flex-1 rounded-xl bg-primary text-primary-foreground py-2.5 text-sm font-bold disabled:opacity-40"
        >
          حفظ
        </button>
      </div>
    </div>
  );
}
