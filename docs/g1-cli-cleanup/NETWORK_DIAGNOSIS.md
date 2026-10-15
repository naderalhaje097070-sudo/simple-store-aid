# Native counter investigation, bounded to the missing G1 evidence

First diagnostic run38701706724 / source d4eeee0d6c392ce19fb0eeac1b69a0d4a9832ddb completed the12 official installer phases with exit0/no timeout. The previous38605846901 uninstrumented stall does not identify an underlying phase, so no historical network/rate-limit/Bun/billing root cause is claimed.

The unchanged application controller then executed37 checks:36 passed. The full named Supabase runtime/baked mismatch was the only classified guard, withHTTP500. Auth desktop/mobile,22 public-table before/after digests and finance-zero passed. IPv4 REJECT changed1→25, IPv6 stayed0. This is24 blocked packets, not proof of external delivery; nevertheless the strict zero-unexpected-packet condition failed. Source/final private-secret receipt checks followed the old hard assertion and were not reached. Cleanup4/4 and artifact secret scan passed. Original failed JSON and archive hashes are preserved in evidence/runtime-first and archive-manifest.json.

Official primary source at the same Wrangler4.149.0 tag provides a focused hypothesis:

- https://github.com/cloudflare/workers-sdk/blob/wrangler%404.149.0/packages/wrangler/src/wrangler-banner.ts — printWranglerBanner returns before updateCheck when getWranglerHideBanner is true.
- https://github.com/cloudflare/workers-sdk/blob/wrangler%404.149.0/packages/wrangler/src/update-check.ts — updateCheck invokes fetchLatestNpmVersion separately from telemetry.
- https://github.com/cloudflare/workers-sdk/blob/wrangler%404.149.0/packages/workers-utils/src/update-check.ts — npm registry lookup,3s timeout, without any metrics-variable gate.
- https://github.com/cloudflare/workers-sdk/blob/wrangler%404.149.0/packages/workers-utils/src/environment-variables/misc-variables.ts — official boolean WRANGLER_HIDE_BANNER, defaultfalse.

One additional runtime-only change sets WRANGLER_HIDE_BANNER=true in the existing clean emulator environment. No dependencies, application, firewall rules, allowance, counter reset, proxy, production endpoint or provider change. The new per-phase snapshots retain the original counter baseline. Deferring the native assertion collects later source/secret checks, but final any-failed-check still fails the job. This is evidence collection, not a waiver.

Second source819291c85825d73854262d76d2030736470ef92b / run38702788681 tests this hypothesis. A repeated counter failure is a handoff blocker; do not guess additional flags or repeat unchanged runs. Even a successful second run cannot retroactively establish the reason for the earlier CLI stall, nor identify packet destinations in the first run without a trace.

## Final observation and stop

Second run executed all39 checks:38PASS, only native_unexpected_outbound_zero false. Counters: before{IPv4:1,IPv6:0};matching-ready{9,0};afterAuth{9,0};after-conflict-stopped{17,0}. Thus16 blocked packets remain,8 per emulator startup, with no increase during Auth UI. Hiding the banner reduced the observed delta24→16 but did not resolve the strict gate. Destination/process stack and complete network cause remain unproven; no success/escape inferred from a REJECT counter. Named mismatch+500, final22-table invariance, financial-zero, tracked-source and credential-free receipt checks all passed. Cleanup4/4 and artifact scan passed. Job remains failure after collecting final evidence; no additional attempt or flag is authorized by this packet. ONE NEXT belongs to planning: a separate bounded startup connect/DNS trace under the unchanged reject firewall, with sanitized attribution; do not execute it as part of this handoff.
