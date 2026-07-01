/* eslint-disable @typescript-eslint/no-explicit-any */
import { useState, useEffect } from "react";
import { Moon, Sun } from "lucide-react";
import { TopBar } from "@/features/layout/TopBar";
import { useTheme } from "@/hooks/useTheme";
import { useTenantId, useTenant, useMyRole, useUpdateTenantName, useUpdateTenantBusinessType } from "@/lib/db";
import { BUSINESS_TYPES, businessTypeLabel } from "@/lib/business-types";

export function SettingsScreen(p: any) {
  const { data: tenantId } = useTenantId();
  const { data: tenant } = useTenant(tenantId);
  const { data: role } = useMyRole(tenantId);
  const updateNameMut = useUpdateTenantName(tenantId);
  const updateBizMut = useUpdateTenantBusinessType(tenantId);
  const [name, setName] = useState("");
  const [bizType, setBizType] = useState<string>("");
  const [savedFlash, setSavedFlash] = useState(false);
  const [bizFlash, setBizFlash] = useState(false);
  useEffect(() => { if (tenant?.name) setName(tenant.name); }, [tenant?.name]);
  useEffect(() => { setBizType(tenant?.business_type ?? ""); }, [tenant?.business_type]);

  const signOut = async () => {
    const { supabase } = await import("@/integrations/supabase/client");
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };

  const save = async () => {
    const v = name.trim();
    if (!v || v === tenant?.name) return;
    await updateNameMut.mutateAsync(v);
    setSavedFlash(true);
    setTimeout(() => setSavedFlash(false), 1500);
  };

  const saveBiz = async () => {
    const v = bizType || null;
    if (v === (tenant?.business_type ?? null)) return;
    await updateBizMut.mutateAsync(v);
    setBizFlash(true);
    setTimeout(() => setBizFlash(false), 1500);
  };

  const roleLabel = role === "owner" ? "صاحب المحل" : role === "staff" ? "موظّف" : "—";

  return (
    <>
      <TopBar title="الإعدادات" onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        <div className="rounded-2xl bg-card border border-border p-4">
          <label className="block text-xs text-muted-foreground mb-1">اسم المحل</label>
          <input
            value={name}
            onChange={e => setName(e.target.value)}
            maxLength={60}
            className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
            placeholder="مثال: بقالة الأمين"
          />
          <button
            onClick={save}
            disabled={updateNameMut.isPending || !name.trim() || name.trim() === tenant?.name}
            className="mt-3 w-full h-10 rounded-xl bg-primary text-primary-foreground text-sm font-semibold disabled:opacity-50"
          >
            {updateNameMut.isPending ? "..." : savedFlash ? "تم الحفظ ✓" : "حفظ"}
          </button>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4">
          <label className="block text-xs text-muted-foreground mb-1">نوع النشاط</label>
          <select
            value={bizType}
            onChange={e => setBizType(e.target.value)}
            className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
          >
            <option value="">غير محدد</option>
            {BUSINESS_TYPES.map(b => (
              <option key={b.value} value={b.value}>{b.label}</option>
            ))}
          </select>
          <p className="mt-2 text-[11px] text-muted-foreground">
            للعرض فقط — لا يؤثر على الحسابات أو المنتجات.
          </p>
          <button
            onClick={saveBiz}
            disabled={updateBizMut.isPending || (bizType || null) === (tenant?.business_type ?? null)}
            className="mt-3 w-full h-10 rounded-xl bg-primary text-primary-foreground text-sm font-semibold disabled:opacity-50"
          >
            {updateBizMut.isPending ? "..." : bizFlash ? "تم الحفظ ✓" : "حفظ"}
          </button>
        </div>

        <div className="rounded-2xl bg-card border border-border divide-y divide-border">
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">دورك في المحل</span>
            <span className="text-sm font-semibold">{roleLabel}</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">نوع النشاط الحالي</span>
            <span className="text-sm font-semibold">{businessTypeLabel(tenant?.business_type)}</span>
          </div>
          <div className="flex items-center gap-3 px-4 py-3">
            <span className="flex-1 text-sm text-muted-foreground">رقم المحل</span>
            <span className="text-[11px] font-mono text-muted-foreground" dir="ltr">{tenantId?.slice(0, 8) ?? "—"}</span>
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border overflow-hidden">
          <button onClick={signOut} className="w-full flex items-center gap-3 px-4 py-3 text-right text-destructive font-semibold">
            <span className="flex-1">تسجيل الخروج</span>
          </button>
        </div>

        <p className="text-[11px] text-muted-foreground text-center pt-2">منجز — دفتر محلك الذكي</p>
      </div>
    </>
  );
}
