import assert from "node:assert/strict";
import { writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { pathToFileURL } from "node:url";
import process from "node:process";

const directory = process.argv[2];
if (!directory) throw new Error("Usage: node tests/app-financial-read/replay.mjs OUTPUT");
const { render } = await import(pathToFileURL(resolve(directory, "server.cjs")));
const results = [];
const warning =
  /تعذّر تحميل البيانات المالية|جارٍ تحميل البيانات المالية|جارٍ تحديث البيانات المالية/;
async function check(name, run) {
  try {
    await run();
    results.push({ name, passed: true });
  } catch (error) {
    results.push({ name, passed: false, error: String(error) });
  }
}
await check("initial loading never claims healthy zero", () => {
  const { html } = render({
    reads: { invoices: "missing", payments: "missing", expenses: "missing" },
  });
  assert.match(html, warning);
  assert.doesNotMatch(html, /وضعك اليوم: جيد/);
});
for (const key of ["invoices", "payments", "expenses"]) {
  await check(`${key} error blocks fabricated profit`, () => {
    const { html } = render({ screen: "profit", reads: { [key]: "error" } });
    assert.match(html, warning);
    assert.doesNotMatch(html, /class="num font-semibold">0</);
  });
}
for (const [screen, key, healthy] of [
  ["debts", "invoices", "لا ديون مستحقة"],
  ["collected", "payments", "لا حركات في هذا النطاق"],
  ["expenses", "expenses", "لا توجد مصروفات في هذا النطاق"],
]) {
  await check(`${screen} missing read cannot claim empty success`, () => {
    const { html } = render({ screen, reads: { [key]: "error" } });
    assert.match(html, warning);
    assert.ok(!html.includes(healthy));
  });
}
await check("cached debt60 survives failure and dependent writes are rejected", async () => {
  const { html, ctx, effects } = render({ screen: "debts", reads: { invoices: "cached-error" } });
  assert.match(html, warning);
  assert.match(html, />60</);
  await assert.rejects(() =>
    ctx.collectDebtAsync({ orderId: "invoice-fixture", amount: 1, method: "cash" }),
  );
  await assert.rejects(() => ctx.settleCourierAsync({ courierId: "courier-fixture", orders: [] }));
  await assert.rejects(() =>
    ctx.updateCourierStateAsync({ orderId: "invoice-fixture", state: "returned" }),
  );
  await assert.rejects(() => ctx.closeDayAsync({}));
  assert.deepEqual(effects, []);
});
await check("partial recovery preserves independently complete debt60", async () => {
  const { html, ctx, effects } = render({ screen: "debts", reads: { payments: "error" } });
  assert.match(html, />60</);
  assert.doesNotMatch(html, warning);
  await ctx.collectDebtAsync({ orderId: "invoice-fixture", amount: 1, method: "cash" });
  assert.equal(effects[0][0], "useCollectDebt");
  await assert.rejects(() => ctx.closeDayAsync({}));
});
await check("complete successful empty reads retain genuine zero/no debt", () => {
  const { html } = render({ screen: "debts", empty: true });
  assert.match(html, /لا ديون مستحقة/);
  assert.match(html, />0</);
  assert.doesNotMatch(html, warning);
});
await check("complete known nonempty debt remains60", () => {
  const { html } = render({ screen: "debts" });
  assert.match(html, />60</);
  assert.doesNotMatch(html, warning);
});
await check("cached empty error is not reassuring no debt", () => {
  const { html } = render({ screen: "debts", empty: true, reads: { invoices: "cached-error" } });
  assert.match(html, warning);
  assert.doesNotMatch(html, /لا ديون مستحقة/);
});
await check("placeholder and tenant-unavailable reads are not current balances", () => {
  for (const spec of [
    { reads: { invoices: "placeholder" } },
    { tenantMissing: true },
    { tenantMissing: true, tenantError: true },
  ]) {
    const { html } = render({ screen: "debts", ...spec });
    assert.match(html, warning);
    assert.doesNotMatch(html, />60</);
  }
});
await check("safe independent writes remain available during read failure", async () => {
  const { ctx, effects } = render({
    reads: { invoices: "error", payments: "error", expenses: "error" },
  });
  await ctx.addExpenseAsync({ type: "نقل", amount: 1, method: "cash" });
  await ctx.addCustomerAsync({ name: "Synthetic" });
  await ctx.createSaleAsync({ items: [], total: 1, paid: 1, delivery: "direct", method: "cash" });
  assert.deepEqual(
    effects.map((x) => x[0]),
    ["useAddExpense", "useAddCustomer", "useCreateSale"],
  );
});
await check("customer metadata absence still retains debt60", () => {
  const { html } = render({ screen: "debts", customerMissing: true });
  assert.match(html, />60</);
  assert.match(html, /بيانات العميل غير متاحة/);
  assert.match(html, /disabled/);
});
await check("cached refreshing balances are explicitly incomplete", async () => {
  const { html, ctx } = render({ screen: "debts", reads: { invoices: "refreshing" } });
  assert.match(html, warning);
  assert.match(html, />60</);
  await assert.rejects(() => ctx.closeDayAsync({}));
});
for (const screen of [
  "invoices",
  "invoice_detail",
  "debt_customer",
  "courier_custody",
  "settlements",
  "day_close",
]) {
  await check(`${screen} does not render finance when invoice read is absent`, () => {
    const { html } = render({ screen, reads: { invoices: "error" } });
    assert.match(html, warning);
    assert.match(html, /الملخص المالي غير متاح/);
  });
}
await check("cached tenant-resolution error invalidates dependent actions", async () => {
  const { html, ctx, effects } = render({ screen: "debts", tenantError: true });
  assert.match(html, warning);
  assert.match(html, />60</);
  await assert.rejects(() =>
    ctx.collectDebtAsync({ orderId: "invoice-fixture", amount: 1, method: "cash" }),
  );
  assert.deepEqual(effects, []);
});
for (const mode of ["error", "cached-error", "missing", "refreshing"]) {
  await check(`money sheet ${mode} keeps the warning inside the sheet`, () => {
    const { detailHtml } = render({ moneyDetails: true, reads: { payments: mode } });
    assert.match(detailHtml, warning);
    assert.match(detailHtml, /حركة اليوم المالية/);
    if (mode === "error" || mode === "missing") assert.doesNotMatch(detailHtml, /المحصّل فعلًا/);
  });
}
await check("invoice payment-read error blocks exports but not independent collection", () => {
  const { detailHtml } = render({ invoiceDetail: true, reads: { payments: "error" } });
  assert.match(detailHtml, warning);
  assert.match(detailHtml, /<button[^>]*disabled=""[^>]*>[\s\S]*?تحميل PDF/);
  assert.match(detailHtml, /<button disabled=""[^>]*>[\s\S]*?طباعة/);
  assert.match(detailHtml, /<button class="w-full rounded-2xl bg-primary[^>]*>تحصيل دفعة/);
});
await check("complete invoice permits both export buttons", () => {
  const { detailHtml } = render({ invoiceDetail: true });
  assert.doesNotMatch(detailHtml, /disabled=""/);
  assert.match(detailHtml, /تحميل PDF/);
  assert.match(detailHtml, /طباعة/);
});
for (const screen of ["customers", "couriers"]) {
  await check(`${screen} keeps directory available without a fabricated balance`, () => {
    const { html } = render({ screen, reads: { invoices: "error" } });
    assert.match(html, warning);
    assert.match(html, screen === "customers" ? /عميل تجريبي/ : /مندوب تجريبي/);
    assert.doesNotMatch(html, /class="[^"]*text-success[^"]*">لا دين/);
  });
}
await check("retry uses the existing read queries", async () => {
  const { ctx, effects } = render({ reads: { payments: "error" } });
  await ctx.retryFinancialReads();
  assert.deepEqual(effects, [
    ["refetch", "invoices"],
    ["refetch", "payments"],
    ["refetch", "expenses"],
    ["refetch", "settings"],
    ["refetch", "dayCloses"],
  ]);
});
await check("missing tenant retry resolves tenant before financial reads", async () => {
  const { ctx, effects } = render({ tenantMissing: true });
  await ctx.retryFinancialReads();
  assert.deepEqual(effects, [["refetch", "tenant"]]);
});
await check("cached tenant-resolution failure retries tenant first", async () => {
  const { ctx, effects } = render({ tenantError: true });
  await ctx.retryFinancialReads();
  assert.deepEqual(effects, [["refetch", "tenant"]]);
});
for (const mode of ["missing", "error", "paused", "placeholder"]) {
  await check(`timezone ${mode} cannot authorize daily summary or close`, async () => {
    const { html, ctx, effects } = render({ settingsRead: mode });
    assert.match(html, warning);
    assert.doesNotMatch(html, /وضعك اليوم: جيد/);
    assert.match(html, /غير متاح/);
    await assert.rejects(() => ctx.closeDayAsync({}));
    assert.deepEqual(effects, []);
    for (const screen of ["profit", "day_close"]) {
      const view = render({ screen, settingsRead: mode });
      assert.match(view.html, /الملخص المالي غير متاح/);
    }
  });
}
await check("cached timezone failure retains known daily amounts and denies close", async () => {
  const { html, ctx, effects } = render({ settingsRead: "cached-error" });
  assert.match(html, warning);
  assert.match(html, />40</);
  assert.equal(ctx.totals.collected, 40);
  await assert.rejects(() => ctx.closeDayAsync({}));
  assert.deepEqual(effects, []);
});
await check("timezone read failure preserves independent debts and collection", async () => {
  const { html, ctx, effects } = render({ screen: "debts", settingsRead: "error" });
  assert.match(html, />60</);
  assert.doesNotMatch(html, warning);
  await ctx.collectDebtAsync({ orderId: "invoice-fixture", amount: 1, method: "cash" });
  assert.equal(effects[0][0], "useCollectDebt");
  await assert.rejects(() => ctx.closeDayAsync({}));
});
await check("successful nullable timezone retains approved default", () => {
  const { html, ctx } = render({ timezone: null });
  assert.equal(ctx.tenantTz, "Africa/Tripoli");
  assert.equal(ctx.tenantTimezoneRead.complete, true);
  assert.doesNotMatch(html, warning);
});
await check("timezone failure retries the settings query", async () => {
  const { ctx, effects } = render({ settingsRead: "error" });
  await ctx.retryFinancialReads();
  assert.ok(effects.some(([kind, query]) => kind === "refetch" && query === "settings"));
});
await check("pilot unavailable timezone is a read boundary rather than a render error", () => {
  for (const mode of ["missing", "error", "paused", "placeholder"]) {
    const { html } = render({ screen: "pilot", settingsRead: mode });
    assert.match(html, /الملخص المالي غير متاح/);
  }
  const cached = render({ screen: "pilot", settingsRead: "cached-error" });
  assert.match(cached.html, warning);
});
writeFileSync(
  resolve(directory, "replay.json"),
  JSON.stringify(
    {
      results,
      passed: results.filter((r) => r.passed).length,
      total: results.length,
      scope:
        "Actual parent and rendered React screens, synthetic reads/mutation transport; no database/provider/browser",
    },
    null,
    2,
  ) + "\n",
);
console.log(JSON.stringify(results, null, 2));
if (results.some((r) => !r.passed)) process.exitCode = 1;
