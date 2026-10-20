# MONJEZ account-chain independent read-only review — 2026-10-19

Outcome under `docs/governance/REVIEW_PROTOCOL.md`: **Changes required**, scoped to account-chain and its integration readiness. Two inherited authorization/integrity defects remain in the final PR71 source. This is not a blanket application audit, human merge approval, or proof of a live exploit.

## Identity and review boundary

Canonical repository: `naderalhaje097070-sudo/simple-store-aid`. Read-only GitHub connector used; no repository/code/provider/production mutation, CI execution, installation, merge, deployment, or secret access. Only this report is written locally.

Read AGENTS, top PROJECT_STATE/TASKS/DECISIONS and REVIEW_PROTOCOL at documentation head `1028441558e7db7b0b25390f2b8ee452b702774b`. The user's canonical repository overrides the historical droid repository selection in AGENTS. The top state expressly leaves the account chain and financial acceptance open.

Open PR metadata independently reconstructs:

| PR | Head | Base relationship |
|---|---|---|
| 56 | b9aa56bc3bb30948d95961c06fd493dfb866f476 | common54 57fb508b9d239aaf4676352dd97654341416c46a |
| 57 | fd2bed16a051a6d4de44f8b97c1a5ba9a36e50fc | 56 |
| 58 | b8fd5e95ab1f6eee07bb6198da3169cd46916962 | 57 |
| 59 | fd95ad2e1966362719965ef282de1e2eb66cb070 | 58 |
| 60 | e4ee6bafc8adec292826769ec37ad1d21e97ae95 | 59 |
| 61 | 315751c46678fa18ffc35dae1e8d6e2cb9b30335 | 60 |
| 62 | 26d6e271ad1a50a26390d25d3236edb5ab47fff7 | 61 |
| 63 | 3cb0d82afe31eb2d81538fd7ae631c10fdfa0357 | 62 |
| 64 | 2ae95ed6175e0859b4c0a1d36d1110f99f19c792 | 63 |
| 65 | f37885b1ff5dcc9ab113e5cbee4516b485cedadd | 64 |
| 66 | 9d30064d0d42667bf4b1de6469c319e625b9f33d | 65 |
| 67 | 6af3e15028a798752eda98c30924b7b30620a356 | sibling above66; not an ancestor selected by68 |
| 68 | 00923287d804f99faa1b70d28cece17f9f33eac3 | 66 |
| 69 | 92ebd529c79ae1df98ec02245d3c22d6bcfc557f | 68 |
| 71 | 7f74b704c4b66d3da1605aa509b7c8e1eb104507 | 69 |

All source locations below refer to final71 `7f74b704c4b66d3da1605aa509b7c8e1eb104507` unless another source is explicitly named. Fetched all 45 final71 migration files directly and inspected grants, policies, triggers, caller checks and later overrides. Independently recomputed all45 SHA256 values against the archived native owner-closure fresh receipt: **45/45 match**. This supports historical source identity; it does not make those runs executions of final71 or the integration foundation.

Foundation executable `823cbcaf4a83ae8b4bea44e314df4c1215a9ba3b` / documentation1028441558 does not compose this chain. Original72 remains6da4dad and main43d6edb are explicitly unchanged in the reviewed top state. Historical account tests cannot close that integration gap.

## Finding AC-01 — active ordinary users can invoke the global security scan

Severity: **Medium**.

File/contract: `supabase/migrations/20261010223557_enforce_live_account_state.sql:975–998`, especially978 and989–994; initial grant in `20260627213042_44ccde2c-0b2b-484c-adc0-c67f078d5e16.sql:170–171`.

Evidence:

- Final definition is SECURITY DEFINER. Its authorization permits current_user postgres/service_role/supabase_admin, otherwise requires is_platform_admin.
- In a SECURITY DEFINER routine, current_user is the function owner, not the ordinary calling role. The retained native43 catalog at `changes/owner-retention-verify/evidence/native-9a5a/catalog.json`, entry `public.run_security_scan`, reports owner postgres, definer true, owner_bypass_rls true, authenticated EXECUTE true, anon false.
- Catalog provenance: companion catalog-result.json pins source `9a5a58f6a8556f009880437c0cf95ac91c38c770`, catalog-only/no-lifecycle/no-fixture scope; final71 preserves catalog Git blob `ca8de3b9c422ffd6a3f2214f95bc48c11dd8cff8`. This historical native catalog corroborates ownership/ACL, not a fresh unauthorized call.
- Final71's migration42 reproduces this authorization and adds the live-account assertion. That assertion deliberately permits every live auth.uid; it is not an admin check. Migration44 only revokes TRUNCATE. Migration45 only adds closure state / changes actor_is_active / creates close_owner_account. Neither revokes this EXECUTE grant nor replaces the scan.
- Therefore the current_user condition is false for an active ordinary authenticated user, and the platform-admin rejection cannot protect the call.

Minimal source-derived counterexample: an unbanned, undeleted, unclosed authenticated user without a platform_admins row sends `POST /rest/v1/rpc/run_security_scan` with `{"p_triggered_by":"ordinary-user"}`. Lifecycle passes; function executes as postgres; platform authorization condition does not reject. It then inserts security_scan_runs and updates global security_scan_findings. No executed exploit or HTTP result is claimed.

Risk: unauthorized global administrative work and security-state mutation, arbitrary trigger labels, repeated expensive catalog scans and possible interference with monitoring. This is inherited from June, retained by PR59, and newly reported in this review; it is not a newly introduced closure bypass. Its demonstrated scope does not include arbitrary table writes or secret disclosure.

Severity rationale: Medium reflects a fixed diagnostic routine with fixed catalog queries/writes and a counts/run-ID response. The caller cannot supply SQL, choose arbitrary table writes, or obtain tenant records through this function. Global monitoring integrity and unnecessary privileged work are still unauthorized; a future finding of sensitive output, practical resource exhaustion, or additional privileged effects would warrant reassessment. Scheduled convenience does not authorize ordinary callers: both the function comment and platform-admin read policies explicitly restrict the intended audience.

Required fix: use a trusted caller-role check that survives SECURITY DEFINER, with an explicit narrowly bounded service/cron exception and an independent auth.uid platform-admin assertion for ordinary authenticated callers. Preserve disabled-account denial and valid scheduled service behavior. Use an additive migration.

Verification method: fresh + populated upgrade on the selected integrated source. Active non-admin owner, staff and no-tenant users must fail with a named authorization error and zero global scan-state delta; inactive admins must fail; active platform admin and approved service/cron calls must still succeed. Verify effective ACL/owner/definition from pg_proc, not only migration text. Existing closure/expiry positives do not test this unauthorized-active-user path.

## Finding AC-02 — owner-writable billing fields undermine the entitlement helper

Severity: **Medium**.

File/contract: `supabase/migrations/20260626142422_e1e5cd70-ffee-4f24-b2ae-eebd0db18705.sql:13,115–118` (full-row UPDATE and owner policy); `20260628075333_7b947a26-c419-48d9-b41e-55909cd48566.sql:55–60` (billing fields); final entitlement definition `20261010223557_enforce_live_account_state.sql:1165–1191`, especially1184–1188.

Evidence:

- Authenticated users retain table-wide INSERT and UPDATE on tenants. The owner UPDATE policy checks only that owner_user_id remains auth.uid. The restrictive current-actor policy adds activity, not column integrity.
- The later subscription migration adds trial_ends_at, subscription_status, subscription_plan, paddle_customer_id and paddle_subscription_id to that table without narrowing owner grants.
- All45 migrations contain no later tenant column UPDATE revoke or validating tenant billing trigger. Native43 catalog corroborates full UPDATE/INSERT, the owner policy, and tenant triggers limited to touch_updated_at and after-INSERT handle_new_tenant; their inspected bodies do not protect billing fields. Migration44 changes only TRUNCATE. Migration45 does not modify this contract.
- tenant_has_active_subscription trusts `tenants.trial_ends_at > now()` as an OR alternative to a provider subscription. It adds only the live-account check.

Minimal source-derived counterexample: an active owner PATCHes their own tenant's trial_ends_at to a future date, leaving owner_user_id unchanged, then calls tenant_has_active_subscription for that tenant. The UPDATE is permitted and the helper returns true without a paid subscription. Likewise onboarding INSERT can supply its own trial/billing fields. This is not merely changing a displayed settings label.

Risk: caller-controlled billing/entitlement state and untrusted provider linkage. **Important scope limit:** inspected app.tsx has no subscription/entitlement call, and this review did not establish a current enforced paywall consumer. This is a proven database authorization/entitlement-contract defect, not a claimed live paywall exploit, Paddle transaction, provider compromise, or demonstrated revenue loss. It predates the account-chain changes and remains inherited at final71.

Required fix: define the allowed owner settings columns and reserve trial/provider/billing fields to trusted server operations, including INSERT. Preserve the supported name/timezone/business-type flows. Do not silently remove trial functionality; record the intended onboarding/trial policy and enforce it server-side.

Verification method: fresh + populated upgrade; ordinary owner attempts to set/extend trial or replace provider IDs must fail with zero stored change. Allowed settings updates and approved server-created trial/subscription events must succeed. Validate helper output for expired, no-subscription, paid, canceled-period and environment cases. Trace every intended entitlement consumer before asserting product paywall protection.

## Scoped assessment of prior work

- **PR59:** live state is read from auth.users; deleted_at and banned_until are enforced for the current actor.33 rewritten public functions each call assert_active_actor and22 authenticated restrictive table policies use actor_is_active. The separate forward profile-policy compensation preserves the predicate while avoiding the documented recursion boundary. Existing function ACLs are preserved by CREATE OR REPLACE, so this lifecycle fix does not repair every inherited role/tenant policy (AC-01/02).
- **PR62 / supporting61,63,64:** issuer derives from validated explicit deployment config; JWKS is issuer/.well-known/jwks.json and accepted audience remains authenticated. No explicit disabling of the OAuth-client claim requirement. Tools pass the real caller token through a publishable client to REST/RPC rather than a service-role client. Inspected crypto fixture uses the actual locked MCP handler, with valid/bad-signature/issuer/audience/expiry/missing-client cases; synthetic fixture tokens are correctly separate from genuine provider lifecycle evidence. Archived natural-expiry evidence names actual provider tokens, elapsed wall time and old/new continuity, and expressly excludes full lifecycle/isolation acceptance. No issuer/client bypass found in this scoped source inspection; no independent crypto/native rerun.
- **PR68:** migration revokes client/PUBLIC TRUNCATE on22 enumerated app-public tables and postgres public defaults, with a fail-closed check for global/inherited defaults. No DML or provider schema change. Archived upgrade receipt c233f156 records non-target privileges/structure and rows unchanged, future-default probe rolled back, and closure_verified/integration_accepted false. It does not claim destructive TRUNCATE execution or universal future-table protection for other creators.
- **PR69:** close_owner_account has no target argument or service-role execution grant; checks authenticated role and auth.uid, locks the retained Auth row, verifies live Auth before the narrow constant idempotent reply, verifies own tenant+owner role, and writes one private marker. Marker table has RLS, no client/service DML, and auth.users FK RESTRICT. Existing active-actor consumers then deny the closed account. No public/financial/Auth row mutation appears in the closure function.
- **PR71:** resolvePaddlePrice checks authoritative current_tenant_id through the same authenticated Supabase context before gateway/keys; nullable tenant is allowed; exact inactive maps separately from unavailable; deadline abort and timer cleanup fail closed. This addresses the previously documented OC-APP-01 only for that function, on an unmerged candidate.
- **Privileged ingress inspection:** email worker requires exact service-key bearer authorization; Paddle webhook verifies provider signature then uses privileged Supabase access. Neither is evidence that all service-origin actions cease on owner closure. No provider request was made. External cancellation, webhook ordering/error recovery and production configuration remain unaccepted operational/billing scope.
- **Deletion claims:** closure retains identity and references; it is not Auth erasure or provider cancellation. Source still contains older Auth-owner -> tenant cascading FKs. For accounts with a closure marker, the added RESTRICT reference prevents ordinary hard deletion while it remains. No destructive hard-delete/cascade was executed by this review, and a cascade's full completion is not inferred from FK text (triggers can abort a transaction). Existing audit actor links and history retention should not be represented as erased/anonymized.
- **Financial49/50:** not independently re-reviewed here. The October lifecycle migration redefines existing financial routines; the parent review owns final-effective financial behavior/ACL reconciliation. Passing the one direct-cash retention fixture is not general financial approval.
- **Direct financial table privileges:** a suspected authenticated INSERT/UPDATE bypass on orders/order_items/payments is not supported. Migration20260627201534 lines511–513 explicitly revokes INSERT/UPDATE/DELETE, and native43 catalog reports all three false for authenticated on each table. Retained staff write policies do not grant privileges. Final44/45 do not regrant them;44 also removes TRUNCATE. This does not validate every financial RPC.

## Evidence independently checked and actual replay limits

Directly fetched native raw JSON and inspected underlying probe source, not just previous reviewers' conclusions:

| Historical evidence | Recomputed/inspected result | Limit |
|---|---|---|
| owner closure source df9221e20b026ad82f6a8365ab203c9023b9963d | fresh166/165 distinct; upgrade171/170 distinct; all observations pass, marker1, integration false | duplicate before/after TRUNCATE label is known OC-EVID-02, not distinct scenarios |
| fixed price source708e43f3e11bbb0882b4930e0b18b7b598c0b36a |121 unique passing observations, integration false | existing OC-APP finding addressed only in unmerged price candidate |
| price baseline6807c198 | inspected original raw matrix and later independent review | no live provider execution by this reviewer |
| MCP issuer29af5b34d3c55c6db1c4debc5d93d8587d2c04fe | genuine OAuth flow and scoped active/ban observations; integration false | original focused adapter proof; later full route is a separate artifact |
| expiry44a0d221e635340b8450334ed9484c3f39f48205 | inspected ordered expiry/continuity observations and explicit limits | historical43 migrations and prior runtime, not integrated foundation |
| TRUNCATE c233f156220b4551e82edccec3eaff9161c20ba3 | all recorded upgrade checks true, integration/closure false | ACL/catalog proof; no destructive statement |

Actually executed in this review:

1. All45 fetched final71 SQL SHA256 checks against the raw native fresh closure receipt:45/45 PASS. Initial oversized single-command attempt failed with argument-list-too-long; bounded read-only batches all passed; no files were created by those checks.
2. Eleven explicit source/archive assertions:22 policies,33 guarded rewrites, trusted-role check, closure FK/self identity/order/no public DML, MCP issuer settings, closure observation acceptance flags and121 unique price observations:PASS.
3. Original two ClosureEvidenceOracle unittest methods replayed from fetched source in memory, compiling only the actual explicit_inactive/expected_fixture helpers and loading the unmodified original test class:2/2 PASS. These validate error-oracle and expected-fixture arithmetic only.

Not rerun: Bun/TS tests, cryptographic MCP verification, SDK requests, native DB/migrations/Auth/PKCE, full TanStack/Cloudflare route, browsers, builds, CI/Quality, scanner RPC, trial mutation, webhook, provider, concurrency or production. No new native logs/ZIPs were fetched or certified in this review; inspected stored JSON is historical evidence, not an independent native replay.

## Remaining acceptance work

AC-01/02 require explicit disposition before merge under REVIEW_PROTOCOL's Medium rule. The selected final integration source must then actually compose the accepted account/security candidates and receive appropriate fresh/populated-upgrade, old/new-token, tenant/employee/privileged-ingress and retained-history proof. Historical final71 evidence does not satisfy that obligation.

Known exclusions remain: in-flight/concurrent closure, multi-store and additional memberships, same-tenant staff continuity, commercial cancellation and retention/erasure policy, complete provider egress, production performance/operations and release/Pilot acceptance. No opening/reopening or marker deletion is an approved rollback. Withdrawal must preserve history; this review implements nothing.

## Financial peer-check addendum requested by lead reviewer

Independent source challenge confirms the following two lead-review findings. This addendum expands only the peer-check scope; it does not replace the lead financial report or assert native SQL execution. Read the lead's verified local41-schema/49/50/59/source50 client material, compared effective account-chain catalog constraints/triggers and final71 definitions, and independently read49/50 remote metadata/files. PR49 head3106b4710fb9214d6f406d5a3fe7bf44fa2823e6;PR50 head193412a01938d752a98689d85acd727664e4dc8e. Local inspected Git blobs:49 migration1e6654acdad1591229df91b77981de264612d738;50 migrationc6a97b4af3b43fc7d6ed2e5b67890aeed77f79d7;59 migrationd632a985f2330c8f969cd49aa9a7d5fba2e38bfe;50 db.ts44c6c3ce7983139686dcff847c197cc5aaf2c357. No model result is called a database test.

**FIN peer1 — High, inherited fractional-quantity / integer-stock mismatch.** Initial20260626143241 products.stock is integer while order_items.qty is numeric(12,2). PR49 core at20260815170000:77–90 accepts positive fractional quantity and144–150 inserts that numeric quantity then assigns stock-v_qty to integer stock; PR50's idempotent entry delegates to this core through v2. There is no whole-unit validation, later stock type change or enforcing trigger in the inspected chain. Counterexample: active authorized staff, valid product with stock10,price100,cost0,one direct paid25 item qty0.25. Item qty>0 and stock>=qty pass; order total25/paid25 satisfies payment/customer constraints. Numeric9.75 assigned to integer stock rounds to10, while the stored item records0.25. Repeating distinct sales can leave stock10 despite fulfilled units. Stock>=0 does not reject it; product trigger only touches updated_at. This is source/cast-semantics reasoning, not an executed stored-value result. Fix must choose/enforce integral quantities or a consistent supported fractional stock representation, then prove persisted sale/return/delete/duplicate-line behavior on fresh and populated-upgrade DBs.

**FIN peer2 — High, financial integration regression from later definition override.** PR49 migration20260815170000:249–263 rejects backward transitions/custody reduction, and300–317 makes update_courier_order_state delegate to the guarded v2. But later migration20261010223557:1209–1257 recreates the same legacy signature with a direct setter, bypassing v2's transition rules; source50 db.ts:614 actually calls this legacy RPC. PR49 grants authenticated EXECUTE;PR50 revokes sale RPCs only;same-signature CREATE OR REPLACE preserves this existing ACL. Native43 catalog corroborates authenticated legacy EXECUTE, and44/45 do not replace/revoke it. Counterexample for a normally ordered composed fresh chain: live same-tenant staff calls pending on a valid courier order with existing customer,courier,total100,paid0,statusdebt,state delivered_full,collected100. The late function passes active/staff/courier checks and writes pending/collected0. Existing nonnegative/not-over-total and49 outcome CHECK allow that row; audit trigger records the change but does not forbid it. No settlement payment is created, so custody can disappear from recorded balances. Auth restrictions are not a transition guard. This is a source-proven composition hazard, not a live exploit or main-branch regression claim. Applying backdated49 after already-applied59 can yield a different effective definition from a fresh chronological chain. Resolve with a forward integration migration preserving both lifecycle and canonical financial transition behavior, and verify effective pg_proc/ACL plus persisted balances for fresh/populated-upgrade orderings. No grant-resurrection claim is made.

