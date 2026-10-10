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
  { name: "@modelcontextprotocol/sdk", minimum: [1, 31, 0] },
  { name: "browserslist", minimum: [4, 28, 7] },
  { name: "fast-uri", minimum: [3, 1, 8] },
  { name: "ip-address", minimum: [10, 7, 1] },
  { name: "js-yaml", minimum: [4, 3, 2] },
  { name: "nanoid", minimum: [3, 3, 18] },
  { name: "postcss", minimum: [8, 5, 18] },
  { name: "proxy-addr", minimum: [2, 0, 8] },
  { name: "shell-quote", minimum: [1, 11, 0] },
  { name: "source-map-js", minimum: [1, 2, 2] },
];

const patchedPackageMajors = new Map([
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
