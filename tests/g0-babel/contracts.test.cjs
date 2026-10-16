const { test } = require("node:test");
const assert = require("node:assert/strict");
const fs = require("node:fs");
const os = require("node:os");
const path = require("node:path");
const { createRequire } = require("node:module");

const parents = [
  "@vitejs/plugin-react",
  "babel-dead-code-elimination",
  "workbox-build",
  "@tanstack/router-plugin",
  "@tanstack/start-plugin-core",
];
const copies = new Map();
for (const parent of parents) {
  const from = createRequire(path.join(process.cwd(), "node_modules", parent, "package.json"));
  const entry = from.resolve("@babel/core");
  const current = copies.get(entry) || { babel: from("@babel/core"), parents: [] };
  current.parents.push(parent);
  copies.set(entry, current);
}
assert(copies.size > 0, "No actual installed Babel copy");
const summary = [];

for (const [entry, { babel, parents: resolvedParents }] of copies) {
  const label = `${babel.version}:${resolvedParents.join(",")}`;
  const cases = [
    "outside-relative",
    "outside-absolute",
    "sibling-map",
    "parent-within-package",
    "inline-map",
    "plain-source",
  ];
  for (const kind of cases) {
    test(`${label} ${kind}`, () => {
      const temp = fs.mkdtempSync(path.join(os.tmpdir(), "g0-babel-map-"));
      try {
        const project = path.join(temp, "package");
        const sourceDir = path.join(project, "src");
        fs.mkdirSync(sourceDir, { recursive: true });
        fs.writeFileSync(
          path.join(project, "package.json"),
          '{"name":"local-map-fixture","private":true}',
        );
        const marker = `LOCAL_ONLY_${kind.replaceAll("-", "_")}_MARKER`;
        const map = {
          version: 3,
          sources: ["original.js"],
          names: [],
          mappings: "AAAA",
          sourcesContent: [marker],
        };
        let input = "const answer = 42;";
        let mapPath;
        if (kind.startsWith("outside")) mapPath = path.join(temp, "outside.map");
        if (kind === "sibling-map") mapPath = path.join(sourceDir, "sibling.map");
        if (kind === "parent-within-package") mapPath = path.join(project, "original.map");
        if (mapPath) {
          fs.writeFileSync(mapPath, JSON.stringify(map));
          const ref =
            kind === "outside-absolute"
              ? mapPath
              : path.relative(sourceDir, mapPath).split(path.sep).join("/");
          input += `\n//# sourceMappingURL=${ref}`;
        }
        if (kind === "inline-map")
          input += `\n//# sourceMappingURL=data:application/json;base64,${Buffer.from(JSON.stringify(map)).toString("base64")}`;
        // inputSourceMap stays at the default automatic behavior, never false.
        const output = babel.transformSync(input, {
          filename: path.join(sourceDir, "input.js"),
          root: project,
          configFile: false,
          babelrc: false,
          sourceMaps: true,
        });
        assert(
          output.map && output.code.includes("const answer = 42;"),
          "Ordinary transform/maps lost",
        );
        const containsMarker = output.map.sourcesContent?.includes(marker) === true;
        summary.push({
          entry,
          version: babel.version,
          parents: resolvedParents,
          kind,
          containsMarker,
          sourcesContent: output.map.sourcesContent,
        });
        if (kind.startsWith("outside"))
          assert.equal(containsMarker, false, "outside-root source map marker disclosed");
        else if (kind === "plain-source") assert.deepEqual(output.map.sourcesContent, [input]);
        else assert.equal(containsMarker, true, "legitimate source map was not retained");
      } finally {
        fs.rmSync(temp, { recursive: true, force: true });
      }
    });
  }
}

process.on("exit", () => {
  fs.mkdirSync("evidence/g0-babel", { recursive: true });
  fs.writeFileSync(
    "evidence/g0-babel/map-observations.json",
    JSON.stringify(summary, null, 2) + "\n",
  );
});
