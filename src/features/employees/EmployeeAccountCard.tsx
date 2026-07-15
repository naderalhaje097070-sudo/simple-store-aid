import { Money } from "@/features/shared/Money";
import type { CourierAccount } from "./employee-db";

export function EmployeeAccountCard({
  account,
  email,
  busy,
  onEmailChange,
  onLink,
  onUnlink,
  onOpenSettlements,
  onResolve,
}: {
  account: CourierAccount;
  email: string;
  busy: boolean;
  onEmailChange: (email: string) => void;
  onLink: () => void;
  onUnlink: () => void;
  onOpenSettlements: () => void;
  onResolve: (status: "approved" | "rejected") => void;
}) {
  return (
    <div className="rounded-2xl bg-card border border-border p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="w-11 h-11 rounded-full bg-primary-soft text-primary flex items-center justify-center font-bold">
          {account.name.slice(0, 1)}
        </div>
        <div className="flex-1 min-w-0">
          <div className="font-bold">{account.name}</div>
          <div className="text-xs text-muted-foreground">{account.phone ?? "بدون رقم هاتف"}</div>
          <div className="mt-1 text-[11px]">
            {account.userId ? (
              <span className="text-success">
                مرتبط: {account.email ?? account.displayName ?? "حساب موظف"}
              </span>
            ) : (
              <span className="text-muted-foreground">لا يوجد حساب مرتبط</span>
            )}
          </div>
        </div>
        <span
          className={`text-[11px] px-2 py-1 rounded-full ${account.isActive ? "bg-success-soft text-success" : "bg-muted text-muted-foreground"}`}
        >
          {account.isActive ? "نشط" : "متوقف"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <div className="rounded-xl bg-background border border-border p-3">
          <div className="text-[11px] text-muted-foreground">طلبات معلقة</div>
          <div className="font-bold mt-1">{account.pendingOrders}</div>
        </div>
        <div className="rounded-xl bg-background border border-border p-3">
          <div className="text-[11px] text-muted-foreground">العهدة الحالية</div>
          <Money v={account.custody} className="font-bold mt-1" />
        </div>
      </div>

      {account.pendingRequest && (
        <div className="rounded-xl bg-warn-soft border border-warn/20 p-3 space-y-2">
          <div className="text-xs font-bold">
            طلب تسوية بقيمة <Money v={account.pendingRequest.amount} />
          </div>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={onOpenSettlements}
              className="rounded-lg bg-primary text-primary-foreground py-2 text-xs font-bold"
            >
              التسويات
            </button>
            <button
              disabled={busy}
              onClick={() => onResolve("approved")}
              className="rounded-lg bg-success text-white py-2 text-xs font-bold disabled:opacity-50"
            >
              اعتماد
            </button>
            <button
              disabled={busy}
              onClick={() => onResolve("rejected")}
              className="rounded-lg bg-muted py-2 text-xs font-bold disabled:opacity-50"
            >
              رفض
            </button>
          </div>
          <p className="text-[10px] text-muted-foreground">
            يجب تصفير العهدة من شاشة التسويات قبل الاعتماد.
          </p>
        </div>
      )}

      {account.userId ? (
        <button
          disabled={busy}
          onClick={onUnlink}
          className="w-full rounded-xl border border-destructive/30 text-destructive py-2.5 text-xs font-bold disabled:opacity-50"
        >
          تعطيل وفصل الحساب
        </button>
      ) : (
        <div className="space-y-2">
          <input
            type="email"
            dir="ltr"
            value={email}
            onChange={(event) => onEmailChange(event.target.value)}
            placeholder="employee@example.com"
            className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm text-left"
          />
          <button
            disabled={busy || !email.trim()}
            onClick={onLink}
            className="w-full rounded-xl bg-primary text-primary-foreground py-2.5 text-xs font-bold disabled:opacity-50"
          >
            ربط الحساب بهذا المندوب
          </button>
        </div>
      )}
    </div>
  );
}
