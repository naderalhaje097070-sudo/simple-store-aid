// Read official npm metadata and verify actual tarball availability before choosing.
const fs = require("node:fs");
const path = require("node:path");
const crypto = require("node:crypto");
const cp = require("node:child_process");

(async () => {
  const out = path.resolve("evidence/g0-node-server");
  fs.mkdirSync(out, { recursive: true });
  const response = await fetch("https://registry.npmjs.org/@hono%2fnode-server");
  const text = await response.text();
  fs.writeFileSync(path.join(out, "registry-packument.json"), text);
  fs.writeFileSync(
    path.join(out, "registry-status.json"),
    JSON.stringify({ status: response.status, url: response.url }),
  );
  if (response.status !== 200) throw Error("Registry failure is not proof of absence");
  const metadata = JSON.parse(text);
  const fixed1 = Object.keys(metadata.versions)
    .filter(
      (v) =>
        /^1\.\d+\.\d+$/.test(v) &&
        (Number(v.split(".")[1]) > 19 ||
          (Number(v.split(".")[1]) === 19 && Number(v.split(".")[2]) >= 15)),
    )
    .sort((a, b) => a.localeCompare(b, undefined, { numeric: true }));
  const selected = fixed1[0] || "2.0.5";
  if (!metadata.versions[selected]) throw Error("No permitted published candidate");
  const rows = [];
  for (const version of ["1.19.14", selected]) {
    const manifest = metadata.versions[version];
    const tar = await fetch(manifest.dist.tarball);
    if (tar.status !== 200) throw Error("Tarball unavailable; do not infer version absence");
    const bytes = Buffer.from(await tar.arrayBuffer());
    const integrity = "sha512-" + crypto.createHash("sha512").update(bytes).digest("base64");
    if (integrity !== manifest.dist.integrity) throw Error("Tarball integrity mismatch");
    fs.writeFileSync(path.join(out, `node-server-${version}.tgz`), bytes);
    fs.writeFileSync(path.join(out, `manifest-${version}.json`), JSON.stringify(manifest, null, 2));
    rows.push({ version, url: tar.url, status: tar.status, bytes: bytes.length, integrity });
    const dir = path.join(out, "package-" + version);
    fs.mkdirSync(dir);
    cp.execFileSync("tar", ["-xzf", path.join(out, `node-server-${version}.tgz`), "-C", dir]);
  }
  fs.writeFileSync(
    path.join(out, "availability.json"),
    JSON.stringify(
      { selected, fixed1, published: metadata.time[selected], tarballs: rows },
      null,
      2,
    ),
  );
  fs.writeFileSync(path.join(out, "selected.txt"), selected + "\n");
})().catch((error) => {
  console.error(error);
  process.exitCode = 1;
});
