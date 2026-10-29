const fs = require("node:fs");
const cp = require("node:child_process");
const assert = require("node:assert/strict");
const ts = require("typescript");
const parser = require("@babel/parser");
const {
  historicalWebhookSource,
} = require("../b-dependency/webhook-bridge.cjs");
const { historicalQuantitySource } = require("../c-source/quantity-bridge.cjs");

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
const metadata = new Set([
  "start",
  "end",
  "loc",
  "extra",
  "comments",
  "tokens",
  "leadingComments",
  "trailingComments",
  "innerComments",
]);
function emit(source, file) {
  return ts.transpileModule(source, {
    fileName: file,
    compilerOptions: {
      target: ts.ScriptTarget.ESNext,
      module: ts.ModuleKind.ESNext,
      jsx: ts.JsxEmit.React,
      removeComments: true,
    },
  }).outputText;
}
function ast(source) {
  return parser.parse(source, { sourceType: "module" });
}
const counters = {
  clientAlias: 0,
  nullGuard: 0,
  messageAlias: 0,
  messageRename: 0,
};
function canon(value, file, revised) {
  if (Array.isArray(value))
    return value
      .map((x) => canon(x, file, revised))
      .filter((x) => x !== undefined);
  if (!value || typeof value !== "object") return value;
  if (revised && file === "src/lib/db.ts") {
    if (
      value.type === "VariableDeclaration" &&
      value.declarations.length === 1
    ) {
      const d = value.declarations[0];
      if (
        d.id.name === "rpcClient" &&
        d.init.type === "Identifier" &&
        d.init.name === "supabase"
      ) {
        counters.clientAlias++;
        return undefined;
      }
    }
    if (
      value.type === "IfStatement" &&
      value.test.type === "BinaryExpression" &&
      value.test.operator === "===" &&
      value.test.left.name === "data" &&
      value.test.right.type === "NullLiteral" &&
      !value.alternate
    ) {
      const t = value.consequent;
      assert.equal(t.type, "ThrowStatement");
      assert.equal(t.argument.type, "NewExpression");
      assert.equal(t.argument.callee.name, "TypeError");
      assert.equal(t.argument.arguments.length, 1);
      assert(
        [
          "get_tenant_today_estimate returned no result",
          "create_sale_with_items returned no result",
        ].includes(t.argument.arguments[0].value),
      );
      counters.nullGuard++;
      return undefined;
    }
    if (value.type === "Identifier" && value.name === "rpcClient")
      return { type: "Identifier", name: "supabase" };
  }
  if (revised && file === "src/routes/lovable/email/queue/process.ts") {
    if (
      value.type === "VariableDeclaration" &&
      value.declarations.length === 1
    ) {
      const d = value.declarations[0];
      if (
        d.id.name === "messages" &&
        d.init.type === "Identifier" &&
        d.init.name === "rawMessages"
      ) {
        counters.messageAlias++;
        return undefined;
      }
    }
    if (value.type === "Identifier" && value.name === "rawMessages") {
      counters.messageRename++;
      return { type: "Identifier", name: "messages" };
    }
  }
  return Object.fromEntries(
    Object.entries(value)
      .filter(([key]) => !metadata.has(key))
      .map(([key, item]) => [key, canon(item, file, revised)]),
  );
}
// These declarations now intentionally change behavior (APP-01/03/04).
// Their current bodies are exercised by the focused actual-source regressions;
// the rest of each module and financial arithmetic must still compare exactly.
const changedDeclarations = {
  "src/lib/db.ts": new Set(["useTenant", "tenantTodayKey"]),
  "src/routes/_authenticated/app.tsx": new Set([
    "MongezzApp",
    "DebtsScreen",
    "DebtCustomerScreen",
    "CourierCustodyScreen",
    "SettlementsScreen",
    "DayCloseScreen",
    "MoneyDetailsSheet",
  ]),
  "src/features/invoices/InvoiceDetailScreen.tsx": new Set([
    "InvoiceDetailScreen",
  ]),
  "src/routes/_authenticated/billing.tsx": new Set(["BillingPage"]),
};
function unchangedModule(tree, file) {
  const changed = changedDeclarations[file];
  if (!changed) return tree;
  tree.program.body = tree.program.body.filter((node) => {
    const declaration =
      node.type === "ExportNamedDeclaration" ? node.declaration : node;
    if (
      declaration?.type === "FunctionDeclaration" &&
      changed.has(declaration.id.name)
    )
      return false;
    return !(
      node.type === "ImportDeclaration" &&
      [
        "@/features/shared/FinancialReadBoundary",
        "@/features/shared/financial-read-state",
      ].includes(node.source.value)
    );
  });
  return tree;
}
function memoBody(source, functionName, variable) {
  const tree = ts.createSourceFile(
    "app.tsx",
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TSX,
  );
  const fn = tree.statements.find(
    (n) => ts.isFunctionDeclaration(n) && n.name?.text === functionName,
  );
  let result;
  function visit(node) {
    if (
      ts.isVariableDeclaration(node) &&
      node.name.getText(tree) === variable &&
      node.initializer &&
      ts.isCallExpression(node.initializer)
    )
      result = node.initializer.arguments[0].body.getText(tree);
    ts.forEachChild(node, visit);
  }
  visit(fn);
  assert(result, `Missing actual ${functionName}.${variable} formula`);
  return result;
}
const sources = new Map();
for (const file of files) {
  const before = cp.execFileSync("git", ["show", `${baseline}:${file}`], {
    encoding: "utf8",
  });
  const after = fs.readFileSync(file, "utf8");
  const a = emit(before, file),
    b = emit(
      historicalQuantitySource(file, historicalWebhookSource(file, after)),
      file,
    );
  assert.deepEqual(
    canon(unchangedModule(ast(a), file), file, false),
    canon(unchangedModule(ast(b), file), file, true),
    file,
  );
  if (file === "src/routes/_authenticated/app.tsx") {
    const currentBase = cp.execFileSync(
      "git",
      ["show", `d9aa04ac316bc1c2adaf021443bc42f42180b828:${file}`],
      { encoding: "utf8" },
    );
    for (const [name, variable] of [
      ["MongezzApp", "totals"],
      ["DayCloseScreen", "t"],
    ]) {
      const originalFormula = memoBody(currentBase, name, variable);
      let currentFormula = memoBody(after, name, variable);
      if (name === "DayCloseScreen") {
        assert.equal(
          (currentFormula.match(/const todayKey = p\.todayKey;/g) || []).length,
          1,
        );
        currentFormula = currentFormula.replace(
          "const todayKey = p.todayKey;",
          "const todayKey = tenantTodayKey(tenantTz);",
        );
      }
      assert.deepEqual(
        canon(
          ast(emit(`function formula() ${originalFormula}`, file)),
          file,
          false,
        ),
        canon(
          ast(emit(`function formula() ${currentFormula}`, file)),
          file,
          false,
        ),
        `${name} arithmetic changed`,
      );
    }
  }
  sources.set(file, { before: a, after: emit(after, file) });
}
assert.deepEqual(counters, {
  clientAlias: 1,
  nullGuard: 2,
  messageAlias: 1,
  messageRename: 1,
});

// Execute the original query/mutation callbacks with a recording client. No
// network or database exists in this contract replay; calls and values are real
// application callbacks, while storage/authorization acceptance remains separate.
const quantitySource = emit(
  fs.readFileSync("src/domain/finance/quantity.ts", "utf8"),
  "quantity.ts",
).replace(/^export /gm, "");
const quantity = new Function(
  quantitySource + "\nreturn { isQuantity, QUANTITY_ERROR }; ",
)();
function callbacks(source, response) {
  const calls = [];
  const client = {
    rpc: async (name, args) => {
      calls.push({ name, args });
      return response;
    },
  };
  const code = source
    .replace(/^import[^;]+;\n/gm, "")
    .replace(/^export /gm, "");
  const run = new Function(
    "supabase",
    "useQuery",
    "useMutation",
    "useQueryClient",
    "isQuantity",
    "QUANTITY_ERROR",
    code +
      "\nreturn { useTenantTodayEstimate, useCreateSale, useDeleteProduct }; ",
  );
  return {
    api: run(
      client,
      (x) => x,
      (x) => x,
      () => ({ invalidateQueries() {} }),
      quantity.isQuantity,
      quantity.QUANTITY_ERROR,
    ),
    calls,
  };
}
async function scenario(kind, data, error) {
  const outcomes = [];
  for (const version of ["before", "after"]) {
    const instance = callbacks(sources.get("src/lib/db.ts")[version], {
      data,
      error: error ?? null,
    });
    try {
      let value;
      if (kind === "today")
        value = await instance.api
          .useTenantTodayEstimate("tenant-fixture")
          .queryFn();
      if (kind === "sale")
        value = await instance.api.useCreateSale("tenant-fixture").mutationFn({
          items: [
            {
              productId: "product-fixture",
              name: "dummy",
              qty: 2,
              price: 50,
              cost: 20,
            },
          ],
          total: 100,
          paid: 40,
          customerId: "customer-fixture",
          delivery: "direct",
          method: "cash",
        });
      if (kind === "product")
        value = await instance.api
          .useDeleteProduct("tenant-fixture")
          .mutationFn("product-fixture");
      outcomes.push({ value, calls: instance.calls });
    } catch (failure) {
      outcomes.push({
        errorName: failure.name,
        errorMessage: failure.message,
        calls: instance.calls,
      });
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
  const today = await scenario("today", {
    today: "2026-10-18",
    timezone: "Africa/Tripoli",
    sales: 100,
    collected: 40,
    expenses: 5,
    realized_profit: 12,
  });
  assert.deepEqual(today.value, {
    today: "2026-10-18",
    timezone: "Africa/Tripoli",
    sales: 100,
    collected: 40,
    expenses: 5,
    realizedProfit: 12,
  });
  await scenario("today", null);
  await scenario("today", null, { message: "fixture_error" });
  const sale = await scenario("sale", {
    success: true,
    order_id: "order-fixture",
    number: 11,
  });
  assert.deepEqual(sale.value, { orderId: "order-fixture", number: "11" });
  assert.deepEqual(sale.calls, [
    {
      name: "create_sale_with_items",
      args: {
        p_customer_id: "customer-fixture",
        p_delivery: "direct",
        p_courier_id: null,
        p_paid: 40,
        p_method: "cash",
        p_items: [{ productId: "product-fixture", qty: 2 }],
      },
    },
  ]);
  await scenario("sale", null);
  await scenario("sale", null, { message: "forbidden_tenant" });
  await scenario("product", { deleted: true });
  await scenario("product", { archived: true, used_in: 2 });
  await scenario("product", null);
  await scenario("product", null, { message: "forbidden_role" });
  const fractionalInput = {
    items: [
      {
        productId: "product-fixture",
        name: "dummy",
        qty: 0.25,
        price: 12.5,
        cost: 2,
      },
    ],
    total: 3.13,
    paid: 3.13,
    delivery: "direct",
    method: "cash",
  };
  const currentSource = sources.get("src/lib/db.ts").after;
  const fractional = callbacks(currentSource, {
    data: { order_id: "quarter", number: 12 },
    error: null,
  });
  assert.deepEqual(
    await fractional.api
      .useCreateSale("tenant-fixture")
      .mutationFn(fractionalInput),
    { orderId: "quarter", number: "12" },
  );
  assert.equal(fractional.calls[0].args.p_items[0].qty, 0.25);
  assert.equal(fractional.calls[0].args.p_paid, 3.13);
  for (const qty of [0, -0.25, 0.001, NaN, Infinity]) {
    const invalid = callbacks(currentSource, { data: null, error: null });
    await assert.rejects(
      invalid.api.useCreateSale("tenant-fixture").mutationFn({
        ...fractionalInput,
        items: [{ ...fractionalInput.items[0], qty }],
      }),
      { message: quantity.QUANTITY_ERROR },
    );
    assert.deepEqual(invalid.calls, []);
  }
  const empty = callbacks(currentSource, { data: null, error: null });
  await assert.rejects(
    empty.api
      .useCreateSale("tenant-fixture")
      .mutationFn({ ...fractionalInput, items: [] }),
    { message: quantity.QUANTITY_ERROR },
  );
  assert.deepEqual(empty.calls, []);
  // A financial wire mutation must remain observable to the same AST comparator.
  const original = sources.get("src/lib/db.ts").before;
  const changed = original.replace(
    "p_paid: input.paid",
    "p_paid: input.paid + 1",
  );
  assert.notEqual(changed, original);
  assert.notDeepEqual(
    canon(ast(original), "src/lib/db.ts", false),
    canon(ast(changed), "src/lib/db.ts", false),
  );
  console.log(
    JSON.stringify({
      files: files.length,
      functionalDeclarationContracts: Object.fromEntries(
        Object.entries(changedDeclarations).map(([file, names]) => [
          file,
          [...names],
        ]),
      ),
      unchangedFinancialMemoBodies: 2,
      intentionalAliasesAndGuards: counters,
      callbackScenarios: 10,
      currentFractionalCallbackControls: 7,
      currentC2ModulesPinned: 2,
      negativeWireMutation: true,
      databaseOrProviderCalls: 0,
    }),
  );
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
