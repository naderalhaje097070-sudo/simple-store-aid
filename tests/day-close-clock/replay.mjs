import assert from "node:assert/strict";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import process from "node:process";
import ts from "typescript";

const out = process.argv[2];
if (!out) throw Error("Output required");
mkdirSync(out, { recursive: true });
const source = readFileSync("src/routes/_authenticated/app.tsx", "utf8");
const ast = ts.createSourceFile("app.tsx", source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const declaration = (name) => {
  const n = ast.statements.find((n) => ts.isFunctionDeclaration(n) && n.name?.text === name);
  if (!n) throw Error("Missing " + name);
  return n.getText(ast);
};
function compile(code, bindings) {
  const js = ts.transpile(code, {
    target: ts.ScriptTarget.ES2022,
    module: ts.ModuleKind.CommonJS,
    jsx: ts.JsxEmit.ReactJSX,
  });
  return new Function(...Object.keys(bindings), js)(...Object.values(bindings));
}
const realDate = Date;
let now = Date.parse("2026-10-19T03:00:00Z");
class FixtureDate extends realDate {
  constructor(...args) {
    super(...(args.length ? args : [now]));
  }
  static now() {
    return now;
  }
}
function hooks() {
  const memos = [],
    states = [],
    effects = [],
    refs = [];
  let mi = 0,
    si = 0,
    ei = 0,
    ri = 0;
  return {
    reset() {
      mi = si = ei = ri = 0;
    },
    effects,
    useMemo(fn, deps) {
      const i = mi++;
      if (!memos[i] || deps.some((d, j) => !Object.is(d, memos[i].deps[j])))
        memos[i] = { deps, value: fn() };
      return memos[i].value;
    },
    useState(initial) {
      const i = si++;
      if (!(i in states)) states[i] = typeof initial === "function" ? initial() : initial;
      return [
        states[i],
        (value) => {
          states[i] = typeof value === "function" ? value(states[i]) : value;
        },
      ];
    },
    useEffect(fn, deps) {
      const i = ei++;
      if (!effects[i] || deps.some((d, j) => !Object.is(d, effects[i].deps[j]))) {
        effects[i]?.cleanup?.();
        effects[i] = { deps, cleanup: fn() };
      }
    },
    useRef(value) {
      const i = ri++;
      return refs[i] ?? (refs[i] = { current: value });
    },
  };
}
const fm = { exports: {} };
compile(readFileSync("src/domain/finance/invoice-selectors.ts", "utf8"), {
  module: fm,
  exports: fm.exports,
});
const dbSource = readFileSync("src/lib/db.ts", "utf8");
const dbAst = ts.createSourceFile("db.ts", dbSource, ts.ScriptTarget.Latest, true);
const todayNode = dbAst.statements.find(
  (n) => ts.isFunctionDeclaration(n) && n.name?.text === "tenantTodayKey",
);
const tm = { exports: {} };
compile(todayNode.getText(dbAst), { module: tm, exports: tm.exports, Date: FixtureDate });
const invoice = {
  id: "invoice",
  items: [{ qty: 1, price: 100, cost: 25 }],
  total: 100,
  paid: 40,
  delivery: "direct",
  customerId: "customer",
  createdAt: "2026-10-18T23:00:00Z",
};
const invoices = [invoice],
  payments = [{ id: "payment", invoiceId: "invoice", amount: 40, createdAt: invoice.createdAt }],
  expenses = [{ amount: 10, createdAt: invoice.createdAt }];
const empty = [];
let timezone = "UTC";
const timers = [];
const h = hooks();
const bindings = {
  ...h,
  ...fm.exports,
  Date: FixtureDate,
  tenantTodayKey: tm.exports.tenantTodayKey,
  setInterval: (fn) => {
    timers.push(fn);
    return timers.length;
  },
  clearInterval() {},
  window: { addEventListener() {}, removeEventListener() {} },
  financialReadState: (q) => ({ hasData: true, complete: true, phase: "ready" }),
  tenantTimezoneReadState: () => ({ hasData: true, complete: true, phase: "ready" }),
  useTenantId: () => ({ data: "synthetic", isError: false }),
  useProducts: () => ({ data: empty }),
  useCustomers: () => ({ data: empty, isLoading: false }),
  useCouriers: () => ({ data: empty }),
  useInvoices: () => ({ data: invoices }),
  usePayments: () => ({ data: payments }),
  useExpenses: () => ({ data: expenses }),
  useTenant: () => ({ data: { timezone } }),
  useDayCloses: () => ({ data: empty }),
  useMyRole: () => ({ data: "owner" }),
};
for (const name of [...source.matchAll(/\b(use[A-Z]\w+)\(tenantId\)/g)].map((x) => x[1]))
  if (!bindings[name])
    bindings[name] = () => ({
      mutateAsync() {
        throw Error("Mutation forbidden");
      },
    });
const appPrefix =
  declaration("MongezzApp").split("  const scaledTotals = totals;")[0] +
  "\nreturn {totals,todayKey,periodStart};}";
const parent = compile(appPrefix + ";return MongezzApp;", bindings);
const dh = hooks();
const dayPrefix = declaration("DayCloseScreen").split("  const Row =")[0] + "\nreturn t;}";
const day = compile(dayPrefix + ";return DayCloseScreen;", {
  ...dh,
  Date: FixtureDate,
  tenantTodayKey: tm.exports.tenantTodayKey,
  ...fm.exports,
});
const renderParent = () => {
  h.reset();
  return parent();
};
const renderDay = (props) => {
  dh.reset();
  return day(props);
};
const results = [];
async function check(name, run) {
  try {
    await run();
    results.push({ name, passed: true });
  } catch (e) {
    results.push({ name, passed: false, error: String(e) });
  }
}
await check("parent timezone-only refresh recomputes stable financial arrays", () => {
  timezone = "UTC";
  assert.equal(renderParent().totals.sales, 0);
  timezone = "America/Los_Angeles";
  assert.equal(renderParent().totals.sales, 100);
});
await check("day-close timezone-only refresh recomputes stable props", () => {
  const totals = { customerDebts: 60, unsettledCustody: 0 };
  const props = {
    invoices,
    payments,
    expenses,
    rawTotals: totals,
    totals,
    tenantTz: "UTC",
    todayKey: "2026-10-19",
  };
  assert.equal(renderDay(props).sales, 0);
  const t = renderDay({ ...props, tenantTz: "America/Los_Angeles", todayKey: "2026-10-18" });
  assert.equal(t.sales, 100);
  assert.equal(t.collected, 40);
  assert.equal(t.expenseTotal, 10);
  assert.equal(t.cashToday, 30);
});
await check("clock invalidates parent day at rollover without financial refetch", () => {
  timezone = "UTC";
  now = Date.parse("2026-10-18T23:59:59Z");
  for (const tick of timers) tick();
  assert.equal(renderParent().totals.sales, 100);
  now = Date.parse("2026-10-19T00:00:01Z");
  for (const tick of timers) tick();
  const p = renderParent();
  assert.equal(p.todayKey, "2026-10-19");
  assert.equal(p.totals.sales, 0);
});
await check("day-close same timezone new day invalidates preview", () => {
  const totals = { customerDebts: 60, unsettledCustody: 0 };
  const props = {
    invoices,
    payments,
    expenses,
    rawTotals: totals,
    totals,
    tenantTz: "UTC",
    todayKey: "2026-10-18",
  };
  now = Date.parse("2026-10-18T23:59:59Z");
  assert.equal(renderDay(props).cashToday, 30);
  now = Date.parse("2026-10-19T00:00:01Z");
  assert.equal(renderDay({ ...props, todayKey: "2026-10-19" }).cashToday, 0);
});
writeFileSync(
  resolve(out, "clock.json"),
  JSON.stringify(
    {
      results,
      passed: results.filter((r) => r.passed).length,
      total: results.length,
      scope:
        "Actual parent and DayClose memo bodies with persistent Object.is hook fixture, stable arrays, synthetic clock; no browser/database close RPC",
    },
    null,
    2,
  ) + "\n",
);
console.log(JSON.stringify(results, null, 2));
if (results.some((r) => !r.passed)) process.exitCode = 1;
