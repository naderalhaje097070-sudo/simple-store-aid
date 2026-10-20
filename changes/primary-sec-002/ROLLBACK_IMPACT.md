# PRIMARY-SEC-002 Rollback Impact

Rollback is limited to dependency metadata and the dependency-security unit guard.

Reverting this batch would restore the previous Critical/High audit exposure and should not be used as a release path.

No data rollback, migration rollback, or production recovery step is involved.

If a patched dependency incompatibility is found later, prefer a focused replacement version within the same major or an upstream parent update rather than removing the security floor wholesale.
