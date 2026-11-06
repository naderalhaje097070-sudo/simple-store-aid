import type { DBDayClose } from "@/lib/day-close-report";
import type { CollectionInput, CollectionResult } from "@/lib/collection-operation";
/* R2 — Shared AppCtx contract.
   Mirrors the `ctx` object literal built inside MongezzApp (src/routes/_authenticated/app.tsx).
   No behavior, no UI, no logic — type-only.

   `any` is used in a handful of places to mirror the existing ctx exactly
   (mutation inputs, lucide icon component, loose row passthroughs). Tightening
   them is out of R2 scope. */
/* eslint-disable @typescript-eslint/no-explicit-any */

import type { Dispatch, SetStateAction } from "react";
import type { FinancialRead } from "./financial-read-state";
import type {
  Product,
  Customer,
  Courier,
  Invoice,
  Expense,
  Payment,
  Screen,
  Period,
} from "./types";

/* ---------- Sub-shapes used by ctx ---------- */

export type AppTone = "warn" | "debt" | "info";

export type AppAlert = {
  id: string;
  tone: AppTone;
  // lucide-react icon component; loose on purpose to avoid coupling to lucide types.
  icon: any;
  text: string;
  onClick: () => void;
};

export type AppTotals = {
  sales: number;
  cogs: number;
  collected: number;
  expenseTotal: number;
  grossProfit: number;
  netProfit: number;
  realizedProfit: number;
  realizedCogs: number;
  realizedRevenue: number;
  customerDebts: number;
  unsettledCustody: number;
  inTransit: number;
  cashToday: number;
  openOnYou: number;
};

export type SaleSummary = {
  total: number;
  paid: number;
  profit: number;
  elapsedMs?: number;
};

export type DayCloseRow = DBDayClose;

export type TenantSettings =
  | {
      timezone?: string | null;
      [k: string]: any;
    }
  | null
  | undefined;

export type CourierState =
  | "pending"
  | "delivered_full"
  | "delivered_partial"
  | "delivered_none"
  | "returned";

/* ---------- AppCtx ---------- */

export interface AppCtx {
  /* Data */
  products: Product[];
  customers: Customer[];
  setCustomers: (_: any) => void;
  couriers: Courier[];
  invoices: Invoice[];
  expenses: Expense[];
  payments: Payment[];
  financialReads: Record<"invoices" | "payments" | "expenses", FinancialRead>;
  tenantTimezoneRead: FinancialRead;
  retryFinancialReads: () => Promise<unknown>;
  myRole: string | null | undefined;

  /* Derived totals */
  totals: AppTotals;
  rawTotals: AppTotals;
  lowStock: number;
  outStock: number;

  /* Period filter */
  period: Period;
  setPeriod: Dispatch<SetStateAction<Period>>;

  /* Alerts + day-close state */
  alerts: AppAlert[];
  closedToday: boolean | null;
  dayClosesRead: FinancialRead;
  setClosedToday: (b: boolean) => void;
  dayCloses: DayCloseRow[];

  /* Tenant */
  tenantId: string | null | undefined;
  tenantTz: string;
  todayKey: string;
  tenantSettings: TenantSettings;

  /* Mutations (loose Promise<any> to keep parity with current ctx) */
  closeDayAsync: (input: any) => Promise<any>;

  /* Navigation / screen state */
  go: (s: Screen) => void;
  back: () => void;
  goHome: () => void;
  setOpenInvoiceId: Dispatch<SetStateAction<string | null>>;
  openInvoiceId: string | null;
  setOpenCustomerId: Dispatch<SetStateAction<string | null>>;
  openCustomerId: string | null;
  setOpenCourierId: Dispatch<SetStateAction<string | null>>;
  openCourierId: string | null;
  setLastSaleSummary: Dispatch<SetStateAction<SaleSummary | null>>;
  lastSaleSummary: SaleSummary | null;
  setScreen: Dispatch<SetStateAction<Screen>>;
  lastCreatedInvoiceId: string | null;
  setLastCreatedInvoiceId: Dispatch<SetStateAction<string | null>>;

  /* UI toggles */
  setQuickExpenseOpen: Dispatch<SetStateAction<boolean>>;
  setMoneyDetailsOpen: Dispatch<SetStateAction<boolean>>;
  showToast: (t: string) => void;

  /* Catalog + customer + courier mutations */
  addCustomerAsync: (input: { name: string; phone?: string }) => Promise<any>;
  addProductAsync: (input: {
    name: string;
    price: number;
    cost: number;
    stock: number;
    is_discount: boolean;
  }) => Promise<any>;
  toggleProductActiveAsync: (input: { id: string; is_active: boolean }) => Promise<any>;
  updateProductAsync: (input: {
    id: string;
    name: string;
    price: number;
    cost: number;
    stock: number;
    is_discount: boolean;
  }) => Promise<any>;
  deleteProductAsync: (productId: string) => Promise<any>;
  addCourierAsync: (input: { name: string; phone?: string }) => Promise<any>;
  addExpenseAsync: (input: {
    type: string;
    amount: number;
    method: "cash" | "transfer";
    note?: string;
  }) => Promise<any>;

  /* Financial mutations */
  createSaleAsync: (input: any) => Promise<any>;
  deleteInvoiceAsync: (orderId: string) => Promise<any>;
  collectDebtAsync: (input: CollectionInput) => Promise<CollectionResult>;
  settleCourierAsync: (input: {
    courierId: string;
    orders: { id: string; customerId?: string; collected?: number }[];
  }) => Promise<any>;
  updateCourierStateAsync: (input: {
    orderId: string;
    state: CourierState;
    collected?: number;
  }) => Promise<any>;
}
