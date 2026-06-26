import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/_authenticated/onboarding")({
  ssr: false,
  head: () => ({
    meta: [
      { title: "إنشاء محلك — منجز" },
      { name: "description", content: "ابدأ بإضافة اسم محلك للبدء في استخدام منجز." },
    ],
  }),
  component: Onboarding,
});

function Onboarding() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!name.trim()) {
      setError("اكتب اسم المحل");
      return;
    }
    setLoading(true);
    try {
      const { data: userRes } = await supabase.auth.getUser();
      const uid = userRes.user?.id;
      if (!uid) throw new Error("جلسة منتهية، أعد الدخول");

      const { data: tenant, error: tErr } = await supabase
        .from("tenants")
        .insert({ name: name.trim(), owner_user_id: uid })
        .select("id")
        .single();
      if (tErr || !tenant) throw tErr ?? new Error("تعذّر إنشاء المحل");

      const { error: pErr } = await supabase
        .from("profiles")
        .update({ tenant_id: tenant.id })
        .eq("id", uid);
      if (pErr) throw pErr;

      const { error: rErr } = await supabase
        .from("user_roles")
        .insert({ user_id: uid, tenant_id: tenant.id, role: "owner" });
      if (rErr) throw rErr;

      navigate({ to: "/app" });
    } catch (err) {
      console.error("onboarding error:", err);
      setError("حدث خطأ، حاول مرة أخرى");
    } finally {
      setLoading(false);
    }
  };

  const signOut = async () => {
    await supabase.auth.signOut();
    window.location.href = "/auth";
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-5 py-10">
      <div className="w-full max-w-sm">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-extrabold">أهلاً بك في منجز</h1>
          <p className="text-sm text-muted-foreground mt-1">لنبدأ بإضافة اسم محلك</p>
        </div>

        <form onSubmit={onCreate} className="rounded-2xl bg-card border border-border p-5 shadow-sm space-y-4">
          <div>
            <label className="block text-xs text-muted-foreground mb-1">اسم المحل</label>
            <input
              autoFocus
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full h-12 rounded-xl border border-input bg-background px-3 text-base"
              placeholder="مثال: بقالة الأمين"
              maxLength={60}
            />
          </div>

          {error && <div className="text-xs text-destructive bg-destructive/10 rounded-lg px-3 py-2">{error}</div>}

          <button type="submit" disabled={loading} className="w-full h-12 rounded-xl bg-primary text-primary-foreground font-semibold disabled:opacity-60">
            {loading ? "..." : "إنشاء المحل والمتابعة"}
          </button>
        </form>

        <button onClick={signOut} className="block mx-auto mt-5 text-xs text-muted-foreground underline">
          تسجيل خروج
        </button>
      </div>
    </div>
  );
}
