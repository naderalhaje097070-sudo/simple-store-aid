import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";

// GHSA-qx66-fv34-fjm8: check every locked copy, including nested resolutions.
// This guards dependency regressions; it does not replace runtime security tests.
const lock = readFileSync(new URL("../../bun.lock", import.meta.url), "utf8");
const patchedPackages = [
  { name: "@tanstack/react-start", minimum: [1, 168, 60] },
  { name: "@tanstack/start-server-core", minimum: [1, 169, 39] },
  // GHSA-p6vx-979v-rg4c: the framework's serializer must also be patched.
  { name: "seroval", minimum: [1, 6, 11] },
  // PRIMARY-SEC-002: registry Critical/High dependency advisories triaged on 2026-10-10.
  { name: "@modelcontextprotocol/sdk", minimum: [1, 32, 0] },
  { name: "vite", minimum: [8, 1, 6] },
  { name: "launch-editor", minimum: [2, 14, 2] },
  { name: "browserslist", minimum: [4, 28, 7] },
  { name: "fast-uri", minimum: [3, 1, 8] },
  { name: "ip-address", minimum: [10, 7, 4] },
  { name: "js-yaml", minimum: [4, 3, 2] },
  { name: "nanoid", minimum: [3, 3, 18] },
  { name: "postcss", minimum: [8, 5, 18] },
  { name: "proxy-addr", minimum: [2, 0, 8] },
  { name: "shell-quote", minimum: [1, 11, 0] },
  { name: "source-map-js", minimum: [1, 2, 2] },
];

const patchedPackageMajors = new Map([
  // SEC-DEP-20261102: exact owner-authorized matching engines and interop patch.
  ["glob", new Map([[14, [14, 0, 2]]])],
  ["minimatch", new Map([[11, [11, 0, 1]]])],
  // SEC-DEP-20261029: old1.x is affected; SDK1.32 explicitly permits patched2.x.
  ["@hono/node-server", new Map([[2, [2, 1, 3]]])],
  // G0-BABEL-01: all copies must stay on the stable patched Babel 7.x line.
  ["@babel/core", new Map([[7, [7, 29, 6]]])],
  // G0-DOMPURIFY-01: cover every optional or nested stable 3.x sanitizer copy.
  ["dompurify", new Map([[3, [3, 4, 17]]])],
  // G0-QS-01: preserve the reviewed stable 6.x parser/serializer security floor.
  ["qs", new Map([[6, [6, 16, 0]]])],
  // G0-HONO-01: all copies must stay on the reviewed, patched stable 4.x line.
  ["hono", new Map([[4, [4, 13, 11]]])],
  [
    "brace-expansion",
    new Map([
      [1, [1, 1, 21]],
      [2, [2, 1, 7]],
      [5, [5, 0, 12]],
    ]),
  ],
]);

describe("TanStack server-function XSS dependency boundary", () => {
  for (const { name, minimum } of patchedPackages) {
    test(`${name} has no vulnerable locked copy`, () => {
      const pattern = new RegExp(String.raw`\[\s*"${name}@([^"]+)"`, "g");
      const versions = [...lock.matchAll(pattern)].map((match) => match[1]);
      expect(versions.length).toBeGreaterThan(0);

      for (const version of versions) {
        // Unreviewed prereleases must not silently satisfy this release gate.
        expect(version).toMatch(/^\d+\.\d+\.\d+$/);
        const [major, minor, patch] = version.split(".").map(Number);
        const [minMajor, minMinor, minPatch] = minimum;
        const safe =
          major > minMajor ||
          (major === minMajor && (minor > minMinor || (minor === minMinor && patch >= minPatch)));
        expect({ package: name, version, safe }).toEqual({ package: name, version, safe: true });
      }
    });
  }

  for (const [name, minimumByMajor] of patchedPackageMajors) {
    test(`${name} has no vulnerable locked copy`, () => {
      const pattern = new RegExp(String.raw`\[\s*"${name}@([^"]+)"`, "g");
      const versions = [...lock.matchAll(pattern)].map((match) => match[1]);
      expect(versions.length).toBeGreaterThan(0);

      for (const version of versions) {
        expect(version).toMatch(/^\d+\.\d+\.\d+$/);
        const [major, minor, patch] = version.split(".").map(Number);
        const minimum = minimumByMajor.get(major);
        expect({ package: name, version, supportedMajor: Boolean(minimum) }).toEqual({
          package: name,
          version,
          supportedMajor: true,
        });

        const [minMajor, minMinor, minPatch] = minimum!;
        const safe =
          major > minMajor ||
          (major === minMajor && (minor > minMinor || (minor === minMinor && patch >= minPatch)));
        expect({ package: name, version, safe }).toEqual({ package: name, version, safe: true });
      }
    });
  }
});

// G0-ESBUILD-COMPAT-PROOF-01: exact owner-authorized exception beyond MCP ^0.27.0.
// Every JS wrapper and platform binary stays on the same reviewed fixed version.
test("esbuild exception has no vulnerable or mismatched locked copy", () => {
  const wrappers = [...lock.matchAll(/\[\s*"esbuild@([^"]+)"/g)].map((match) => match[1]);
  const platforms = [...lock.matchAll(/\[\s*"@esbuild\/[^@"]+@([^"]+)"/g)].map((match) => match[1]);
  expect(wrappers.length).toBeGreaterThan(0);
  expect(platforms.length).toBe(26);
  for (const version of [...wrappers, ...platforms]) expect(version).toBe("0.28.1");
});

test("owner-authorized glob and minimatch exception stays exact with its interop patch", () => {
  const pkg = JSON.parse(readFileSync(new URL("../../package.json", import.meta.url), "utf8"));
  for (const group of ["overrides", "resolutions"]) {
    expect(pkg[group].glob).toBe("14.0.2");
    expect(pkg[group].minimatch).toBe("11.0.1");
  }
  expect(pkg.patchedDependencies).toEqual({
    "minimatch@11.0.1": "patches/minimatch@11.0.1.patch",
  });
  const patch = readFileSync(new URL("../../patches/minimatch@11.0.1.patch", import.meta.url));
  expect(createHash("sha256").update(patch).digest("hex")).toBe(
    "1c2e49a5e9608bdf3b904c9f3ee62b02cc8677e46167ec9d70f117cd3dc07015",
  );
  for (const [name, expected] of [
    ["glob", "14.0.2"],
    ["minimatch", "11.0.1"],
  ]) {
    const copies = [...lock.matchAll(new RegExp(String.raw`\[\s*"${name}@([^"]+)"`, "g"))].map(
      (match) => match[1],
    );
    expect(copies.length).toBeGreaterThan(0);
    for (const version of copies) expect(version).toBe(expected);
  }
});
