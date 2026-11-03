import { build } from "esbuild";
import fs from "node:fs/promises";
import path from "node:path";
const out = path.resolve(process.argv[2]);
await fs.mkdir(out, { recursive: true });
await build({
  entryPoints: ["tests/c5-collection/browser-fixture.tsx"],
  outfile: path.join(out, "app.js"),
  bundle: true,
  platform: "browser",
  jsx: "automatic",
  define: { "import.meta.env.VITE_SUPABASE_URL": '"http://127.0.0.1:54321"' },
  alias: {
    "@/integrations/supabase/client": path.resolve("tests/c5-collection/browser-client.ts"),
    "@": path.resolve("src"),
  },
  plugins: [
    {
      name: "unrelated-pdf-boundary",
      setup(b) {
        b.onResolve({ filter: /^@\/lib\/invoice-pdf$/ }, () => ({
          path: "pdf",
          namespace: "fixture",
        }));
        b.onLoad({ filter: /.*/, namespace: "fixture" }, () => ({
          contents:
            'export const ensureFont=async()=>{};export const downloadInvoicePdf=()=>{throw Error("excluded PDF")};export const printInvoice=()=>{throw Error("excluded PDF")};',
          loader: "js",
        }));
      },
    },
  ],
});
await fs.writeFile(
  path.join(out, "index.html"),
  '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><div id="root"></div><script src="/app.js"></script></html>',
);
