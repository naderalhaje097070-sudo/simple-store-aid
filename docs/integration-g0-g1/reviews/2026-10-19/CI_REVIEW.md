# Independent CI, source identity, generation and observer review

Date: 2026-10-19. Reviewer did not implement the candidate. Read-only GitHub review; no code fixes, native workflow reruns, provider requests, merge, deployment, production or secret access.

**Scoped outcome: Changes required.** One confirmed **existing Medium** CI failure-masking issue needs a fix or explicit decision under REVIEW_PROTOCOL. No introduced blocker was confirmed in the inspected generation, identity or observer changes. This is not approval of financial/account-chain composition or release readiness.

## Exact scope and provenance

- Canonical repository: `naderalhaje097070-sudo/simple-store-aid`.
- Reviewed executable SHA: `823cbcaf4a83ae8b4bea44e314df4c1215a9ba3b`.
- Documentation SHA: `1028441558e7db7b0b25390f2b8ee452b702774b`.
- Original72: `6da4dadbe9391bb48c8c4c41dcb688728003fb81`; base54: `57fb508b9d239aaf4676352dd97654341416c46a`.
- Main was identified by the parent review as `43d6edbccb66fb06ce0fcb93734ad59532d1aeae`; no main write was performed.

Read AGENTS, current state/tasks/decisions, REVIEW_PROTOCOL, integration REPORT and REVIEW_REQUEST. The user's canonical repository instruction supersedes the historical droid repository line. GitHub exact-ref responses supplied source files and blob identities. The recursive candidate tree was complete, not truncated. GitHub comparison established the original72 inheritance; original54 Quality was fetched separately to classify the finding below.

## Confirmed finding CI-1

**Severity:** Medium.

**Classification:** Existing in base54 and original72; retained in the candidate. The candidate changes this selector's extension list, not its error handling. This does not disprove the candidate's separately measured full-lint result.

**File or contract:** `.github/workflows/quality.yml:37–41` at exact candidate SHA `823cbcaf4a83ae8b4bea44e314df4c1215a9ba3b`, blob `34971fd99d6f40b095570cb11b560438e25b387f`.

**Evidence:** `mapfile -t files < <(git diff ... | grep ... || true)` discards failure of `git diff`. The parent shell observes successful `mapfile`, receives no files, then exits zero through the no-changed-files branch. `set -euo pipefail` does not repair this process-substitution status propagation. The exact selector, copied from the candidate workflow into a temporary real git fixture, with nonzero nonexistent `BASE_SHA=ffffffffffffffffffffffffffffffffffffffff`, produced:

```text
exit: 0
stdout: No changed JavaScript or TypeScript files to lint.
stderr: fatal: bad object ffffffffffffffffffffffffffffffffffffffff
```

Reproduction receipt: `changed-lint-invalid-base.json`. The exact base54 file contains the same construction; GitHub's original72-to-candidate patch shows only `mjs|cjs` added on this line.

**Risk:** An unavailable/invalid comparison base can silently skip the changed-source lint gate and report success. The new extension coverage therefore remains conditional on successful file discovery. Current G0 run39172903511 ran `eslint .` directly and is not affected by this selector defect.

**Required fix:** Make changed-file discovery an independently checked command; propagate git errors before filtering extensions. Treat grep's no-match status separately from discovery failure. Preserve correct behavior for genuine no-source diffs and include mjs/cjs coverage. Alternatively, an explicit owner decision must record this inherited Medium before merge, as REVIEW_PROTOCOL requires.

**Verification method:** A real git fixture should fail on invalid/unavailable base; valid no-source changes should pass; valid changed TS/TSX/JS/JSX/MJS/CJS paths should invoke lint, including a failing diagnostic. No repository fix was made in this review.

## Checks with no confirmed introduced finding

**Identity.** Independently compared every manifest entry to GitHub's complete candidate tree: exactly279 protected blob paths, no missing/additional protected tree path, no hash mismatch. Compared all41 migration paths/hashes with the independently fetched base54 tree: all match. The committed-manifest check, schema bool rejection, canonical remote, ancestor check, normalized relative paths, duplicate rejection, tracked/untracked nonignored path set, leaf regular-file check and Git blob digest are enforced. Documentation/state exclusions are explicit; this is not a claim that legacy383 blobs remain unchanged. Manifest changes are themselves review inputs rather than an external cryptographic trust root. This review does not enlarge the guard to ignored build/dependency artifacts.

**Generation/build ownership.** Exactly nine hardcoded allowed paths, pinned formatter version, before/after SHA256 allowlist, duplicate/missing path rejection and expected output hashes. Independently fetched all nine candidate outputs; each exact byte sequence matches its manifest afterSha256. Validation/formatting completes across the batch before the write loop. The build entry forwards argv to actual Vite, stops on build failure and propagates formatter failure. No reset/restore masks source drift. The final G0 includes tracked-diff and complete identity checks after both real builds. The local protocol controls prove validation failures cause no partial writes; they do not claim filesystem-wide transactional rollback if a write itself fails. A failed write still exits nonzero. No pinned-Prettier compatibility replay was independently run locally.

**Observer.** Individual live tasks are inspected even when a leader is terminal. Terminal metadata does not fabricate a process row. Live unreadable executable, timeout and metadata failures remain sticky and bounded; safe enums/integers replace raw error strings/paths. The runtime still rejects unmapped explicit nonloopback TIDs. Deferred trace/counter failures remain in the check list and cause a nonzero exit. The failure flag is only initialized in the constructor, not cleared after a later successful read. Firewall counters are measured continuously rather than reset between matching/Auth/conflict phases. No observer repair was treated as proof of the old failure's exact cause.

**Proof masking/test integrity.** Inspected the emitted-runtime comparator's alias/null-guard normalization and actual source delta. It admits one same-client alias, exactly two named null-result TypeError guards and the queue local alias/rename. The counter totals are asserted; actual candidate alias/guard bodies are consistent with that scope. The ten callback scenarios and p_paid negative are callback/stub evidence, not DB/provider acceptance. Existing modified trace/CF-fetch tests are formatting changes in the comparison. No changed test was found to silently turn its asserted failure into success. No lint rules/ignore config relaxation was present in the original72 candidate delta. MJS/CJS selection is wider, with the inherited discovery gap above retained.

**Privacy/containment evidence.** The runtime stores bounded static error categories, hashes and sanitized trace fields; pointer-only raw send tracing avoids payload publication. Credential-bearing app/build/auth logs remain outside the upload directory. Workflow quarantine occurs before bounded directory upload. Existing privacy tests include arbitrary-field/name rejection and native/Node delegation without real DNS. This is a review of this harness and the inspected artifacts, not a blanket repository secret audit.

## Native evidence independently inspected, without rerunning

Retrieved complete job logs through the GitHub connector and inspected relevant checkout, command, outcome, failure and cleanup sections; also fetched run/job/step metadata and artifact metadata. Local success/failure ZIP bytes were accepted only after their SHA256 matched independently fetched GitHub artifact digests.

| Run | Exact source / result | Independently corroborated evidence |
|---|---|---|
| G0 `39172903511`, attempt1 |823cbcaf; success |quality117809500361/audit117809500180; exact checkout; lint0errors13warnings; typecheck;66unit174expect;9-file/10callback proof; build-entry subcases;8wrapper/67dummybrowser; two real builds;9postprocessed outputs;279identity before/after; audit raw `{}`; no skipped required gate |
| G1 `39172903470`, attempt1 |823cbcaf; success |runtime117809500338/environment117809500057; exact checkout;40/40; native tracer confirmation; final receipts match artifact12153176856 digest `02ad1526cc023bff4c22af68752fd6fad3e53066a30ae79bf8e07e4aff87d458` |
| Old G1 `39171846934`, attempt1 |44df8e888c966e12ae26900e254b41c7fe1b17d0; failure |runtime117806374640 fails deferred acceptance; receipt39/40, only bounded_egress_trace_collected false; conflict lineage read_failed=true; artifact12152967146 digest `03a8366bf79cd9ce83efd87b02a85170116ce3d4a2543c2e957090b22906fd9e` |

Final trace receipts have complete=true, no unmapped nonloopback TIDs, read_failed=false, monitor_stopped=true and no failure records for both phases; observed terminal-task counts4matching/2conflict. Continuous counters are IPv4 `1→1`, IPv6 `0→0`. Named mismatch receipt is HTTP500, exact build_runtime_supabase_mismatch, unclassified_error=false. Cleanup receipt has all four checks true. Old conflict receipt provides no exact read-error reason; its failure remains unresolved historically and is not relabeled harmless.13warnings remain visible. These are observed pre-existing native results, **not a live independent native rerun**.

## Focused local verification and limits

- 58 existing focused Python fixtures independently replayed successfully:16identity,10ProcessMap,9trace/privacy/delegation,17visual/named-guard,6cleanup. Partial-snapshot collection attempts initially failed on missing fetched test dependencies; those logs are preserved. After exact dependencies were fetched, the complete focused run passed.
- Real build-entry test passed with three child-process subcases: argv forwarding, nonzero Vite propagation/no postprocessor, nonzero postprocessor propagation.
- 12 independent protocol controls passed in `review_protocol_negatives.py`: nine generation cases, three runtime stop/attribution cases. The generation controls deliberately use a deterministic formatter stub and synthetic fixture hashes; they prove batch/CLI/version/hash/symlink failure gating, not real Prettier semantics. Runtime controls execute the exact candidate stop() AST with mocked process/trace boundaries and prove an unmapped nonloopback terminal TID still makes the trace incomplete.
- The exact changed-source selector's missing-base negative reproduced CI-1; preserved as an expected finding, not hidden as a passing test.

No new native full build, frozen install, audit, DB/browser/Auth/emulator, live ptrace or production test was performed. No independent full financial49/50, account-state59–71, migration-upgrade semantics, provider or release review is claimed. No code was fixed. Existing current native results support the reported mechanical foundation snapshot but do not resolve the separate financial/account-chain risks or this inherited Medium CI decision.

Evidence directory: this report's sibling `github-evidence-summary.json`, `verified-native-receipts.json`, `generated-hashes.json`, `changed-lint-invalid-base.json`, `independent-protocol-results.json`, focused local logs and complete native job logs. Source snapshots live under `source/`; documentation inputs under `docs-head/`.
