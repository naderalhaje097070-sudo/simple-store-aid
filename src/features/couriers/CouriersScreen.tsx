import { useState } from "react";
import { TopBar } from "@/features/layout/TopBar";
import { Money } from "@/features/shared/Money";
import type { Courier, Invoice } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";

export function CouriersScreen(p: AppCtx) {
  const [open, setOpen] = useState(false);
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const submit = async () => {
    if (!name.trim()) return;
    await p.addCourierAsync({ name: name.trim(), phone: phone.trim() || undefined });
    setName(""); setPhone(""); setOpen(false);
    p.showToast("تم إضافة المندوب");
  };
  return (
    <>
      <TopBar title="المندوبون" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-2">
        {p.couriers.map((c: Courier) => {
          const list = p.invoices.filter((i: Invoice) => i.courierId === c.id);
          const custody = list.filter((i: Invoice) => i.courierState === "delivered_partial" || i.courierState === "delivered_full").reduce((s: number, i: Invoice) => s + (i.collectedByCourier ?? 0), 0);
          return (
            <button key={c.id} onClick={() => { p.setOpenCourierId(c.id); p.go("courier_custody"); }} className="w-full text-right rounded-2xl bg-card border border-border p-3 flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-warn-soft text-warn flex items-center justify-center font-bold">{c.name[0]}</div>
              <div className="flex-1">
                <div className="font-bold text-sm">{c.name}</div>
                <div className="text-xs text-muted-foreground"><span className="num">{list.length}</span> طلب</div>
              </div>
              <div className="text-left">
                <div className="text-[11px] text-muted-foreground">عهدة غير مصفّاة</div>
                <Money v={custody} className="text-warn font-bold text-sm" />
              </div>
            </button>
          );
        })}
        {p.couriers.length === 0 && (
          <div className="rounded-2xl bg-muted/40 border border-border p-6 text-center text-sm text-muted-foreground">
            لا يوجد مندوبون بعد. أضف أول مندوب توصيل.
          </div>
        )}
        <button onClick={() => setOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة مندوب</button>
      </div>

      {open && (
        <div className="fixed inset-0 z-50 bg-black/40 flex items-end" onClick={() => setOpen(false)}>
          <div className="w-full bg-card rounded-t-3xl p-4 space-y-3" onClick={e => e.stopPropagation()}>
            <div className="font-bold">إضافة مندوب</div>
            <input value={name} onChange={e => setName(e.target.value)} placeholder="اسم المندوب" className="w-full rounded-xl bg-muted px-3 py-3 text-sm" />
            <input value={phone} onChange={e => setPhone(e.target.value)} placeholder="رقم الهاتف (اختياري)" inputMode="tel" className="w-full rounded-xl bg-muted px-3 py-3 text-sm" />
            <div className="flex gap-2">
              <button onClick={() => setOpen(false)} className="flex-1 rounded-xl bg-muted py-3 text-sm font-bold">إلغاء</button>
              <button onClick={submit} disabled={!name.trim()} className="flex-1 rounded-xl bg-primary text-primary-foreground py-3 text-sm font-bold disabled:opacity-40">حفظ</button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
