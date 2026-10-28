import assert from "node:assert/strict";
import { spawn } from "node:child_process";
import { once } from "node:events";
import { writeFileSync } from "node:fs";
import { createConnection } from "node:net";
import { setTimeout as pause } from "node:timers/promises";

// No real Auth, provider, database, production identity or customer data.
const origin = "http://127.0.0.1:54329";
const env = {
  ...process.env,
  HOST: "127.0.0.1",
  PORT: "54329",
  NITRO_HOST: "127.0.0.1",
  NITRO_PORT: "54329",
};
for (const key of ["LOVABLE_API_KEY", "SUPABASE_SERVICE_ROLE_KEY", "NODE_OPTIONS"]) delete env[key];
const child = spawn(process.execPath, [".output/server/index.mjs"], {
  env,
  stdio: ["ignore", "pipe", "pipe"],
});
let diagnostics = "";
for (const stream of [child.stdout, child.stderr])
  stream.on("data", (data) => {
    diagnostics = (diagnostics + data).slice(-16000);
  });
const checks = [];
async function incompleteUpload(mode) {
  const payload = mode === "declared" ? "{}" : "x".repeat(65537);
  const response = await new Promise((resolve, reject) => {
    const socket = createConnection({ host: "127.0.0.1", port: 54329 });
    let reply = "";
    const timer = setTimeout(() => {
      socket.destroy();
      reject(new Error("Refusal socket did not close after reply"));
    }, 4000);
    socket.on("data", (chunk) => {
      reply += chunk.toString();
      if (reply.length > 8192) socket.destroy(new Error("Unbounded refusal body"));
    });
    socket.on("error", reject);
    socket.on("close", () => {
      clearTimeout(timer);
      resolve(reply);
    });
    socket.on("connect", () => {
      const length =
        mode === "declared" ? "Content-Length: 1000000000" : "Transfer-Encoding: chunked";
      socket.write(
        `POST /mcp HTTP/1.1\r\nHost: 127.0.0.1:54329\r\nConnection: keep-alive\r\nContent-Type: application/json\r\n${length}\r\n\r\n`,
      );
      // Intentionally leave the declared body or final chunk unfinished.
      socket.write(
        mode === "declared" ? payload : `${payload.length.toString(16)}\r\n${payload}\r\n`,
      );
    });
  });
  assert.match(response, /^HTTP\/1\.1 413 /);
  assert.match(response, /\r\nconnection: close\r\n/i);
  assert.match(response, /\{"error":"MCP_REQUEST_LIMIT"\}/);
  checks.push({ mode, incompleteUpload: true, status: 413, socketClosedAfterResponse: true });
}
try {
  let ready = false;
  for (let i = 0; i < 100; i++) {
    if (child.exitCode !== null) throw new Error("Native server exited before readiness");
    try {
      await fetch(`${origin}/mcp`, { redirect: "error", signal: AbortSignal.timeout(300) });
      ready = true;
      break;
    } catch {
      await pause(100);
    }
  }
  assert(ready, "Native server unavailable");
  const post = (path, body) =>
    fetch(origin + path, {
      method: "POST",
      body,
      headers: {
        "content-type": "application/json",
        accept: "application/json, text/event-stream",
      },
      redirect: "manual",
      signal: AbortSignal.timeout(8000),
    });
  for (const path of [
    "/mcp",
    "/MCP",
    "/%6dcp",
    "/mcp/",
    "/.mcp/invoke-tool/list_products",
    "/%2emcp/invoke-tool/list_products",
  ]) {
    const response = await post(path, JSON.stringify({ oversized: "x".repeat(65536) }));
    assert.equal(response.status, 413, path);
    checks.push({ path, status: response.status, oversized: true });
  }
  const malformed = await post("/mcp", "private-body");
  assert.equal(malformed.status, 400);
  assert.deepEqual(await malformed.json(), { error: "MCP_REQUEST_INVALID" });
  checks.push({ path: "/mcp", malformed: true, status: malformed.status });
  await incompleteUpload("declared");
  await incompleteUpload("chunked");
  const unauth = await post(
    "/mcp",
    JSON.stringify({ jsonrpc: "2.0", id: 1, method: "tools/list", params: {} }),
  );
  assert.equal(unauth.status, 401);
  checks.push({ path: "/mcp", missingBearer: true, status: unauth.status });
  const input = await post("/mcp", JSON.stringify({ values: Array(257).fill(0) }));
  assert.equal(input.status, 413);
  checks.push({ path: "/mcp", members: true, status: input.status });
  writeFileSync(
    process.argv[2],
    JSON.stringify(
      {
        source: process.env.GITHUB_SHA,
        nativeNode: process.version,
        entry: "src/server.ts",
        checks,
        liveAuthOrProvider: false,
      },
      null,
      2,
    ) + "\n",
  );
  console.log(JSON.stringify({ nativeHTTP: checks.length, passed: true }));
} catch (error) {
  console.error(diagnostics);
  throw error;
} finally {
  child.kill("SIGTERM");
  await Promise.race([once(child, "exit"), pause(3000)]);
  if (child.exitCode === null) child.kill("SIGKILL");
}
