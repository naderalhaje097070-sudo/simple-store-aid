import { afterEach, beforeEach, expect, spyOn, test } from "bun:test";
import { ToolContext } from "@lovable.dev/mcp-js";
import listCustomers from "../../src/lib/mcp/tools/list-customers";
import listProducts from "../../src/lib/mcp/tools/list-products";
import listRecentOrders from "../../src/lib/mcp/tools/list-recent-orders";

const url = "https://supabase.fixture.invalid";
const originalUrl = process.env.SUPABASE_URL;
const originalKey = process.env.SUPABASE_PUBLISHABLE_KEY;
const accountCheck = "/rest/v1/rpc/current_tenant_id";
const authenticated = new ToolContext({
  type: "oauth",
  principal: {
    claims: {},
    issuer: "https://issuer.fixture.invalid",
    resource: "https://tool.fixture.invalid",
    acceptedAudiences: ["authenticated"],
    scopes: [],
  },
  bearer: { token: "unit-fixture-bearer" },
});

let calls: string[];
let fetchMock: ReturnType<typeof spyOn<typeof globalThis, "fetch">>;

beforeEach(() => {
  process.env.SUPABASE_URL = url;
  process.env.SUPABASE_PUBLISHABLE_KEY = "unit-fixture-key";
  calls = [];
  fetchMock = spyOn(globalThis, "fetch").mockImplementation(async () => {
    throw new Error("Unconfigured test fetch");
  });
});

afterEach(() => {
  fetchMock.mockRestore();
  if (originalUrl === undefined) delete process.env.SUPABASE_URL;
  else process.env.SUPABASE_URL = originalUrl;
  if (originalKey === undefined) delete process.env.SUPABASE_PUBLISHABLE_KEY;
  else process.env.SUPABASE_PUBLISHABLE_KEY = originalKey;
});

function respond(account: () => Response) {
  fetchMock.mockImplementation(async (input, init) => {
    const request = new Request(input, init);
    const target = new URL(request.url);
    expect(target.origin).toBe(url);
    expect(request.headers.get("Authorization")).toBe("Bearer unit-fixture-bearer");
    calls.push(target.pathname);
    return target.pathname === accountCheck ? account() : Response.json([]);
  });
}

for (const [table, tool] of [
  ["products", listProducts],
  ["customers", listCustomers],
  ["orders", listRecentOrders],
] as const) {
  test(`${table}: checks account state before an empty successful read`, async () => {
    respond(() => Response.json(null));
    const result = await tool.handler({}, authenticated);
    expect(calls).toEqual([accountCheck, `/rest/v1/${table}`]);
    expect(result.structuredContent).toEqual({ [table]: [] });
    expect(result.isError).toBeUndefined();
  });

  test(`${table}: returns the explicit inactive error without querying rows`, async () => {
    respond(() => Response.json({ code: "42501", message: "account_inactive" }, { status: 403 }));
    const result = await tool.handler({}, authenticated);
    expect(calls).toEqual([accountCheck]);
    expect(result).toEqual({
      content: [{ type: "text", text: "account_inactive" }],
      isError: true,
    });
  });

  test(`${table}: fails closed when account state cannot be verified`, async () => {
    respond(() => Response.json({ code: "XX000", message: "fixture error" }, { status: 500 }));
    const result = await tool.handler({}, authenticated);
    expect(calls).toEqual([accountCheck]);
    expect(result).toEqual({
      content: [{ type: "text", text: "account_state_unavailable" }],
      isError: true,
    });
  });

  test(`${table}: unauthenticated call does not contact the database`, async () => {
    const result = await tool.handler({}, new ToolContext(undefined));
    expect(fetchMock).not.toHaveBeenCalled();
    expect(result).toEqual({
      content: [{ type: "text", text: "Not authenticated" }],
      isError: true,
    });
  });
}
