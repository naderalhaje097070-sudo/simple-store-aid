import { describe, expect, test } from "bun:test";
import {
  canCollectCustomerDebtForInvoice,
  getCourierCustodyForInvoice,
  getCustomerDebtForInvoice,
  getInvoiceGrossMargin,
  getInvoiceItemCost,
  getInvoiceItemMargin,
  getInvoiceRemainingAmount,
  getPendingCourierValueForInvoice,
  isReturnedOrder,
  type FinanceInvoice,
} from "../../src/domain/finance/invoice-selectors";

const direct = (overrides: Partial<FinanceInvoice> = {}): FinanceInvoice => ({
  items: [{ qty: 2, price: 50, cost: 30 }],
  total: 100,
  paid: 0,
  delivery: "direct",
  ...overrides,
});

const courier = (overrides: Partial<FinanceInvoice> = {}): FinanceInvoice => ({
  items: [{ qty: 2, price: 50, cost: 30 }],
  total: 100,
  paid: 0,
  delivery: "courier",
  courierState: "pending",
  ...overrides,
});

describe("invoice finance selectors", () => {
  test("direct fully paid has zero remaining debt", () => {
    const invoice = direct({ paid: 100 });
    expect(getInvoiceRemainingAmount(invoice)).toBe(0);
    expect(getCustomerDebtForInvoice(invoice)).toBe(0);
  });

  test("direct partially paid debt equals remaining", () => {
    const invoice = direct({ paid: 40 });
    expect(getInvoiceRemainingAmount(invoice)).toBe(60);
    expect(getCustomerDebtForInvoice(invoice)).toBe(60);
  });

  test("direct full debt equals total", () => {
    expect(getCustomerDebtForInvoice(direct({ paid: 0 }))).toBe(100);
  });

  test("returned direct order has no customer debt or courier custody", () => {
    const invoice = direct({ courierState: "returned" });
    expect(isReturnedOrder(invoice)).toBe(true);
    expect(getCustomerDebtForInvoice(invoice)).toBe(0);
    expect(getCourierCustodyForInvoice(invoice)).toBe(0);
  });

  test("courier pending is pending value, not customer debt", () => {
    const invoice = courier({ courierState: "pending" });
    expect(getPendingCourierValueForInvoice(invoice)).toBe(100);
    expect(getCustomerDebtForInvoice(invoice)).toBe(0);
  });

  test("courier delivered_none creates full customer debt", () => {
    expect(getCustomerDebtForInvoice(courier({ courierState: "delivered_none" }))).toBe(100);
  });

  test("courier delivered_partial creates debt for uncollected part", () => {
    expect(
      getCustomerDebtForInvoice(
        courier({ courierState: "delivered_partial", collectedByCourier: 35 }),
      ),
    ).toBe(65);
  });

  test("courier delivered_full creates no customer debt", () => {
    expect(
      getCustomerDebtForInvoice(
        courier({ courierState: "delivered_full", collectedByCourier: 100 }),
      ),
    ).toBe(0);
  });

  test("courier returned has no customer debt or courier custody", () => {
    const invoice = courier({ courierState: "returned", collectedByCourier: 100 });
    expect(isReturnedOrder(invoice)).toBe(true);
    expect(getCustomerDebtForInvoice(invoice)).toBe(0);
    expect(getCourierCustodyForInvoice(invoice)).toBe(0);
  });

  test("courier custody full equals collected money", () => {
    expect(
      getCourierCustodyForInvoice(
        courier({ courierState: "delivered_full", collectedByCourier: 100 }),
      ),
    ).toBe(100);
  });

  test("courier custody partial equals collected money", () => {
    expect(
      getCourierCustodyForInvoice(
        courier({ courierState: "delivered_partial", collectedByCourier: 35 }),
      ),
    ).toBe(35);
  });

  test("zero remaining stays zero", () => {
    expect(getInvoiceRemainingAmount(direct({ paid: 100 }))).toBe(0);
  });

  test("item cost is cost times quantity", () => {
    expect(getInvoiceItemCost({ qty: 3, price: 20, cost: 7 })).toBe(21);
  });

  test("gross margin is total minus item costs", () => {
    expect(
      getInvoiceGrossMargin(direct({ total: 100, items: [{ qty: 2, price: 50, cost: 30 }] })),
    ).toBe(40);
  });

  test("direct debt can be collected", () => {
    expect(canCollectCustomerDebtForInvoice(direct({ paid: 40 }))).toBe(true);
  });

  test("returned order cannot be collected", () => {
    expect(canCollectCustomerDebtForInvoice(direct({ courierState: "returned" }))).toBe(false);
  });

  test("courier pending cannot be collected", () => {
    expect(canCollectCustomerDebtForInvoice(courier({ courierState: "pending" }))).toBe(false);
  });

  test("courier delivered_none can be collected", () => {
    expect(canCollectCustomerDebtForInvoice(courier({ courierState: "delivered_none" }))).toBe(
      true,
    );
  });

  test("courier delivered_partial cannot be collected before settlement", () => {
    expect(
      canCollectCustomerDebtForInvoice(
        courier({ courierState: "delivered_partial", collectedByCourier: 35 }),
      ),
    ).toBe(false);
  });

  test("courier delivered_full cannot be collected", () => {
    expect(
      canCollectCustomerDebtForInvoice(
        courier({ courierState: "delivered_full", collectedByCourier: 100 }),
      ),
    ).toBe(false);
  });

  test("item margin uses price minus cost times quantity", () => {
    expect(getInvoiceItemMargin(direct({ items: [{ qty: 3, price: 20, cost: 7 }] }))).toBe(39);
  });

  test("gross margin and item margin remain separate concepts", () => {
    const invoice = direct({
      total: 90,
      items: [{ qty: 2, price: 50, cost: 30 }],
    });

    expect(getInvoiceGrossMargin(invoice)).toBe(30);
    expect(getInvoiceItemMargin(invoice)).toBe(40);
  });
});
