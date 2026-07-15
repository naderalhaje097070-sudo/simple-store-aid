import { createFileRoute } from "@tanstack/react-router";
import { useMyRole, useTenantId } from "@/lib/db";
import { EmployeePortal } from "@/features/employees/EmployeePortal";

// Delivery staff are isolated from the owner application at the route boundary.
export const Route = createFileRoute("/_authenticated/employee" as never)({
  ssr: false,
  head: () => ({ meta: [{ title: "طلباتي وعهدتي — منجز" }] }),
  component: EmployeePage,
});

function EmployeePage() {
  const { data: tenantId } = useTenantId();
  const { data: role, isLoading } = useMyRole(tenantId);

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

  if (role !== "staff") {
    window.location.replace("/app");
    return null;
  }

  return <EmployeePortal tenantId={tenantId} />;
}
