import { build } from "esbuild";
import fs from "node:fs/promises";
import path from "node:path";
import assert from "node:assert/strict";
import ts from "typescript";
const out = path.resolve(process.argv[2]);
await fs.mkdir(out, { recursive: true });
const source = await fs.readFile("src/routes/_authenticated/app.tsx", "utf8");
const ast = ts.createSourceFile("app.tsx", source, ts.ScriptTarget.Latest, true, ts.ScriptKind.TSX);
const names = ["SaleScreen", "PaymentSheet", "SaleQuickScreen"];
const functions = names
  .map((name) => {
    const matches = ast.statements.filter(
      (node) => ts.isFunctionDeclaration(node) && node.name?.text === name,
    );
    assert.equal(matches.length, 1);
    return matches[0].getText(ast);
  })
  .join("\n");
const icons = ast.statements
  .find((node) => ts.isImportDeclaration(node) && node.moduleSpecifier.text === "lucide-react")
  .getText(ast);
const imports = `import {useState,useMemo,useEffect,useRef} from 'react';
import {Money,fmt} from '@/features/shared/Money';
import {Sheet} from '@/features/shared/Sheet';
import {TopBar} from '@/features/layout/TopBar';
import {QuantityInput} from '@/features/shared/QuantityInput';
import {getSaleTotal,getSaleLineTotal} from '@/domain/finance/invoice-selectors';
import {isQuantity,stepQuantity,sumQuantities,QUANTITY_ERROR} from '@/domain/finance/quantity';
import {newSaleOperationId,saleErrorMessage} from '@/lib/sale-operation';`;
await build({
  entryPoints: ["tests/c4-sale/fixture.tsx"],
  outfile: path.join(out, "app.js"),
  bundle: true,
  platform: "browser",
  jsx: "automatic",
  define: { "import.meta.env.VITE_SUPABASE_URL": '"http://127.0.0.1:54321"' },
  alias: {
    "@/integrations/supabase/client": path.resolve("tests/c4-sale/browser-client.ts"),
    "@tanstack/react-query": path.resolve("tests/c4-sale/browser-query.ts"),
    "@": path.resolve("src"),
  },
  plugins: [
    {
      name: "actual-sale-functions",
      setup(builder) {
        builder.onResolve({ filter: /^__ACTUAL_CARTS__$/ }, () => ({
          path: "actual-carts",
          namespace: "actual",
        }));
        builder.onLoad({ filter: /.*/, namespace: "actual" }, () => ({
          loader: "tsx",
          resolveDir: process.cwd(),
          contents: imports + icons + functions + "\nexport {SaleScreen,SaleQuickScreen};",
        }));
      },
    },
  ],
});
await fs.writeFile(
  path.join(out, "index.html"),
  '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><div id="root"></div><script src="/app.js"></script></html>',
);
