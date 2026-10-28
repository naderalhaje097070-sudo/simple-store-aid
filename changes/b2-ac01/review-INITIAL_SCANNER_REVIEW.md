# B2 / AC-01 early independent review

Reviewed proposal stage **7c87cfb13c6f6f121f7e7909ac17a61b1e405b96**, tree `10661120d832723f2238fe4466daf8e45abbbf34`; generated-migration candidate **00b465ad397f8e3e715ec13b6835c110ab4e4469**, tree `cbff7285a0cdaa9635c2030d7db2d9cd1e7324f9`. Base B1 handoff5b66c0e1. Non-implementing reviewer; no DB, Auth/provider, production, migration or historical suite execution.

**Early outcome: Changes required.** One confirmed Medium harness-safety issue is described below. Final functional acceptance is also pending exact-final-source native fresh/upgrade evidence. No new scanner authorization bypass was established from source review; B3/B4/B5/B6 remain outside this review.

## Source assessment

The root cause is correctly identified: the old SECURITY DEFINER check consulted current_user, which becomes the function owner. The previously captured connection role was unused. The proposed explicit role allowlist avoids that owner bypass and does not trust p_triggered_by or JWT/user-metadata role text. The authenticated path requires the existing live platform-admin predicate; trusted service/SQL identities retain the existing live-guard exemption boundary. The activity assertion remains first, before authorization and all scanner writes; IS DISTINCT FROM true denies unknown/null conditions.

Search_path is restricted to pg_catalog then pg_temp, with application references qualified. This follows PostgreSQL's documented requirement to search the writable temporary schema last. Ownership/ACL preservation through CREATE OR REPLACE must still be confirmed in native catalogs; the upgrade oracle compares OID, owner, ACL, signature and return type. The entire scanner body starting at the first INSERT is independently byte-identical to the inherited45-migration definition: only authorization/error and search_path change. No financial, schedule, grant or provider-contract change was found.

The actual candidate has1372 blobs and16 additions, with zero original path/blob/mode modifications or deletions versus B1. All45 original migrations remain exact; the46th migration is byte-identical to the reviewed payload. CLI generator metadata ties its filename and SHA256 `3bb54ed00e2fb4a7567a34bebfd781af3db9e7a2c9dfc76517c748c1e72b3f66` to stage7c87. I did not run that CLI.

## B2-EVID-UPLOAD-01 — Medium, confirmed failure-path defect

File/contract: `.github/workflows/b2-scanner-auth.yml`, credential scan at216–219 and always-upload at223–228 in reviewed stage.

Evidence: the cleanup step copies evidence directly into `ac01-evidence`. Its detector raises AssertionError on credential-like content but leaves the detected file in that same directory. The following upload-artifact step has if: always() and uploads that directory even after detection failure.

I executed only the exact four-line scan block in an isolated temporary review fixture containing a deliberately invalid synthetic marker, no real credential. It detected the marker, raised, and left the payload inside the configured upload sink. No workflow upload was performed and no actual leak was observed. Raw result: `credential-upload-before.json`; exact reviewed workflow snapshot: `stage-workflow.yml.txt`.

Risk: a detector hit does not prevent publication of the detected payload; evidence can contradict the intended credential-free artifact boundary.

Required fix: quarantine or remove unsafe content before the always-upload step can see it; retain a sanitized failure/digest receipt and legitimate failure evidence. Do not simply hide all failed runs. Add an offline sensitive negative control proving that detected content is absent from the upload sink and the job remains failed.

## Oracle coverage and limits

The denial helper correctly requires401/403 plus42501 and distinguishes exact inactive versus unauthorized errors; HTTP500, transport, expiry and unrelated errors do not pass. The probe establishes real admin/service positives, forbidden ordinary/staff/anonymous calls, metadata/trigger/JWT-claim spoofing, banned/closed old-token denial, durable allowed scans, public/private fingerprints and an actual trusted SQL call. Upgrade records preserve data and compare all non-scanner catalogs; source/proposal body equality is checked.

One claim needs alignment: intake says ordinary owners across tenants, while seed currently contains one ordinary owner and two staff subjects across two tenants; the other owner is a platform administrator. Add the second ordinary owner or narrow the stated denominator. This is an evidence-description gap, not a newly demonstrated authorization bypass.

The safe search_path is currently structure-checked; a live temporary-catalog shadow negative is not present. Trusted SQL proof is an actual call under the cron role, not observation of a scheduled tick. Financial tables are intentionally empty; B2 proves scanner-only effects and populated nonfinancial upgrade preservation, not B5's wider nonempty financial/authorization matrix.

ONE NEXT within B2: fix/dispose the upload finding and align the actor ledger, then review the exact final migration/tests/workflow SHA against actual native fresh46 and populated45→46 receipts, precise denials, unaffected positives, complete fingerprints/catalog invariants, containment and cleanup. Do not transfer pending or earlier-source results to a changed candidate.
