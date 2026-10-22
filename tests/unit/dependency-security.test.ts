import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";

// GHSA-qx66-fv34-fjm8: check every locked copy, including nested resolutions.
// This guards dependency regressions; it does not replace runtime security tests.
const lock = readFileSync(new URL("../../bun.lock", import.meta.url), "utf8");
const patchedPackages = [
  { name: "@tanstack/react-start", minimum: [1, 168, 60] },
  { name: "@tanstack/start-server-core", minimum: [1, 169, 39] },
  // GHSA-p6vx-979v-rg4c: the framework's serializer must also be patched.
  { name: "seroval", minimum: [1, 6, 2] },
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
  // G0-NODE-SERVER-01: include nested copies and keep the reviewed stable 1.x line.
  ["@hono/node-server", new Map([[1, [1, 19, 15]]])],
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
