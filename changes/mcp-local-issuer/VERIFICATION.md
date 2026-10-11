# Focused candidate verification — 2026-10-11

Source29af5b34d3c55c6db1c4debc5d93d8587d2c04fe actual handler lifecycle: GREEN,
51 controls. Run38165648102 job114547536750 / artifact11712066666. Full sanitized
receipt is versioned in evidence/native-29af.json and printed in the job log. The
provisional PR comment6112517145 said52 controls; correct count is51.

| Boundary | Actual result |
| --- | --- |
| Genuine local OAuth code/PKCE / provider verification | A+B pass; client-bound tokens |
| initialize / initialized / stateless / tools catalog | A+B200 /202 empty / no session-id / exact four tools200 |
| Four tools before ban | A4/4 +B4/4 succeed |
| Persisted B ban | PUT200 and SQL banned_until>now true |
| Same pre-ban B token | Four explicit account_inactive tool errors; no empty-list acceptance |
| Other tenant A after ban | Four successful calls |
| Containment / stored state |0 blocked requests,0 SDK exceptions,22 public hashes identical |
| Seven finance tables / cleanup | all zero / keys removed and stack destroyed without backup |

CLI2.101.0, Bun1.2.14, SDK0.20.1, actual Auth imagev2.188.1. Actual pinned Auth
source internal/models/oauth_authorization.go confirms SecureAlphanumeric(32), matching
corrected harness guard (earlier v2.194 diagnostic source has same public contract).

Quality38165648142 PASS: typecheck, changed-file lint,66 units/159 assertions,
offline server boundary, browser containment, mode-env build and regular build.
Issuer contract38165648144 PASS6/6/34 assertions. Python6/6 PASS. Synthetic crypto
unit tests exercise strict negatives independently; they are not genuine-token proof.
Separate agent source review and independent local targeted rerun found no new bypass.
Final-head evidence/review remain required after this receipt and formatter cleanup;
results will be appended to PR62 and #55 on the exact head without altering it again.

Baseline red3771dcb run38140972804, and first repaired candidate febaeae failures
(run38165292169 formatting, run38165292174 wrong public-ID UUID assumption) are
retained. No historical broad fresh/upgrade regression suite repeated.

Scope: actual application MCP definition plus locked protocol handler over local HTTP,
not the full TanStack HTTP route. Nonempty finance or foreign-tenant payloads, cloud
OAuth deployment, concurrency, main integration and release approval remain unproven.
Draft PR62 is stacked on draftPR61/60, all unmerged. No merge, deploy or production
change occurred. ONE NEXT: planning review for a separately authorized full-route batch.
