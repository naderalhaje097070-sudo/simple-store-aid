import { auth, defineMcp } from "@lovable.dev/mcp-js";
import { resolveSupabaseMcpIssuer } from "../../../config/supabase-build-config";
import listProducts from "./tools/list-products";
import listCustomers from "./tools/list-customers";
import listRecentOrders from "./tools/list-recent-orders";
import todaySummary from "./tools/today-summary";

// These values are baked by Vite only after the shared environment contract passes.
// The server entry separately enforces that runtime bindings match this identity.
const issuer = resolveSupabaseMcpIssuer({
  MONGEZZ_DEPLOY_TARGET: import.meta.env.MONGEZZ_DEPLOY_TARGET,
  VITE_SUPABASE_URL: import.meta.env.VITE_SUPABASE_URL,
  VITE_SUPABASE_PUBLISHABLE_KEY: import.meta.env.VITE_SUPABASE_PUBLISHABLE_KEY,
  VITE_SUPABASE_PROJECT_ID: import.meta.env.VITE_SUPABASE_PROJECT_ID,
});

export default defineMcp({
  name: "mongezz-mcp",
  title: "Mongezz",
  version: "0.1.0",
  instructions:
    "Read-only access to the signed-in shop owner's Mongezz data: products, customers, recent orders/invoices, and today's financial summary. All queries are scoped to the authenticated user via RLS.",
  auth: auth.oauth.issuer({
    issuer,
    jwksUri: `${issuer}/.well-known/jwks.json`,
    acceptedAudiences: "authenticated",
  }),
  tools: [listProducts, listCustomers, listRecentOrders, todaySummary],
});
