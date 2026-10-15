import { downloadInvoicePdf } from "../../src/lib/invoice-pdf";

// Test entry only: the real invoice implementation and dependencies are bundled unchanged.
Object.assign(window, {
  runLocalInvoice: () =>
    downloadInvoicePdf({
      shopName: "متجر تجريبي محلي",
      number: "17",
      issuedAt: "2026-10-15T12:00:00Z",
      customerName: "عميل وهمي",
      delivery: "direct",
      items: [{ name: "صنف تجريبي", qty: 2, price: 50 }],
      total: 100,
      paid: 40,
      remaining: 60,
      method: "cash",
      status: "partial",
    }),
});
