// Verify the local package's published CJS/ESM APIs and actual resolution.
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { pathToFileURL } = require("node:url");
const { createRequire } = require("node:module");
const load = createRequire(path.join(process.cwd(), "package.json"));
const cjsFile = load.resolve("@rollup/plugin-node-resolve");
const cjs = load("@rollup/plugin-node-resolve");
const expected = {
  dedupe: [],
  extensions: [".mjs", ".js", ".json", ".node"],
  resolveOnly: [],
  moduleDirectories: ["node_modules"],
  modulePaths: [],
  ignoreSideEffectsForRoot: false,
  allowExportsFolderMapping: true,
};
async function main() {
  const esmFile = path.resolve(path.dirname(cjsFile), "../es/index.js");
  const esm = await import(pathToFileURL(esmFile).href);
  const directory = fs.mkdtempSync(path.join(os.tmpdir(), "b7-rollup-"));
  const { rollup } = load("rollup");
  const receipt = [];
  try {
    const packageDirectory = path.join(directory, "node_modules", "b7-fixture");
    fs.mkdirSync(packageDirectory, { recursive: true });
    fs.writeFileSync(
      path.join(packageDirectory, "package.json"),
      JSON.stringify({
        name: "b7-fixture",
        version: "1.0.0",
        type: "module",
        exports: "./index.js",
      }),
    );
    fs.writeFileSync(path.join(packageDirectory, "index.js"), "export const value = 37;\n");
    const entry = path.join(directory, "entry.mjs");
    fs.writeFileSync(entry, 'import { value } from "b7-fixture"; export { value };\n');
    for (const [kind, api] of [
      ["CommonJS", cjs],
      ["ESM", esm],
    ]) {
      assert.deepEqual(api.DEFAULTS, expected);
      assert.equal(Object.isFrozen(api.DEFAULTS), true);
      for (const value of Object.values(api.DEFAULTS)) {
        if (Array.isArray(value)) assert.equal(Object.isFrozen(value), true);
      }
      const copy = api.nodeResolve({ extensions: [".mjs"], moduleDirectories: ["custom"] });
      assert.equal(copy.name, "node-resolve");
      assert.deepEqual(api.DEFAULTS, expected);
      const warnings = [];
      const bundle = await rollup({
        input: entry,
        plugins: [api.nodeResolve()],
        onwarn: (warning) => warnings.push(warning.code),
      });
      try {
        const result = await bundle.generate({ format: "es" });
        assert.deepEqual(warnings, []);
        assert.equal(result.output.length, 1);
        assert.equal(result.output[0].imports.length, 0);
        assert.match(result.output[0].code, /37/);
        assert.match(result.output[0].code, /export/);
      } finally {
        await bundle.close();
      }
      receipt.push({
        kind,
        defaults: true,
        nestedFrozen: true,
        instanceIsolation: true,
        actualPackageResolution: true,
      });
    }
    assert.notEqual(cjs.DEFAULTS, esm.DEFAULTS);
    assert.notEqual(cjs.DEFAULTS.extensions, esm.DEFAULTS.extensions);
    console.log(JSON.stringify({ ok: true, node: process.version, receipt }, null, 2));
  } finally {
    fs.rmSync(directory, { recursive: true, force: true });
  }
}
main().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
