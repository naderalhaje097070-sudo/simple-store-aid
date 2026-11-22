import { defineTool } from "@lovable.dev/mcp-js";
import { z } from "zod";
import { authorizeMcpTableRead } from "../account-client.server";

export default defineTool({
  name: "list_customers",
  title: "List customers",
  description: "List customers in the signed-in user's shop.",
  inputSchema: {
    search: z.string().optional().describe("Optional case-insensitive name substring filter."),
    limit: z.number().int().min(1).max(200).optional(),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async ({ search, limit }, ctx) => {
    const access = await authorizeMcpTableRead(ctx);
    if (!access.ok) return access.result;
    let q = access.supabase
      .from("customers")
      .select("id,name,phone")
      .order("name")
      .limit(limit ?? 50);
    if (search) q = q.ilike("name", `%${search}%`);
    const { data, error } = await q;
    if (error) return { content: [{ type: "text", text: error.message }], isError: true };
    return {
      content: [{ type: "text", text: JSON.stringify(data) }],
      structuredContent: { customers: data ?? [] },
    };
  },
});
