import { expect, test } from "bun:test";
import mcp from "../../src/lib/mcp/index";

test("actual MCP definition uses the approved local issuer", () => {
  expect(mcp.auth).toMatchObject({
    type: "oauth",
    issuer: "http://127.0.0.1:54321/auth/v1",
  });
});
