import { useEffect, useState } from "react";
import { supabase } from "@/integrations/supabase/client";
import {
  loadCollection,
  COLLECTION_EVENT,
  collectionErrorMessage,
  type CollectionRecord,
  type CollectionInput,
  type CollectionResult,
} from "@/lib/collection-operation";
import { saleScope, SALE_ENVIRONMENT } from "@/lib/sale-operation";

export function CollectionRecovery({
  tenantId,
  onRetry,
  onOpen,
}: {
  tenantId: string | null | undefined;
  onRetry: (input: CollectionInput) => Promise<CollectionResult>;
  onOpen: (orderId: string) => void;
}) {
  const [state, setState] = useState<{
    tenantId: string;
    entry: CollectionRecord | null;
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
        const entry = loadCollection(saleScope(SALE_ENVIRONMENT, tenantId, data.user.id));
        setState({ tenantId, entry, error: "" });
      } catch (error) {
        if (!disposed && current === generation)
          setState({
            tenantId,
            entry: null,
            error: collectionErrorMessage(error),
          });
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
    window.addEventListener(COLLECTION_EVENT, update);
    update();
    return () => {
      disposed = true;
      generation++;
      subscription.unsubscribe();
      window.removeEventListener("storage", update);
      window.removeEventListener(COLLECTION_EVENT, update);
    };
  }, [tenantId]);
  if (!state || state.tenantId !== tenantId || (!state.entry && !state.error)) return null;
  const entry = state.entry;
  return (
    <section
      role="status"
      aria-label="استعادة عملية التحصيل"
      className="m-4 rounded-xl border border-warn bg-warn-soft p-3 space-y-2 text-sm"
    >
      {state.error ? (
        <p role="alert">{state.error}</p>
      ) : entry?.status === "pending" ? (
        <>
          <p>
            توجد عملية تحصيل لم تتأكد نتيجتها. إعادة المحاولة تستعيد العملية نفسها وتحمي من تكرار
            الدفعة.
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
                await onRetry({
                  ...entry.input,
                  expectedActorId: entry.scope.actorId,
                });
                onOpen(entry.input.orderId);
              } catch (error) {
                setRetryError(collectionErrorMessage(error));
              } finally {
                setBusy(false);
              }
            }}
          >
            {busy ? "جارٍ التحقق…" : "استعادة التحصيل المحفوظ"}
          </button>
        </>
      ) : entry?.result ? (
        <>
          <p>تم تأكيد آخر تحصيل محفوظ.</p>
          <button
            className="underline"
            onClick={() => {
              onOpen(entry.input.orderId);
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
