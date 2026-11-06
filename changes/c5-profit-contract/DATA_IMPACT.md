# Data and history

Recommended view writes no rows, rewrites no base table and adds no backfill. Existing day_closes.realized_profit135,expense5 and all snapshot rows stay byte-identical through upgrade. New net130 is computed from the SAME recorded snapshot, not today's reconstruction of old payments. Numeric arithmetic has no new rounding/clamp. Null inputs are not coalesced to healthy zero; actual source columns are NOT NULL.

Known source close_day writers use gross basis; legacy authenticated owner direct INSERT/UPDATE and unknown external/service writers mean historical input correctness is unproven. The projection is mathematically derived reporting, not retroactive audit certification. If manual/imported rows violate that basis, assess under a separate authorized plan before treating them as audited; no automatic correction.

Production data volumes, external integrations, provenance and runtime catalog are unmeasured. Native populated55→56 must retain row hashes/counts and saved expense/margin values, including old snapshots whose underlying live payments later change. Reclosing a day keeps existing close_day semantics; this proposal does not make the old mutable upsert an immutable accounting close.
