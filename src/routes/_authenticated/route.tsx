import { createFileRoute, Outlet, redirect, useNavigate } from "@tanstack/react-router";
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

function AuthenticatedLayout() {
  const navigate = useNavigate();
  const [checking, setChecking] = useState(true);
  const [hasTenant, setHasTenant] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;
    void (async () => {
      const { data: userRes } = await supabase.auth.getUser();
      const uid = userRes.user?.id;
      if (!uid) {
        navigate({ to: "/auth" });
        return;
      }
      const { data: profile } = await supabase
        .from("profiles")
        .select("tenant_id")
        .eq("id", uid)
        .maybeSingle();
      if (!active) return;
      const ok = !!profile?.tenant_id;
      setHasTenant(ok);
      setChecking(false);
      const path = window.location.pathname;
      const isPlatformAdminRoute = path.startsWith("/platform-admin");
      // Route-level redirect to onboarding if no tenant and not already there
      if (!ok && !isPlatformAdminRoute && path !== "/onboarding") {
        navigate({ to: "/onboarding" });
      }
      if (ok && path === "/onboarding") {
        navigate({ to: "/app" });
      }
    })();
    return () => {
      active = false;
    };
  }, [navigate]);

  if (checking) {
    return (
      <div className="min-h-screen flex items-center justify-center text-sm text-muted-foreground">
        جاري التحميل…
      </div>
    );
  }

  if (
    hasTenant === false &&
    !window.location.pathname.startsWith("/platform-admin") &&
    window.location.pathname !== "/onboarding"
  ) {
    return null;
  }

  return <Outlet />;
}
