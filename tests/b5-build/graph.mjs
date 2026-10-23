// Diagnostic only: parse actual emitted modules; never execute the app or access a database.
import { readFileSync, writeFileSync, readdirSync, existsSync } from "node:fs";
import { resolve, dirname, relative } from "node:path";
import { createRequire } from "node:module";
import { createHash } from "node:crypto";

const require = createRequire(resolve("package.json"));
const { parse } = require("acorn");
const root = resolve(".output/server");
const sha = (bytes) => createHash("sha256").update(bytes).digest("hex");
const files = [];
function visit(dir) {
  for (const entry of readdirSync(dir, { withFileTypes: true })) {
    const path = resolve(dir, entry.name);
    if (entry.isDirectory()) visit(path);
    else if (path.endsWith(".mjs") || path.endsWith(".js")) files.push(path);
  }
}
visit(root);
const modules = {};
for (const path of files) {
  const source = readFileSync(path, "utf8");
  const ast = parse(source, { ecmaVersion: "latest", sourceType: "module", locations: true });
  const item = {
    sha256: sha(source),
    bytes: Buffer.byteLength(source),
    static_imports: [],
    dynamic_imports: [],
    helper_definitions: [],
    helper_imports: [],
    helper_calls: [],
    helper_exports: [],
  };
  const name = relative(root, path);
  function target(value) {
    if (!value.startsWith(".")) return { external: value };
    return {
      module: relative(root, resolve(dirname(path), value)),
      exists: existsSync(resolve(dirname(path), value)),
    };
  }
  function walk(node, functionDepth = 0) {
    if (!node || typeof node !== "object") return;
    if (node.type === "ImportDeclaration") {
      item.static_imports.push(target(node.source.value));
      for (const s of node.specifiers) {
        if (/^__commonJS(?:Min)?$/.test(s.local.name))
          item.helper_imports.push({
            local: s.local.name,
            imported: s.imported?.name,
            from: target(node.source.value),
            line: node.loc.start.line,
          });
      }
    }
    if (node.type === "ExportNamedDeclaration") {
      if (node.source) item.static_imports.push(target(node.source.value));
      for (const s of node.specifiers)
        if (/^__commonJS(?:Min)?$/.test(s.local.name))
          item.helper_exports.push({
            local: s.local.name,
            exported: s.exported.name,
            line: node.loc.start.line,
          });
    }
    if (node.type === "ExportAllDeclaration") item.static_imports.push(target(node.source.value));
    if (node.type === "ImportExpression" && typeof node.source.value === "string")
      item.dynamic_imports.push(target(node.source.value));
    if (node.type === "VariableDeclarator" && /^__commonJS(?:Min)?$/.test(node.id.name ?? ""))
      item.helper_definitions.push({
        name: node.id.name,
        kind: node.init?.type,
        line: node.loc.start.line,
      });
    if (node.type === "CallExpression" && /^__commonJS(?:Min)?$/.test(node.callee.name ?? ""))
      item.helper_calls.push({
        name: node.callee.name,
        line: node.loc.start.line,
        direct_top_level: functionDepth === 0,
      });
    const childDepth =
      functionDepth +
      (/^(?:FunctionDeclaration|FunctionExpression|ArrowFunctionExpression)$/.test(node.type)
        ? 1
        : 0);
    for (const [key, value] of Object.entries(node)) {
      if (key === "loc") continue;
      if (Array.isArray(value)) value.forEach((child) => walk(child, childDepth));
      else if (value && typeof value === "object") walk(value, childDepth);
    }
  }
  walk(ast);
  modules[name] = item;
}
function staticPath(from, to, seen = new Set()) {
  if (from === to) return [to];
  if (seen.has(from)) return null;
  seen.add(from);
  for (const edge of modules[from]?.static_imports ?? []) {
    if (!edge.module) continue;
    const path = staticPath(edge.module, to, seen);
    if (path) return [from, ...path];
  }
  return null;
}
const helper_cycles = [];
for (const [name, item] of Object.entries(modules)) {
  for (const binding of item.helper_imports) {
    const owner = binding.from.module;
    const definition = modules[owner]?.helper_exports.find((x) => x.exported === binding.imported);
    const cycle = owner && definition && staticPath(owner, name);
    if (cycle)
      helper_cycles.push({ consumer: name, binding, definition, static_cycle: [name, ...cycle] });
  }
}
const resolvePackage = (name, from) => {
  const r = createRequire(from);
  const path = r.resolve(name + "/package.json");
  return {
    path: relative(process.cwd(), path),
    version: JSON.parse(readFileSync(path, "utf8")).version,
  };
};
const public_hashes = {};
function hashPublic(dir) {
  for (const e of readdirSync(dir, { withFileTypes: true })) {
    const p = resolve(dir, e.name);
    if (e.isDirectory()) hashPublic(p);
    else public_hashes[relative(resolve(".output/public"), p)] = sha(readFileSync(p));
  }
}
hashPublic(resolve(".output/public"));
const record = {
  diagnostic_only: true,
  source: process.env.EXPECTED_SOURCE,
  variant: process.env.B5_BUILD_VARIANT,
  no_database_or_app_execution: true,
  packages: {
    vite: resolvePackage("vite", resolve("package.json")),
    root_rolldown: resolvePackage("rolldown", resolve("package.json")),
    vite_rolldown: resolvePackage("rolldown", require.resolve("vite/package.json")),
    nitro: resolvePackage("nitro", resolve("package.json")),
    nitro_rolldown: resolvePackage("rolldown", require.resolve("nitro/package.json")),
  },
  helper_cycles,
  eager_helper_cycles: helper_cycles.filter(
    (cycle) =>
      modules[cycle.consumer].helper_calls.some(
        (call) => call.name === cycle.binding.local && call.direct_top_level,
      ) &&
      modules[cycle.binding.from.module].helper_definitions.some(
        (definition) =>
          definition.name === cycle.definition.local &&
          definition.kind === "ArrowFunctionExpression",
      ),
  ),
  scope:
    "Direct module-level helper calls only; deferred function calls and unknown aliases are not classified as eager. Static export-all edges included.",
  public_hashes,
  modules,
};
writeFileSync(process.argv[2], JSON.stringify(record, null, 2) + "\n");
console.log(
  JSON.stringify({
    variant: record.variant,
    modules: files.length,
    helper_cycles: helper_cycles.length,
    packages: record.packages,
  }),
);
if (process.argv.includes("--require-no-eager-cycle") && record.eager_helper_cycles.length)
  process.exitCode = 1;
