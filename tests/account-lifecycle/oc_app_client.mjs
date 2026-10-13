// Test runner only: serialize the locked TanStack wire protocol, never import a handler.
import { toJSONAsync, fromCrossJSON } from "seroval";
let input = "";
for await (const chunk of process.stdin) input += chunk;
const args = JSON.parse(input);
const payload = await toJSONAsync({ data: args.data });
const headers = { "x-tsr-serverFn": "true", "Sec-Fetch-Site": "same-origin", Accept: "application/json" };
if (args.token) headers.Authorization = `Bearer ${args.token}`;
const response = await fetch(`http://127.0.0.1:54325/_serverFn/${args.id}?payload=${encodeURIComponent(JSON.stringify(payload))}`, { headers, redirect: "manual" });
const raw = await response.text();
let decoded;
try { decoded = fromCrossJSON(JSON.parse(raw), { refs: new Map() }); } catch { decoded = {}; }
const known = ["account_inactive", "account_state_unavailable", "Price not found", "Unauthorized: No authorization header provided", "Unauthorized: Invalid token", "Unauthorized: Only Bearer tokens are supported", "Unauthorized: No token provided"];
const error = decoded?.error;
const message = error?.message ?? (decoded instanceof Error ? decoded.message : undefined);
process.stdout.write(JSON.stringify({ status: response.status, result: decoded?.result === "pri_oc_app_dummy" ? decoded.result : undefined, error: known.includes(message) ? message : undefined, content_type: response.headers.get("content-type"), raw_contains_dummy: raw.includes("pri_oc_app_dummy"), serialized: response.headers.get("x-tss-serialized"), unknown: !known.includes(message) && decoded?.result !== "pri_oc_app_dummy", diagnostic_keys: Object.keys(decoded ?? {}) }));
