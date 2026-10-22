# B-DEP-IDENTITY-01 — independent source disposition 2

Reviewer: /root/dep_identity_review. Reviewed latest unpublished local source after continuation. This addendum supersedes the two open source dispositions in IMPLEMENTATION_REVIEW_DRAFT.md; it does not claim a published or native-tested final head.

## Closed findings

- BDEP-REVIEW-01 Medium CLOSED in inspected source: rejectUnread() cancels existing unlocked request bodies without awaiting client-controlled cancellation. Early declared-length/aborted/used-body conditions share this path. Focused cancellation controls are present.
- BDEP-REVIEW-02 Medium CLOSED in inspected source: verifier now retrieves the complete fixed B_BASE_SHA migration tree and compares50 path/blob/mode identities. Regression controls coherently rewriting migration049 plus the new manifest, or its executable mode plus the manifest, require rejection.

Independently executed `python tests/g01-acceptance/test_integrated_identity.py`:29 tests passed. Re-inspected helper/server wiring, entry.test.ts, native-http.mjs and b-dep-verify.yml read-only. No introduced Critical/High or remaining blocking source finding identified in those inspected changes.

## Verification wiring gap to resolve before final acceptance

The current b-dep-verify.yml executes the29 disposable fixture tests but does not yet call verify(Path.cwd()) against the actual committed B manifest. The old g01-acceptance.yml runs on a different historical branch and cannot be assumed to execute this current-source check. Add actual committed-tree identity verification and durable receipt to the current workflow after manifest publication. Negative fixture tests alone are not actual-source identity evidence.

## Pending evidence and precise limits

The standalone native HTTP fixture runs the actual built application entry and existing missing-bearer handler; it does not contact a live database, authorization server or provider. The compiled actual-entry fixture stubs only the delegated framework handler and proves placement, byte/header replay and refusal before delegation; it is not full OAuth/transport proof. Actual current-source frozen install, typecheck, lint, unit tests, build/source invariance, complete supported audit and native HTTP results remain pending. Native Windows-specific claims still require actual Windows execution.

The official preparation graph changes Vite-required rolldown/lightningcss/platform dependencies and relocates already-existing picomatch4.0.4/4.0.7 copies. It must be described as an explained generated graph delta rather than a four-package-only lock edit. Current captured baseline has13 package/advisory entries and10 unique GHSA, including two additional Vite advisories; earlier11/8 counts remain historical.

Formal outcome remains Blocked pending missing evidence. No whole-B/B5/B6/merge/deployment/production acceptance is granted.
