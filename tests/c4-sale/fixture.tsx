import { useState } from "react";
import { createRoot } from "react-dom/client";
import { SaleScreen, SaleQuickScreen } from "__ACTUAL_CARTS__";
import { SaleRecovery } from "@/features/sales/SaleRecovery";
import { useCreateSale } from "@/lib/db";
const tenant = "22222222-2222-4222-8222-222222222222";
const product = {
  id: "33333333-3333-4333-8333-333333333333",
  name: "صنف تجريبي",
  price: 12.5,
  cost: 2,
  stock: 10,
  lowAt: 1,
  is_active: true,
};
// Inactive product: the database rejects it (product_inactive), so the sale
// screens must not offer it.
const inactive = {
  id: "44444444-4444-4444-8444-444444444444",
  name: "صنف موقوف",
  price: 9,
  cost: 1,
  stock: 5,
  lowAt: 1,
  is_active: false,
};
function Fixture() {
  const mutation = useCreateSale(tenant);
  const start = location.hash === "#sale" ? "sale" : "sale_quick";
  const [view, setView] = useState(start),
    [opened, setOpened] = useState(""),
    [toast, setToast] = useState("");
  const context = {
    products: [product, inactive],
    customers: [],
    couriers: [],
    invoices: [],
    createSaleAsync: mutation.mutateAsync,
    addCustomerAsync: async () => {
      throw Error("not in fixture scope");
    },
    back() {},
    goHome() {},
    showToast: setToast,
    setLastSaleSummary() {},
    setLastCreatedInvoiceId: setOpened,
    setScreen: setView,
  };
  return (
    <>
      <SaleRecovery
        tenantId={tenant}
        onRetry={mutation.mutateAsync}
        onOpen={(id) => {
          setOpened(id);
          setView("result");
        }}
      />
      <output id="opened">{opened}</output>
      <output id="toast">{toast}</output>
      {view === "sale" ? (
        <SaleScreen {...context} />
      ) : view === "sale_quick" ? (
        <SaleQuickScreen {...context} />
      ) : (
        <button onClick={() => setView(start)}>بيع جديد</button>
      )}
    </>
  );
}
createRoot(document.getElementById("root")!).render(<Fixture />);
