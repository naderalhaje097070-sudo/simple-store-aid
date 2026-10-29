# C3 migrations/rollout
Original20260815170000/171000 copied byte-exact from original50. All51 current SQL untouched. Pinned2.101.0 migration new c3_reconcile_financial_adapters actually generated20261029044024; telemetry disabled. No invented timestamp. Correction transaction has lock_timeout5s, CREATE OR REPLACE/grants/schema notify only; no row scans/backfill/index rebuild. Original August constraint ALTER may need ACCESS EXCLUSIVE orders lock; table/index creation original. Volume/lock timing unknown; fixture success cannot prove production performance.

Fresh: chronological53 without correction → expected-red → forward54. Upgrade: accepted51 + nonempty sale → migration up --local --include-all original2 → expected-red53 → forward54. CLI help verified include-all/local. Observe actual history, catalog bodies/owner/settings/ACL and fingerprints in both orders. Original CHECK stays NOT VALID.

29Oct official changelog scanned; upcoming hostedTLS1.2 cipher deprecation does not alter local loopback tests. Official function/role docs checked. AdvertisedCLI2.122 not installed;2.101.0 preserved. Advisor only if official CLI has --local; otherwise record unavailable, no production fallback/clean-advisor claim.

Release requires C4 client, explicit C identity, C5/C6, backup/preflight/restore and separate owner action. No production migration authorized.
