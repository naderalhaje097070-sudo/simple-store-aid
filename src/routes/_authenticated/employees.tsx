import { createFileRoute } from "@tanstack/react-router";
import { useState } from "react";
import { ArrowRight } from "lucide-react";
import { useMyRole, useTenantId } from "@/lib/db";
import { EmployeeAccountsList } from "@/features/employees/EmployeeAccountsList";

export const Route = createFileRoute("/_authenticated/employees" as never)({
  ssr: false,
  head: () => ({ meta: [{ title: "حسابات الموظفين — منجز" }] }),
  component: OwnerEmployeesPage,
});

function OwnerEmployeesPage() {
  const { data: tenantId } = useTenantId();
  const { data: role, isLoading } = useMyRole(tenantId);
  const [toast, setToast] = useState<string | null>(null);

  const showToast = (message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  };

  if (isLoading || !tenantId) {
    return (
      <div
        dir="rtl"
        className="min-h-screen flex items-center justify-center text-sm text-muted-foreground"
      >
        جاري التحميل…
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground pb-10">
      <header className="sticky top-0 z-20 bg-background/95 backdrop-blur border-b border-border px-4 py-3">
        <div className="max-w-3xl mx-auto flex items-center gap-3">
          <button
            onClick={() => {
              window.location.href = "/app";
            }}
            className="w-10 h-10 rounded-xl border border-border flex items-center justify-center"
            aria-label="العودة"
          >
            <ArrowRight className="w-4 h-4" />
          </button>
          <h1 className="font-bold">حسابات الموظفين</h1>
        </div>
      </header>

      <EmployeeAccountsList
        tenantId={tenantId}
        isOwner={role === "owner"}
        onToast={showToast}
        onOpenSettlements={() => {
          window.location.href = "/app";
        }}
      />

      {toast && (
        <div className="fixed bottom-5 left-1/2 -translate-x-1/2 rounded-xl bg-foreground text-background px-4 py-2 text-xs shadow-lg">
          {toast}
        </div>
      )}
    </div>
  );
}
