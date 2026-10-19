/** Bundle the actual debt screens without importing the authenticated app or backend. */
import { readFileSync, mkdirSync, writeFileSync } from "node:fs";
import { resolve } from "node:path";
import { createHash } from "node:crypto";
import ts from "typescript";
import { buildSync } from "esbuild";

const root = process.cwd();
const output = process.argv[2];
if (!output)
  throw new Error("Usage: bun tests/app-debt-missing-customer/build.ts OUTPUT_DIRECTORY");
mkdirSync(output, { recursive: true });
const file = resolve(root, "src/routes/_authenticated/app.tsx");
const source = readFileSync(file, "utf8");
const tree = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const screens = ["DebtsScreen", "DebtCustomerScreen"].map((name) => {
  const declaration = tree.statements.find(
    (node) => ts.isFunctionDeclaration(node) && node.name?.text === name,
  );
  if (!declaration) throw new Error(`Missing actual screen: ${name}`);
  return declaration.getText(tree);
});
const contents = `
import {createRoot} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {Phone, MessageCircle} from 'lucide-react';
import {TopBar} from './src/features/layout/TopBar';
import {Money, fmt} from './src/features/shared/Money';
import {EmptyState} from './src/features/shared/EmptyState';
import {getCustomerDebtForInvoice} from './src/domain/finance/invoice-selectors';
${screens.join("\n")}
const root = createRoot(document.getElementById('root'));
const customer = {id:'customer-fixture', name:'عميل تجريبي', phone:'000'};
const invoice = {id:'invoice-fixture', number:'001', customerId:customer.id,
  items:[{qty:1, price:100, cost:25}], total:100, paid:40, delivery:'direct'};
let state;
window.effects = [];
const effect = (kind, value) => window.effects.push([kind, value]);
function render() {
  const props = {...state,
    setOpenCustomerId:id=>{effect('customer',id);state.openCustomerId=id;},
    setOpenInvoiceId:id=>effect('invoice',id),
    go:screen=>{effect('go',screen);state.screen=screen;render();},
    back:()=>{effect('back');state.screen='debts';render();},
    goHome:()=>effect('home'),
    collectDebtAsync:input=>effect('collect',input),
    createSaleAsync:input=>effect('sale',input),
  };
  flushSync(()=>root.render(state.screen==='debts'
    ? <DebtsScreen {...props}/> : <DebtCustomerScreen {...props}/>));
}
window.fixture = {
  reset(overrides={}) {
    state={screen:'debts', customers:[], invoices:[invoice],
      openCustomerId:customer.id, customersLoading:false,
      financialReads:{invoices:{hasData:true,complete:true,phase:'ready'}}, ...overrides};
    window.effects=[];
    render();
  },
  update(patch) { Object.assign(state, patch); render(); },
  customer,
  // A second customer and unassigned invoice must not enter the selected debt.
  unrelatedInvoices:[
    {...invoice,id:'other-invoice',number:'002',customerId:'another-customer',total:900},
    {...invoice,id:'unassigned-invoice',number:'003',customerId:undefined,total:800},
    {...invoice,id:'returned-invoice',number:'004',courierState:'returned'},
    {...invoice,id:'pending-invoice',number:'005',delivery:'courier',courierState:'pending'},
  ],
};
window.fixture.reset();
`;
buildSync({
  stdin: { contents, resolveDir: root, sourcefile: "debt-ui-fixture.tsx", loader: "tsx" },
  bundle: true,
  platform: "browser",
  format: "iife",
  jsx: "automatic",
  outfile: resolve(output, "bundle.js"),
});
const receipt = {
  app_sha256: createHash("sha256").update(source).digest("hex"),
  screens: ["DebtsScreen", "DebtCustomerScreen"],
  method: "Original TypeScript AST declarations; actual shared UI and finance selector imports",
};
writeFileSync(resolve(output, "bundle-source.json"), JSON.stringify(receipt, null, 2) + "\n");
console.log(JSON.stringify(receipt));
