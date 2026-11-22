import { defineTool } from "@lovable.dev/mcp-js";
import { z } from "zod";
import { authorizeMcpTableRead } from "../account-client.server";

export default defineTool({
  name: "list_products",
  title: "List products",
  description: "List products in the signed-in user's shop, with price, cost, and stock.",
  inputSchema: {
    limit: z.number().int().min(1).max(200).optional().describe("Max rows to return (default 50)."),
    only_active: z.boolean().optional().describe("If true, return only active products."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async ({ limit, only_active }, ctx) => {
    const access = await authorizeMcpTableRead(ctx);
    if (!access.ok) return access.result;
    let q = access.supabase
      .from("products")
      .select("id,name,price,cost,stock,is_active,is_discount")
      .order("name")
      .limit(limit ?? 50);
    if (only_active) q = q.eq("is_active", true);
    const { data, error } = await q;
    if (error) return { content: [{ type: "text", text: error.message }], isError: true };
    return {
      content: [{ type: "text", text: JSON.stringify(data) }],
      structuredContent: { products: data ?? [] },
    };
  },
});
