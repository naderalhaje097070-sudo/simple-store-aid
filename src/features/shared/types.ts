// Extracted from src/routes/_authenticated/app.tsx (R1) — no logic changes.

export type Product = {
  id: string;
  name: string;
  price: number;
  cost: number;
  stock: number;
  lowAt: number;
  is_discount?: boolean;
  is_active?: boolean;
};
export type Customer = { id: string; name: string; phone?: string };
export type Courier = { id: string; name: string; phone?: string };
export type InvoiceItem = {
  productId: string;
  name: string;
  qty: number;
  price: number;
  cost: number;
};
export type Invoice = {
  id: string;
  number: string;
  items: InvoiceItem[];
  total: number;
  paid: number;
  customerId?: string;
  delivery: "direct" | "courier";
  courierId?: string;
  status: "paid" | "partial" | "debt";
  courierState?: "pending" | "delivered_none" | "delivered_partial" | "delivered_full" | "returned";
  collectedByCourier?: number;
  time: string;
  createdAt: string;
};
export type Expense = {
  id: string;
  type: string;
  amount: number;
  method: "cash" | "transfer";
  time: string;
  createdAt: string;
  note?: string;
};
export type Payment = {
  id: string;
  kind: "sale" | "debt_collection" | "settlement";
  method: "cash" | "transfer" | "settlement";
  amount: number;
  invoiceId?: string;
  invoiceNumber?: string;
  customerId?: string;
  courierId?: string;
  time: string;
  createdAt: string;
};

export type Screen =
  | "home"
  | "invoices"
  | "invoice_detail"
  | "inventory"
  | "shop"
  | "profit"
  | "collected"
  | "debts"
  | "debt_customer"
  | "courier_custody"
  | "settlements"
  | "expenses"
  | "customers"
  | "couriers"
  | "settings"
  | "sale"
  | "sale_quick"
  | "sale_success"
  | "day_close"
  | "pilot";

export type Period = "day" | "week" | "month";
