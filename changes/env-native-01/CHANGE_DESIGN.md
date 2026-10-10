# Proposed design — Gate 3, awaiting intake approval

Root cause: valid JWT identity is reused by policy/role predicates without consulting
current account state. Owner direct-UID policies and SECURITY DEFINER RPCs make a
tenant-helper-only patch incomplete. The real archived own-tenant read confirms one
path; broader paths remain to be reproduced, not presumed exploited.

Smallest coherent correction: one live caller lifecycle predicate below the API,
enforced across direct RLS and all exposed privileged actor paths. Prefer a private,
caller-bound helper returning only active/denied; validate Auth schema and ban-expiry
contract first. Guard existing tenant/role/admin checks and mandatory direct-UID
policies without changing their resource/financial rules. Definer RPCs need explicit
guard at entry or a proven mandatory shared guard. Trusted service jobs must remain
separate and least-privilege. JWT metadata or UI redirects cannot supply this state.

Options retained for catalog review: restrictive authenticated policies AND existing
permissive rules, versus editing each existing expression in a new migration. Do not
choose based on lexical inventory alone. All public definer bypass paths must be
resolved before implementation; no magic blanket claim from one helper edit.

Acceptance: L01–L15 in TEST_IMPACT on baseline/final exact source with honest failure
classification; fresh/prior-state migration compatibility, stable active RPC contracts,
no history mutation, explicit grants/search_path and measured indexed lookup cost.
No flag that bypasses denial. Rollout only after independent high-risk review and
human merge/deploy approval. In-flight transaction semantics and unban/expiry controls
must be recorded before live acceptance, not silently broadened in implementation.

PR decomposition: current draft prep/oracle; after owner-approved intake, isolated
Gate4 live harness/baseline; then one forward-only auth correction with final negative
and active controls. Financial execution remains a later gated dependent task.
ONE NEXT: owner review/approve this exact lifecycle intake and L01–L15 harness scope,
then execute the focused clean baseline on a verified disposable runner.
