// Bundles the actual src/routes/auth.tsx sign-in/sign-up screen for a browser test.
import { build } from "esbuild";
import fs from "node:fs/promises";
import path from "node:path";
const out = path.resolve(process.argv[2]);
await fs.mkdir(out, { recursive: true });
await build({
  entryPoints: ["tests/auth-signup/fixture.tsx"],
  outfile: path.join(out, "app.js"),
  bundle: true,
  platform: "browser",
  jsx: "automatic",
  define: { "process.env.NODE_ENV": '"production"' },
  alias: {
    "@tanstack/react-router": path.resolve("tests/auth-signup/router-stub.tsx"),
    "@/integrations/supabase/client": path.resolve("tests/auth-signup/client.ts"),
    "@/integrations/lovable/index": path.resolve("tests/auth-signup/lovable-stub.ts"),
    "@": path.resolve("src"),
  },
});
await fs.writeFile(
  path.join(out, "index.html"),
  '<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8"><div id="root"></div><script src="/app.js"></script></html>',
);
console.log("AUTH_SIGNUP_BUILD_OK " + out);
