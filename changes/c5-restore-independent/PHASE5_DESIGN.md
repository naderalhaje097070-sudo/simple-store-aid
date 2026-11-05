# C5 independent restore — Phase5 SQL replay diagnosis and recovery

Date: 2026-11-05 (Africa/Tripoli). Base 9306fe4da073d3ee688dce7d5bf5baf052f228ab; branch integration/g0-g1-reconcile-2026-10-18.
Same existing C5 task. No production, core financial SQL, migration, unban, policy, merge or deployment change.

## Intake and acceptance
Phase4 restores exactly8 scoped grants and all metadata in fresh/upgrade, then fails at undifferentiated SQL before original-result replay. Distinguish sample SELECT, authenticated actor context and each original replay stage; publish only finite diagnostic labels. Measure selected actor's current status using the existing canonical actor_is_active guard under its saved real-token claims and authenticated role. Preserve the exact old sample query and all existing financial gates in diagnostic iteration.

Source inspection shows the original collection fixture deliberately leaves staff1 banned while recovery selects oldest completed request with >=20 balance without live-authority selection. This is a hypothesis, not runtime proof. Neither an unban nor weakening assert_active_actor is allowed.

## Diagnostic implementation
psql VERBOSITY=verbose is captured privately. Emit only allowlisted SQLSTATE/domain error labels and finite replay-stage names; never raw SQL, messages, claims or identifiers. Canonical actor context emits two validated booleans, active and subject_matches. All selected rows and owners/ACL/RLS/metadata gates remain.

61 local safety cases pass; prior57 test methods preserved by AST. Exact-source native fresh/upgrade, G0 and B1 pending. A correction must follow measured evidence and add positive replay plus blocked-actor negative coverage, without skipping archived business state.

## Completion
Complete existing original-result/no-effect/foreign-denial/payload-conflict/exactly-once-new-payment tests, preserve failed diagnostic evidence and raw workflow artifact ZIPs. Full C5/integration acceptance remains false until the separate full financial journey, independent C6, ownerC7 and RC/Pilot sequence. This drill excludes restored HTTP/Auth, role-password/encryption-key recovery, all-provider-data/PITR/RPO/RTO acceptance.

## Measured diagnostic and correction
Diagnostic 56ce610e2a7286c2c0a461cfe26094dba484b42a, native41992098519, both fresh/upgrade: stage original_replay, SQLSTATE42501, account_inactive, subject_matches=true and canonical active=false. All65 recorded checks passed before expected blocking exception; cleanup/source invariance preserved. G041992098543 and B141992098546 SUCCESS. The source's intentional staff ban was faithfully restored; the positive replay sample was invalid.

Correction keeps the oldest blocked saved request as a mandatory negative control, requires its account_inactive denial and unchanged complete selected relations, then replays a completed saved request owned by a currently active authenticated actor. Select an active foreign-tenant actor for the existing denial. Every actor uses the canonical restored actor_is_active guard and real saved-token subject, never an admin replay. No account mutations. Fail closed if blocked or active saved request or active foreign actor missing; validate all request identities/values before actor queries, bound candidate list to128 (SQL limit129 detects overflow), cache only read-only live contexts. Source rows/archive/full metadata assertions remain exact.

69 local cases pass;61 diagnostic cases AST-preserved and8 selection regressions added. Exact correction native fresh/upgrade/G0/B1 pending. No full C5/integration/independent-C6/merge/Pilot acceptance implied.
