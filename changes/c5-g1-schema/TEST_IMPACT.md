# Hosted disposition — 3 November 2026

Exact executable96ad7996a647eb6716ab36d050c96e72ad9963e1 passed G1 41547084595 (native41checks+environment), G0 41547084637 and B1 41547084623, all attempt1. Cleanup and credential scan pass. [Actual results and limits](RESULT.md), [raw evidence index](hosted/index.json). The original test plan/local history below is retained; its pending-hosted wording is superseded by this disposition. Full financial C5/C6/C7 remain open.

---

# Test impact and actual local results

- Prior hosted baseline41492623347 failed exact41_migrations; preserved historical raw artifacts from the SEC delivery remain unchanged.
- New regression was added before runtime modification:18target tests passed and runtime-wiring test failed (19total,1failure), proving the old gate was still present. No assertion weakened to make it pass.
- After implementation: target19 and source-admission21 tests PASS. Old G1 contracts17, cleanup6, integrated identity29, process-map10 PASS. Initial egress suite7pass/2errors was an incomplete scratch checkout: unchanged dns_trace.c/cjs had not been fetched. Retrieved exact GitHub bytes without editing them; all9egress tests then PASS. This local setup failure remains recorded, not a code regression.
- Changed Python modules compile; G1 YAML parses, retains two jobs, and both require C5 source/target tests. No local native SQL/emulator/browser execution: Docker/psql are unavailable. Do not transfer unit success to hosted acceptance.
- Hosted exact-head G1 runtime/environment and automatically affected G0/compatibility workflows must be inspected to completion; no manual unrelated historical reruns. Raw safe receipts/failure/cleanup and run metadata are saved at final handoff. C5 full persisted financial/concurrency/isolation/browser→DB/restore and C6 review remain NOT VERIFIED by this batch.
