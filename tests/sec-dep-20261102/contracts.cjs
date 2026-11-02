const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const crypto = require("node:crypto");
const vm = require("node:vm");
const { createRequire } = require("node:module");
const { pathToFileURL } = require("node:url");
const { test, after } = require("node:test");
const ts = require("typescript");
const minimatch = require("minimatch");
const glob = require("glob");

const root = fs.mkdtempSync(path.join(os.tmpdir(), "monjez-sec-20261102-"));
const files = path.join(root, "files");
fs.mkdirSync(files);
for (const [name, body] of [
  ["a.js", "alpha"],
  ["b.css", "beta"],
  ["skip.js", "skip"],
  [".hidden.js", "hidden"],
  ["sub/c.js", "child"],
]) {
  const file = path.join(files, name);
  fs.mkdirSync(path.dirname(file), { recursive: true });
  fs.writeFileSync(file, body);
}
after(() => fs.rmSync(root, { recursive: true, force: true }));

function packageRoot(name) {
  let folder = path.dirname(require.resolve(name));
  for (let n = 0; n < 15; n++) {
    const file = path.join(folder, "package.json");
    if (fs.existsSync(file) && JSON.parse(fs.readFileSync(file, "utf8")).name === name)
      return folder;
    const parent = path.dirname(folder);
    if (parent === folder) break;
    folder = parent;
  }
  throw Error("Cannot locate actual installed package " + name);
}

test("fixed installed versions retain callable and named minimatch imports", () => {
  assert.equal(
    JSON.parse(fs.readFileSync(path.join(packageRoot("minimatch"), "package.json"))).version,
    "11.0.1",
  );
  assert.equal(
    JSON.parse(fs.readFileSync(path.join(packageRoot("glob"), "package.json"))).version,
    "14.0.2",
  );
  assert.equal(typeof minimatch, "function");
  assert.equal(minimatch.minimatch, minimatch);
  assert.equal(minimatch("x.js", "*.js"), true);
  assert.equal(minimatch("x.css", "*.js"), false);
  assert.equal(minimatch.minimatch(".config.ts", "*.ts", { dot: true }), true);
});

test("actual CJS config-array keeps positive and ignored selection", () => {
  const { ConfigArray } = require("@eslint/config-array");
  const configs = new ConfigArray([{ files: ["**/*.js"], ignores: ["**/skip.js"], tag: "js" }], {
    basePath: files,
    schema: { tag: { merge: "replace", validate: "string" } },
  });
  configs.normalizeSync();
  assert.equal(configs.getConfig(path.join(files, "a.js")).tag, "js");
  assert.equal(configs.getConfig(path.join(files, "b.css")), undefined);
  assert.equal(configs.getConfig(path.join(files, "skip.js")), undefined);
});

test("actual ESM config-array loads through its real default import", async () => {
  const file = path.join(packageRoot("@eslint/config-array"), "dist/esm/index.js");
  const { ConfigArray } = await import(pathToFileURL(file).href);
  assert.equal(typeof ConfigArray, "function");
});

test("actual eslintrc ESM override tester retains include exclude and parent denial", async () => {
  const file = path.join(packageRoot("@eslint/eslintrc"), "lib/config-array/override-tester.js");
  const { OverrideTester } = await import(pathToFileURL(file).href);
  const selector = OverrideTester.create(["**/*.js"], ["**/skip.js"], files);
  assert.equal(selector.test(path.join(files, "a.js")), true);
  assert.equal(selector.test(path.join(files, "b.css")), false);
  assert.equal(selector.test(path.join(files, "skip.js")), false);
  assert.throws(() => OverrideTester.create(["../*.js"], [], files), /Invalid override pattern/);
});

test("actual filelist retains legacy namespace matching behavior", () => {
  const { FileList } = require("filelist");
  const actual = new FileList(path.join(files, "**/*.js"))
    .toArray()
    .map((f) => path.relative(files, f))
    .sort();
  assert.deepEqual(actual, ["a.js", "skip.js", "sub/c.js"]);
});

test("actual TypeScript-estree selected match function uses the installed named engine", () => {
  const file = path.join(
    packageRoot("@typescript-eslint/typescript-estree"),
    "dist/useProgramFromProjectService.js",
  );
  const source = fs.readFileSync(file, "utf8");
  const ast = ts.createSourceFile(file, source, ts.ScriptTarget.Latest, true, ts.ScriptKind.JS);
  const matches = ast.statements.filter(
    (node) => ts.isFunctionDeclaration(node) && node.name?.text === "filePathMatchedBy",
  );
  assert.equal(matches.length, 1);
  const context = { minimatch_1: minimatch };
  vm.runInNewContext(matches[0].getText(ast) + "\nthis.match=filePathMatchedBy;", context, {
    timeout: 1000,
  });
  assert.equal(context.match(".config.ts", ["*.ts"]), true);
  assert.equal(context.match("x.css", ["*.ts"]), false);
  assert.equal(context.match("x.ts", undefined), false);
});

test("actual glob synchronous and asynchronous contracts preserve ignored files", async () => {
  const options = { cwd: files, ignore: ["**/skip.js"] };
  assert.deepEqual(glob.globSync("**/*.js", options).sort(), ["a.js", "sub/c.js"]);
  assert.deepEqual((await glob.glob("**/*.js", options)).sort(), ["a.js", "sub/c.js"]);
});

test("actual complete Workbox getFileDetails module retains file size and hash", () => {
  const file = path.join(packageRoot("workbox-build"), "build/lib/get-file-details.js");
  const { getFileDetails } = require(file);
  const result = getFileDetails({
    globDirectory: files,
    globPattern: "**/*.js",
    globFollow: false,
    globIgnores: ["**/skip.js"],
  });
  const hash = (text) => crypto.createHash("md5").update(text).digest("hex");
  assert.deepEqual(
    result.globbedFileDetails.sort((a, b) => a.file.localeCompare(b.file)),
    [
      { file: "a.js", size: 5, hash: hash("alpha") },
      { file: "sub/c.js", size: 5, hash: hash("child") },
    ],
  );
  assert.equal(result.warning, "");
});

test("fixed minimatch enforces the configured preprocessing cap and quadratic cutoff", () => {
  const pattern = Array.from({ length: 5 }, (_, i) => `**/../x${i}/y${i}/`).join("") + "file.js";
  const capped = new minimatch.Minimatch(pattern, { optimizationLevel: 2, braceExpandMax: 8 });
  assert.ok(capped.globParts.length <= 8);
  const single = new minimatch.Minimatch("literal");
  let comparisons = 0;
  single.partsMatch = () => {
    comparisons++;
    return false;
  };
  single.secondPhasePreProcess(Array.from({ length: 1001 }, (_, i) => ["literal" + i]));
  assert.equal(comparisons, 0);
});

test("fixed glob stops real dummy-tree work after cancellation", async () => {
  const tree = path.join(root, "abort-tree");
  function seed(dir, depth) {
    fs.mkdirSync(dir, { recursive: true });
    fs.writeFileSync(path.join(dir, "dummy.js"), "dummy");
    if (depth) for (let i = 0; i < 2; i++) seed(path.join(dir, "child" + i), depth - 1);
  }
  seed(tree, 3);
  const controller = new AbortController();
  let calls = 0,
    pending = 0;
  const instrumented = {
    ...fs,
    readdir(...args) {
      calls++;
      pending++;
      const callback = args.pop();
      fs.readdir(...args, (...reply) => {
        pending--;
        if (calls === 1) controller.abort(new Error("bounded SEC cancellation"));
        callback(...reply);
      });
    },
  };
  await assert.rejects(
    glob.glob("**/*.js", { cwd: tree, fs: instrumented, signal: controller.signal }),
    /bounded SEC cancellation/,
  );
  const rejectedAt = calls;
  await new Promise((resolve) => setTimeout(resolve, 100));
  assert.equal(rejectedAt, 1);
  assert.equal(calls, rejectedAt);
  assert.equal(pending, 0);
});

test("removing only the interop addition reproduces the original CJS callable failure", () => {
  const file = path.join(packageRoot("minimatch"), "dist/commonjs/index.js");
  const source = fs.readFileSync(file, "utf8");
  const statement = "module.exports = Object.assign(exports.minimatch, exports);";
  assert.ok(source.includes(statement));
  const module = { exports: {} };
  const context = {
    module,
    exports: module.exports,
    require: createRequire(file),
    process,
    console,
  };
  vm.runInNewContext(source.replace(statement, ""), context, { filename: file, timeout: 1000 });
  assert.equal(typeof module.exports.minimatch, "function");
  assert.equal(typeof module.exports, "object");
  assert.throws(() => module.exports("a.js", "*.js"), /not a function/);
});
