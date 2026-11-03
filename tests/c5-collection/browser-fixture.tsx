// Real components, hook, React Query, SDK, Auth, REST and DB. Only application
// shell routing and unrelated PDF export are fixture boundaries.
import { useState } from "react";
import { createRoot } from "react-dom/client";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { InvoiceDetailScreen } from "@/features/invoices/InvoiceDetailScreen";
import { CollectionRecovery } from "@/features/invoices/CollectionRecovery";
import { useCollectDebt, useInvoices, usePayments } from "@/lib/db";
import { ready } from "./browser-client";
const config = window.collectionFixture;
const client = new QueryClient({
  defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
});
function Fixture() {
  const invoices = useInvoices(config.tenant),
    payments = usePayments(config.tenant),
    collect = useCollectDebt(config.tenant);
  const [toast, setToast] = useState("");
  const reads = {
    invoices: { complete: invoices.isSuccess },
    payments: { complete: payments.isSuccess },
  };
  const context = {
    invoices: invoices.data ?? [],
    payments: payments.data ?? [],
    customers: [],
    couriers: [],
    openInvoiceId: config.order,
    financialReads: reads,
    collectDebtAsync: collect.mutateAsync,
    showToast: setToast,
    back() {},
    goHome() {},
    retryFinancialReads() {
      void invoices.refetch();
      void payments.refetch();
    },
  };
  return (
    <>
      <CollectionRecovery
        tenantId={config.tenant}
        onRetry={collect.mutateAsync}
        onOpen={() => {}}
      />
      <output id="toast">{toast}</output>
      <output id="paid">{invoices.data?.find((i) => i.id === config.order)?.paid}</output>
      <InvoiceDetailScreen {...context} />
    </>
  );
}
ready.then(({ error }) => {
  if (error) throw Error("fixture auth");
  createRoot(document.getElementById("root")!).render(
    <QueryClientProvider client={client}>
      <Fixture />
    </QueryClientProvider>,
  );
});
