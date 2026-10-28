# B3 / AC-02 final independent review

**Review Protocol outcome for merging the current head: Changes required.** The general High dependency-audit blocker DEP-20261021 remains open. **The scoped AC-02 correction is accepted on the candidate and B3's independent technical review is complete.** No further B3 SQL correction is requested. This is not approval to merge package B or accept an RC; B4 and the subsequent B5/B6/B7 gates remain open.

Exact reviewed and native-tested source: **117f59289a01c56aeb764be27acfbb45663ec439**, tree `7314cc95072b41698019ef63b707d642382748e3`. Base B2 handoff: `b6ee480f6b11901e8714569f22ad6c63ae088d1a`. Main18700dee is unchanged and does not contain this correction. The review is independent of implementation. I edited only review records, executed pure local source/oracle checks and replayed actual native evidence; I did not run Supabase, SQL, Auth/provider operations, production or historical suites, and made no GitHub/source changes.

## Findings and disposition

| Finding / requirement | Severity and origin | Disposition |
| --- | --- | --- |
| AC-02: client-writable trial/billing fields undermine stored entitlement helper | Medium, inherited canonical finding | Addressed within B3 on117f; baseline bypass reproduced and corrected-state behavior verified. Not fixed on main; no enforced-paywall claim. |
| Disabled-employee and otherwise-permitted inactive INSERT coverage | Required authorization matrix, no demonstrated new source bypass | Completed on117f using an actual staff Auth ban, old JWT, minimal INSERT/settings/read checks and unaffected staff/owner positives. |
| DEP-20261021 | High, current general dependency barrier; not introduced by AC-02 | Open. Blocks current-head/package-B merge and RC acceptance; remediation is outside this SQL correction and required before B5/B6 acceptance. |

No unresolved introduced AC-02 authorization blocker was found. The pending initial review and earlier8f266/intermediateacdf611 results remain attributed to their original sources. The earlier B2 failure evidence and its correction remain preserved, not relabeled.

## Root cause and correction

The inherited authenticated table-level INSERT/UPDATE grant included the five later-added trial/billing columns. Owner/live-actor RLS restricted rows but did not restrict these assignments. Native baseline proves real owner JWTs persist all five UPDATEs and an INSERT containing all five; an expired-trial helper result changes from false to true after a client extension. This establishes the stored helper bypass, not a complete payment-enforcement exploit.

The single forward transaction removes the broad table rights, explicitly revokes the five column rights, then grants INSERT/UPDATE only on the other seven existing columns. Removing the table grant is necessary because PostgreSQL combines table/column privileges and inherited/PUBLIC grants. Actual has_column_privilege observations cover12 columns ×3 roles ×3 privileges: the five protected INSERT/UPDATE rights are absent for authenticated; its seven other writes and all SELECT rights remain, while anon/service effective rights are preserved.

The real onboarding payload name+owner_user_id and the three settings PATCHes remain supported. Existing14-day defaults, RLS/live-actor guard, owner/profile trigger, functions and subscription semantics are unchanged. Backend authority is demonstrated by trusted local service-role PATCH before/after the denial batch and service INSERT afterward; this is not execution of the Paddle webhook or proof of its durability. The owner-run forward compensation revokes client writes instead of restoring the vulnerable grant; it was source-reviewed, not applied. The migration design records metadata-lock/rollout, volume, audit and rollback considerations; no production lock-duration or workload benchmark is claimed.

## Source preservation

Independent complete remote-tree comparison found1435 blobs,16 additions and zero modifications/deletions/mode changes to any of B2's1419 original files. All346 prior protected path/blob/mode entries and46 migrations remain exact; the candidate has350 protected paths and47 migrations. App, package/lock, A manifest, B2 code and all earlier SQL remain unchanged. The generated migration equals the reviewed proposal byte-for-byte, SHA256 `ba73676bfd7ae7b030105ea050067aa0585584946a4aa4406dab2cf8e933d21f`; CLI2.101.0 generator metadata is attributed to stage435e45ea/run39567132845.

The final delta from8f266 changes only the probe and migration-impact document: disabled staff, inactive minimal INSERTs, unaffected staff positive and actual PostgreSQL-version evidence. SQL, workflow, denial helper and unit file are unchanged. Local added-file bytes were matched to remote blobs. Six existing binary blobs are unavailable in the local source copy; their preservation is established by the complete remote tree comparison. No local frozen-install or full local-checkout identity is claimed.

## Actual final-source evidence

I independently fetched GitHub run/job/artifact metadata and decoded raw logs, read the actual JSON/catalog/advisor/cleanup receipts, and compared all16 extracted members with the original digest-verified ZIPs. [Native run39568502042](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39568502042), attempt1, succeeded on117f with CLI2.101.0 and PostgreSQL17.6 on Linux:

| Job / phase | Observed result |
| --- | --- |
| prepare119116554339 | Success |
| fresh47 /119116694091 |240 named checks,0 failures |
| populated46 baseline /119116693990 |52 checks; expected vulnerable persisted INSERT/UPDATE and helper false→true, not an accepted old denial |
| same upgrade46→47 corrected state |211 named checks,0 failures |

Both final modes verify five protected fields with non-null/null assignments, same-value repetitions, genuine SQL DEFAULT attempts, mixed safe+protected PATCH, new/existing upsert, safe metadata upsert without resetting entitlement, homogeneous bulk and multirow atomicity. Column attacks require permission42501 and unchanged data; invalid payload, expiry, transport or server errors cannot satisfy the oracle. The SQL DEFAULT checks assert42501 and snapshot equality; raw SQL stderr is not separately archived.

Two owners/two active staff, other-tenant and anonymous paths, banned/closed owners and a disabled employee are covered. Staff/cross/inactive settings attempts use otherwise-permitted columns, so forbidden billing grants cannot mask the row/state guard. Banned owner, closed owner and disabled staff minimal INSERTs actually return403/42501 with unchanged fingerprints. Disabled staff had a known-row200 before the real ban; its old-token read/settings are403 afterward, while active staffA and ownerB remain successful. The disabled-employee representation is an Auth ban, not every possible membership-removal mechanism.

The populated migration compares all22 public-table fingerprints plus the private closure marker before further writes. Only tenant write ACL/column ACL/effective-right entries change; other relation ACLs, memberships, functions, policies, triggers, defaults, constraints and tenant structure match. Data includes synthetic accounts and billing metadata; financial tables remain empty. The fixed client extension leaves helper false, a trusted write restores true, and B2's ordinary-scanner denial still passes.

Both cleanup receipts show the credential-free blocked-egress canary, zero unexpected IPv4/IPv6 rejects, deleted status/actor files and a stopped stack. The preserved B2 quarantine helper and successful-publication-output gate protect the artifact sink. This is probe-UID containment, not a container-wide egress audit. Actual local advisors report45 performance WARNs per mode:43 auth_rls_initplan and2 multiple_permissive_policies; there is no clean-advisor claim.

| Final artifact | Independently matched SHA256 |
| --- | --- |
| fresh12331226867 |`6bf76d6ebb2a82ec5fa018bb6d09b3e2e6944bebd34a7ca845e87d0916b3dc32`|
| upgrade12331122418 |`54f9c4d7f2f9c70a5c15133f86d87a77335170e44b35139fcde1c0adbbad615b`|

I locally ran the new five pure oracle units,12 independent truth-table cases and four deliberately defective oracle mutations on8f266; all units/cases passed and all bad mutations were rejected. Their helper/unit source is unchanged on117f, whose native jobs also execute the five units successfully. Final evidence consistency checks passed207/207. These are evidence/helper checks, not independent live DB executions or a vulnerability-coverage percentage. Explicit and same_value labels use the same stored non-null fixture value: with null there are two distinct payload values per field, not three. The separate expiry-extension case uses a genuinely different trial value. Arbitrary heterogeneous bulk is not tested.

## Current merge barrier and continuation

Frozen compatibility run39568502102/job119116554312 succeeds on117f:76 units, four original wire round trips, formatting/type/full lint, build and tracked-generation invariance. Full lint retains12 warnings. This does not override G0: I read the actual audit job119116554257 in run39568502010, which exits1 with11 package/advisory entries,8 distinct advisories and3 distinct High. Locked SDK1.31.0, Hono4.13.7, launch-editor2.14.1 and Vite8.0.16 are unchanged by B3. Application-specific applicability is not fully resolved; no exemption or dependency repair is established by this review. The separate quality job119116554749 still fails at `Protected source path set changed` against the preserved A manifest. Neither failure is waived or relabeled as green.

No provider/browser/paywall/concurrency/production or nonempty financial-lifecycle acceptance is inferred. B4 APP-02, DEP-20261021, B5 integrated validation/identity reconciliation, B6 whole-package independent acceptance and the owner's B7 merge decision remain open. A later documentation-only publication must preserve this exact350 protected path/blob/mode set and47 SQL, keep the failed/pending evidence and truthful per-SHA attribution, and receive a bounded final preservation check without rerunning these successful tests.

Review records: `final-source-preservation.json`, `final-native-expected.json`, `final-native-verification.json`, `audit-review.json`, `first-native-replay.json` and the original initial/oracle records. **ONE NEXT: B4 / APP-02** under the standing plan; resolve the audit barrier before B5/B6 final acceptance. No B merge/RC approval is granted.
