// Current-source behavioural controls formerly inside runtime.cjs, which ran them
// on a historically reconstructed copy of the source (retired history pins).
// These run on the CURRENT application modules with a recording client: no
// network or database. Sale wire/quantity controls live in tests/c4-sale/contracts.test.cjs.
const test = require("node:test");
const assert = require("node:assert/strict");
const cp = require("node:child_process");
const fs = require("node:fs");
const ts = require("typescript");
const parser = require("@babel/parser");
const { loadApplication } = require("../c4-sale/loader.cjs");
// Objects created inside the loader realm: compare as plain data.
const plain = (value) => JSON.parse(JSON.stringify(value));

function app(response) {
  const calls = [];
  const client = {
    auth: {
      async getUser() {
        return { data: { user: { id: "actor-fixture" } }, error: null };
      },
    },
    rpc(name, args) {
      calls.push({ name, args: args === undefined ? undefined : JSON.parse(JSON.stringify(args)) });
      const result = Promise.resolve(response);
      result.abortSignal = () => result;
      return result;
    },
  };
  const loaded = loadApplication({ client });
  return {
    db: loaded.load("src/lib/db.ts"),
    quantity: loaded.load("src/domain/finance/quantity.ts"),
    calls,
  };
}

test("today estimate maps the RPC row to the screen model", async () => {
  const h = app({
    data: {
      today: "2026-10-18",
      timezone: "Africa/Tripoli",
      sales: 100,
      collected: 40,
      expenses: 5,
      realized_profit: 12,
    },
    error: null,
  });
  assert.deepEqual(plain(await h.db.useTenantTodayEstimate("tenant-fixture").queryFn()), {
    today: "2026-10-18",
    timezone: "Africa/Tripoli",
    sales: 100,
    collected: 40,
    expenses: 5,
    realizedProfit: 12,
  });
  assert.deepEqual(h.calls, [{ name: "get_tenant_today_estimate", args: undefined }]);
});
test("today estimate: missing row is an error, not zeros", async () => {
  const h = app({ data: null, error: null });
  await assert.rejects(h.db.useTenantTodayEstimate("t").queryFn(), {
    name: "TypeError",
    message: /returned no result$/,
  });
});
test("today estimate: RPC error propagates", async () => {
  const failure = { message: "fixture_error" };
  const h = app({ data: null, error: failure });
  await assert.rejects(h.db.useTenantTodayEstimate("t").queryFn(), (e) => e === failure);
});
for (const [data, expected] of [
  [{ deleted: true }, { deleted: true, archived: false, usedIn: 0 }],
  [
    { archived: true, used_in: 2 },
    { deleted: false, archived: true, usedIn: 2 },
  ],
  [null, { deleted: false, archived: false, usedIn: 0 }],
])
  test("delete product maps " + JSON.stringify(data), async () => {
    const h = app({ data, error: null });
    assert.deepEqual(
      plain(await h.db.useDeleteProduct("t").mutationFn("product-fixture")),
      expected,
    );
    assert.deepEqual(h.calls, [
      { name: "delete_product_safe", args: { p_product_id: "product-fixture" } },
    ]);
  });
test("delete product: RPC error is raised", async () => {
  const h = app({ data: null, error: { message: "forbidden_role" } });
  await assert.rejects(
    h.db.useDeleteProduct("t").mutationFn("p"),
    (e) => e?.name === "Error" && typeof e.message === "string" && e.message.length > 0,
  );
});
test("sale with no items is refused before any RPC", async () => {
  const h = app({ data: null, error: null });
  await assert.rejects(
    h.db.useCreateSale("tenant-fixture").mutationFn({
      operationId: "00000000-0000-4000-8000-000000000001",
      items: [],
      total: 0,
      paid: 0,
      delivery: "direct",
      method: "cash",
    }),
    { message: h.quantity.QUANTITY_ERROR },
  );
  assert.deepEqual(h.calls, []);
});

// Financial arithmetic of the home totals and the day-close summary must equal the
// last accepted formulas on the integration branch (03584a4), on the current
// app.tsx. An intended formula change must update this reference commit in review.
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
const canon = (v) =>
  Array.isArray(v)
    ? v.map(canon)
    : v && typeof v === "object"
      ? Object.fromEntries(
          Object.entries(v)
            .filter(([k]) => !metadata.has(k))
            .map(([k, x]) => [k, canon(x)]),
        )
      : v;
const emit = (body) =>
  parser.parse(
    ts.transpileModule(`function formula() ${body}`, {
      compilerOptions: { target: ts.ScriptTarget.ESNext, removeComments: true },
    }).outputText,
    { sourceType: "module" },
  );
function memoBody(source, fn, variable) {
  const tree = ts.createSourceFile(
    "app.tsx",
    source,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TSX,
  );
  const decl = tree.statements.find((n) => ts.isFunctionDeclaration(n) && n.name?.text === fn);
  let body;
  (function visit(n) {
    if (
      ts.isVariableDeclaration(n) &&
      n.name.getText(tree) === variable &&
      n.initializer &&
      ts.isCallExpression(n.initializer)
    )
      body = n.initializer.arguments[0].body.getText(tree);
    ts.forEachChild(n, visit);
  })(decl);
  assert(body, `missing ${fn}.${variable}`);
  return body;
}
const reviewed = cp.execFileSync(
  "git",
  ["show", "03584a4e974fabbfc6ebc7029b7ed52a257f2b23:src/routes/_authenticated/app.tsx"],
  { encoding: "utf8" },
);
const current = fs.readFileSync("src/routes/_authenticated/app.tsx", "utf8");
for (const [fn, variable] of [
  ["MongezzApp", "totals"],
  ["DayCloseScreen", "t"],
])
  test(`${fn}.${variable} arithmetic equals the reviewed formula`, () => {
    const now = memoBody(current, fn, variable);
    assert.deepEqual(canon(emit(memoBody(reviewed, fn, variable))), canon(emit(now)));
  });
test("arithmetic comparator detects a changed formula", () => {
  const body = memoBody(current, "MongezzApp", "totals");
  const changed = body.replace(/\+/, "-");
  assert.notEqual(changed, body);
  assert.notDeepEqual(canon(emit(body)), canon(emit(changed)));
});
