import { spawnSync } from "node:child_process";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const vite = fileURLToPath(new URL("../node_modules/vite/bin/vite.js", import.meta.url));
const build = spawnSync(process.execPath, [vite, "build", ...process.argv.slice(2)], {
  cwd: root,
  stdio: "inherit",
});
if (build.error) throw build.error;
if (build.status !== 0) process.exit(build.status ?? 1);

// MCP writes its generated routes during the real Vite build. Normalize only
// reviewed generator outputs afterward; an unknown output fails the build.
const format = spawnSync(
  process.execPath,
  [fileURLToPath(new URL("./format-generated.mjs", import.meta.url))],
  { cwd: root, stdio: "inherit" },
);
if (format.error) throw format.error;
process.exit(format.status ?? 1);
