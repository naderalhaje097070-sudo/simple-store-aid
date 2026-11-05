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
