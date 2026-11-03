# C5-COLLECTION-RETRY-01 — tested candidate

Date: 3 November 2026. Repository: `naderalhaje097070-sudo/simple-store-aid`.
Branch: `integration/g0-g1-reconcile-2026-10-18`.
Exact tested executable: `a52ee17d57a02da46bc8fb03547711de697ecfea`.
Main remains `220fc2066b4d6254b1803b5e32919c47d60a9c7e`.

## Outcome

The owner-authorized keyed collection candidate passed its bounded stored-financial and real-component browser acceptance on fresh55 and populated54→55 databases. One intended20 collection on100 remains paid20/one payment after a hidden committed response and exact replay. A separate intentional20 payment uses another UUID and produces paid40/two payments. Original e0a75541 failed unkeyed baseline remains historical evidence; it has not been relabelled.

Status: **Implemented → Tested on the candidate branch only**. Not Merged, Released, or Production Ready. Full C5 and integration acceptance remain false.

## Implementation and authority

Owner approval of specific proposal570ec47e is recorded in issue55/comment6596692353. Candidate39f25d6 introduced the CLI-generated forward migration `20261103060658_c5_keyed_debt_collection.sql`, keyed RPC, durable scoped client identity and actual invoice/recovery UI. Canonical accounting and all prior54 migrations remain unchanged. Authenticated access to the old unkeyed entry point is revoked as authorized. Server-side live actor/tenant/staff authorization, payload/actor binding, transactional reservation/result and canonical row locks are authoritative.

Subsequent commits repaired verification admission, fixtures and isolated transport only. GitHub comparison bc642b8→a52ee17d contains zero product or SQL changes. See [verification history](VERIFICATION_REPAIR.md); no failed attempt is treated as acceptance.

## Exact-source verification

All runs below completed SUCCESS, attempt1, on a52ee17d.

| Gate | Run | Evidence |
| --- | --- | --- |
| C5 collection | [41696369037](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41696369037) | Fresh108 controls; upgraded111; direct RPC retry target; desktop and mobile actual collection components→locked SDK→Auth/RPC→stored database |
| G0 quality/audit | [41696369315](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41696369315) | Types, 0 lint errors/15 warnings,97 unit tests/300 expectations,43 read-server and11 read-browser cases,67 browser containment cases, both builds, source guard before/after builds; full audit raw{} |
| G1 | [41696369007](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41696369007) | 41 nonfinancial checks; actual Cloudflare SSR/Auth desktop-mobile, target conflict denial, unchanged financial data, containment and cleanup |
| B1 compatibility | [41696369090](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/41696369090) | Existing composition compatibility gate |

C5 precredential checks include19 source mutation controls,11 migration target controls,4 history controls,28 collection callback contracts,35 unchanged sale callback contracts and5 financial verdict controls. Current source admission covers474 protected entries and exactly55 migrations with original54 preserved. C4 native fresh/populated and recording browser previously passed on bc642b8 (run41633766459); this is explicitly historical, not a separate C4 run on a52ee17d.

C5 covers same-key payload conflicts, cross-tenant and same-tenant different-actor replay denial, anonymous/banned actor denial, authenticated raw bypass denial, direct ledger privilege closure/RLS, atomic failed reservation rollback, concurrent same-key single effect, distinct equal payments, old-result replay without balance regression, existing sale/custody/settlement/return/report invariants and fractional quantities. Native actual-hook recovery persists the identity across a simulated long time interval. Browser cases verify hidden reply, reload recovery, authoritative invoice reread and a genuinely new payment at desktop/mobile widths.

The direct-RPC target's `actual_UI_retry_observed:false` describes that direct-RPC test only. Separate browser receipts prove the controlled actual-component browser cases. No real-customer duplication incident is claimed.

Local verification during repair:30 source/target controls and28 collection contracts passed; native import preflight, YAML/Python syntax and port consistency passed. No local Docker/Postgres result is claimed; persisted finance was verified by the isolated hosted jobs.

## Containment, cleanup and diagnostics

The final UID policy admits only loopback API54321, database54322 and fixture4173, plus established loopback replies from fixture4173. A credential-free same-UID HTTP round trip now precedes credentials. Both final C5 jobs report zero unexpectedIPv4 and zeroIPv6 rejects, removed status/state/stack/private files, and successful publication guards. G1 cleanup also passed.

Earlier84bac6d9 failed with36 IPv4 rejects in each mode because fixture server replies were blocked. Cleanup removed the isolated resources, but zero-egress acceptance and safe artifact publication failed. [Labelled safe log transcription](evidence/84bac6d9/firewall-failure.json) retains that failure without publishing private logs.

Local database advisors completed with **0 errors,45 warnings**:43 auth_rls_initplan and2 multiple_permissive_policies. These warnings require review in the remaining performance/security acceptance; they are not an all-clear. Lint's additional warning is Fast Refresh in the new isolated browser fixture. No unrelated warning cleanup was performed.

## Evidence and limits

[Artifact index](evidence/manifest.json) records17 original ZIP archives and verified SHA256 digests; original failed d589f826 receipts are retained beside successful evidence. [Machine-readable result](RESULT.json) gives source/run/status/counts. Archive bytes were verified before Git storage.

The financial browser uses actual collection UI, hooks, React Query, SDK, Auth and stored database. Application-shell routing and unrelated PDF export are fixture boundaries. G1 exercises the full shell only for nonfinancial login. Full application financial journey coverage, nonempty disaster restore, operational backup/recovery acceptance and independent C6 review are not claimed here. This review is by the implementer, not an independent approval.

## Resume point

**ONE NEXT: remaining C5 acceptance**, starting with safe restore of a nonempty database snapshot including the new idempotency ledger, then the same persisted invariants/replay/isolation checks and remaining integrated financial-journey coverage. Reuse these existing fixtures and evidence. After C5, obtain independent C6 review, then the owner's protected C7 merge decision.

Five original drafts27/35/39/49/50 remain unchanged; #50 is tracking context, not a PR containing this entire integration branch. No new PR, merge, deployment, production operation, closure, history rewrite or new cost was performed. Rollback/release coordination remains as documented in the approved impact packet: the new client and RPC/ACL transition must be coordinated; do not re-enable the unkeyed bypass or rewrite applied migration history as a shortcut.
