import { useState } from "react";
import type { AppCtx } from "@/features/shared/AppContext";
import {
  useCourierAccounts,
  useLinkCourierAccount,
  useResolveSettlementRequest,
  useUnlinkCourierAccount,
} from "./employee-db";
import { EmployeeAccountCard } from "./EmployeeAccountCard";

export function EmployeeAccountsList({ context: p }: { context: AppCtx }) {
  const isOwner = p.myRole === "owner";
  const accounts = useCourierAccounts(p.tenantId, isOwner);
  const linkAccount = useLinkCourierAccount(p.tenantId);
  const unlinkAccount = useUnlinkCourierAccount(p.tenantId);
  const resolveRequest = useResolveSettlementRequest(p.tenantId);
  const [emails, setEmails] = useState<Record<string, string>>({});
  const [error, setError] = useState<string | null>(null);

  const run = async (action: () => Promise<unknown>, success: string) => {
    setError(null);
    try {
      await action();
      p.showToast(success);
    } catch (err) {
      setError(err instanceof Error ? err.message : "تعذّر إتمام العملية");
    }
  };

  if (!isOwner) {
    return <div className="px-4 pt-10 text-center text-sm text-muted-foreground">إدارة الموظفين متاحة لصاحب المحل فقط.</div>;
  }

  return (
    <div className="px-4 pt-3 space-y-3 max-w-3xl mx-auto">
      <div className="rounded-2xl bg-primary-soft border border-primary/20 p-4 text-xs leading-6">
        <div className="font-bold text-sm mb-1">حساب مستقل لكل مندوب</div>
        يفتح الموظف حسابًا في منجز أولًا، ثم تربطه هنا ببريده. سيشاهد طلباته وعهدته فقط، ولا يرى أرباح المحل أو طلبات غيره.
      </div>

      {error && <div className="rounded-xl bg-destructive/10 text-destructive px-3 py-2 text-xs">{error}</div>}
      {accounts.isLoading && <div className="text-center py-10 text-sm text-muted-foreground">جاري تحميل الموظفين…</div>}
      {accounts.error && <div className="text-center py-10 text-sm text-destructive">{accounts.error.message}</div>}

      <div className="space-y-3">
        {(accounts.data ?? []).map((account) => (
          <EmployeeAccountCard
            key={account.courierId}
            account={account}
            email={emails[account.courierId] ?? ""}
            busy={linkAccount.isPending || unlinkAccount.isPending || resolveRequest.isPending}
            onEmailChange={(email) => setEmails((current) => ({ ...current, [account.courierId]: email }))}
            onLink={() => run(
              () => linkAccount.mutateAsync({ courierId: account.courierId, email: emails[account.courierId] ?? "" }),
              "تم ربط حساب الموظف",
            )}
            onUnlink={() => run(() => unlinkAccount.mutateAsync(account.courierId), "تم تعطيل حساب الموظف")}
            onOpenSettlements={() => {
              p.setOpenCourierId(account.courierId);
              p.go("settlements");
            }}
            onResolve={(status) => account.pendingRequest
              ? run(
                  () => resolveRequest.mutateAsync({ requestId: account.pendingRequest!.id, status }),
                  status === "approved" ? "تم اعتماد طلب التسوية" : "تم رفض طلب التسوية",
                )
              : Promise.resolve()}
          />
        ))}
      </div>

      {!accounts.isLoading && (accounts.data?.length ?? 0) === 0 && (
        <div className="rounded-2xl bg-card border border-border p-8 text-center text-sm text-muted-foreground">
          أضف مندوبًا أولًا، ثم ارجع لربط حسابه.
        </div>
      )}
    </div>
  );
}
