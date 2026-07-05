/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState } from "react";
import { AlertTriangle, PackageX } from "lucide-react";
import type { Product } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { StatusChip } from "@/features/shared/StatusChip";
import { EmptyState } from "@/features/shared/EmptyState";
import { Money } from "@/features/shared/Money";
import { AddProductSheet } from "./AddProductSheet";

export function InventoryScreen(p: AppCtx) {
  const [filter, setFilter] = useState<"all" | "low" | "out">("all");
  const [editing, setEditing] = useState<Product | null>(null);
  const [addOpen, setAddOpen] = useState(false);
  const list = p.products.filter((pr: Product) => {
    if (filter === "low") return pr.stock > 0 && pr.stock <= pr.lowAt;
    if (filter === "out") return pr.stock === 0;
    return true;
  });
  return (
    <>
      <TopBar title="المخزون" onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <div className="flex gap-2">
          {[{ id: "all", l: "الكل" }, { id: "low", l: "منخفض" }, { id: "out", l: "نفد" }].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id as any)} className={`px-4 py-1.5 rounded-full text-xs font-bold ${filter === f.id ? "bg-primary text-primary-foreground" : "bg-card border border-border"}`}>{f.l}</button>
          ))}
        </div>
        <div className="space-y-2">
          {list.length === 0 && filter === "out" && <EmptyState text="لا منتجات نافدة — جيد 👍" />}
          {list.length === 0 && filter !== "out" && <EmptyState text="لا منتجات بهذا التصنيف — أضف منتجاً جديداً" />}
          {list.map((pr: Product) => (
            <div key={pr.id} className={`rounded-2xl border p-3 ${pr.stock === 0 ? "bg-debt-soft/40 border-debt/20" : "bg-card border-border"} ${pr.is_active === false ? "opacity-60" : ""}`}>
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-bold text-sm">{pr.name}</div>
                  <div className="mt-1 flex items-center gap-2">
                    {pr.is_active === false && <StatusChip kind="warn">موقوف</StatusChip>}
                    {pr.is_discount && <StatusChip kind="info">تخفيض</StatusChip>}
                    {pr.stock === 0 && <StatusChip kind="debt" icon={<PackageX className="w-3 h-3" />}>نفد</StatusChip>}
                    {pr.stock > 0 && pr.stock <= pr.lowAt && <StatusChip kind="warn" icon={<AlertTriangle className="w-3 h-3" />}>منخفض <span className="num">{pr.stock}</span></StatusChip>}
                    {pr.stock > pr.lowAt && <StatusChip kind="info">متوفر <span className="num">{pr.stock}</span></StatusChip>}
                  </div>
                </div>
                <div className="text-left"><Money v={pr.price} className="text-sm" /></div>
              </div>
              <div className="mt-2 flex gap-2 flex-wrap">
                <button onClick={() => setEditing(pr)} className="flex-1 rounded-xl bg-card border border-border text-xs font-bold py-2">تعديل</button>
                {pr.stock === 0 && pr.is_active !== false && (
                  <button onClick={async () => { try { await p.toggleProductActiveAsync({ id: pr.id, is_active: false }); p.showToast("تم إيقاف العرض"); } catch (e: any) { p.showToast(e?.message ?? "تعذّر"); } }} className="flex-1 rounded-xl bg-card border border-debt/30 text-debt text-xs font-bold py-2">إيقاف العرض</button>
                )}
                {pr.is_active === false && (
                  <button onClick={async () => { try { await p.toggleProductActiveAsync({ id: pr.id, is_active: true }); p.showToast("تم تفعيل المنتج"); } catch (e: any) { p.showToast(e?.message ?? "تعذّر"); } }} className="flex-1 rounded-xl bg-card border border-border text-xs font-bold py-2">إعادة العرض</button>
                )}
                <button
                  onClick={async () => {
                    if (!window.confirm(`حذف المنتج "${pr.name}"؟\nإذا استُخدم في فواتير سابقة سيتم إيقافه فقط للحفاظ على السجلات.`)) return;
                    try {
                      const r = await p.deleteProductAsync(pr.id);
                      if (r.deleted) p.showToast("تم حذف المنتج");
                      else if (r.archived) p.showToast(`استُخدم في ${r.usedIn} فاتورة — تم إيقافه فقط`);
                    } catch (e: any) { p.showToast(e?.message ?? "تعذّر الحذف"); }
                  }}
                  className="rounded-xl bg-card border border-debt/40 text-debt text-xs font-bold py-2 px-3"
                  aria-label="حذف المنتج"
                >حذف</button>
              </div>
            </div>
          ))}
        </div>
        <button onClick={() => setAddOpen(true)} className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold">＋ إضافة منتج</button>
      </div>

      {addOpen && <AddProductSheet existingNames={(p.products ?? []).map((x: Product) => String(x.name || "").trim().toLowerCase())} onClose={() => setAddOpen(false)} onSave={async (data) => {
        try { await p.addProductAsync(data); setAddOpen(false); p.showToast("تمت إضافة المنتج"); }
        catch (e: any) { p.showToast(e?.message ?? "تعذّر الحفظ"); }
      }} />}
      {editing && <AddProductSheet
        mode="edit"
        initial={{ name: editing.name, price: editing.price, cost: editing.cost ?? 0, stock: editing.stock, is_discount: !!editing.is_discount }}
        existingNames={(p.products ?? []).filter((x: Product) => x.id !== editing.id).map((x: Product) => String(x.name || "").trim().toLowerCase())}
        onClose={() => setEditing(null)}
        onSave={async (data) => {
          try { await p.updateProductAsync({ id: editing.id, ...data }); setEditing(null); p.showToast("تم تحديث المنتج"); }
          catch (e: any) { p.showToast(e?.message ?? "تعذّر الحفظ"); }
        }}
      />}
    </>
  );
}
