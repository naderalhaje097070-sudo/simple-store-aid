// Real exported generator, manifest CLI and module runner; dummy data only.
import { test } from "node:test";
import assert from "node:assert/strict";
import * as fs from "node:fs";
import * as path from "node:path";
import { fileURLToPath } from "node:url";
import { spawnSync } from "node:child_process";
import { mcpPlugin as tanstack } from "@lovable.dev/mcp-js/stacks/tanstack/vite";
import { mcpPlugin as edge } from "@lovable.dev/mcp-js/stacks/supabase/vite";
const out = path.resolve("evidence/g0-esbuild");
const fixture = () => fs.mkdtempSync(path.join(process.cwd(), ".g0-esbuild-fixture-"));
function put(root, name, content) {
  const p = path.join(root, name);
  fs.mkdirSync(path.dirname(p), { recursive: true });
  fs.writeFileSync(p, content);
}
function config(root) {
  return { root, envDir: root, envPrefix: ["VITE_"], base: "/", mode: "production" };
}
const entry = `import { defineMcp, defineTool } from '@lovable.dev/mcp-js';
import { z } from 'zod';
import { prefix } from './local';
const literal: string = import.meta.env.VITE_FIXTURE;
export default defineMcp({name:'compat-fixture',title:'Fixture',version:'1.0.0',metrics:false,
tools:[defineTool({name:'echo',title:'Echo',description:'Dummy echo',inputSchema:{value:z.string()},
handler:({value})=>({content:[{type:'text',text:prefix+literal+value}]})})]});`;
function prepare(root) {
  put(
    root,
    "package.json",
    JSON.stringify({
      type: "module",
      dependencies: { "@lovable.dev/mcp-js": "0.20.1", zod: "^4.4.3" },
    }),
  );
  put(root, "src/lib/mcp/index.ts", entry);
  put(root, "src/lib/mcp/local.ts", 'export const prefix: string = "local:";');
  put(root, ".env.production", "VITE_FIXTURE=defined:");
}
test("actual TanStack route generator is idempotent and protects authored files", () => {
  const root = fixture();
  try {
    prepare(root);
    const p = tanstack();
    p.configResolved(config(root));
    p.buildStart();
    const routes = [
      "mcp.ts",
      "[.]well-known/oauth-protected-resource.ts",
      "[.mcp]/list-tools.ts",
      "[.mcp]/invoke-tool/$tool.ts",
    ];
    // The official generator escapes only the segment beginning with a dot.
    const files = fs
      .readdirSync(path.join(root, "src/routes"), { recursive: true })
      .filter((x) => x.endsWith(".ts"));
    assert.equal(files.length, routes.length);
    const snapshot = Object.fromEntries(
      files.map((x) => [x, fs.readFileSync(path.join(root, "src/routes", x), "utf8")]),
    );
    assert.match(snapshot["mcp.ts"], /createTanStackMcpHandler/);
    assert.match(snapshot["[.mcp]/invoke-tool/$tool.ts"], /createTanStackInvokeToolHandler/);
    p.buildStart();
    for (const [f, bytes] of Object.entries(snapshot))
      assert.equal(fs.readFileSync(path.join(root, "src/routes", f), "utf8"), bytes);
    put(root, "src/routes/mcp.ts", "// authored sentinel");
    assert.throws(() => p.buildStart(), /refusing to overwrite/);
    assert.equal(
      fs.readFileSync(path.join(root, "src/routes/mcp.ts"), "utf8"),
      "// authored sentinel",
    );
    fs.mkdirSync(out, { recursive: true });
    fs.writeFileSync(path.join(out, "tanstack-generated.json"), JSON.stringify(snapshot, null, 2));
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
test("real MCP Edge generator bundles TS/local imports/env and regenerates safely", async () => {
  const root = fixture();
  let previousDeno;
  try {
    prepare(root);
    const p = edge();
    await p.configResolved(config(root));
    await p.buildStart();
    const f = path.join(root, "supabase/functions/mcp/index.ts");
    const code = fs.readFileSync(f, "utf8");
    assert.match(code, /npm:@lovable.dev\/mcp-js@/);
    assert.match(code, /npm:zod@\^4\.4\.3/);
    assert.match(code, /local:/);
    assert.match(code, /defined:/);
    assert.ok(!code.includes("import.meta.env"));
    await p.buildStart();
    assert.equal(fs.readFileSync(f, "utf8"), code);
    put(root, "src/lib/mcp/local.ts", 'export const prefix: string = "changed:";');
    await p.buildStart();
    const updated = fs.readFileSync(f, "utf8");
    assert.match(updated, /changed:/);
    assert.notEqual(updated, code);
    // Node harness substitutes runtime specifiers only; original emitted bytes retained.
    // No Deno install/deploy or external npm fetch. This does not certify Deno runtime.
    const executable = updated.replace(
      /"npm:([^"@]+|@[^/]+\/[^"@]+)@[^"/]+([^"\n]*)"/g,
      (_all, name, subpath) => JSON.stringify(import.meta.resolve(name + subpath)),
    );
    let handler;
    previousDeno = globalThis.Deno;
    globalThis.Deno = {
      serve: (h) => {
        handler = h;
      },
    };
    await import("data:text/javascript;base64," + Buffer.from(executable).toString("base64"));
    assert.equal(typeof handler, "function");
    const response = await handler(
      new Request("http://127.0.0.1/functions/v1/mcp/.mcp/invoke-tool/echo", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ value: "value" }),
      }),
    );
    assert.equal(response.status, 200);
    assert.match(await response.text(), /changed:defined:value/);
    fs.mkdirSync(out, { recursive: true });
    fs.writeFileSync(path.join(out, "edge-generated.ts"), code);
    put(root, "supabase/functions/mcp/index.ts", "// authored sentinel");
    await assert.rejects(() => p.buildStart(), /refusing to overwrite/);
    assert.equal(fs.readFileSync(f, "utf8"), "// authored sentinel");
  } finally {
    globalThis.Deno = previousDeno;
    fs.rmSync(root, { recursive: true, force: true });
  }
});
test("official manifest CLI executes Vite SSR loader twice with stable output", () => {
  const root = fixture();
  try {
    prepare(root);
    put(root, "src/lib/mcp/index.ts", entry.replace("import.meta.env.VITE_FIXTURE", '"runner:"'));
    put(
      root,
      "vite.config.mjs",
      `import { mcpPlugin } from '@lovable.dev/mcp-js/stacks/tanstack/vite'; export default {plugins:[mcpPlugin()]};`,
    );
    const cli = path.join(
      path.dirname(fileURLToPath(import.meta.resolve("@lovable.dev/mcp-js"))),
      "cli/extract-manifest.cjs",
    );
    let previous;
    for (let i = 0; i < 2; i++) {
      const r = spawnSync(process.execPath, [cli, root], { encoding: "utf8", timeout: 45000 });
      fs.mkdirSync(out, { recursive: true });
      fs.writeFileSync(
        path.join(out, `manifest-cli-${i}.json`),
        JSON.stringify(
          { status: r.status, stdout: r.stdout, stderr: r.stderr, error: r.error?.message },
          null,
          2,
        ),
      );
      assert.equal(r.status, 0, r.stderr);
      const bytes = fs.readFileSync(path.join(root, ".lovable/mcp/manifest.json"), "utf8");
      const m = JSON.parse(bytes);
      assert.equal(m.mcp.server.name, "compat-fixture");
      assert.equal(m.mcp.tools[0].name, "echo");
      assert.equal(m.mcp.tools[0].inputSchema.properties.value.type, "string");
      assert.equal(m.auth.type, "none");
      if (i) assert.equal(bytes, previous);
      previous = bytes;
    }
    fs.writeFileSync(path.join(out, "cli-generated-manifest.json"), previous);
  } finally {
    fs.rmSync(root, { recursive: true, force: true });
  }
});
