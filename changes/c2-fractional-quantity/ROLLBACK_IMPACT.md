# Rollback

Do not cast fractional stock back to integer or silently round historic/current quantities. A later code rollback must remain compatible with numeric stock; forward compensation may remove faulty behavior only after assessing preserved fractional data, never drop data or recreate non-idempotent/auth bypasses. Applied old files stay immutable and original branches remain.

This batch does not execute production migration, backup, rollback drill or restore. Before release, schedule type-change locks, backup/restore and a separately reviewed compensation. Unmerged candidate can be reverted additively on integration without history rewrite.
