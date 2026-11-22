import { defineTool } from "@lovable.dev/mcp-js";
import { z } from "zod";
import { authorizeMcpTableRead } from "../account-client.server";

export default defineTool({
  name: "list_recent_orders",
  title: "List recent orders",
  description: "List the most recent sales orders/invoices, with totals, paid amount, and status.",
  inputSchema: {
    limit: z.number().int().min(1).max(100).optional().describe("Max rows (default 20)."),
    status: z.enum(["paid", "partial", "debt"]).optional().describe("Optional status filter."),
  },
  annotations: { readOnlyHint: true, idempotentHint: true, openWorldHint: false },
  handler: async ({ limit, status }, ctx) => {
    const access = await authorizeMcpTableRead(ctx);
    if (!access.ok) return access.result;
    let q = access.supabase
      .from("orders")
      .select(
        "id,number,total,paid,status,delivery,courier_state,customer_id,courier_id,created_at",
      )
      .order("created_at", { ascending: false })
      .limit(limit ?? 20);
    if (status) q = q.eq("status", status);
    const { data, error } = await q;
    if (error) return { content: [{ type: "text", text: error.message }], isError: true };
    return {
      content: [{ type: "text", text: JSON.stringify(data) }],
      structuredContent: { orders: data ?? [] },
    };
  },
});
