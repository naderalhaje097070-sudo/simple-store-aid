import type { AppCtx } from "@/features/shared/AppContext";
import { TopBar } from "@/features/layout/TopBar";
import { EmployeeAccountsList } from "./EmployeeAccountsList";

export function EmployeesScreen(p: AppCtx) {
  return (
    <>
      <TopBar title="حسابات الموظفين" onBack={p.back} onHome={p.goHome} />
      <EmployeeAccountsList context={p} />
    </>
  );
}
