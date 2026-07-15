import { useState } from "react";
import { Phone } from "lucide-react";
import { Money } from "@/features/shared/Money";
import type { EmployeePortalOrder } from "./employee-db";

const labels: Record<EmployeePortalOrder["courierState"], string> = {
  pending: "قيد التوصيل",
  delivered_full: "تم التسليم كاملًا",
  delivered_partial: "تم التسليم جزئيًا",
  delivered_none: "تم التسليم دون تحصيل",
};

export function EmployeeOrderCard({
  order,
  busy,
  onUpdate,
}: {
  order: EmployeePortalOrder;
  busy: boolean;
  onUpdate: (
    state: "pending" | "delivered_full" | "delivered_partial" | "delivered_none" | "returned",
    collected?: number,
  ) => void;
}) {
  const [partialOpen, setPartialOpen] = useState(false);
  const [partialAmount, setPartialAmount] = useState("");
  const remaining = Math.max(order.total - order.paid, 0);

  return (
    <article className="rounded-2xl bg-card border border-border p-4 space-y-3">
      <div className="flex items-start gap-3">
        <div className="flex-1">
          <div className="font-bold">طلب #{order.number}</div>
          <div className="text-xs text-muted-foreground mt-1">
            {new Date(order.createdAt).toLocaleString("ar-LY", {
              dateStyle: "short",
              timeStyle: "short",
            })}
          </div>
        </div>
        <span className="rounded-full bg-primary-soft text-primary px-2 py-1 text-[11px] font-bold">
          {labels[order.courierState]}
        </span>
      </div>

      <div className="rounded-xl bg-background border border-border p-3">
        <div className="font-bold text-sm">{order.customer?.name ?? "عميل"}</div>
        {order.customer?.phone && (
          <a
            href={`tel:${order.customer.phone}`}
            className="mt-1 inline-flex items-center gap-1 text-xs text-primary"
            dir="ltr"
          >
            <Phone className="w-3.5 h-3.5" />
            {order.customer.phone}
          </a>
        )}
      </div>

      <div className="space-y-1 text-xs">
        {order.items.map((item, index) => (
          <div key={`${item.name}-${index}`} className="flex justify-between gap-3">
            <span>
              {item.name} × {item.qty}
            </span>
            <Money v={item.unitPrice * item.qty} />
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="rounded-xl bg-background border border-border p-3">
          <div className="text-muted-foreground">المطلوب من العميل</div>
          <Money v={remaining} className="font-bold mt-1" />
        </div>
        <div className="rounded-xl bg-warn-soft border border-warn/20 p-3">
          <div className="text-warn">المحصّل بيدك</div>
          <Money v={order.collectedByCourier} className="font-bold mt-1" />
        </div>
      </div>

      {order.courierState === "pending" && (
        <div className="grid grid-cols-2 gap-2">
          <button
            disabled={busy}
            onClick={() => onUpdate("delivered_full")}
            className="rounded-xl bg-success text-white py-2.5 text-xs font-bold disabled:opacity-50"
          >
            تسليم كامل
          </button>
          <button
            disabled={busy}
            onClick={() => setPartialOpen((value) => !value)}
            className="rounded-xl bg-warn text-white py-2.5 text-xs font-bold disabled:opacity-50"
          >
            تحصيل جزئي
          </button>
          <button
            disabled={busy}
            onClick={() => onUpdate("delivered_none")}
            className="rounded-xl bg-primary text-primary-foreground py-2.5 text-xs font-bold disabled:opacity-50"
          >
            دون تحصيل
          </button>
          <button
            disabled={busy}
            onClick={() => onUpdate("returned")}
            className="rounded-xl border border-destructive/30 text-destructive py-2.5 text-xs font-bold disabled:opacity-50"
          >
            مرتجع
          </button>
        </div>
      )}

      {partialOpen && order.courierState === "pending" && (
        <div className="rounded-xl bg-background border border-border p-3 space-y-2">
          <label className="text-xs text-muted-foreground">المبلغ المحصّل جزئيًا</label>
          <input
            type="number"
            inputMode="decimal"
            min="0"
            max={remaining}
            value={partialAmount}
            onChange={(event) => setPartialAmount(event.target.value)}
            className="w-full h-11 rounded-xl border border-input bg-card px-3"
          />
          <button
            disabled={busy || Number(partialAmount) <= 0 || Number(partialAmount) >= remaining}
            onClick={() => onUpdate("delivered_partial", Number(partialAmount))}
            className="w-full rounded-xl bg-warn text-white py-2.5 text-xs font-bold disabled:opacity-50"
          >
            تأكيد التحصيل الجزئي
          </button>
        </div>
      )}
    </article>
  );
}
