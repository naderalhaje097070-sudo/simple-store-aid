// Verify the locked client's JSON protocol before any local DB setup.
import assert from "node:assert/strict";
import { toCrossJSONAsync, fromCrossJSON } from "seroval";
import { defaultSerovalPlugins } from "@tanstack/router-core/ssr/client";
for (const value of [
  { result: "pri_oc_app_dummy", error: undefined, context: {} },
  { error: new Error("Price not found"), context: {} },
  { error: new Error("account_inactive"), context: {} },
  { error: new Error("account_state_unavailable"), context: {} },
]) {
  const json = await toCrossJSONAsync(value, { plugins: defaultSerovalPlugins });
  const decoded = fromCrossJSON(json, { plugins: defaultSerovalPlugins });
  assert.equal(decoded.result, value.result);
  assert.equal(decoded.error?.message, value.error?.message);
}
console.log("OC_APP_WIRE: four locked JSON result/error round trips PASS");
