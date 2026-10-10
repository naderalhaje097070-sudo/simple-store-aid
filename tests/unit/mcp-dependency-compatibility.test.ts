import { expect, test } from "bun:test";
import { auth, defineMcp, defineTool } from "@lovable.dev/mcp-js";
import { createMcpProtocolHandler } from "@lovable.dev/mcp-js/protocols/mcp";
import { z } from "zod";

// Synthetic adapter checks exercise the locked SDK without project data or tools.
let calls = 0;
const echo = defineTool({
  name: "echo",
  title: "Echo",
  description: "Synthetic compatibility fixture",
  inputSchema: { value: z.string() },
  handler: ({ value }) => {
    calls += 1;
    return { content: [{ type: "text", text: value }] };
  },
});
const definition = {
  name: "review-fixture",
  title: "Review fixture",
  version: "1.0.0",
  instructions: "",
  metrics: false,
  tools: [echo],
};
const handler = createMcpProtocolHandler(defineMcp(definition));

function request(method: string, params: unknown) {
  return new Request("http://127.0.0.1/mcp", {
    method: "POST",
    headers: { "Content-Type": "application/json", Accept: "application/json, text/event-stream" },
    body: JSON.stringify({ jsonrpc: "2.0", id: 1, method, params }),
  });
}

async function responseBody(response: Response) {
  if (response.headers.get("content-type")?.includes("application/json")) return response.json();
  const text = await response.text();
  const data = text.split("\n").find((line) => line.startsWith("data: "));
  if (!data) throw new Error("Missing MCP SSE response data");
  return JSON.parse(data.slice(6));
}

test("Lovable MCP adapter initializes with the overridden SDK", async () => {
  const response = await handler(
    request("initialize", {
      protocolVersion: "2025-03-26",
      capabilities: {},
      clientInfo: { name: "review", version: "1.0.0" },
    }),
  );
  expect(response.status).toBe(200);
  expect((await responseBody(response)).result.serverInfo.name).toBe("review-fixture");
});

test("Lovable MCP adapter lists and invokes a Zod tool", async () => {
  const listed = await responseBody(await handler(request("tools/list", {})));
  expect(listed.result.tools[0].name).toBe("echo");
  const invoked = await responseBody(
    await handler(
      request("tools/call", {
        name: "echo",
        arguments: { value: "fixture-value" },
      }),
    ),
  );
  expect(invoked.result.content).toEqual([{ type: "text", text: "fixture-value" }]);
});

test("invalid arguments do not invoke the synthetic tool", async () => {
  const before = calls;
  const rejected = await responseBody(
    await handler(
      request("tools/call", {
        name: "echo",
        arguments: { value: 42 },
      }),
    ),
  );
  expect(Boolean(rejected.error || rejected.result?.isError)).toBe(true);
  expect(calls).toBe(before);
});

test("protected fixture rejects a missing bearer without external requests", async () => {
  const protectedHandler = createMcpProtocolHandler(
    defineMcp({
      ...definition,
      auth: auth.oauth.issuer({
        issuer: "https://issuer.example.invalid",
        resource: "http://127.0.0.1/mcp",
      }),
    }),
  );
  const before = calls;
  expect((await protectedHandler(request("tools/list", {}))).status).toBe(401);
  expect(calls).toBe(before);
});
