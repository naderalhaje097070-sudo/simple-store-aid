# RECOVERY-02 — Second Independent Review (financial + security)

Reviewer: Claude subagent. I did not take part in the implementation or in earlier verification.
Date: 2026-11-09. Mode: read-only. I modified no repo files. I ran no writes or DDL on the rehearsal database. I made no production or Lovable calls.
Rehearsal DB `tlmoytnyslmhwdkmpsup`: SELECT queries only, against the catalog and `recovery_evidence.production_extract`.

Integrity of inputs: `sha256sum -c CHECKSUMS.sha256` passes 9/9. Each scratchpad copy is byte-identical (`cmp`) to `supabase/migrations/` on the working tree. `origin/main` = `866ea500…`, which matches the package's source commit.

---

## Task 1 — Financial correctness — **ACCEPT-WITH-CONDITIONS**

### 1a. Expected values, computed from code before I read any result
I worked through the code in `20261010223557` (close_day L189–273, collect_order_debt L275–321, create_sale_with_items L323–413, delete_order_with_restore_stock L457–491, return_courier_order L937–973, settle_courier_orders L1103–1163, update_courier_order_state L1209–1256).

| Order | After the operations | total | paid | status | delivery / courier_state | payments |
|---|---|---|---|---|---|---|
| A: direct 2×P1, paid 100, then collect 40 | | 200 | 140 | partial | direct / NULL | sale 100, debt_collection 40 |
| B: courier 1×P2, paid 0 → delivered_full (collected_by_courier 50) → settle | | 50 | 50 | paid | direct / NULL (L1152) | courier_settlement 50 |
| C: courier 1×P2, paid 0 → return | | 50 | 0 | **debt** (unchanged) | direct / returned, courier_id NULL | — |
| D: direct 1×P2, paid 0 (needs a customer, else `customer_required_for_debt`) → delete | row deleted | — | — | — | — | — |
| Expense | 5 | | | | | |

close_day:
- **sales** = 200 + 50 + 50 = **300**. The returned order C still counts, because L211–213 has no status or courier_state filter.
- **collected** = 100 + 40 + 50 = **190**.
- **expenses** = **5**.
- **customer_debts** = A (partial, direct): 200 − 140 = 60. C ('debt'): the `returned` branch gives 0 (L227). B is paid. Total **60**.
- **unsettled_custody** = **0**. No row has delivery='courier' with a courier_id once B is settled and C is returned.
- **realized_profit**:
  - A: profit 2×(100−40) = 120. 100/200×120 = 60, plus 40/200×120 = 24.
  - B: profit 30. 50/50×30 = 30.
  - Total **114**.
- Stock: P1 = start − 2. P2 = start − 1 (C and D are restored). From a start of 10/10 that gives 8/9.

**Comparison:** the package (§3.1) and evidence `r02_verification_claude_20261107.T2` claim 300/190/5/114/60/0 and stock 8/9. **This matches my independent computation exactly.**

### 1b. Does the migration change any financial logic?
I extracted all 33 function definitions from the pre-state snapshot (`prod_snapshot/rollback_october.sql`) and from `20261010223557`, then diffed them with the `PERFORM monjez_private.assert_active_actor();` line removed:
- 25/33 are identical apart from the guard.
- 8/33 (`current_tenant_id`, `current_tenant_timezone`, `has_owner_role`, `has_role`, `has_staff_or_owner_role`, `is_platform_admin`, `tenant_has_active_subscription`, `tenant_today`) change from `LANGUAGE sql` to `plpgsql` with `RETURN (<same expression>)`. Every one of these is a scalar or EXISTS over a primary key, so the results are the same.
- **The migrations make no financial-logic change.**

### 1c. Defects that existed before these migrations and are carried into them (not introduced)
1. **settle_courier_orders custody check bypass (MEDIUM, not the "low / no money effect" the concurrency evidence states).**
   - L1133 `v_order.courier_id <> p_courier_id` evaluates to NULL when `courier_id IS NULL`, so the check is skipped.
   - Any staff user can pass a **returned** order (courier_id NULL, courier_state 'returned', status 'debt') with any valid courier id.
   - L1152 then sets `courier_state = NULL`, which erases the 'returned' marker.
   - Consequences:
     - close_day's customer_debts now counts that order's full total (L228 branch).
     - `collect_order_debt` no longer blocks it (L296–297), so a "collection" can be recorded for goods already returned to stock. That inflates collected and realized_profit.
   - Concurrency run C4 shows the bypass: the second settle returned `success, settled_count 1, total_collected 0`.
2. **Returned orders count in `sales`.** The package already acknowledges this (§4) and it needs a product decision.

Conditions: track item 1 as a financial defect with a forward fix (`IS DISTINCT FROM`, and reject orders whose courier_state is NULL or 'returned'). It does not block this change because rollback would not remove it.

---

## Task 2 — Security of the 9 migrations — **ACCEPT-WITH-CONDITIONS**

### 2a. Can a banned, deleted or closed account bypass the guard?
Static enumeration on the rehearsal (post-migration). I queried `pg_proc` for the public schema with `has_function_privilege('authenticated', …)` and checked each body for `assert_active_actor`:
- **44 public functions.** Every SECURITY DEFINER function that `authenticated` can EXECUTE contains the guard, with three exceptions:
  - `close_owner_account()`: by design. It does its own live Auth check (owner_closure L33–41). An already-closed user only gets a constant `{"status":"closed"}`.
  - `email_queue_wake()`: a trigger function. PostgreSQL refuses direct calls to trigger functions, so this is not a bypass. Revoking EXECUTE anyway is recommended.
  - `touch_updated_at()` and `update_updated_at_column()`: trigger functions, SECURITY INVOKER.
- Unguarded functions that `authenticated` cannot execute: `_fin_audit_trigger`, `_log_platform_admin_action`, `handle_new_tenant`, `handle_new_user`, `next_order_number`, `email_queue_dispatch`, `apply_subscription_webhook`.
- **Tables:** the production extract (`tables_rls`) lists 22 public tables. All 22 carry `monjez_live_actor` AS RESTRICTIVE TO authenticated. There are **no views** in public. The `supabase_realtime` publication is empty. Storage has 0 buckets and 0 policies.
- **Not covered by the guard. Schemas outside the app; nothing here is introduced by the migrations:**
  - `net._http_response` and `net.http_request_queue`: RLS off, and anon/authenticated hold SELECT/INSERT/UPDATE/DELETE/TRUNCATE. This is the Supabase/pg_net default. It is exploitable only if `net` is an API-exposed schema. I could not read the PostgREST exposed-schemas setting.
  - `extensions.pg_stat_statements` (anon/authenticated SELECT).
  - `realtime.messages`.
  - `storage.*` (unused).
- **Systemic gap:**
  - Any **future** public table gets no live-actor policy automatically.
  - `pg_default_acl` for **supabase_admin in public** still grants `arwdDxtm`, including TRUNCATE, to anon and authenticated. SEC-TRUNCATE only fixed postgres's defaults; the default ACL query shows this.
- Guard-logic review:
  - `assert_active_actor` trusts `current_setting('role')`, which PostgREST sets from the signed JWT. A client cannot set it to service_role.
  - Deleted users are covered both ways: a hard delete leaves no row, and `deleted_at` is checked.
  - `banned_until` is compared with `statement_timestamp()`.
  - Closure is per user. **Staff of a closed owner's tenant can keep operating it, and the Paddle subscription is not cancelled**, so billing continues. This is a product decision; record it.

### 2b. tenants column grants (tenant_entitlement_01 L7–8)
- **UPDATE(owner_user_id): safe.** The policy is `owners update their tenant` with USING and CHECK both `owner_user_id = auth.uid()`, so a transfer is impossible. The package and T6 confirm a transfer is RLS-denied. INSERT is constrained by CHECK `owner_user_id = auth.uid()`.
- **UPDATE(id): not exploitable, but unjustified.**
  - 13 foreign keys reference `tenants(id)` with the default NO ACTION on update.
  - `handle_new_tenant` always inserts a `user_roles` row, so any change to `id` fails with an FK violation.
  - The `monjez_private.billing_*` tables hold tenant_id **without** an FK. No app path updates `id`: `origin/main` updates only name, business_type and timezone (`src/lib/db.ts:102,114,126`) and inserts only name and owner_user_id (`src/routes/_authenticated/onboarding.tsx:65-69`).
  - **Condition:** narrow the grants in a forward follow-up to INSERT(name, owner_user_id, timezone, business_type) and UPDATE(name, timezone, business_type). Drop id, created_at and updated_at; an owner can currently backdate `created_at`.
- Residual (pre-existing): AC-02's "only the trusted backend assigns entitlement" is not fully true.
  - The column default gives every client-inserted tenant `trial_ends_at = now()+14d` and `subscription_status 'trialing'`.
  - The profiles UPDATE policy lets a user point `profiles.tenant_id` at any tenant they own.
  - Together these allow an unlimited fresh-trial cycle, though on an empty store.

### 2c. sec_truncate guard
- Correct: the creator guard requires `current_user = 'postgres'` (L7), and the migration aborts if a global default ACL grants TRUNCATE.
- REVOKE covers all 22 tables from anon, authenticated and PUBLIC.
- Gaps:
  - It does not check or fix supabase_admin's per-schema defaults (above).
  - **The `current_user = postgres` requirement is not proven for Lovable's migration tool.** If that tool runs as another role, the migration aborts. That is safe, but it breaks the staged plan.

### 2d. apply_subscription_webhook
- **Authorization: good.**
  - SECURITY INVOKER.
  - Requires both `current_user` and the `role` GUC to be `service_role` (L70 / errors L34).
  - EXECUTE is granted to service_role only.
  - The private tables are revoked from every other role.
  - The app calls it with the service-role key (`src/routes/api/public/payments/webhook.ts:9`).
- **Idempotency: good.**
  - PK (environment, event_id), plus advisory locks per subscription and per event.
  - A replay with a different body raises `billing_event_id_conflict`.
  - C3 under real concurrency gave 1 receipt per event.
- Weaknesses:
  1. **Lock conflict (confirmed by C3).** `SELECT tenants … FOR UPDATE` (L130 / errors L97) with `lock_timeout 2s` conflicts with FK `KEY SHARE` locks from any concurrent sale or collection on the same tenant. The result is 55P03, then HTTP 503, then a Paddle retry. Recommend `FOR NO KEY UPDATE`.
  2. **Permanent refusals.** Raises such as `billing_event_order_ambiguous` (identical `occurred_at` with a different state), `billing_legacy_order_unknown` and `billing_creation_snapshot_required` (when `created` never arrives) become a permanent 503 loop with no alerting or reconciliation runbook. Production has 0 subscription rows (restore hashes: `subscriptions:0`), so the legacy paths are dormant today.
  3. Stale re-projection (package §3.3): I found no ordering that breaks it.
     - `stale` requires an earlier receipt, which implies the subscription row exists, so `v_old_state` is defined.
     - Updates before `created` are refused.
     - A newer subscription supersedes an older one only on `created` with a strictly later `created_at`.
     - Sandbox never projects to tenants.

### 2e. Ordering hazards inside the set
- **Migrations 1 and 2 must be applied back to back.** Migration 2's header (L1–4) says the policy from migration 1 makes `profiles` policy expansion recurse, which breaks profile updates and onboarding until migration 2 is applied.
- **Migrations 7–9 must be applied together.** Migration 9 exists because the 40001 codes in 7–8 trigger PostgREST/Hasql retry loops.

---

## Task 3 — Compatibility with origin/main — **ACCEPT**

`git grep` on `origin/main`:
- **RPCs:**
  - current_tenant_id, get_tenant_today_estimate, delete_product_safe, create_sale_with_items, delete_order_with_restore_stock, collect_order_debt, settle_courier_orders, update_courier_order_state and close_day (`src/lib/db.ts`): signatures unchanged and still granted to authenticated.
  - run_security_scan (`platform-admin.tsx:817`): authenticated platform admin is allowed.
  - Email RPCs (`src/routes/lovable/email/queue/process.ts`): service-role client (L83, L102), so the guard passes.
  - apply_subscription_webhook (`webhook.ts:19`): the payload keys match the 11-key allow-list exactly, and the regexes match (`subscription-webhook.server.ts`).
- **Direct writes:**
  - tenants update name, business_type, timezone and insert name, owner_user_id: all inside the new column grants.
  - profiles update tenant_id (onboarding:58): unchanged.
  - products, customers, couriers and expenses inserts and updates: unchanged.
- `src/lib/account-state.server.ts:31` already expects `42501 / account_inactive`, which the new guard produces.
- **Important:** production already runs code that calls `apply_subscription_webhook`, which **does not exist in production**. Every Paddle webhook currently returns 503 in production. Applying migrations 7–9 fixes that. Leaving production in its current state is itself a defect.
- Not verified: onboarding's `insert(...).select("id")` under the new column grants through real PostgREST. T6 tested updates, not this insert.

---

## Task 4 — Rollback script — **ACCEPT-WITH-CONDITIONS** (do not run it as-is in production)

Verified:
- `rollback_october.sql` is BEGIN + `rollback_body.sql` + COMMIT (diff).
- The md5 of the body is `47862d3fbc20511435b22684cdd2320c`, matching the evidence's `script_md5_body`.
- 33 `CREATE OR REPLACE FUNCTION` statements restore exactly the pre-state bodies; my diff in 1b confirms they equal the migration bodies minus the guard. CREATE OR REPLACE keeps existing ACLs.
- The only GRANT/REVOKE lines (L1075–1078) touch tenants and TRUNCATE. **The email hotfix grants are not touched, so they are preserved.** This agrees with the evidence (`acl_match 35/35`).

Problems:
1. **Irreversible data destruction.** `DROP SCHEMA monjez_private CASCADE` (L1074) deletes `owner_account_closures`, which **silently reopens closed accounts**, plus `billing_webhook_receipts` and `billing_tenant_bindings`. CASCADE also drops any unforeseen dependent without warning.
   - Fix: export these tables first, drop the objects explicitly, and use `DROP SCHEMA … RESTRICT`.
2. **Ledger edit** (L1079 `DELETE FROM supabase_migrations.schema_migrations`).
   - It contradicts DECISIONS 2026-11-09 ("No direct SQL plus a hand-written ledger row").
   - If Lovable's tool records **different version ids**, this DELETE does nothing and the ledger keeps claiming the migrations are applied.
   - If the 9 files stay in the repo, a later tool run may try to reapply them.
3. **Statements that can fail:**
   - `ALTER DEFAULT PRIVILEGES FOR ROLE postgres` (L1078) needs postgres or a member of it.
   - The DELETE on `supabase_migrations` needs privileges on that schema.
   - 22× `DROP POLICY` take ACCESS EXCLUSIVE locks with **no `lock_timeout`**, so they can queue behind live traffic and stall it.
4. **The script is valid only while nothing else has changed these 33 functions.** It blindly restores snapshot bodies, so any later migration to them (for example the repo's `20261028…`/`20261029…` create_sale changes) would be silently reverted.
5. **Rollback re-opens known holes, by definition:**
   - tenants billing columns become writable by authenticated (table-level INSERT/UPDATE).
   - `run_security_scan` becomes callable by any authenticated user (its `current_user` check is always 'postgres' inside SECURITY DEFINER).
   - TRUNCATE comes back for authenticated on 21 tables.
   - The webhook RPC disappears, so webhooks return to 503.
   The owner must accept this explicitly.
6. No statement has a non-transactional side effect. There are no nextval, pg_net, cron or dblink calls, and pgmq appears only inside function bodies. The script commits atomically. The irreversible part is item 1 once committed.

---

## Task 5 — Evidence sufficiency — **ACCEPT-WITH-CONDITIONS**

Strong:
- Equivalence gate: 42/42 functions, 59 policies, 183 columns, 58 indexes, 79 constraints, 13 triggers, 42 ledger rows.
- 9/9 checksums.
- T2 matches my independent computation.
- Real concurrency: 4 scenarios, separate backends via pg_cron, no double money effect.
- Rollback proven inside a rolled-back transaction.
- Export restore proven: 22/22 tables identical (`restore_proof_table_hashes.txt`). Daily backups verified by owner screenshot.

Gaps:
1. **Package is stale or contradictory.**
   - §4 says there is no backup and no concurrency test; later evidence (commits 415cb3e, 2340a33, e3b2e49) supersedes that.
   - PROJECT_STATE says "owner states all production data is synthetic", while DECISIONS says the export "contains real customer data". Resolve this before approval.
2. **Apply path is not rehearsed.** Lovable's migration tool has not been tested for:
   - executing role (SEC-TRUNCATE requires postgres);
   - version ids recorded;
   - handling of the files' own BEGIN/COMMIT;
   - whether the tool rewrites SQL.
   Post-apply byte or md5 identity against the rehearsal is not yet planned as a gate.
3. **No end-to-end app test.** Nothing ran origin/main against the migrated schema through real PostgREST and JWT: onboarding insert, platform-admin scan, email processor, signed Paddle sandbox webhook. All tests were SQL-level role emulation.
4. **T3 dynamic coverage** was 12 functions and 22 tables. My static enumeration closes the function-coverage question (2a), but there is no dynamic test of the remaining authenticated-callable functions.
5. Not tested: concurrent close_day against sale or collection, and webhook against a long sale (C3 shows 55P03).
6. Version drift: PostgreSQL 17.11 vs 17.6 and pg_net 0.20.4 vs 0.20.3. The rehearsal email-fix ledger version (20261107205203) differs from production's (20261107214500).
7. In-place Lovable restore has not been rehearsed (accepted residual risk).
8. Email non-exploitation: no queue message ever existed (msg_id sequences unused, 0 archive), which is strong for confidentiality. There was no API/PostgREST log review for `/rpc/read_email_batch` calls.

---

## Overall verdict — **ACCEPT-WITH-CONDITIONS**

The 9 migrations are financially neutral; the only logic change is the guard, verified by diff. They are a real security improvement: they close live-account bypass, tenant billing-column writes, open scanner execution and client TRUNCATE, and they supply the webhook RPC that production code already calls. They are **ready to be presented to the owner for an approved, staged production apply only after the conditions below are met.** They are **not** ready to apply as the package currently stands, mainly because the apply path and the rollback script are unsafe or unproven.

## Required conditions (before the production apply)
1. Rehearse the exact Lovable migration-tool path on a non-production project, or obtain a written confirmation from Lovable, covering:
   - executing role = postgres;
   - recorded version ids;
   - transaction handling;
   - SQL unaltered.
   Gate each stage on md5(prosrc), ACL and policy counts matching the rehearsal (81 public policies, 46 functions).
2. Stage boundaries: apply **1 + 2 back to back** (profiles recursion), and **7 + 8 + 9 together** (40001 retry loops). Set `lock_timeout` for the policy DDL. Apply shortly after the 05:40 UTC backup, and take and verify a fresh owner export first.
3. Rewrite the rollback:
   - export the `monjez_private` tables first;
   - drop objects explicitly and use `DROP SCHEMA … RESTRICT`;
   - add `SET LOCAL lock_timeout`;
   - remove or replace the hand-written ledger DELETE with a mechanism consistent with Lovable's history, and verify the versions it targets;
   - add a precondition that aborts if any of the 33 functions differ from the post-apply md5 (no later changes).
   The owner must explicitly accept that rollback reopens the AC-02, scanner, TRUNCATE and webhook holes and reopens closed accounts.
4. Run a post-apply smoke test through the real app (origin/main) on production with a test account:
   - onboarding insert and tenant settings update;
   - sale, collect and close_day on a synthetic tenant (or in the rehearsal through PostgREST before apply);
   - platform-admin scan;
   - a banned test user receiving `account_inactive`;
   - a Paddle sandbox webhook returning 200.
5. Update the review package: backup, concurrency and restore status; resolve whether production data is synthetic or real.
6. File forward-only follow-ups (non-blocking, tracked):
   - settle_courier_orders NULL-custody bypass that resurrects returned orders as debt (MEDIUM);
   - narrow the tenants column grants (drop id, created_at, updated_at);
   - webhook `FOR NO KEY UPDATE`, plus alerting and a reconciliation runbook for permanent P0001 refusals;
   - revoke EXECUTE on `email_queue_wake`;
   - supabase_admin default ACL in public;
   - a CI or scanner check that every new public table gets `monjez_live_actor`;
   - product decisions on returned orders in sales and on billing and staff access after owner closure.

## Could not verify
- PostgREST exposed-schemas configuration in production (decides whether `net.*` and `extensions.*` are reachable).
- Lovable migration tool behaviour (role, versions, transactions).
- Production PostgREST/API logs for past email-RPC calls.
- Real JWT/PostgREST behaviour of `current_setting('role')` inside the guard. It is correct by PostgREST design, but I did not execute it myself.
- Whether production data is synthetic (the two documents conflict).
- That the rehearsal still equals production today. The equivalence gate dates from 2026-11-07; I did not re-query production, by rule.
- The test runs themselves. I re-derived T2 by hand but did not re-execute T1–T10 (read-only mandate).
