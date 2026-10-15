# Independent review — G1-CLI-CLEANUP-01, 2026-10-15

Outcome: **Blocked pending missing evidence.** The CLI now installs and the exact named SSR mismatch, after-state, source/secret and cleanup checks actually execute. G1 remains unaccepted because the unchanged zero-unexpected-outbound-attempt oracle fails. This review authorizes no merge, deployment, release, PR48 closure or G0 exception.

## Independence and reviewed sources

The reviewer implemented no harness, application, workflow or GitHub change. This REVIEW.md is the reviewer's only file edit. Read AGENTS.md, PROJECT_STATE.md, TASKS.md, DECISIONS.md and the applicable governance protocols. Reviewed installer instrumentation, cleanup helper/fixtures, workflow, named-message classifier, runtime changes and intake/impact records. No CI dispatch, database/browser/Auth/financial replay, production/provider access or account change was performed by the reviewer.

Starting PR72 source is f2e54d33233ac4ddfa51782b7c1a2534f441eed8; first executed source d4eeee0d6c392ce19fb0eeac1b69a0d4a9832ddb; final executed runtime source **819291c85825d73854262d76d2030736470ef92b**. Directly fetched all three nontruncated GitHub trees. The final tree has435 blobs; compared with430 starting blobs,424 existing blobs are unchanged, six changed paths are the focused runtime workflow/controller, three root checkpoints and their fingerprint allowlist, and five new paths are the three harness files and two intake/impact notes. Application, package/lock, configuration, generated auth and all41 migrations are unchanged. Delivery-only documentation/evidence additions are not a runtime retest; final publication must disclose any further source differences.

Independently fetched official setup-cli source at afb1b15109756ea5cf9d8985a359d9095235ca2b. Its9645-byte main.ts hashes to9ab8da10c0e6ac30dc793094383b973604e95598ccd6c81a05a83a3d1a55cd68, matching the corrected checked constant. Instrumentation changes only12 static phase messages in the scratch action copy, restores the source, pins CLI2.101.0 and retains action Bun1.3.10/frozen dependencies. Timeout bounds the process group and sends KILL after TERM even when the parent has exited. The timeout-kill path was source-reviewed, not exercised by a hosted timeout: both new installs succeeded.

## Actual independent re-execution and evidence inspection

Executed locally, with no application/database/network body:

- `PYTHONDONTWRITEBYTECODE=1 python tests/g01-acceptance/test_cleanup.py`:6 tests PASS, including absent user, present/no processes, remaining processes, lookup failure, pgrep error codes and unavailable/timed-out reads. Reexecuted after the runtime control-flow change.
- `PYTHONDONTWRITEBYTECODE=1 python tests/g01-acceptance/test_g1_contracts.py`:17 tests PASS; generic500, partial phrase, another named guard and wrong status still fail. Reexecuted after the runtime control-flow change.
- Imported the installer instrumentation against the independently verified official source:12 unique phase markers; modified upstream source rejected by checksum. The initial scratch extra-newline checksum discrepancy was corrected before publication; the final constant was independently computed from API content.
- Actual read-only local `pgrep` probes: current UID reports processes_remaining/false, unused UID2147483646 reports no_processes/true, and the absent real g01-app username reports user_absent/true. Fixture failures do not become success.

Directly fetched old runtime job115996388720 logs: Bun1.3.10 dependency installation completed, then `bun src/main.ts` ran17:21:37.913–17:45:55.724UTC before cancellation; no deeper phase was logged. The old failed3/4 cleanup receipt is retained. Neither new successful install identifies the historical stall's underlying cause; do not claim a proven Bun, download, rate-limit or billing cause.

Directly fetched first-run environment116311206421, runtime116311206661 and Quality116311226831 logs. Environment passed17 tests and six safe sentinels. Runtime installed all12 CLI phases successfully, executed37 checks/36PASS and failed native outbound equality: IPv4 baseline1→25, IPv6zero. Exact named mismatch+500, public snapshots and finance-zero passed; source/final private-secret checks were not reached in that first run. Cleanup4/4 and evidence scan passed. First runtime ZIP SHA256209d083d73713333e7dc6fe918ceca090c0b6f726ba07def7d6ad319901b9507 and environment ZIP5409e3ae527530655c43497b094595a02e1015bf0769f6048debf19902292bfd match the manifest; five stored runtime JSON receipts match their raw members. Original runtime-progress also remains in the raw archive.

## Final actual hosted result

Directly fetched final runtime job116314775547 in run38702788681 and Quality job116314798867 in run38702796165. Independently inspected final raw receipts and verified ZIP SHA2569fbd455504f0b2bd2181ce6df8e0844fc37f32d0797f21585386d133444a4a10; every extracted member matches its ZIP bytes.

| Final boundary | Verified result |
| --- | --- |
| Pinned installer | All12 phases PASS; exit0; no timeout; CLI2.101.0/Bun1.3.10 |
| Runtime controller |39 checks,38PASS; job correctly FAILED through deferred_acceptance_checks_failed |
| Positive SSR/Auth | Actual matching SSR200 and desktop/mobile authenticated UI PASS |
| Required mismatch | HTTP500 AND complete expected SEC_ENV_CONFIG_ERROR runtime/baked Supabase mismatch PASS; only build_runtime_supabase_mismatch classified |
| After-state | All22 public table count/digests unchanged; final financial tables zero |
| Source/secret checks | tracked_source_unchanged and credential_free_receipt PASS |
| Native counter | FAIL: IPv4 baseline1→matching_ready9→after_auth_ui9→after_conflict_stopped17; IPv6 remains0 |
| Cleanup/evidence |4/4 PASS; process_state=no_processes; containers absent; credential scan PASS |

Automatic Quality passed60 unit tests/125 expectations, eight actual-wrapper/stub cases and67 dummy browser transport scenarios. It checked out synthetic PR merge451036ff8392ba617b89bf87658a0c529fbe9f41, not the branch commit directly; independently fetched its nontruncated435-blob tree and verified exact path/blob/mode equality with819291c8. No protected branch merge occurred. These bounded checks do not grant full lint, audit, financial or account-lifecycle acceptance.

## Findings and limits

Severity: Medium — unresolved G1 native-outbound acceptance blocker.

File/contract: runtime.py/native_unexpected_outbound_zero and isolated emulator startup.

Evidence: final REJECT counters add eight IPv4 packets before matching SSR readiness and eight more across the conflict emulator start, with no added packets during Auth UI. The firewall remained unchanged and rejected these packets; the counters do not establish16 unique connections or successful external delivery. Packet destination, initiating process and deeper startup call site remain unproven. No counter reset, allow rule or alternate500 was accepted.

Required next verification: planning should authorize a bounded startup connect/DNS trace with the same deny rules and safe sanitized evidence, identify the16 remaining blocked packets, then select a source-supported minimal harness correction and repeat only the affected gate. Do not execute that next phase as part of this handoff or add speculative flags.

Independently read Wrangler4.149.0 official banner, update-check and environment-variable sources. WRANGLER_HIDE_BANNER=true returns before the separate npm update check; WRANGLER_SEND_METRICS=false alone does not cover it. The focused flag is justified by source, but observed24→16 blocked packets proves only partial reduction across these runs, not packet destinations or complete causality. The new per-phase evidence and deferred failure preserve the strict acceptance requirement while permitting later source/secret checks to execute.

No new Critical/High source defect was found in this bounded test/CI change. Cleanup's absent-user defect is corrected without suppressing lookup/read errors. The old installer root cause remains unresolved historical evidence, while current installation is operationally unblocked. G1 still fails; G0 full lint/advisory disposition and inherited G2 account-lifecycle defect remain separate and unaccepted. No production, Paddle, financial write workflow, new dependency, migration, merge, deployment or launch approval occurred.

Rollback is an additive revert of this batch's harness/workflow/checkpoint changes on the same draft; no applied migration or data compensation is needed. Stop after the documented handoff. ONE NEXT belongs to planning: bounded trace of the isolated emulator startup packets under unchanged egress denial.
