# B2 / AC-01 final independent review

**Verdict: Approved for human merge — B2 / AC-01 only.** This accepts the reviewed scanner-authorization correction and its bounded evidence. It permits the plan to advance to B3; it does not accept package B or authorize merging the integration branch before B3–B6 and the owner's merge decision.

Exact reviewed and native-tested source: **7a4fb5811c35a053109860c3155074087b930489**, tree `a0aa94a168f1588bad54b58a1edb027c3f164fa9`. Base: B1 handoff `5b66c0e10c4b32419b42e2033bb2026f7e27b889`. Non-implementing reviewer; I made no source/GitHub changes and ran no DB, Auth, provider, production or historical suite actions. Local execution was limited to new pure denial/publication tests and synthetic offline controls.

## Findings and disposition

| Finding | Origin / severity | Final disposition |
| --- | --- | --- |
| AC-01 scanner owner-role authorization bypass | Inherited B2 blocker / Medium | Closed within B2. The upgrade baseline actually reproduces an unauthorized successful scan; the new definition denies it with42501 while real authorized calls remain successful. |
| B2-EVID-UPLOAD-01 detected credentials left in an always-upload sink | Introduced harness defect / Medium | Closed on7a4fb581 by whole-batch quarantine and a successful-publication-output requirement. Independent sensitive tests verified closure. No actual credential disclosure was observed. |
| Ordinary-owner tenant denominator differed from intake | Evidence gap | Closed: a second ordinary owner has a separate tenant, real login and precise denial/data-invariant controls in both native modes. |

No unresolved Critical/High/Medium finding was identified in this scoped review. The original `INITIAL_SCANNER_REVIEW.md` Changes required verdict and `credential-upload-before.json` failure remain intact; neither is converted into a passing historical result.

## Authorization and preservation

The SECURITY DEFINER function now authorizes the captured SQL connection role, rather than the definer's current_user. Authenticated callers must satisfy the existing live platform-admin predicate. Explicit service/supabase-admin roles and the default trusted SQL session preserve the intended privileged boundary. Null/unknown authorization fails closed; trigger text, user metadata and JWT-claim text do not establish connection authority. The existing live activity assertion remains before authorization and every scanner write.

The function search_path is pg_catalog then pg_temp; application references remain qualified. Independent comparison established that the entire scanner body from its first INSERT onward is byte-identical to the inherited definition. The replacement changes authorization/error handling and search_path only. Runtime catalogs confirm unchanged OID, owner, ACL, arguments, return type and definer flag; all other measured function, relation, policy and cron definitions remain equal across the upgrade.

Independent complete-tree comparison found1373 blobs,17 additions and **zero** changes/deletions/mode changes to any of B1's1356 original files. The original341 protected files and45 migrations are exact; the candidate has346 protected files and46 migrations. The applied migration is byte-identical to the reviewed proposal, SHA256 `3bb54ed00e2fb4a7567a34bebfd781af3db9e7a2c9dfc76517c748c1e72b3f66`. App, formulas, package/lock, earlier migrations and A's identity manifest are unchanged. This does not relabel A's preserved288/41 identity gate as compatible with the B superset; resolving the lifecycle of historical acceptance remains B5 work.

## Actual native evidence

I independently fetched run metadata, jobs, decoded raw authorization logs and artifact metadata from GitHub, then read the actual saved JSON/catalog/cleanup receipts and compared every extracted member with the digest-verified ZIP bytes.

Run [39498640904](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39498640904), attempt1, succeeded on the exact source above, with CLI2.101.0 and isolated disposable loopback stacks:

| Job / phase | Actual result |
| --- | --- |
| prepare118890142768 | Success |
| fresh118890249252 /46 applied migrations |95/95 checks,0 failures |
| upgrade118890249168 /45 before migration |48/48 checks, including the expected vulnerable unauthorized200 and an explicitly red denial assertion |
| same upgrade /46 after migration |59/59 checks,0 failures |

The post-migration cases include real admin/service200 positives with durable success, two ordinary owners, two staff, anonymous, trigger spoofing, forged SQL JWT claims, previously valid banned/closed-admin tokens, and unaffected positive controls. Denials require the permission SQLSTATE42501 and the intended unauthorized or account-inactive message; transport/server/expiry errors cannot satisfy the denial oracle. Runtime comparisons cover all22 public tables plus the private closure marker. Immediate populated-upgrade equality is checked before further calls, and the catalogs change only in the intended scanner body/settings. An actual trusted SQL call under the cron job's stored identity succeeds without altering non-scanner data.

Both cleanup receipts confirm the credential-free blocked-egress canary, zero unexpected IPv4/IPv6 rejects, deleted local status/actor files and a stopped stack. Both artifact uploads passed the new publication gate. The ZIP digests independently match GitHub metadata and upload logs:

| Artifact | SHA256 |
| --- | --- |
|12299091301 fresh|`fad21d21e0a6f4b6ab330f9d420a58fe1e8670a03232684ad479798efd64a978`|
|12299007157 upgrade|`0a41f99a9adf7376f1dcaa7d3405718b21ae7d2d63bbf6dc54548b196401a55e`|

Reviewer evidence checks passed77/77. Separately, the new pure unit suite passed5/5 and independent exact-source/synthetic safety controls passed22/22. The latter exercise nested unsafe content, whole-batch removal, a known non-JWT secret, symlinks, read failure, existing quarantine, clean evidence and output-gate ordering. Failure-path gating is supported by helper execution plus workflow source inspection; no failing GitHub upload was intentionally triggered. Earlier successful run39497699622 remains attributed only to00b465, not this final source.

## Limits and continuation

This is synthetic local scanner authorization evidence, not deployment or production acceptance. Financial tables are empty; populated upgrade means users/tenants/scanner history, not B5's nonempty financial lifecycle matrix. Per-operation row/fingerprint comparisons execute in the native probe; not every intermediate snapshot is separately archived. Search_path protection has source/catalog evidence without a live temporary-catalog shadow negative. The cron proof invokes the actual stored SQL identity; it does not observe a scheduled tick. No concurrency, real provider, billing/trial or webhook durability claim is made. B3 AC-02, B4 APP-02, B5 lifecycle acceptance and B6 whole-package review remain pending.

Raw reviewer records: `final-source-preservation.json`, `native-review-expected.json`, `native-review-verification.json`, `SAFETY_FIX_REVIEW.md` and the preserved initial failure records. Any documentation-only handoff must preserve this exact346 protected path/blob/mode set and46 migrations, retain the failed evidence and truthful result attribution, and receive a final publication-preservation check without rerunning these successful tests.

**ONE NEXT: B3 / AC-02 trial and billing correction.**
