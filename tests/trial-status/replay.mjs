import assert from "node:assert/strict";
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createRequire } from "node:module";
import process from "node:process";
import ts from "typescript";
import { build } from "esbuild";

const out = process.argv[2];
if (!out) throw new Error("Usage: node tests/trial-status/replay.mjs OUTPUT");
mkdirSync(out, { recursive: true });
const dbSource = readFileSync("src/lib/db.ts", "utf8");
const ast = ts.createSourceFile("db.ts", dbSource, ts.ScriptTarget.Latest, true);
const hook = ast.statements.find(
  (n) => ts.isFunctionDeclaration(n) && n.name?.text === "useTenant",
);
if (!hook) throw new Error("Missing actual tenant hook");
const hookJs = ts.transpile(hook.getText(ast), { module: ts.ModuleKind.CommonJS });
const queryModule = { exports: {} };
const selected = [];
let row, queryError;
const client = {
  from(name) {
    assert.equal(name, "tenants");
    return {
      select(columns) {
        selected.push(columns);
        return this;
      },
      eq() {
        return this;
      },
      async maybeSingle() {
        return {
          data: row
            ? Object.fromEntries(
                selected
                  .at(-1)
                  .split(",")
                  .map((k) => [k, row[k]]),
              )
            : null,
          error: queryError,
        };
      },
    };
  },
};
new Function("module", "exports", "useQuery", "supabase", hookJs)(
  queryModule,
  queryModule.exports,
  (x) => x,
  client,
);
const actualQuery = queryModule.exports.useTenant("synthetic-tenant");

const billingSource = readFileSync("src/routes/_authenticated/billing.tsx", "utf8");
const billingAst = ts.createSourceFile(
  "billing.tsx",
  billingSource,
  ts.ScriptTarget.Latest,
  true,
  ts.ScriptKind.TSX,
);
const billing =
  billingAst.statements
    .filter(
      (n) =>
        !(
          ts.isVariableStatement(n) &&
          n.declarationList.declarations.some((d) => d.name.getText(billingAst) === "Route")
        ),
    )
    .map((n) => n.getText(billingAst))
    .join("\n") + "\nexport { BillingPage };";
const plugin = {
  name: "isolated-trial",
  setup(b) {
    b.onResolve(
      {
        filter:
          /^(fixture:billing|@\/lib\/db|@\/integrations\/supabase\/client|@\/lib\/paddle|@\/hooks\/usePaddleCheckout|@\/components\/PaymentTestModeBanner|@tanstack\/react-query|@tanstack\/react-router)$/,
      },
      (a) => ({ path: a.path, namespace: "trial" }),
    );
    b.onLoad({ filter: /.*/, namespace: "trial" }, (a) => ({
      loader: "tsx",
      resolveDir: process.cwd(),
      contents: {
        "fixture:billing": billing,
        "@/lib/db":
          "export const useTenantId=()=>globalThis.__trial.tenantId;export const useTenant=()=>globalThis.__trial.tenant;",
        "@/integrations/supabase/client": "export const supabase={};",
        "@/lib/paddle": 'export const getPaddleEnvironment=()=>"sandbox";',
        "@/hooks/usePaddleCheckout":
          "export const usePaddleCheckout=()=>({openCheckout(){throw Error('provider forbidden')},loading:false});",
        "@/components/PaymentTestModeBanner": "export const PaymentTestModeBanner=()=>null;",
        "@tanstack/react-query": "export const useQuery=()=>globalThis.__trial.sub;",
        "@tanstack/react-router":
          "import React from 'react';export const createFileRoute=()=>x=>x;export const Link=({children})=>React.createElement('a',null,children);",
      }[a.path],
    }));
  },
};
const bundled = await build({
  stdin: {
    contents:
      "import React from 'react';import {renderToStaticMarkup} from 'react-dom/server';import {BillingPage} from 'fixture:billing';export const render=()=>renderToStaticMarkup(React.createElement(BillingPage));",
    loader: "tsx",
    resolveDir: process.cwd(),
  },
  bundle: true,
  platform: "node",
  format: "cjs",
  write: false,
  plugins: [plugin],
  jsx: "automatic",
});
const mod = { exports: {} };
new Function("require", "module", "exports", bundled.outputFiles[0].text)(
  createRequire(import.meta.url),
  mod,
  mod.exports,
);
const ready = (data) => ({ data, isPending: false, isError: false, isFetching: false });
const results = [];
async function check(name, run) {
  try {
    await run();
    results.push({ name, passed: true });
  } catch (e) {
    results.push({ name, passed: false, error: String(e) });
  }
}
async function renderTrial(overrides = {}) {
  row = {
    id: "synthetic-tenant",
    name: "Synthetic",
    timezone: "UTC",
    business_type: null,
    trial_ends_at: "2099-01-01T00:00:00Z",
    ...overrides.row,
  };
  queryError = overrides.queryError ?? null;
  let data;
  try {
    data = await actualQuery.queryFn();
  } catch {
    data = undefined;
  }
  globalThis.__trial = {
    tenantId: ready("synthetic-tenant"),
    tenant: ready(data),
    sub: ready(null),
    ...overrides,
  };
  return mod.exports.render();
}
await check("actual tenant query returns selected real trial column", async () => {
  await renderTrial();
  assert(selected.at(-1).split(",").includes("trial_ends_at"));
  assert.equal(globalThis.__trial.tenant.data.trial_ends_at, "2099-01-01T00:00:00Z");
});
await check("valid future trial is active", async () =>
  assert.match(await renderTrial(), /في الفترة التجريبية المجانية/),
);
await check("expired trial is expired", async () =>
  assert.match(
    await renderTrial({ row: { trial_ends_at: "2020-01-01T00:00:00Z" } }),
    /انتهت التجربة المجانية/,
  ),
);
await check("null trial is absent rather than an invented expiry", async () =>
  assert.match(await renderTrial({ row: { trial_ends_at: null } }), /لا توجد فترة تجريبية مسجلة/),
);
await check("active subscription precedes trial", async () =>
  assert.match(
    await renderTrial({ sub: ready({ status: "active", product_id: "mongezz_starter" }) }),
    /مشترك في/,
  ),
);
for (const key of ["tenantId", "tenant", "sub"]) {
  await check(`${key} loading is not expired`, async () => {
    const html = await renderTrial({
      [key]: { data: undefined, isPending: true, isError: false, isFetching: true },
    });
    assert.match(html, /جارٍ تحميل حالة الاشتراك/);
    assert.doesNotMatch(html, /انتهت التجربة المجانية/);
  });
  await check(`${key} error is not expired`, async () => {
    const html = await renderTrial({
      [key]: { data: undefined, isPending: false, isError: true, isFetching: false },
    });
    assert.match(html, /تعذّر تحميل حالة الاشتراك/);
    assert.doesNotMatch(html, /انتهت التجربة المجانية/);
  });
}
await check("invalid trial date is unavailable", async () =>
  assert.match(
    await renderTrial({ row: { trial_ends_at: "invalid-date" } }),
    /تعذّر تحميل حالة الاشتراك/,
  ),
);
await check("actual tenant query propagates database failure", async () => {
  queryError = new Error("synthetic read failure");
  await assert.rejects(actualQuery.queryFn, queryError);
  queryError = null;
});
writeFileSync(
  resolve(out, "trial.json"),
  JSON.stringify(
    {
      results,
      passed: results.filter((x) => x.passed).length,
      total: results.length,
      scope:
        "Actual tenant query projection and React SSR billing; synthetic query client/transport; no provider",
    },
    null,
    2,
  ) + "\n",
);
console.log(
  JSON.stringify(
    {
      passed: results.filter((x) => x.passed).length,
      total: results.length,
      failures: results.filter((x) => !x.passed),
    },
    null,
    2,
  ),
);
if (results.some((x) => !x.passed)) process.exitCode = 1;
