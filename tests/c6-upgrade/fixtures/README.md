# Local test fixtures for the C6 acceptance gate

**`old_emergency_revert_e32f92b.sql.fixture`:** the pre-fix emergency revert.
- **What it is:** the exact bytes of `docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql` at commit `e32f92b91824971c7d947dfd4c3b74a29211fdb2`.
- **Digests:** git blob `09c3ce918063e1fcf70c08a0f2930595dca26d94`; sha256 `f357c099a3a67b0f454ebe02188eabfd62d29fe6ec1d9f10f099a61867ab0aae`; 276 bytes.
- **Why it is here:** that commit is not in the integration branch's history, so `review_fixes.sh` could no longer reach it.
- **How it is used:**
  - only by `review_fixes.sh` (check S4), to prove that the pre-fix revert would have re-granted the legacy RPCs while stuck after C2;
  - that script verifies the sha256, copies the file into its output directory, and runs it only inside `BEGIN … ROLLBACK` against its own local replica container;
  - it compares the bytes with `e32f92b` when that commit is reachable.
- **Not an apply file:**
  - never run it against any other database, and never against production;
  - the current, fixed revert is `docs/reviews/c6-apply/EMERGENCY_unblock_legacy_frontend_revert.sql`, which is unchanged.
