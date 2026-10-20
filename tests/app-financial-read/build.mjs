/** Actual app/container and screens; synthetic read hooks, no database or provider. */
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createHash } from "node:crypto";
import process from "node:process";
import ts from "typescript";
import { build } from "esbuild";

const output = process.argv[2];
if (!output) throw new Error("Usage: node tests/app-financial-read/build.mjs OUTPUT");
mkdirSync(output, { recursive: true });
const root = process.cwd();
const source = readFileSync("src/routes/_authenticated/app.tsx", "utf8");
const ast = ts.createSourceFile("app.tsx", source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
let captures = 0;
// Only test observability is inserted; query mapping, formulas, guards and JSX are original.
const app = ast.statements
  .filter(
    (node) =>
      ts.isImportDeclaration(node) ||
      ts.isFunctionDeclaration(node) ||
      ts.isTypeAliasDeclaration(node),
  )
  .map((node) => {
    let text = node.getText(ast);
    if (ts.isFunctionDeclaration(node) && node.name?.text === "MongezzApp") {
      const marker = "  const hideNav =";
      if (!text.includes(marker)) throw new Error("Missing context observation boundary");
      text = text.replace(marker, "  globalThis.__readContext = ctx;\n" + marker);
      text = text.replace(
        'useState<Screen>("home")',
        'useState<Screen>(globalThis.__readSpec.screen ?? "home")',
      );
      captures += 1;
    }
    return text;
  })
  .join("\n");
if (captures !== 1) throw new Error("Expected exactly one actual app declaration");

const dbNames = [...source.matchAll(/import\s*\{([^}]+)\}\s*from\s*"@\/lib\/db"/gs)].flatMap(
  (match) =>
    match[1]
      .split(",")
      .map((s) => s.trim())
      .filter((s) => s && !s.startsWith("type ")),
);
const db = dbNames
  .map((name) => {
    if (name === "tenantTodayKey")
      return `export const tenantTodayKey=(tz)=>new Intl.DateTimeFormat('en-CA',{timeZone:tz}).format(new Date());`;
    const reads = { useInvoices: "invoices", usePayments: "payments", useExpenses: "expenses" };
    if (reads[name]) return `export const ${name}=()=>globalThis.__readQueries.${reads[name]};`;
    if (name === "useTenantId")
      return `export const useTenantId=()=>({data:globalThis.__readSpec.tenantMissing?null:'tenant-fixture',status:globalThis.__readSpec.tenantError?'error':'success',isError:!!globalThis.__readSpec.tenantError,refetch:async()=>{globalThis.__readEffects.push(['refetch','tenant']);}});`;
    const rows = {
      useProducts: "products",
      useCustomers: "customers",
      useCouriers: "couriers",
      useDayCloses: "dayCloses",
    };
    if (rows[name])
      return `export const ${name}=()=>({data:globalThis.__readData.${rows[name]},isLoading:false});`;
    if (name === "useTenant")
      return `export const useTenant=()=>globalThis.__readQueries.settings;`;
    if (name === "useMyRole") return `export const useMyRole=()=>({data:'owner'});`;
    return `export const ${name}=()=>({mutateAsync:async(input)=>{globalThis.__readEffects.push([${JSON.stringify(name)},input]);return {};}});`;
  })
  .join("\n");

const fixture = `
export function reset(spec={}) {
 globalThis.__readSpec=spec; globalThis.__readEffects=[];
 const now=new Date().toISOString();
 const invoice={id:'invoice-fixture',number:'001',customerId:'customer-fixture',
  items:[{productId:'product-fixture',name:'Synthetic product',qty:1,price:100,cost:25}],
  total:100,paid:40,status:'partial',delivery:'direct',createdAt:now,time:'12:00'};
 globalThis.__readData={
  products:[{id:'product-fixture',name:'Synthetic product',stock:10,price:100,cost:25,lowAt:2,active:true}],
  customers:spec.customerMissing?[]:[{id:'customer-fixture',name:'عميل تجريبي',phone:'000'}],
  couriers:[{id:'courier-fixture',name:'مندوب تجريبي'}],dayCloses:[],
  invoices:spec.empty?[]:[invoice],
  payments:spec.empty?[]:[{id:'payment-fixture',kind:'sale',method:'cash',amount:40,invoiceId:invoice.id,createdAt:now,time:'12:00'}],
  expenses:spec.empty?[]:[{id:'expense-fixture',type:'نقل',amount:10,method:'cash',createdAt:now,time:'12:00'}]
 };
 globalThis.__readQueries={};
 for(const key of ['invoices','payments','expenses']) {
  const mode=spec.reads?.[key]??'ready';
  const data=['missing','error','paused'].includes(mode)?undefined:globalThis.__readData[key];
  globalThis.__readQueries[key]={data,status:mode.includes('error')?'error':data===undefined?'pending':'success',
   fetchStatus:mode==='paused'?'paused':['missing','refreshing'].includes(mode)?'fetching':'idle',
   isPlaceholderData:mode==='placeholder',isError:mode.includes('error'),isPending:data===undefined,
   isLoading:mode==='missing',isFetching:['missing','refreshing'].includes(mode),
   refetch:async()=>{globalThis.__readEffects.push(['refetch',key]);return {};}};
 }
 const settingsMode=spec.settingsRead??'ready';
 globalThis.__readQueries.settings={
  data:['missing','error','paused'].includes(settingsMode)?undefined:{id:'tenant-fixture',name:'Synthetic shop',timezone:spec.timezone===undefined?'UTC':spec.timezone},
  status:settingsMode.includes('error')?'error':['missing','paused'].includes(settingsMode)?'pending':'success',
  fetchStatus:settingsMode==='paused'?'paused':['missing','refreshing'].includes(settingsMode)?'fetching':'idle',
  isPlaceholderData:settingsMode==='placeholder',
  refetch:async()=>{globalThis.__readEffects.push(['refetch','settings']);return {};}
 };
}
export function update(spec) {
 const context=globalThis.__readContext;
 reset({...globalThis.__readSpec,...spec,reads:{...globalThis.__readSpec.reads,...spec.reads}});
 return context;
}
export function context(){return globalThis.__readContext;}
export function effects(){return globalThis.__readEffects;}
`;
const plugin = {
  name: "isolated-read-fixture",
  setup(build) {
    build.onResolve({ filter: /^fixture:(app|db|state|router|pdf|client)$/ }, (args) => ({
      path: args.path,
      namespace: "fixture",
    }));
    build.onResolve({ filter: /^@\/lib\/db$/ }, () => ({
      path: "fixture:db",
      namespace: "fixture",
    }));
    build.onResolve({ filter: /^@tanstack\/react-router$/ }, () => ({
      path: "fixture:router",
      namespace: "fixture",
    }));
    build.onResolve({ filter: /^@\/lib\/invoice-pdf$/ }, () => ({
      path: "fixture:pdf",
      namespace: "fixture",
    }));
    build.onResolve({ filter: /^@\/integrations\/supabase\/client$/ }, () => ({
      path: "fixture:client",
      namespace: "fixture",
    }));
    build.onLoad({ filter: /.*/, namespace: "fixture" }, (args) => {
      const code = {
        "fixture:app": app + "\nexport {MongezzApp, MoneyDetailsSheet};",
        "fixture:db": db,
        "fixture:state": fixture,
        "fixture:router":
          "export const createFileRoute=()=>x=>x;export const useRouter=()=>({invalidate(){}});",
        "fixture:pdf":
          "export const downloadInvoicePdf=async()=>{globalThis.__readEffects.push(['pdf']);};export const printInvoice=()=>{globalThis.__readEffects.push(['print']);};export const ensureFont=async()=>{};",
        "fixture:client":
          "export const supabase={auth:{signOut:async()=>{globalThis.__readEffects.push(['signOut']);}}};",
      }[args.path];
      if (!code) throw new Error("Unknown fixture module");
      return { contents: code, loader: "tsx", resolveDir: root };
    });
  },
};
const common = {
  bundle: true,
  jsx: "automatic",
  plugins: [plugin],
  tsconfig: resolve("tsconfig.json"),
  logLevel: "warning",
};
await build({
  ...common,
  stdin: {
    contents: `import React from 'react';import {renderToStaticMarkup} from 'react-dom/server';import {MongezzApp, MoneyDetailsSheet} from 'fixture:app';import {InvoiceDetailScreen} from '@/features/invoices/InvoiceDetailScreen';import * as f from 'fixture:state';export function render(spec){f.reset(spec);const html=renderToStaticMarkup(React.createElement(MongezzApp));const ctx=f.context();const detailHtml=spec?.moneyDetails?renderToStaticMarkup(React.createElement(MoneyDetailsSheet,{totals:ctx.totals,period:ctx.period,reads:[...Object.values(ctx.financialReads),...(ctx.period==="day"?[ctx.tenantTimezoneRead]:[])],onRetry:ctx.retryFinancialReads,onClose:()=>{},onOpenProfit:()=>{}})):spec?.invoiceDetail?renderToStaticMarkup(React.createElement(InvoiceDetailScreen,{...ctx,openInvoiceId:'invoice-fixture'})):undefined;return {html,detailHtml,ctx,effects:f.effects()};}`,
    resolveDir: root,
    sourcefile: "financial-read-server.tsx",
    loader: "tsx",
  },
  platform: "node",
  format: "cjs",
  outfile: resolve(output, "server.cjs"),
});
await build({
  ...common,
  stdin: {
    contents: `import React from 'react';import {createRoot} from 'react-dom/client';import {flushSync} from 'react-dom';import {MongezzApp} from 'fixture:app';import * as f from 'fixture:state';let root=createRoot(document.getElementById('root'));let key=0;function draw(){flushSync(()=>root.render(<MongezzApp key={key}/>));}window.fixture={reset(spec={}){f.reset(spec);key++;draw();},update(spec){f.update(spec);draw();},go(screen){flushSync(()=>f.context().go(screen));},openInvoice(){flushSync(()=>{f.context().setOpenInvoiceId('invoice-fixture');f.context().go('invoice_detail');});},context:f.context,effects:f.effects};window.fixture.reset();`,
    resolveDir: root,
    sourcefile: "financial-read-browser.tsx",
    loader: "tsx",
  },
  platform: "browser",
  format: "iife",
  outfile: resolve(output, "bundle.js"),
});
writeFileSync(
  resolve(output, "source.json"),
  JSON.stringify(
    {
      app_sha256: createHash("sha256").update(source).digest("hex"),
      method:
        "Original AST imports/types/functions; only ctx capture and initial-screen injection for test observability; real React/screens/selectors; synthetic hooks and provider I/O",
    },
    null,
    2,
  ) + "\n",
);
