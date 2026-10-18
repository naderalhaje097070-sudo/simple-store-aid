import assert from "node:assert/strict";
import { createHash } from "node:crypto";
import fs from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";
import * as prettier from "prettier";

// Repeatable postprocessing of reviewed generator outputs. This does not alter
// Lovable's upstream generator or accept newly generated code without review.
const root = fileURLToPath(new URL("../", import.meta.url));
const manifest = JSON.parse(
  await fs.readFile(new URL("./generated-format-manifest.json", import.meta.url), "utf8"),
);
const allowed = new Set([
  "src/integrations/lovable/index.ts",
  "src/integrations/supabase/auth-attacher.ts",
  "src/integrations/supabase/auth-middleware.ts",
  "src/integrations/supabase/client.server.ts",
  "src/integrations/supabase/client.ts",
  "src/routes/[.mcp]/invoke-tool/$tool.ts",
  "src/routes/[.mcp]/list-tools.ts",
  "src/routes/[.well-known]/oauth-protected-resource.ts",
  "src/routes/mcp.ts",
]);
assert.equal(prettier.version, manifest.formatter, "Unreviewed formatter version");
assert.equal(manifest.files.length, allowed.size, "Generated scope must contain nine unique paths");
const check = process.argv.includes("--check");
assert(process.argv.slice(2).every((arg) => arg === "--check"), "Unknown argument");
const digest = (data) => createHash("sha256").update(data).digest("hex");
const pending = [];
for (const item of manifest.files) {
  assert(allowed.delete(item.path), "Unexpected or duplicate generated path");
  const file = path.join(root, item.path);
  assert(!(await fs.lstat(file)).isSymbolicLink(), "Generated paths must be regular files");
  const before = await fs.readFile(file, "utf8");
  const hash = digest(before);
  assert(
    hash === item.beforeSha256 || hash === item.afterSha256,
    `Unreviewed generated input: ${item.path}`,
  );
  const config = await prettier.resolveConfig(file);
  const after = await prettier.format(before, { ...config, filepath: file });
  assert.equal(digest(after), item.afterSha256, `Unexpected generated output: ${item.path}`);
  if (check) assert.equal(before, after, `Generated formatting required: ${item.path}`);
  pending.push({ file, after });
}
assert.equal(allowed.size, 0, "Missing generated path");
// Validate the complete batch before writing anything.
if (!check) for (const item of pending) await fs.writeFile(item.file, item.after);
console.log(`GENERATED_FORMAT_${check ? "CHECK" : "WRITE"}_PASS: ${pending.length}`);
