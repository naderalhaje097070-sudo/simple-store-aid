import { test } from "node:test";
import assert from "node:assert/strict";
import { decodeDayCloseReport, decodeDayCloseReports } from "../../src/lib/day-close-report.ts";
import {
  financialReadState,
  requireFinancialReads,
} from "../../src/features/shared/financial-read-state.ts";

const row = {
  id: "saved-close",
  tenant_id: "tenant-a",
  closed_for: "2026-11-06",
  sales: 275,
  collected: 225,
  expenses: 5,
  realized_profit: 135,
  realized_margin_before_expenses: 135,
  realized_net_profit: 130,
  customer_debts: 0,
  unsettled_custody: 0,
  note: null,
  created_at: "2026-11-06T10:00:00Z",
};

test("retains legacy margin and consumes server net without another expense subtraction", () => {
  const result = decodeDayCloseReport(row);
  assert.equal(result.realizedProfit, 135);
  assert.equal(result.realizedMarginBeforeExpenses, 135);
  assert.equal(result.realizedNetProfit, 130);
  assert.equal(result.expenses, 5);
});

test("negative and decimal server net pass through without clamping or rounding", () => {
  assert.equal(decodeDayCloseReport({ ...row, realized_net_profit: -15 }).realizedNetProfit, -15);
  assert.equal(
    decodeDayCloseReport({ ...row, realized_net_profit: 1.228 }).realizedNetProfit,
    1.228,
  );
});

test("required nullable report values never silently become zero or an empty identity", () => {
  for (const field of [
    "id",
    "closed_for",
    "created_at",
    "sales",
    "collected",
    "expenses",
    "realized_profit",
    "realized_margin_before_expenses",
    "realized_net_profit",
    "customer_debts",
    "unsettled_custody",
  ]) {
    assert.throws(() => decodeDayCloseReport({ ...row, [field]: null }));
  }
  for (const value of [NaN, Infinity, -Infinity]) {
    assert.throws(() => decodeDayCloseReport({ ...row, realized_net_profit: value }));
  }
});

test("missing and errored view reads are unavailable; cached refreshing reads cannot authorize close", () => {
  const pending = financialReadState(
    {
      data: undefined,
      status: "pending",
      fetchStatus: "fetching",
      isPlaceholderData: false,
    },
    true,
    false,
  );
  const failed = financialReadState(
    {
      data: undefined,
      status: "error",
      fetchStatus: "idle",
      isPlaceholderData: false,
    },
    true,
    false,
  );
  const cached = financialReadState(
    {
      data: [row],
      status: "success",
      fetchStatus: "fetching",
      isPlaceholderData: false,
    },
    true,
    false,
  );
  for (const read of [pending, failed, cached]) {
    assert.equal(read.complete, false);
    assert.throws(() => requireFinancialReads([read]));
  }
  assert.equal(pending.hasData, false);
  assert.equal(failed.hasData, false);
  assert.equal(cached.hasData, true);
  const empty = financialReadState(
    {
      data: [],
      status: "success",
      fetchStatus: "idle",
      isPlaceholderData: false,
    },
    true,
    false,
  );
  assert.equal(empty.complete, true);
  requireFinancialReads([empty]);
});

test("missing report collection is an error; a successful empty collection remains valid", () => {
  assert.throws(() => decodeDayCloseReports(null));
  assert.deepEqual(decodeDayCloseReports([]), []);
  assert.equal(decodeDayCloseReports([row])[0].realizedNetProfit, 130);
});
