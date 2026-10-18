const fs = require("node:fs");
const cp = require("node:child_process");
const assert = require("node:assert/strict");
const ts = require("typescript");
const parser = require("@babel/parser");

const baseline = "d0a172e7060a5a8a782a923f42986ac7d6287bab";
const files = [
  "src/lib/db.ts",
  "src/lib/invoice-pdf.ts",
  "src/lib/paddle.ts",
  "src/features/invoices/InvoiceDetailScreen.tsx",
  "src/features/shared/types.ts",
  "src/routes/_authenticated/app.tsx",
  "src/routes/_authenticated/billing.tsx",
  "src/routes/api/public/payments/webhook.ts",
  "src/routes/lovable/email/queue/process.ts",
];
const metadata = new Set(["start", "end", "loc", "extra", "comments", "tokens", "leadingComments", "trailingComments", "innerComments"]);
function emit(source, file) {
  return ts.transpileModule(source, {
    fileName: file,
    compilerOptions: { target: ts.ScriptTarget.ESNext, module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.React, removeComments: true },
  }).outputText;
}
function ast(source) {
  return parser.parse(source, { sourceType: "module" });
}
const counters = { clientAlias: 0, nullGuard: 0, messageAlias: 0, messageRename: 0 };
function canon(value, file, revised) {
  if (Array.isArray(value)) return value.map((x) => canon(x, file, revised)).filter((x) => x !== undefined);
  if (!value || typeof value !== "object") return value;
  if (revised && file === "src/lib/db.ts") {
    if (value.type === "VariableDeclaration" && value.declarations.length === 1) {
      const d = value.declarations[0];
      if (d.id.name === "rpcClient" && d.init.type === "Identifier" && d.init.name === "supabase") {
        counters.clientAlias++;
        return undefined;
      }
    }
    if (value.type === "IfStatement" && value.test.type === "BinaryExpression" && value.test.operator === "===" && value.test.left.name === "data" && value.test.right.type === "NullLiteral" && !value.alternate) {
      const t = value.consequent;
      assert.equal(t.type, "ThrowStatement");
      assert.equal(t.argument.type, "NewExpression");
      assert.equal(t.argument.callee.name, "TypeError");
      assert.equal(t.argument.arguments.length, 1);
      assert(["get_tenant_today_estimate returned no result", "create_sale_with_items returned no result"].includes(t.argument.arguments[0].value));
      counters.nullGuard++;
      return undefined;
    }
    if (value.type === "Identifier" && value.name === "rpcClient") return { type: "Identifier", name: "supabase" };
  }
  if (revised && file === "src/routes/lovable/email/queue/process.ts") {
    if (value.type === "VariableDeclaration" && value.declarations.length === 1) {
      const d = value.declarations[0];
      if (d.id.name === "messages" && d.init.type === "Identifier" && d.init.name === "rawMessages") {
        counters.messageAlias++;
        return undefined;
      }
    }
    if (value.type === "Identifier" && value.name === "rawMessages") {
      counters.messageRename++;
      return { type: "Identifier", name: "messages" };
    }
  }
  return Object.fromEntries(Object.entries(value).filter(([key]) => !metadata.has(key)).map(([key, item]) => [key, canon(item, file, revised)]));
}
const sources = new Map();
for (const file of files) {
  const before = cp.execFileSync("git", ["show", `${baseline}:${file}`], { encoding: "utf8" });
  const after = fs.readFileSync(file, "utf8");
  const a = emit(before, file), b = emit(after, file);
  assert.deepEqual(canon(ast(a), file, false), canon(ast(b), file, true), file);
  sources.set(file, { before: a, after: b });
}
assert.deepEqual(counters, { clientAlias: 1, nullGuard: 2, messageAlias: 1, messageRename: 1 });

// Execute the original query/mutation callbacks with a recording client. No
// network or database exists in this contract replay; calls and values are real
// application callbacks, while storage/authorization acceptance remains separate.
function callbacks(source, response) {
  const calls = [];
  const client = { rpc: async (name, args) => { calls.push({ name, args }); return response; } };
  const code = source.replace(/^import[^;]+;\n/gm, "").replace(/^export /gm, "");
  const run = new Function("supabase", "useQuery", "useMutation", "useQueryClient", code + "\nreturn { useTenantTodayEstimate, useCreateSale, useDeleteProduct }; ");
  return { api: run(client, (x) => x, (x) => x, () => ({ invalidateQueries() {} })), calls };
}
async function scenario(kind, data, error) {
  const outcomes = [];
  for (const version of ["before", "after"]) {
    const instance = callbacks(sources.get("src/lib/db.ts")[version], { data, error: error ?? null });
    try {
      let value;
      if (kind === "today") value = await instance.api.useTenantTodayEstimate("tenant-fixture").queryFn();
      if (kind === "sale") value = await instance.api.useCreateSale("tenant-fixture").mutationFn({ items: [{ productId: "product-fixture", name: "dummy", qty: 2, price: 50, cost: 20 }], total: 100, paid: 40, customerId: "customer-fixture", delivery: "direct", method: "cash" });
      if (kind === "product") value = await instance.api.useDeleteProduct("tenant-fixture").mutationFn("product-fixture");
      outcomes.push({ value, calls: instance.calls });
    } catch (failure) {
      outcomes.push({ errorName: failure.name, errorMessage: failure.message, calls: instance.calls });
    }
  }
  assert.deepEqual(outcomes[0].calls, outcomes[1].calls);
  if (data === null && !error && (kind === "today" || kind === "sale")) {
    assert.equal(outcomes[0].errorName, "TypeError");
    assert.equal(outcomes[1].errorName, "TypeError");
    assert.match(outcomes[1].errorMessage, /returned no result$/);
  } else assert.deepEqual(outcomes[0], outcomes[1]);
  return outcomes[1];
}
(async () => {
  const today = await scenario("today", { today: "2026-10-18", timezone: "Africa/Tripoli", sales: 100, collected: 40, expenses: 5, realized_profit: 12 });
  assert.deepEqual(today.value, { today: "2026-10-18", timezone: "Africa/Tripoli", sales: 100, collected: 40, expenses: 5, realizedProfit: 12 });
  await scenario("today", null);
  await scenario("today", null, { message: "fixture_error" });
  const sale = await scenario("sale", { success: true, order_id: "order-fixture", number: 11 });
  assert.deepEqual(sale.value, { orderId: "order-fixture", number: "11" });
  assert.deepEqual(sale.calls, [{ name: "create_sale_with_items", args: { p_customer_id: "customer-fixture", p_delivery: "direct", p_courier_id: null, p_paid: 40, p_method: "cash", p_items: [{ productId: "product-fixture", qty: 2 }] } }]);
  await scenario("sale", null);
  await scenario("sale", null, { message: "forbidden_tenant" });
  await scenario("product", { deleted: true });
  await scenario("product", { archived: true, used_in: 2 });
  await scenario("product", null);
  await scenario("product", null, { message: "forbidden_role" });
  // A financial wire mutation must remain observable to the same AST comparator.
  const original = sources.get("src/lib/db.ts").before;
  const changed = original.replace("p_paid: input.paid", "p_paid: input.paid + 1");
  assert.notEqual(changed, original);
  assert.notDeepEqual(canon(ast(original), "src/lib/db.ts", false), canon(ast(changed), "src/lib/db.ts", false));
  console.log(JSON.stringify({ files: files.length, intentionalAliasesAndGuards: counters, callbackScenarios: 10, negativeWireMutation: true, databaseOrProviderCalls: 0 }));
})().catch((error) => { console.error(error); process.exitCode = 1; });
