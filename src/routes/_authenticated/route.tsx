import { createFileRoute, Outlet, redirect } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/_authenticated")({
  beforeLoad: async () => {
    if (typeof window === "undefined") return;
    const { data, error } = await supabase.auth.getUser();
    if (error || !data.user) throw redirect({ to: "/auth" });
    return { user: data.user };
  },
  component: AuthenticatedLayout,
});

type AccessState = "checking" | "allowed" | "redirecting" | "disabled";

function AuthenticatedLayout() {
  const [access, setAccess] = useState<AccessState>("checking");

  useEffect(() => {
    let active = true;
    void (async () => {
      const { data: userRes } = await supabase.auth.getUser();
      const uid = userRes.user?.id;
      if (!uid) {
        window.location.replace("/auth");
        return;
      }

      const { data: rawProfile } = await supabase
        .from("profiles")
        .select("tenant_id,disabled_at" as never)
        .eq("id", uid)
        .maybeSingle();
      if (!active) return;

      const profile = rawProfile as unknown as {
        tenant_id?: string | null;
        disabled_at?: string | null;
      } | null;
      if (profile?.disabled_at) {
        setAccess("disabled");
        return;
      }

      const path = window.location.pathname;
      const isPlatformAdminRoute = path.startsWith("/platform-admin");
      const tenantId = profile?.tenant_id ?? null;

      if (!tenantId && !isPlatformAdminRoute) {
        if (path !== "/onboarding") {
          setAccess("redirecting");
          window.location.replace("/onboarding");
          return;
        }
        setAccess("allowed");
        return;
      }

      if (tenantId) {
        const { data: roleRow } = await supabase
          .from("user_roles")
          .select("role")
          .eq("tenant_id", tenantId)
          .eq("user_id", uid)
          .maybeSingle();
        if (!active) return;

        const role = roleRow?.role;
        if (role === "staff" && path !== "/employee") {
          setAccess("redirecting");
          window.location.replace("/employee");
          return;
        }
        if (role === "owner" && (path === "/employee" || path === "/onboarding")) {
          setAccess("redirecting");
          window.location.replace("/app");
          return;
        }
      }

      setAccess("allowed");
    })();

    return () => {
      active = false;
    };
  }, []);

  if (access === "disabled") {
    return (
      <div dir="rtl" className="min-h-screen bg-background flex items-center justify-center p-5">
        <div className="w-full max-w-sm rounded-2xl bg-card border border-border p-5 text-center space-y-3">
          <div className="font-bold">تم تعطيل حساب الموظف</div>
          <p className="text-xs text-muted-foreground">راجع صاحب المحل لإعادة تفعيل الحساب.</p>
          <button
            onClick={async () => {
              await supabase.auth.signOut();
              window.location.href = "/auth";
            }}
            className="w-full rounded-xl bg-muted py-3 text-sm font-bold"
          >
            تسجيل الخروج
          </button>
        </div>
      </div>
    );
  }

  if (access !== "allowed") {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        جاري التحميل…
      </div>
    );
  }

  return <Outlet />;
}
