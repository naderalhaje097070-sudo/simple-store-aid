import { expect, test } from "bun:test";
import {
  boundMcpRequest,
  MCP_REQUEST_BYTES,
  MCP_REQUEST_DEPTH,
  MCP_REQUEST_MEMBERS,
} from "../../src/lib/mcp/request-boundary";

function post(body: string, path = "/mcp", headers: Record<string, string> = {}) {
  return new Request(`http://127.0.0.1${path}`, { method: "POST", body, headers });
}

function streamed(chunks: Uint8Array[], headers: Record<string, string> = {}) {
  let canceled = false;
  const body = new ReadableStream<Uint8Array>({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(chunk);
      controller.close();
    },
    cancel() {
      canceled = true;
    },
  });
  const options = { method: "POST", body, headers, duplex: "half" };
  return { request: new Request("http://127.0.0.1/mcp", options), canceled: () => canceled };
}

async function status(request: Request) {
  const result = await boundMcpRequest(request);
  return result instanceof Response ? result.status : 200;
}

test("valid MCP bytes, headers and live abort signal reach the existing handler unchanged", async () => {
  const controller = new AbortController();
  const body = '{ "jsonrpc":"2.0", "id":1, "method":"tools/list", "params":{} }';
  const request = new Request("http://127.0.0.1/mcp", {
    method: "POST",
    body,
    headers: { authorization: "Bearer dummy", "x-client": "fixture" },
    signal: controller.signal,
  });
  const result = await boundMcpRequest(request);
  expect(result).toBeInstanceOf(Request);
  if (!(result instanceof Request)) throw new Error("Expected bounded request");
  expect(await result.text()).toBe(body);
  expect([...result.headers]).toEqual([...request.headers]);
  controller.abort();
  expect(result.signal.aborted).toBe(true);
});

test("non-MCP requests and MCP non-POST requests retain object and unread body identity", async () => {
  for (const request of [
    post("unparsed", "/api/webhooks/paddle"),
    post("unparsed", "/app"),
    new Request("http://127.0.0.1/mcp"),
    post("unparsed", "/mcp%2F"),
  ]) {
    expect(await boundMcpRequest(request)).toBe(request);
    expect(request.bodyUsed).toBe(false);
  }
});

test("router-normalized aliases and companion tool routes cannot bypass limits", async () => {
  for (const path of [
    "/mcp",
    "/MCP",
    "/mcp/",
    "/%6dcp",
    "/%4dCP/",
    "/x/../mcp",
    "/.mcp/invoke-tool/list_products",
    "/%2emcp/invoke-tool/list_products",
    "/.MCP/INVOKE-TOOL/x/",
  ]) {
    expect(await status(post(" ".repeat(MCP_REQUEST_BYTES + 1), path))).toBe(413);
  }
});

test("exact byte limit passes; one extra byte is rejected without relying on Content-Length", async () => {
  const body = JSON.stringify({ value: "x".repeat(MCP_REQUEST_BYTES - 12) });
  expect(new TextEncoder().encode(body).length).toBe(MCP_REQUEST_BYTES);
  expect(await status(post(body))).toBe(200);
  expect(await status(post(body + " "))).toBe(413);
});

test("UTF-8 bytes, not UTF-16 character count, enforce the body budget", async () => {
  const body = JSON.stringify({ value: "😀".repeat(MCP_REQUEST_BYTES / 4) });
  expect(body.length).toBeLessThan(MCP_REQUEST_BYTES);
  expect(await status(post(body))).toBe(413);
});

test("chunked bodies with absent or forged-small length cannot exceed the actual byte budget", async () => {
  const variants: Record<string, string>[] = [{}, { "content-length": "1" }];
  for (const headers of variants) {
    const fixture = streamed([new Uint8Array(MCP_REQUEST_BYTES), new Uint8Array(2)], headers);
    expect(await status(fixture.request)).toBe(413);
  }
});

test("declared oversize and invalid lengths fail before reading the body", async () => {
  expect(
    await status(post("{}", "/mcp", { "content-length": String(MCP_REQUEST_BYTES + 1) })),
  ).toBe(413);
  expect(await status(post("{}", "/mcp", { "content-length": "invalid" }))).toBe(400);
});

test("early refusals preserve the response transport and signal close-after-response", async () => {
  for (const length of ["65537", "invalid"]) {
    let canceled = false;
    const body = new ReadableStream<Uint8Array>({
      cancel() {
        canceled = true;
        return new Promise<void>(() => {});
      },
    });
    const options = { method: "POST", body, headers: { "content-length": length }, duplex: "half" };
    expect([400, 413]).toContain(await status(new Request("http://127.0.0.1/mcp", options)));
    expect(canceled).toBe(false);
    expect(body.locked).toBe(false);
  }
});

test("combined array/object member budget accepts the boundary and rejects one extra", async () => {
  expect(
    await status(post(JSON.stringify({ values: Array(MCP_REQUEST_MEMBERS - 1).fill(0) }))),
  ).toBe(200);
  expect(await status(post(JSON.stringify({ values: Array(MCP_REQUEST_MEMBERS).fill(0) })))).toBe(
    413,
  );
  expect(
    await status(
      post(JSON.stringify(Object.fromEntries(Array.from({ length: 257 }, (_, i) => [`k${i}`, 0])))),
    ),
  ).toBe(413);
});

test("deep bounded inputs cannot reach recursive downstream schema validation", async () => {
  const nesting = (depth: number) => "[".repeat(depth) + "{}" + "]".repeat(depth);
  expect(await status(post(nesting(MCP_REQUEST_DEPTH)))).toBe(200);
  expect(await status(post(nesting(MCP_REQUEST_DEPTH + 1)))).toBe(413);
});

test("malformed JSON and invalid UTF-8 get fixed errors without echoing input", async () => {
  for (const request of [post("private-input"), streamed([new Uint8Array([0xff])]).request]) {
    const result = await boundMcpRequest(request);
    expect(result).toBeInstanceOf(Response);
    if (!(result instanceof Response)) throw new Error("Expected rejection");
    expect(result.status).toBe(400);
    expect(await result.json()).toEqual({ error: "MCP_REQUEST_INVALID" });
    expect(result.headers.get("cache-control")).toBe("no-store");
    expect(result.headers.get("connection")).toBe("close");
  }
});

test("abort settles an outstanding read even when client cancellation never settles", async () => {
  let canceled = false;
  const body = new ReadableStream<Uint8Array>({
    cancel() {
      canceled = true;
      return new Promise<void>(() => {});
    },
  });
  const controller = new AbortController();
  const options = { method: "POST", body, signal: controller.signal, duplex: "half" };
  const pending = status(new Request("http://127.0.0.1/mcp", options));
  controller.abort();
  expect(await pending).toBe(400);
  expect(canceled).toBe(true);
});

test("already-aborted inputs and stream failures never pass to the protocol handler", async () => {
  const controller = new AbortController();
  controller.abort();
  expect(
    await status(
      new Request("http://127.0.0.1/mcp", {
        method: "POST",
        body: "{}",
        signal: controller.signal,
      }),
    ),
  ).toBe(400);
  const body = new ReadableStream<Uint8Array>({
    start(c) {
      c.error(new Error("private-stream-error"));
    },
  });
  const options = { method: "POST", body, duplex: "half" };
  expect(await status(new Request("http://127.0.0.1/mcp", options))).toBe(400);
});

test("stalled reads have a finite deadline", async () => {
  const body = new ReadableStream<Uint8Array>();
  const options = { method: "POST", body, duplex: "half" };
  expect(await status(new Request("http://127.0.0.1/mcp", options))).toBe(408);
}, 10_000);
