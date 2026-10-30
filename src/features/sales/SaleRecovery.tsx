import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import {
  loadSale,
  saleScope,
  SALE_ENVIRONMENT,
  SALE_EVENT,
  saleErrorMessage,
  type SaleRecord,
  type SaleInput,
  type CreatedSale,
} from "@/lib/sale-operation";

export function SaleRecovery({
  tenantId,
  onRetry,
  onOpen,
}: {
  tenantId: string | null | undefined;
  onRetry: (input: SaleInput) => Promise<CreatedSale>;
  onOpen: (orderId: string) => void;
}) {
  const [state, setState] = useState<{
    tenantId: string;
    entry: SaleRecord | null;
    error: string;
  } | null>(null);
  const [busy, setBusy] = useState(false);
  const [retryError, setRetryError] = useState("");
  useEffect(() => {
    let generation = 0,
      disposed = false;
    const refresh = async () => {
      const current = ++generation;
      setState(null);
      if (!tenantId) return;
      try {
        const { data, error } = await supabase.auth.getUser();
        if (disposed || current !== generation) return;
        if (error) throw error;
        if (!data.user) return;
        const entry = loadSale(saleScope(SALE_ENVIRONMENT, tenantId, data.user.id));
        setState({ tenantId, entry, error: "" });
      } catch (error) {
        if (!disposed && current === generation)
          setState({ tenantId, entry: null, error: saleErrorMessage(error) });
      }
    };
    const update = () => {
      void refresh();
    };
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(() => {
      generation++;
      setState(null);
      // Do not call an async Auth API while the SDK's auth callback is locked.
      setTimeout(() => {
        if (!disposed) update();
      }, 0);
    });
    window.addEventListener("storage", update);
    window.addEventListener(SALE_EVENT, update);
    update();
    return () => {
      disposed = true;
      generation++;
      subscription.unsubscribe();
      window.removeEventListener("storage", update);
      window.removeEventListener(SALE_EVENT, update);
    };
  }, [tenantId]);
  if (!state || state.tenantId !== tenantId || (!state.entry && !state.error)) return null;
  const entry = state.entry;
  return (
    <section
      role="status"
      aria-label="استعادة عملية البيع"
      className="m-4 rounded-xl border border-warn bg-warn-soft p-3 space-y-2 text-sm"
    >
      {state.error ? (
        <p role="alert">{state.error}</p>
      ) : entry?.status === "pending" ? (
        <>
          <p>
            توجد عملية بيع لم تتأكد نتيجتها. إعادة المحاولة تستعيد العملية نفسها وتحمي من تكرار
            الفاتورة.
          </p>
          <button
            disabled={busy}
            aria-busy={busy}
            className="rounded-lg bg-primary px-4 py-2 text-primary-foreground disabled:opacity-50"
            onClick={async () => {
              if (busy) return;
              setBusy(true);
              setRetryError("");
              try {
                const result = await onRetry({
                  ...entry.input,
                  expectedActorId: entry.scope.actorId,
                });
                onOpen(result.orderId);
              } catch (error) {
                setRetryError(saleErrorMessage(error));
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "جارٍ التحقق…" : "استعادة البيع المحفوظ"}
          </button>
        </>
      ) : entry?.result ? (
        <>
          <p>آخر نتيجة حفظ: الفاتورة {entry.result.number}.</p>
          <button
            className="underline"
            onClick={() => {
              if (entry.result) onOpen(entry.result.orderId);
            }}
          >
            عرض الفاتورة
          </button>
        </>
      ) : null}
      {retryError && <p role="alert">{retryError}</p>}
    </section>
  );
}
