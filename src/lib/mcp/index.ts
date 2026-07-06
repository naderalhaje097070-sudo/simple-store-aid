import { auth, defineMcp } from "@lovable.dev/mcp-js";
import listProducts from "./tools/list-products";
import listCustomers from "./tools/list-customers";
import listRecentOrders from "./tools/list-recent-orders";
import todaySummary from "./tools/today-summary";

// The OAuth issuer MUST be the direct Supabase host, not the .lovable.cloud proxy.
const projectRef = import.meta.env.VITE_SUPABASE_PROJECT_ID ?? "project-ref-unset";

export default defineMcp({
  name: "mongezz-mcp",
  title: "Mongezz",
  version: "0.1.0",
  instructions:
    "Read-only access to the signed-in shop owner's Mongezz data: products, customers, recent orders/invoices, and today's financial summary. All queries are scoped to the authenticated user via RLS.",
  auth: auth.oauth.issuer({
    issuer: `https://${projectRef}.supabase.co/auth/v1`,
    acceptedAudiences: "authenticated",
  }),
  tools: [listProducts, listCustomers, listRecentOrders, todaySummary],
});
