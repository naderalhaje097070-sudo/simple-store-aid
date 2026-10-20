# Rollback and compensation

This preparation: close draft before merge; if later human-merged, additive revert
of this packet/tests/notices. Preserve GitHub evidence; never force push. No schema
or data compensation needed now.

Future authorization migration: stop rollout on active-user denial/caller incompatibility.
Human-approved compensating forward migration restores previous function/policy/grant
definitions from pinned catalog, without data deletion. Restoring permissive access
reintroduces the known disabled-token risk, so it cannot be an automatic fallback;
consider keeping affected entry points unavailable pending correction. No production
rollback command executed. Auth unban is an owner lifecycle action, not test cleanup
in a live environment. Disposable fixture teardown stops stack/runner only.
