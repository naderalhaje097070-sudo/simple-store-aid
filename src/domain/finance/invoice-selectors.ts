import { isQuantity } from "./quantity";

// Creation must match the existing SQL numeric(12,2) accumulator: each positive
// line rounds to cents before summation. Stored invoice totals remain authoritative.
export function getSaleLineTotal(item: { price: number; qty: number }): number {
  if (!isQuantity(item.price, true) || !isQuantity(item.qty))
    throw new RangeError("invalid_sale_amount");
  const cents = BigInt(Math.round(item.price * 100));
  const quantityUnits = BigInt(Math.round(item.qty * 100));
  const total = (cents * quantityUnits + 50n) / 100n;
  return Number(total) / 100;
}

export function getSaleTotal(items: { price: number; qty: number }[]): number {
  const cents = items.reduce(
    (sum, item) => sum + BigInt(Math.round(getSaleLineTotal(item) * 100)),
    0n,
  );
  return Number(cents) / 100;
}

export type FinanceInvoiceItem = {
  qty: number;
  price: number;
  cost: number;
};

export type FinanceInvoice = {
  items: FinanceInvoiceItem[];
  total: number;
  paid: number;
  delivery: "direct" | "courier";
  courierState?: "pending" | "delivered_none" | "delivered_partial" | "delivered_full" | "returned";
  collectedByCourier?: number;
};

export function getInvoiceRemainingAmount(invoice: Pick<FinanceInvoice, "total" | "paid">): number {
  return invoice.total - invoice.paid;
}

export function isReturnedOrder(invoice: Pick<FinanceInvoice, "courierState">): boolean {
  return invoice.courierState === "returned";
}

export function getCustomerDebtForInvoice(invoice: FinanceInvoice): number {
  if (isReturnedOrder(invoice)) return 0;

  if (invoice.delivery === "direct") {
    return getInvoiceRemainingAmount(invoice);
  }

  const courierState = invoice.courierState ?? "pending";
  if (courierState === "delivered_none") return invoice.total;
  if (courierState === "delivered_partial")
    return invoice.total - (invoice.collectedByCourier ?? 0);

  return 0;
}

export function getCourierCustodyForInvoice(invoice: FinanceInvoice): number {
  if (isReturnedOrder(invoice) || invoice.delivery !== "courier") return 0;

  if (invoice.courierState === "delivered_partial" || invoice.courierState === "delivered_full") {
    return invoice.collectedByCourier ?? 0;
  }

  return 0;
}

export function getPendingCourierValueForInvoice(invoice: FinanceInvoice): number {
  if (isReturnedOrder(invoice) || invoice.delivery !== "courier") return 0;

  const courierState = invoice.courierState ?? "pending";
  return courierState === "pending" ? invoice.total : 0;
}

export function canCollectCustomerDebtForInvoice(invoice: FinanceInvoice): boolean {
  const customerDebt = getCustomerDebtForInvoice(invoice);
  if (customerDebt <= 0) return false;
  if (isReturnedOrder(invoice)) return false;

  if (invoice.delivery === "direct") return true;

  return invoice.courierState === "delivered_none" && getCourierCustodyForInvoice(invoice) === 0;
}

export function getInvoiceItemCost(item: FinanceInvoiceItem): number {
  return item.cost * item.qty;
}

export function getInvoiceItemMargin(invoice: Pick<FinanceInvoice, "items">): number {
  return invoice.items.reduce((sum, item) => sum + (item.price - item.cost) * item.qty, 0);
}

export function getInvoiceGrossMargin(invoice: Pick<FinanceInvoice, "total" | "items">): number {
  return invoice.total - invoice.items.reduce((sum, item) => sum + getInvoiceItemCost(item), 0);
}
