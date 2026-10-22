import { getNormalizedURL } from "@tanstack/router-core/ssr/server";

// The four read-only tools accept at most two scalar arguments. Bound the whole
// envelope before the SDK's schema validator; mcp-js 0.20.1 exposes no SDK limits.
export const MCP_REQUEST_BYTES = 64 * 1024;
export const MCP_REQUEST_MEMBERS = 256;
export const MCP_REQUEST_DEPTH = 32;
export const MCP_READ_DEADLINE_MS = 5_000;

function rejection(status: number): Response {
  return Response.json(
    { error: status === 413 ? "MCP_REQUEST_LIMIT" : "MCP_REQUEST_INVALID" },
    { status, headers: { "cache-control": "no-store" } },
  );
}

function rejectUnread(request: Request, status: number): Response {
  // Do not wait for a client-controlled cancellation promise on early refusal.
  if (request.body && !request.body.locked) void request.body.cancel().catch(() => {});
  return rejection(status);
}

function isMcpPost(request: Request): boolean {
  if (request.method !== "POST") return false;
  // Use the same public normalizer as Start's request entry. Static routes are
  // case-insensitive; decoding twice would disagree with the router.
  const pathname = getNormalizedURL(request.url).url.pathname.replace(/\/+$/, "").toLowerCase();
  return pathname === "/mcp" || pathname.startsWith("/.mcp/invoke-tool/");
}

function withinStructureLimit(value: unknown): boolean {
  const pending: { value: unknown; depth: number }[] = [{ value, depth: 0 }];
  let members = 0;
  while (pending.length) {
    const current = pending.pop()!;
    if (current.value === null || typeof current.value !== "object") continue;
    if (current.depth > MCP_REQUEST_DEPTH) return false;
    const children = Object.values(current.value);
    members += children.length;
    if (members > MCP_REQUEST_MEMBERS) return false;
    for (const child of children) pending.push({ value: child, depth: current.depth + 1 });
  }
  return true;
}

export async function boundMcpRequest(request: Request): Promise<Request | Response> {
  if (!isMcpPost(request)) return request;
  const declared = request.headers.get("content-length");
  if (declared !== null && (!/^\d+$/.test(declared) || !Number.isSafeInteger(Number(declared)))) {
    return rejectUnread(request, 400);
  }
  if (declared !== null && Number(declared) > MCP_REQUEST_BYTES) return rejectUnread(request, 413);
  if (!request.body || request.bodyUsed || request.body.locked || request.signal.aborted) {
    return rejectUnread(request, 400);
  }

  const reader = request.body.getReader();
  const bytes = new Uint8Array(MCP_REQUEST_BYTES);
  let size = 0;
  let timer: ReturnType<typeof setTimeout> | undefined;
  let interrupt: (reason: number) => void = () => {};
  const interrupted = new Promise<number>((resolve) => {
    interrupt = resolve;
    timer = setTimeout(() => resolve(408), MCP_READ_DEADLINE_MS);
  });
  const abort = () => interrupt(400);
  request.signal.addEventListener("abort", abort, { once: true });
  try {
    while (true) {
      const next = await Promise.race([reader.read(), interrupted]);
      if (typeof next === "number") return rejection(next);
      if (next.done) break;
      if (size + next.value.byteLength > MCP_REQUEST_BYTES) return rejection(413);
      bytes.set(next.value, size);
      size += next.value.byteLength;
    }
    if (request.signal.aborted) return rejection(400);
    const body = bytes.slice(0, size);
    let input: unknown;
    try {
      input = JSON.parse(new TextDecoder("utf-8", { fatal: true }).decode(body));
    } catch {
      return rejection(400);
    }
    if (!withinStructureLimit(input)) return rejection(413);
    // Replay the original bytes, headers and abort signal to existing auth and
    // protocol handlers. Do not reserialize, log inputs, or change non-MCP flows.
    return new Request(request, { body });
  } catch {
    return rejection(400);
  } finally {
    if (timer !== undefined) clearTimeout(timer);
    request.signal.removeEventListener("abort", abort);
    // A client-controlled stalled stream must not hold a rejection open.
    void reader.cancel().catch(() => {});
    reader.releaseLock();
  }
}
