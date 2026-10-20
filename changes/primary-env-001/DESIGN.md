# Reconciliation design

Root cause: an implicit production credential fallback and absence of one build/runtime environment contract. Reuse PR48 current source head31958e53438b377a9896dd0bf7e9c268c1f14aef, not its stale PR description/earlier green ancestor. Stack onto immutable PR53 head54c930166a776828566876771efdec86a997fa53; preserve its generated lock and security guards.

Additional bounded fixes: (1) reject known privileged key formats before browser defines; (2) isolate safe proxy fixtures and add explicit proxy rejection scenarios; (3) attach auth/destructive routing to whole contexts, matching existing visual design. Add offline actual-server-wrapper runtime scenarios.

No feature flag: fail-closed startup is the intended guard. Rollout is draft -> independent exact-source review -> hosted/current-head evidence + isolated integration prerequisites -> human-controlled environment-specific release. User authorized this implementation on 2026-10-10 and continuation without hosted Actions; that does not accept blocked release gates.

Governance timing: intake and defect reproduction were recorded before reuse. This packet records impact/design reconciliation of already-existing PR48 work during this batch; it does not pretend these new documents existed before reuse.
