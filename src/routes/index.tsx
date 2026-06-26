import { createFileRoute, redirect } from "@tanstack/react-router";
import { useEffect } from "react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/")({
  ssr: false,
  beforeLoad: async () => {
    if (typeof window === "undefined") return;
    const { data } = await supabase.auth.getSession();
    if (data.session) throw redirect({ to: "/app" });
    throw redirect({ to: "/auth" });
  },
  component: Splash,
});

function Splash() {
  // beforeLoad redirects; this only renders during the brief client navigation.
  useEffect(() => {}, []);
  return (
    <div className="min-h-screen flex items-center justify-center bg-background">
      <div className="text-muted-foreground text-sm">جاري التحميل…</div>
    </div>
  );
}
