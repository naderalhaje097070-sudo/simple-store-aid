import { build } from "vite";
import react from "@vitejs/plugin-react";
import tailwindcss from "@tailwindcss/vite";
import path from "node:path";
const cwd = process.cwd();
await build({
  configFile: false,
  root: path.resolve("tests/c5-journey"),
  publicDir: path.resolve("public"),
  plugins: [
    react(),
    tailwindcss(),
    {
      name: "excluded-pdf-export",
      resolveId(id) {
        if (id === "@/lib/invoice-pdf") return "\0journey-pdf";
      },
      load(id) {
        // The "@" alias resolves "@/lib/invoice-pdf" before resolveId above can
        // see it, so also stub the resolved module file itself.
        if (id === "\0journey-pdf" || id === path.join(cwd, "src/lib/invoice-pdf.ts"))
          return 'export const ensureFont=async()=>{};export const downloadInvoicePdf=()=>{throw Error("PDF excluded")};export const printInvoice=()=>{throw Error("PDF excluded")};';
      },
    },
  ],
  resolve: {
    alias: [
      {
        find: "@/integrations/supabase/client",
        replacement: path.join(cwd, "tests/c5-journey/client.ts"),
      },
      { find: "@", replacement: path.join(cwd, "src") },
    ],
  },
  define: {
    "import.meta.env.VITE_SUPABASE_URL": JSON.stringify("http://127.0.0.1:54321"),
  },
  build: {
    outDir: path.resolve(process.argv[2]),
    emptyOutDir: true,
    sourcemap: false,
  },
});
