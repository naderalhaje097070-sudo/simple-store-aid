# Data and history

Existing profiles has no account-disabled authorization column in this candidate.
Use provider-managed live Auth ban state only after verifying pinned schema and
behavior; do not derive permissions from user_metadata or frozen JWT claims.
No data/role/profile/assignment deletion, financial update or backfill is proposed.
Auth/profile/tenant foreign keys have deletion cascades: deleting a user/tenant is
not an acceptable disabling mechanism. Owner unlinking/employee product behavior
is not expanded by this defect; historic audit actor IDs and financial rows remain.
Prove before/after canonical content checksums under trusted isolated observation,
not disabled-user visibility. No production data volume is inspected here.
