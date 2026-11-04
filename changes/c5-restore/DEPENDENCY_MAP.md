# DEPENDENCY_MAP

C5-RESTORE-01 test-only scope and acceptance are specified in [INTAKE](INTAKE.md).

Existing C5 native financial/browser probe → nonempty local DB → container-version pg_dump/pg_restore → separate target DB → row/catalog comparison and SQL-role replay. Existing publication guard and cleanup retain authority.
