import { build } from "esbuild";
import fs from "node:fs/promises";
import path from "node:path";
const out = process.argv[2];
await fs.mkdir(out, { recursive: true });
await build({
  entryPoints: ["tests/c2-quantity/fixture.tsx"],
  outfile: path.join(out, "app.js"),
  bundle: true,
  platform: "browser",
  jsx: "automatic",
  alias: { "@": path.resolve("src") },
});
await fs.writeFile(
  path.join(out, "index.html"),
  '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><div id="root"></div><script src="/app.js"></script></html>',
);
