import { useState, useEffect, useRef } from "react";
import { supabase } from "@/integrations/supabase/client";
import {
  newCollectionId,
  collectionErrorMessage,
  type CollectionInput,
} from "@/lib/collection-operation";
import {
  Info,
  AlertTriangle,
  CheckCircle2,
  Clock,
  TrendingUp,
  FileDown,
  Printer,
} from "lucide-react";
import {
  downloadInvoicePdf,
  printInvoice,
  ensureFont as ensureInvoiceFont,
  type InvoicePdfData,
} from "@/lib/invoice-pdf";
import { useTenantId, useTenant } from "@/lib/db";
import type { Invoice, Customer, Courier, Payment } from "@/features/shared/types";
import type { AppCtx } from "@/features/shared/AppContext";
import { StatusChip } from "@/features/shared/StatusChip";
import { Sheet } from "@/features/shared/Sheet";
import { Money, fmt } from "@/features/shared/Money";
import { FinancialReadNotice } from "@/features/shared/FinancialReadBoundary";
import { TopBar } from "@/features/layout/TopBar";
import {
  canCollectCustomerDebtForInvoice,
  getCourierCustodyForInvoice,
  getCustomerDebtForInvoice,
  getInvoiceGrossMargin,
  getInvoiceItemCost,
  getInvoiceRemainingAmount,
  isReturnedOrder,
} from "@/domain/finance/invoice-selectors";

/* --------------- INVOICE DETAIL --------------- */
export function InvoiceDetailScreen(p: AppCtx) {
  const { data: tenantId } = useTenantId();
  const { data: tenant } = useTenant(tenantId);
  // All hooks must run before any early return (react-hooks/rules-of-hooks).
  const [pdfBusy, setPdfBusy] = useState(false);
  const [collectOpen, setCollectOpen] = useState(false);
  const [collectAmt, setCollectAmt] = useState("");
  const [collectMethod, setCollectMethod] = useState<"cash" | "transfer">("cash");
  const [collectionDraft, setCollectionDraft] = useState<CollectionInput | null>(null);
  const [collectBusy, setCollectBusy] = useState(false);
  const collectLock = useRef(false);
  useEffect(() => {
    ensureInvoiceFont();
  }, []);
  const canUseBalance = p.financialReads.invoices.complete;
  const canExport = canUseBalance && p.financialReads.payments.complete;
  const inv: Invoice | undefined = p.invoices.find((i: Invoice) => i.id === p.openInvoiceId);
  if (!inv)
    return (
      <>
        <TopBar title="فاتورة" onBack={p.back} onHome={p.goHome} />
        <div className="p-4 text-sm text-muted-foreground">لم يتم العثور على الفاتورة</div>
      </>
    );
  const cust = p.customers.find((c: Customer) => c.id === inv.customerId);
  const isReturned = isReturnedOrder(inv);
  const remaining = getInvoiceRemainingAmount(inv);
  // A returned order has its stock restored and carries no customer debt,
  // even though status stays 'debt' and delivery flips to 'direct'.
  const customerRemaining = getCustomerDebtForInvoice(inv);
  const canCollectCustomerDebt = canCollectCustomerDebtForInvoice(inv);
  const courierCustody = getCourierCustodyForInvoice(inv);
  const cogs = inv.items.reduce((s, it) => s + getInvoiceItemCost(it), 0);
  const profit = getInvoiceGrossMargin(inv);

  const submitCollect = async () => {
    const a = Number(collectAmt);
    if (
      collectLock.current ||
      (!collectionDraft &&
        (!canUseBalance ||
          !canCollectCustomerDebt ||
          !Number.isFinite(a) ||
          a <= 0 ||
          a > customerRemaining))
    )
      return;
    collectLock.current = true;
    setCollectBusy(true);
    try {
      let input = collectionDraft;
      if (!input) {
        const { data, error } = await supabase.auth.getUser();
        if (error || !data.user) throw new Error("account unavailable");
        input = {
          operationId: newCollectionId(),
          expectedActorId: data.user.id,
          orderId: inv.id,
          amount: a,
          method: collectMethod,
        };
        setCollectionDraft(input);
      }
      await p.collectDebtAsync(input);
      setCollectOpen(false);
      setCollectionDraft(null);
      setCollectAmt("");
      setCollectMethod("cash");
    } catch (e) {
      p.showToast?.(collectionErrorMessage(e));
    } finally {
      collectLock.current = false;
      setCollectBusy(false);
    }
  };

  return (
    <>
      <TopBar title={`فاتورة #${inv.number}`} onBack={p.back} onHome={p.goHome} />
      <div className="px-4 pt-3 space-y-3">
        {isReturned && (
          <div className="rounded-2xl bg-warn-soft border border-warn/20 p-3 text-xs text-warn flex items-start gap-2">
            <Info className="w-4 h-4 shrink-0 mt-0.5" />
            <span>
              هذه الفاتورة <b>أُرجعت</b> — رجعت البضاعة للمخزون، ولا يوجد دين على العميل ولا عهدة
              على المندوب.
            </span>
          </div>
        )}
        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-xs text-muted-foreground">العميل</div>
              <div className="font-bold mt-0.5">
                {remaining > 0 ? (cust?.name ?? "—") : (cust?.name ?? "بدون عميل")}
              </div>
            </div>
            {isReturned ? (
              <StatusChip kind="warn" icon={<AlertTriangle className="w-3 h-3" />}>
                أُرجعت
              </StatusChip>
            ) : (
              <>
                {inv.status === "paid" && (
                  <StatusChip kind="paid" icon={<CheckCircle2 className="w-3 h-3" />}>
                    مدفوع
                  </StatusChip>
                )}
                {inv.status === "partial" && (
                  <StatusChip kind="partial" icon={<Clock className="w-3 h-3" />}>
                    جزئي
                  </StatusChip>
                )}
                {inv.status === "debt" && (
                  <StatusChip kind="debt" icon={<AlertTriangle className="w-3 h-3" />}>
                    دين
                  </StatusChip>
                )}
              </>
            )}
          </div>
          <div className="text-xs text-muted-foreground mt-2">
            {inv.time} {inv.delivery === "courier" && "· توصيل عبر مندوب"}
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4">
          <div className="text-xs font-bold text-muted-foreground mb-2">الأصناف</div>
          <div className="space-y-2">
            {inv.items.map((it, i) => (
              <div key={i} className="flex items-center justify-between text-sm">
                <div>
                  {it.name}{" "}
                  <span className="text-muted-foreground">
                    × <span className="num">{it.qty}</span>
                  </span>
                </div>
                <Money v={it.qty * it.price} />
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-2xl bg-card border border-border p-4 space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-muted-foreground">الإجمالي</span>
            <Money v={inv.total} />
          </div>
          <div className="flex justify-between">
            <span className="text-muted-foreground">المدفوع للصندوق</span>
            <Money v={inv.paid} className="text-success" />
          </div>
          {inv.delivery === "courier" && courierCustody > 0 && (
            <div className="flex justify-between">
              <span className="text-muted-foreground">بيد المندوب (عهدة)</span>
              <Money v={courierCustody} className="text-warn" />
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-muted-foreground">المتبقي على العميل</span>
            <Money v={customerRemaining} className={customerRemaining > 0 ? "text-debt" : ""} />
          </div>
        </div>

        <div className="rounded-2xl bg-profit-soft border border-profit/20 p-4">
          <div className="flex items-center gap-2 text-profit text-xs font-bold">
            <TrendingUp className="w-4 h-4" /> ربح الفاتورة (تقديري)
          </div>
          <div className="mt-1">
            <Money v={profit} className="text-lg text-profit" />
          </div>
          <div className="text-[11px] text-muted-foreground mt-1">
            التكلفة وقت البيع: <span className="num">{fmt(cogs)}</span> د.ل
          </div>
        </div>

        {/* Payment timeline */}
        {(() => {
          const invPayments = (p.payments as Payment[])
            .filter((pm) => pm.invoiceId === inv.id)
            .sort((a, b) => (a.time < b.time ? -1 : 1));
          if (invPayments.length === 0 && remaining === inv.total) return null;
          return (
            <div className="rounded-2xl bg-card border border-border p-4">
              <div className="text-xs font-bold text-muted-foreground mb-2">سجل الدفعات</div>
              <div className="space-y-1.5">
                {invPayments.map((pm) => (
                  <div key={pm.id} className="flex items-center justify-between text-xs">
                    <span className="text-muted-foreground">
                      {pm.kind === "sale"
                        ? "بيع"
                        : pm.kind === "debt_collection"
                          ? "تحصيل دفعة"
                          : "تسوية مندوب"}
                      {" · "}
                      {pm.method === "cash" ? "نقدي" : pm.method === "transfer" ? "تحويل" : "تسوية"}
                      {" · "}
                      {pm.time}
                    </span>
                    <Money v={pm.amount} className="text-success font-bold" />
                  </div>
                ))}
                {customerRemaining > 0 && (
                  <div className="flex items-center justify-between text-xs pt-2 border-t border-border mt-2">
                    <span className="text-debt">المتبقي على العميل</span>
                    <Money v={customerRemaining} className="text-debt font-bold" />
                  </div>
                )}
              </div>
            </div>
          );
        })()}

        {(() => {
          const courierName = inv.courierId
            ? p.couriers.find((c: Courier) => c.id === inv.courierId)?.name
            : undefined;
          const salePm = (p.payments as Payment[]).find(
            (pm) => pm.invoiceId === inv.id && pm.kind === "sale",
          );
          const method = (salePm?.method ?? "cash") as "cash" | "transfer";
          const createdAt = inv.createdAt ? new Date(inv.createdAt) : new Date();
          const dateText = createdAt.toLocaleDateString("en-GB");
          const data: InvoicePdfData = {
            shopName: tenant?.name ?? "محلي",
            number: String(inv.number),
            issuedAt: createdAt,
            dateText,
            timeText: inv.time,
            customerName: cust?.name,
            customerPhone: cust?.phone,
            courierName,
            delivery: inv.delivery,
            items: inv.items.map((it) => ({ name: it.name, qty: it.qty, price: it.price })),
            total: inv.total,
            paid: inv.paid,
            collectedByCourier: courierCustody,
            remaining: customerRemaining,
            method,
            status: inv.status,
          };
          const handlePdf = async () => {
            if (!canExport) return;
            setPdfBusy(true);
            try {
              await downloadInvoicePdf(data);
              p.showToast?.("تم تحميل الفاتورة");
            } catch (e) {
              console.error(e);
              p.showToast?.("تعذّر إنشاء PDF");
            } finally {
              setPdfBusy(false);
            }
          };
          return (
            <>
              <FinancialReadNotice
                reads={[p.financialReads.payments]}
                onRetry={p.retryFinancialReads}
              />
              <div className="grid grid-cols-2 gap-2">
                <button
                  disabled={pdfBusy || !canExport}
                  onClick={handlePdf}
                  className="rounded-2xl bg-card border border-border py-3 font-bold text-sm flex items-center justify-center gap-1.5 disabled:opacity-50"
                >
                  <FileDown className="w-4 h-4" />
                  {pdfBusy ? "..." : "تحميل PDF"}
                </button>
                <button
                  disabled={!canExport}
                  onClick={() => {
                    if (canExport) printInvoice(data);
                  }}
                  className="rounded-2xl bg-card border border-border py-3 font-bold text-sm flex items-center justify-center gap-1.5"
                >
                  <Printer className="w-4 h-4" />
                  طباعة
                </button>
              </div>
              {canCollectCustomerDebt && (
                <button
                  disabled={customerRemaining <= 0 || !canUseBalance}
                  onClick={() => {
                    setCollectionDraft(null);
                    setCollectOpen(true);
                  }}
                  className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40"
                >
                  تحصيل دفعة
                </button>
              )}
            </>
          );
        })()}
      </div>

      {collectOpen && (
        <Sheet
          onClose={() => {
            if (!collectLock.current) setCollectOpen(false);
          }}
          title="تحصيل دفعة"
        >
          <FinancialReadNotice
            reads={[p.financialReads.invoices]}
            onRetry={p.retryFinancialReads}
          />
          <div className="space-y-3">
            <div className="text-sm text-muted-foreground">
              المتبقي: <Money v={customerRemaining} className="text-debt" />
            </div>
            <input
              disabled={collectBusy || collectionDraft !== null}
              value={collectAmt}
              onChange={(e) => setCollectAmt(e.target.value)}
              inputMode="decimal"
              placeholder="المبلغ"
              className="w-full rounded-xl border border-border bg-background px-3 py-3 text-base num text-right"
            />
            {Number(collectAmt) > customerRemaining && (
              <div className="text-xs text-debt">لا يمكن تحصيل أكثر من المتبقي</div>
            )}
            <div>
              <label className="text-xs font-bold text-muted-foreground">طريقة الدفع</label>
              <div className="mt-1 grid grid-cols-2 gap-2">
                <button
                  disabled={collectBusy || collectionDraft !== null}
                  onClick={() => setCollectMethod("cash")}
                  className={`py-2 rounded-xl text-sm font-bold ${collectMethod === "cash" ? "bg-primary text-primary-foreground" : "bg-muted"}`}
                >
                  نقدي
                </button>
                <button
                  disabled={collectBusy || collectionDraft !== null}
                  onClick={() => setCollectMethod("transfer")}
                  className={`py-2 rounded-xl text-sm font-bold ${collectMethod === "transfer" ? "bg-primary text-primary-foreground" : "bg-muted"}`}
                >
                  تحويل
                </button>
              </div>
            </div>
            <button
              disabled={
                collectBusy ||
                (!collectionDraft &&
                  (!canUseBalance || !Number(collectAmt) || Number(collectAmt) > customerRemaining))
              }
              onClick={submitCollect}
              className="w-full rounded-2xl bg-primary text-primary-foreground py-3 font-bold disabled:opacity-40"
            >
              {collectBusy
                ? "جارٍ التحقق…"
                : collectionDraft
                  ? "إعادة محاولة التحصيل نفسه"
                  : "تأكيد التحصيل"}
            </button>
          </div>
        </Sheet>
      )}
    </>
  );
}
