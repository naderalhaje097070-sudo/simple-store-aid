# RECOVERY-02 rollback scripts R1 to R5: independent review

Date: 2026-11-09. This was a read-only review. I modified no repository file. I used no Lovable or production tool. I ran only read-only SELECTs on the rehearsal project `tlmoytnyslmhwdkmpsup`.

Files reviewed (md5 matches the `r02_staged_rollback_test_20261109` evidence row):

| Script | md5 |
|---|---|
| R1_live_actor_1_2.sql | 0271b1a11ce529501e1a0e29640d50d6 |
| R2_truncate_3.sql | 4cec3360690278cfda461ad13759c461 |
| R3_owner_closure_4.sql | 4848c125132e5d3b9d41c02fe4d60af4 |
| R4_scanner_entitlement_5_6.sql | 0351cb230fde9a5c57e42ed605cbeefa |
| R5_webhook_7_8_9.sql | d09444149722c973f7bbfc79bfb04306 |

All line numbers below are per file. Paths are relative to `docs/reviews/rollback/` and `supabase/migrations/`.

## Verdicts

| Script | Verdict | Short reason |
|---|---|---|
| R5 | ACCEPT-WITH-CONDITIONS | Exactly undoes stage 5. It returns Paddle webhooks to the failing pre-state, and the stage-5 tables are left behind, so the same files can never be applied again. |
| R4 | ACCEPT-WITH-CONDITIONS | The scanner body is byte-identical to the stage-1 version, and the tenants ACL equals the pre-state. It reopens the scanner and billing-column holes. It has no check that it runs against the expected state. |
| R3 | ACCEPT-WITH-CONDITIONS | `actor_is_active` is byte-identical to the stage-1 version. Closed accounts silently become usable again. The leftover `ON DELETE RESTRICT` foreign key is a lasting side effect. |
| R2 | ACCEPT-WITH-CONDITIONS | The table grants match the production `grants` extract exactly (21 tables, authenticated only). The default ACL is correct by reasoning, but I could not compare it with a production capture. |
| R1 | ACCEPT-WITH-CONDITIONS | All 33 functions equal the production pre-snapshot, 22 policies are dropped, and the hotfix is preserved. It has no check that it runs against the expected state, and it takes 22 ACCESS EXCLUSIVE locks. |

None of the scripts is REJECT. None can be run as-is without the conditions listed under "Required fixes".

## 1. Correctness per stage

### R5 undoes stage 5 (20261021132651, 20261021134621, 20261021140746)
- Forward: `20261021132651:39` uses `CREATE FUNCTION`, not `CREATE OR REPLACE`. So the function did not exist before, and dropping it is the exact undo. 134621 and 140746 only `CREATE OR REPLACE` the same signature and repeat the ACL (`:3`, `:269-270`).
- R5:5 drops `apply_subscription_webhook(text,text,text,timestamptz,jsonb)`. That is the same signature as `132651:302`.
- Nothing depends on the function. In the rehearsal, `pg_depend` returns 0 rows for it.
- Left in place by design: `monjez_private.billing_webhook_receipts`, `billing_tenant_bindings`, both policies and the index (`132651:3-37`). These are harmless for security: RLS is on and only service_role has access (`:20-21`, `:34-35`). They are not harmless operationally:
  - Re-applying 132651 would fail at `CREATE TABLE` (`:3`).
  - The bindings keep tenant/subscription state that can go stale while the RPC is absent.
- The app calls the RPC: `src/routes/api/public/payments/webhook.ts:19`. After R5, every payment event fails again. That is the pre-state the plan describes at line 14, but the plan's rollback section (lines 61-72) does not say it.

### R4 undoes stage 4 (20261020210549, 20261021080927)
- `run_security_scan`: I extracted R4:5-131 and the stage-1 block from `20261010223557` programmatically. They are byte-identical (5540 bytes each). That is correct given that R5 already ran and stage 1 is still in effect.
- Stage 4 has no GRANT or REVOKE on the scanner (`20261020210549`, grep). `CREATE OR REPLACE` keeps the ACL, which in the rehearsal is `{postgres,authenticated,service_role}=X`. That equals the snapshot ACL.
- Tenants:
  - Forward `20261021080927:4` revokes table-level INSERT and UPDATE. Under PostgreSQL rules a table-level REVOKE also clears the column grants. Forward `:7-8` then grants 7 columns.
  - R4:133 revokes exactly those 7 columns, and R4:134 restores table-level INSERT and UPDATE.
  - The production pre-state matches: the `grants` extract shows authenticated insert/update on tenants, and `column_explicit_grants` has 0 rows. Combined with R2, the result is `authenticated=arwDxtm` with 0 column ACLs, which is what the evidence row records.
  - The statement order (column revoke, then table grant) is valid.
  - The production-only `sandbox_exec=ar` entry is not touched.

### R3 undoes stage 3 (20261013221918)
- R3:5-13 is byte-identical to the stage-1 `actor_is_active` (`20261010223557:7-15`, diffed). The signature, owner and ACL are unchanged by `CREATE OR REPLACE`.
- R3:14 drops `close_owner_account()`.
  - The forward migration created it with `CREATE FUNCTION` (`:27`), so it did not exist before.
  - Nothing depends on it (`pg_depend` returns 0), and `src/` never calls it.
- The `actor_is_active` body is a plain SQL-language function, not `BEGIN ATOMIC`, so there is no dependency on `owner_account_closures`. Keeping the table does not block anything.
- Left in place: `monjez_private.owner_account_closures` with `FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE RESTRICT`. I confirmed this in the rehearsal (`owner_account_closures_user_id_fkey`). This is **not fully harmless**:
  - After rollback, any auth user with a closure row cannot be deleted through Supabase Auth or admin deleteUser. The delete fails with an FK violation.
  - This is a new constraint that did not exist in the before-state.
- Re-applying 221918 would fail at `CREATE TABLE` (`:5`).

### R2 undoes stage 2 (20261013120223)
- Forward `:29-52` revokes TRUNCATE on 22 tables from anon, authenticated and PUBLIC.
- R2:5 grants TRUNCATE on 21 tables to authenticated, leaving out `tenant_counters`. The production `grants` extract (`recovery_evidence.production_extract`, key `grants`) shows exactly this pre-state:
  - authenticated has `can_truncate=true` on these 21 tables;
  - `tenant_counters` has no authenticated or anon privileges at all;
  - anon has no TRUNCATE anywhere.
  So the narrower re-grant is exact. Re-granting to anon or PUBLIC would have been wrong.
- R2:6 runs `ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT TRUNCATE ON TABLES TO authenticated`.
  - The current rehearsal default ACL for `postgres/public/r` is `{postgres=arwdDxtm, authenticated=arwdxtm, service_role=arwdDxtm}`. It has no anon or PUBLIC entry.
  - The forward migration removed only `D` from those entries, so restoring `D` for authenticated alone reproduces `arwdDxtm`. The evidence says "default ACL restored".
  - I did not see a production capture of `pg_default_acl` (see "Could not verify").
- The grantor is postgres (R2:3 guard), which matches the original `/postgres` grantor.

### R1 undoes stage 1 (20261010223557, 20261010225012)
- **33 functions.** I split R1 into its 33 `CREATE OR REPLACE` blocks and compared each with `functions_before.json` `def`: **33/33 identical**, ignoring only the trailing newline. The set of names equals the set the forward migration redefines (diffed). The `CREATE ... RETURNS` lines are identical, so `CREATE OR REPLACE` cannot fail on a changed return type or renamed parameter.
- **Stacked redefinitions.**
  - `run_security_scan` was set to its stage-1 form by R4, then to its pre-stage-1 form by R1. Correct.
  - `actor_is_active` was set to its stage-1 form by R3. R1 leaves it in place, unused. Correct.
- **Policies.** R1 drops 22 `monjez_live_actor` policies, the same 22 tables as forward `:37-146`. Dropping the profiles policy also absorbs the `ALTER POLICY` in `20261010225012:6-8`, so no separate undo is needed.
- **ACLs and the hotfix.** R1 contains no GRANT or REVOKE (top-level statement scan below). `CREATE OR REPLACE` preserves `proacl`, so the hotfix `20261107214500` (ACL-only on `enqueue_email`, `read_email_batch`, `delete_email`, `move_to_dlq` and `email_queue_dispatch`) survives. The snapshot ACLs for those 4 functions are already service_role-only, which means the snapshot was taken after the hotfix and is consistent with it.
- **Left in place.** Schema `monjez_private`, `actor_is_active`, `assert_active_actor`, `USAGE` for authenticated and service_role, and EXECUTE for authenticated and service_role.
  - These are harmless for security: the functions only return or assert the caller's own status.
  - They block re-applying `20261010223557`, because `CREATE SCHEMA monjez_private` (`:3`) and `CREATE FUNCTION` (`:7`, `:17`) have no `IF NOT EXISTS`.

## 2. Partial-chain safety

I analysed this statically. The evidence row itself says "partial chains not separately tested".

| Stop after | Resulting state | Calls to missing objects? | Weaker than both before and after? | Safe? |
|---|---|---|---|---|
| R5 | Stages 1-4 active, webhook RPC absent | Only the app route (`webhook.ts:19`) to the dropped RPC. Payments return to the pre-state failure. No DB function references it. | No | Yes (functional regression equals the pre-state) |
| R5+R4 | Stages 1-3; scanner is the stage-1 body; tenants billing columns writable | No. The scanner calls `monjez_private.assert_active_actor` and `public.is_platform_admin`, both present. | No. The scanner `current_user` check is always true inside SECURITY DEFINER, so any authenticated active user can run the scan. That is the pre-state weakness, plus the active-account check. | Yes |
| R5..R3 | Stages 1-2; closure not enforced; `close_owner_account` absent | No | No (equals the pre-state with respect to closure). Closed owners regain access. | Yes, with the FK RESTRICT caveat |
| R5..R2 | Stage 1 only; TRUNCATE for authenticated on 21 tables plus default ACL | No | No. TRUNCATE bypasses RLS, so the restrictive policies do not cover it, exactly as before stage 1. | Yes |
| R5..R1 | Before-state for functions, policies and grants; `monjez_private` objects remain | No | No | Yes |

Out-of-order or skipped runs are **not** guarded:
- R4 run while stage 5 is applied works mechanically, because the webhook does not depend on the scanner or the tenants grants. But it silently leaves the ledger and the state inconsistent with the documented order.
- R1 run before R4 would replace `run_security_scan` with the pre-stage-1 body while the ledger still lists `20261020210549`. The stage-4 fix would be lost silently.
- No script checks that the higher stages are already undone.

## 3. Ledger

Each script deletes exactly the versions of its own stage:

| Script | Line | Versions deleted |
|---|---|---|
| R5 | 6 | 20261021132651, 20261021134621, 20261021140746 |
| R4 | 135 | 20261020210549, 20261021080927 |
| R3 | 15 | 20261013221918 |
| R2 | 7 | 20261013120223 |
| R1 | 1074 | 20261010223557, 20261010225012 |

- Together they cover the 9 versions exactly, with no overlap.
- Every delete is `version IN (literal list)`, so none can ever match `20261107214500`, `20261107205203` or the baseline rows. The rehearsal ledger has 53 rows. The evidence records 44 after the full chain, with both email fixes retained.
- Weakness: no script asserts the affected row count. If production recorded different version ids, for example because of the apply method, a delete would affect 0 rows and the script would still COMMIT, leaving the ledger claiming the stage is applied.

## 4. Data

- Top-level statement scan, with dollar-quoted bodies stripped:
  - R1 contains only BEGIN, SET LOCAL, the guard DO, 33 CREATE OR REPLACE, 22 DROP POLICY, the ledger DELETE and COMMIT.
  - R2 to R5 contain only GRANT, REVOKE, ALTER DEFAULT PRIVILEGES, CREATE OR REPLACE, DROP FUNCTION, the ledger DELETE and the guard.
  - The `DELETE FROM public.payments/order_items/orders/products` lines in R1 (about lines 328-354) are inside function bodies (`delete_order_with_restore_stock`, `delete_product_safe`). They are restored definitions, not executed statements.
- **No business table and no `monjez_private` table row is deleted or modified.** `billing_webhook_receipts`, `billing_tenant_bindings` and `owner_account_closures` are kept. The evidence records that the synthetic receipt and closure rows were kept.
- What becomes unenforced:

| After | No longer enforced |
|---|---|
| R5 | Paddle webhook processing. Events fail again and Paddle retries. Receipts and bindings freeze. |
| R4 | Scanner restricted to platform admins (AC-01). Billing and entitlement columns protected from authenticated users (AC-02): an owner can set `subscription_status`, `trial_ends_at` and the `paddle_*` columns on their tenant. |
| R3 | Owner closure. Closed owners can log in and operate again, unless banned or deleted. The closure rows remain, but nothing reads them. |
| R2 | TRUNCATE protection. Any authenticated user can TRUNCATE 21 tables, bypassing RLS. New public tables created by postgres get TRUNCATE for authenticated again. |
| R1 | The live-account guard. Banned or deleted users with a still-valid JWT can read and write through RLS and all 33 RPCs. |

## 5. Failure modes

- **A statement fails midway.** The transaction aborts and nothing from that script is committed. This applies to a lock timeout (55P03), the guard (`ROLLBACK_REQUIRES_POSTGRES`) or any error. All statements are transactional DDL, DCL or DML.
- **No non-transactional statements.** There is no `CONCURRENTLY`, VACUUM, `ALTER SYSTEM`, `pg_net`, `cron`, `dblink` or `nextval` at top level. `ALTER DEFAULT PRIVILEGES` is transactional.
- **Client behaviour is the real risk.**
  - In psql without `ON_ERROR_STOP=1`, the statements after an error print "current transaction is aborted" and `COMMIT` turns into `ROLLBACK`. psql can still exit 0, so the operator may believe the script succeeded.
  - If several R files are concatenated or run in one session without `ON_ERROR_STOP`, a failed R4 would be followed by a committed R3, R2 and R1. That is the out-of-order state described in section 2.
- **Order within each script is valid.**
  - The DROP FUNCTION statements (R5:5, R3:14) have no dependants.
  - R3 replaces `actor_is_active` while the table still exists. The order is irrelevant for a plain SQL function.
  - R4 revokes the column grants before granting the table privilege. Either order would give the same ACL.
  - R1 recreates the functions before dropping the policies. The policies reference `monjez_private.actor_is_active`, which is not dropped.
- **Locks.**
  - R1 takes ACCESS EXCLUSIVE on 22 tables, one per DROP POLICY. Lock acquisition is serialized inside one transaction, so the locks held early are kept while it waits for later ones. With a 5s `lock_timeout` per lock, worst-case blocking of app traffic is about 22 × 5s if every lock waits.
  - R4 and R2 take locks on tenants and the 21 tables for the GRANT and REVOKE.
  - Any failure rolls back cleanly and can be retried.
- **Guard.** `current_user <> 'postgres'` covers the TRUNCATE grantor, `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` and function ownership. Running as `supabase_admin` is refused. That is safe, but it is a blocker if the operator's connection is not postgres.

## 6. Not reverted by design, and whether the plan says so

| Item | Stated in the plan (`RECOVERY-02_PRODUCTION_PLAN.md`)? |
|---|---|
| Webhook failure returns (R5) | Only implicitly, at line 14 ("every payment event fails now"). Not in the rollback section. |
| AC-02 billing columns writable, scanner open to any authenticated user (R4) | **No** |
| Closed accounts usable again (R3) | **No.** Line 66 says closure records "remain", which reads as reassurance but hides that they are no longer enforced. |
| TRUNCATE hole reopened (R2) | **No** |
| Live-account guard removed (R1) | **No** |
| `monjez_private` objects, tables and the RESTRICT FK left in place | Partly. Line 66 mentions receipts and closures kept. The FK side effect is not mentioned. |
| Re-applying the same 9 files after rollback is impossible (`CREATE SCHEMA`/`CREATE TABLE` without IF NOT EXISTS) | **No** |
| Partial chains untested | **No.** Line 68 cites only the full chain. |

The second review (`RECOVERY-02_SECOND_REVIEW.md:223`) required explicit owner acceptance of the reopened holes. That is not yet reflected in the plan. Its condition 3 also asked for a precondition that aborts if functions differ from their post-apply md5. The new scripts have no such check (R1:1-3, R3:1-3, R4:1-3 contain only the role guard).

## Required fixes (before any production use)

1. **State preconditions in each Rk.** Add a DO block that raises unless the state is as expected:
   - every ledger version of a stage higher than k is absent, and every version of stage k is present;
   - `md5(pg_get_functiondef(...))` (or `md5(prosrc)`) of each function the script replaces equals the post-apply value recorded in the rehearsal: R1 (33 functions), R3 (`actor_is_active`), R4 (`run_security_scan`).

   This enforces order and prevents silently reverting later edits.
2. **Ledger row count.** Use `GET DIAGNOSTICS` or `WITH d AS (DELETE ... RETURNING 1)` and raise unless the count equals 2, 1, 1, 2 or 3 for that script.
3. **Execution procedure.** Run one file per invocation with `psql -v ON_ERROR_STOP=1 -f Rk.sql`, never concatenated. After each script, run a read-only verification gate (function md5, ACLs, policy count, ledger) before running the next.
4. **Plan text.** In the rollback section, list for each Rk what becomes unenforced (section 4 table) and get the owner's explicit acceptance. Correct line 66 to say that closures stop being enforced after R3.
5. **Roll-forward.** State that after any rollback, re-applying the stage requires a new forward migration (or manual cleanup of `monjez_private` objects, which needs separate approval). The original files will fail on `CREATE SCHEMA`/`CREATE TABLE`.
6. **FK side effect.** Record the `owner_account_closures` FK `ON DELETE RESTRICT` side effect after R3 and R1. Optionally have R3 drop only that constraint, keeping the rows; this needs an owner decision.
7. **Partial-chain test.** Rehearse at least R5 only and R5+R4 in a rolled-back transaction, because "stop after the failing stage" is the main intended use (plan line 65).

## Could not verify

- That production's `pg_default_acl` for `postgres/public/r` before stage 2 was exactly `authenticated=arwdDxtm` with no anon or PUBLIC entry. I inferred it from the rehearsal's current state and the forward migration. I saw no production capture of that ACL.
- That production will record the 9 versions with exactly these ids. This depends on the direct-apply procedure at plan line 27.
- Real lock contention or duration under production traffic.
- Partial chains: none was executed. Section 2 is static analysis.
- That production still equals the rehearsal today. The rehearsal equivalence gate is dated 2026-11-07, and by rule I did not query production.
- Whether any closure rows exist in production, which determines whether the FK RESTRICT side effect matters.

## Commands run

- `cat`, `grep` and `diff` over the 5 scripts and 10 migration files.
- A Python comparison of 33 R1 blocks against `functions_before.json`: 33/33 identical.
- Byte comparison of the R4 scanner body against the stage-1 body: identical.
- `diff` of R3 `actor_is_active` against stage 1 `:7-15`: identical.
- `md5sum` of the scripts: they match the evidence row.
- Read-only SELECTs on `tlmoytnyslmhwdkmpsup`:
  - the ledger, tenants ACL and column ACLs, `pg_default_acl` and TRUNCATE privileges;
  - `monjez_private` functions, the FK on `owner_account_closures`, and `pg_depend` for the dropped functions;
  - the `recovery_evidence.production_extract` keys `grants`, `column_explicit_grants`, `r02_staged_rollback_test_20261109` and `r02_rollback_test_20261108`.
