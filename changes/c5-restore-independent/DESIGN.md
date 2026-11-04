# Design and primary-source review
Prior restore failed because pg_cron cannot be installed in a second database in the same cluster. Preserve that diagnostic; new cluster uses original postgres DB name.
Exact source container/image/role inventory and installed tool help are discovered before target creation. A unique bootstrap superuser avoids collisions with pg_dumpall roles-only output. Read role definitions without passwords; restore with ON_ERROR_STOP. Start same image with raw initdb/postgres, bypassing Supabase service bootstrap scripts. pg_restore --create restores DB settings/ACL/owner and full archive into postgres; no excluded objects.
Same source image and preloads used; cron.launch_active_jobs=off at startup; no TCP or network. Snapshot compares named metadata rather than cluster OIDs and includes prior assertions. Roles/memberships have one explicit target-only bootstrap exclusion. Encrypted-key recovery remains unproven.
Primary sources checked4Nov2026:
- https://supabase.com/changelog.md and postgres-15-19-17-11-breaking-changes: current managed patch changes do not require upgrading the pinned isolated fixture for this bounded test. Production image/version/security assessment is not accepted here.
- https://raw.githubusercontent.com/supabase/postgres/17.6.1.106/Dockerfile-17 : source-image family has initdb/Postgres, ICU support and extension key-script files; installed runtime identity still attested.
- https://www.postgresql.org/docs/17/app-pg-dumpall.html : roles/memberships require separate recovery; no-role-passwords omits credential recovery.
- https://www.postgresql.org/docs/17/app-pgrestore.html : --create includes DB owner/settings/ACL; --exit-on-error fails immediately.
- https://www.postgresql.org/docs/17/catalog-pg-database.html : PG17 uses datlocale, not old daticulocale.
- https://github.com/citusdata/pg_cron#setting-up-pg_cron : one cron database per cluster; disable launch without modifying job definitions.
- https://docs.docker.com/engine/containers/run/ : exact image, no-network, tmpfs, no host publication; inherited EXPOSE metadata is not a host port binding.
Native acceptance pending; this is prepared/implemented design, not a successful restore report.
