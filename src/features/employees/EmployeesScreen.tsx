import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { EmployeeAccountsList } from "./EmployeeAccountsList";

export function EmployeesScreen(p: AppCtx) {
  return (
    <>
      <TopBar title="حسابات الموظفين" onBack={p.back} onHome={p.goHome} />
      <EmployeeAccountsList
        tenantId={p.tenantId}
        isOwner={p.myRole === "owner"}
        onToast={p.showToast}
        onOpenSettlements={(courierId) => {
          p.setOpenCourierId(courierId);
          p.go("settlements");
        }}
      />
    </>
  );
}
