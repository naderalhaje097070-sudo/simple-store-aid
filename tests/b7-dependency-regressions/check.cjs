/* Bounded offline regressions derived from seven official GitHub advisories.
 * No application server, credential, external request or JavaScript evaluation.
 */
const assert = require("node:assert/strict");
const path = require("node:path");
const { createRequire } = require("node:module");
const { spawnSync } = require("node:child_process");
const root = path.resolve(process.env.DEPENDENCY_TEST_ROOT || process.cwd());
const load = createRequire(path.join(root, "package.json"));
const sdk = createRequire(load.resolve("@modelcontextprotocol/sdk/package.json"));
const express = createRequire(sdk.resolve("express/package.json"));
const ajv = createRequire(sdk.resolve("ajv/package.json"));
const terser = createRequire(load.resolve("@rollup/plugin-terser"));
const uri = ajv("fast-uri");
const serialize = terser("serialize-javascript");
const { z } = load("zod");
const Ajv = sdk("ajv");
const results = [];
let compressedObservation;
function run(name, fn, advisory) {
  try {
    fn();
    results.push({ name, advisory, pass: true });
  } catch (error) {
    results.push({ name, advisory, pass: false, error: String(error.message).slice(0, 500) });
  }
}
run(
  "compressed trailing bytes preserve process and independent raw consumer",
  () => {
    const child = spawnSync(
      process.execPath,
      [path.join(__dirname, "compressed-child.cjs"), express.resolve("body-parser")],
      { encoding: "utf8", timeout: 8000, maxBuffer: 65536 },
    );
    compressedObservation = {
      status: child.status,
      signal: child.signal,
      error: child.error?.code,
      stderr: child.stderr?.slice(0, 2000),
    };
    assert.equal(child.error, undefined, `child: ${child.error}`);
    assert.equal(child.status, 0, child.stderr);
    const result = JSON.parse(child.stdout);
    assert.deepEqual(result, {
      delayedDeflate: true,
      gzip: true,
      charset: true,
      healthy: true,
      rawConsumer: true,
    });
  },
  "GHSA-27r3-jxmh-p828",
);
run(
  "bounded array rejects before element work",
  () => {
    let elements = 0;
    let later = 0;
    const element = z.string().refine(() => {
      elements++;
      return true;
    });
    const schema = z
      .array(element)
      .max(2)
      .refine(() => {
        later++;
        return true;
      });
    const result = schema.safeParse(["a", "b", "c"]);
    assert.equal(result.success, false);
    assert.deepEqual(
      result.error.issues.map((issue) => issue.code),
      ["too_big"],
    );
    assert.equal(elements, 0);
    assert.equal(later, 0);
    for (const collection of [
      z
        .set(z.string())
        .max(1)
        .safeParse(new Set([1, 2])),
      z
        .map(z.string(), z.string())
        .max(1)
        .safeParse(
          new Map([
            [1, 1],
            [2, 2],
          ]),
        ),
    ]) {
      assert.equal(collection.success, false);
      assert.deepEqual(
        collection.error.issues.map((issue) => issue.code),
        ["too_big"],
      );
    }
  },
  "GHSA-mrhx-c7xc-m3w5",
);
run(
  "encoded schemes remain inert",
  () => {
    for (const input of ["%6Aavascript:alert(1)", "%u006Aavascript:alert(1)"]) {
      assert.notEqual(uri.parse(input).scheme, "javascript");
      assert.ok(!/^javascript:/i.test(uri.normalize(input)));
      assert.throws(
        () => uri.resolve("https://example.invalid/", input),
        /URI scheme is malformed/,
      );
    }
    assert.equal(uri.equal("%68ttp://a/", "http://a/"), false);
  },
  "GHSA-w74x-v6f9-j3xg",
);
run(
  "relative normalization retains resolution target",
  () => {
    const base = "https://example.invalid/one/two/index";
    for (const ref of ["a/../b", "../x"])
      assert.equal(uri.resolve(base, uri.normalize(ref)), uri.resolve(base, ref));
    assert.equal(uri.equal("../x", "x"), false);
  },
  "GHSA-xhq7-xmqj-769h",
);
run(
  "ambiguous authority fails closed",
  () => {
    for (const input of [
      "http://a@b@evil.example/",
      "http://exam\tple.invalid/",
      "http://exam\rple.invalid/",
      "http://exam\nple.invalid/",
    ]) {
      assert.ok(uri.parse(input).error, `missing parse error for ${JSON.stringify(input)}`);
    }
  },
  "GHSA-wjr9-j795-jxcr",
);
run(
  "suffix output cannot inject scheme",
  () => {
    for (const input of ["javascript:alert(1)", "data:text/plain,a", "vbscript:msgbox(1)"]) {
      const output = uri.normalize(input, { reference: "suffix", scheme: "x" });
      assert.equal(uri.parse(output).scheme, undefined);
    }
  },
  "GHSA-333x-w4r6-6crp",
);
run(
  "serialized spoofed function cannot close HTML script",
  () => {
    function f() {}
    function g() {}
    f.toString = () => "function f(){return 1}//</script";
    g.toString = () => "function g(x){return x} > <img src=x onerror=alert(1)>";
    const output = serialize({ a: { f }, g }, { space: 2 });
    assert.ok(!/<\/script(?:[\t\n\f\r />]|$)/i.test(output));
  },
  "GHSA-m5mm-p8h7-m29v",
);
run("valid schemas transforms URI and serializer still work", () => {
  assert.deepEqual(
    z
      .array(z.number())
      .overwrite((a) => a.slice(0, 2))
      .max(2)
      .parse([1, 2, 3]),
    [1, 2],
  );
  assert.deepEqual(z.array(z.string()).max(2).parse(["a", "b"]), ["a", "b"]);
  assert.equal(
    z.map(z.string(), z.string()).max(1).safeParse(new Set()).error.issues[0].code,
    "invalid_type",
  );
  const validator = new Ajv().compile({
    $id: "https://schemas.example.invalid/item",
    type: "object",
    properties: { count: { type: "integer" } },
    required: ["count"],
    additionalProperties: false,
  });
  assert.equal(validator({ count: 2 }), true);
  assert.equal(validator({ count: "2" }), false);
  assert.equal(uri.parse("https://example.invalid/a").host, "example.invalid");
  assert.equal(uri.resolve("https://example.invalid/a/", "../b"), "https://example.invalid/b");
  assert.equal(serialize({ safe: "</script>" }).includes("</script>"), false);
  assert.equal(serialize({ a: 1 }), '{"a":1}');
});
const baseline = process.argv.includes("--baseline");
const failed = results.filter((r) => !r.pass);
const expected = new Set(results.filter((r) => r.advisory).map((r) => r.advisory));
const failures = new Set(failed.map((r) => r.advisory));
const ok = baseline
  ? expected.size === 7 &&
    expected.size === failures.size &&
    [...expected].every((x) => failures.has(x)) &&
    results.filter((r) => !r.advisory).every((r) => r.pass) &&
    compressedObservation?.status === 1 &&
    /ERR_STREAM_WRITE_AFTER_END|Z_DATA_ERROR/.test(compressedObservation.stderr)
  : failed.length === 0;
console.log(
  JSON.stringify(
    {
      mode: baseline ? "vulnerable-baseline" : "patched",
      node: process.version,
      compressedObservation,
      results,
      ok,
    },
    null,
    2,
  ),
);
process.exitCode = ok ? 0 : 1;
