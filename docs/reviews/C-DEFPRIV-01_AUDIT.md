# C-DEFPRIV-01: default privileges and TRUNCATE audit (read-only)

- **Date:** 2026-11-10
- **Scope:** owner instruction 2026-11-10. This is a read-only audit. No SQL that changes a database was run and no migration was created.
- **Database read:** the local disposable stack (Supabase CLI 2.101.0) built from the integration migrations, plus #87 and #88 applied locally.
- **Production:** not read. The queries to confirm each finding on production are listed in §5. They need the owner's approval, because they are a production operation, even though they are read-only catalog queries.

## 1. Facts (catalog queries, local)

| # | Fact | Evidence |
|---|---|---|
| F1 | `postgres` is not a superuser and is **not a member of `supabase_admin`**. | `rolsuper=f`; `pg_has_role('postgres','supabase_admin','MEMBER') = f` |
| F2 | **Defaults of `supabase_admin` in `public`:** `anon` and `authenticated` get `arwdDxtm` on tables (TRUNCATE included), `rwU` on sequences and `X` on functions. | `pg_default_acl`: supabase_admin, public, r/S/f |
| F3 | **Defaults of `postgres` in `public`:** `authenticated` gets `arwdxtm` on tables (no TRUNCATE, since SEC-TRUNCATE), `rwU` on sequences and `X` on functions. `anon` gets nothing. | `pg_default_acl`: postgres, public |
| F4 | **There is no global default ACL for `postgres`.** Every new function `postgres` creates, in any schema, is executable by **PUBLIC**, which includes `anon`. | `acldefault('f','postgres') = {=X/postgres,postgres=X/postgres}` |
| F5 | **Every public object is owned by `postgres`:** 23 tables, 1 view, 1 sequence, 47 functions. None is owned by `supabase_admin`. | `pg_class`, `pg_proc` owners |
| F6 | **No public table grants TRUNCATE** to `anon` or `authenticated`. | `has_table_privilege(...,'TRUNCATE')`: none |
| F7 | **Only 2 public functions are executable by anon/PUBLIC:** `touch_updated_at()` and `update_updated_at_column()`. Both are trigger functions and cannot be called as RPCs. Every other function had PUBLIC revoked explicitly, migration by migration. | `has_function_privilege('anon',...)` |
| F8 | **Every public table has RLS on.** One table lacks `monjez_live_actor`: `financial_idempotency`. It grants **nothing** to anon or authenticated and is reachable only through SECURITY DEFINER functions, so it is not exploitable. | `relacl = {postgres,service_role}`; 0 policies |
| F9 | **`authenticated` holds UPDATE on `orders_number_seq`** (the `setval` right), from F3. The sequence is effectively unused: `authenticated` cannot INSERT into `orders`, the only writer `_create_sale_with_items_core` numbers orders from `tenant_counters`, and `orders.number` has no unique index. | `relacl`; `next_order_number` source; `pg_indexes` |
| F10 | **Exposed schemas:** the repo has no `[api] schemas`, so the CLI default `public, graphql_public` applies locally. Production's PostgREST exposed-schemas setting is **unknown**, which is the same gap recorded in the second review for `net.*`. | `supabase/config.toml` |

## 2. Exploit paths

| Path | Precondition | Effect | Today |
|---|---|---|---|
| P1 (F2) | Any table, sequence or function created in `public` **by `supabase_admin`**, for example an extension installed from the dashboard into `public` or a platform upgrade. | `anon` and `authenticated` get full rights, including TRUNCATE, with no RLS unless someone adds it. It is exposed through PostgREST because `public` is exposed. | Not present locally (F5). **Unverified on production.** |
| P2 (F4) | A future migration creates a function and forgets `REVOKE … FROM PUBLIC`. | `anon` can call it through `/rest/v1/rpc`. If it is SECURITY DEFINER, it runs with owner rights. | Not present (F7). It relies on every author remembering the REVOKE. |
| P3 (F3) | A future table in `public` without RLS. | Any signed-in user can read and write every tenant's rows in it. | Not present (F8). Nothing enforces it. |
| P4 (F9) | A signed-in user. | Can `setval` an unused sequence. No integrity effect today. | Low. |

## 3. What a migration can and cannot fix

- **P1 cannot be fixed from a migration.** `ALTER DEFAULT PRIVILEGES FOR ROLE supabase_admin` requires membership in `supabase_admin` (F1), so it would fail with a permission error. A fix needs Supabase or platform action. Within our control are detection (§4.B) and a rule never to install extensions into `public`.
- **P2 can be fixed by `postgres` for itself:** `ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;`. This global entry removes the PUBLIC grant from future functions only. Existing functions keep their ACLs.
- **P3 is better caught than defaulted away.** Revoking the default table rights from `authenticated` would make every Lovable-generated table need explicit grants. That is a larger behaviour change for the generated code path.

## 4. Proposed smallest safe correction (for owner approval of scope)

**A. One forward migration (DB change, after approval):**

```sql
-- C-DEFPRIV-01: functions created later by postgres are not executable by PUBLIC (anon) by default.
ALTER DEFAULT PRIVILEGES FOR ROLE postgres REVOKE EXECUTE ON FUNCTIONS FROM PUBLIC;
-- optional, P4: the unused order-number sequence needs no client UPDATE (setval).
REVOKE UPDATE ON SEQUENCE public.orders_number_seq FROM authenticated;
```

Effects and dependencies:
- **Future functions in `public`** are still executable by `authenticated` and `service_role`, through the per-schema default (F3).
- **Future functions in other schemas** (for example a new `monjez_private` helper used inside an RLS policy) are no longer PUBLIC-executable. They need an explicit `GRANT EXECUTE … TO authenticated`, or the policy that calls them fails with 42501. The release suites run real RLS paths, so they would catch a missed grant.
- **A future intentionally anonymous RPC** needs an explicit `GRANT … TO anon`. None exists today (F7).
- **The migration must run as `postgres`.** This is the same condition SEC-TRUNCATE already has; the production apply role is still listed as unproven in the second review.
- **Rollback:** `ALTER DEFAULT PRIVILEGES FOR ROLE postgres GRANT EXECUTE ON FUNCTIONS TO PUBLIC;` and `GRANT UPDATE ON SEQUENCE public.orders_number_seq TO authenticated;`.

**B. A catalog guard in release-finance (no DB change, test only).** It fails the release on the candidate database if:
1. any object in `public` is owned by a role other than `postgres` (catches P1);
2. any `public` table that grants anything to `anon` or `authenticated` has RLS off or lacks `monjez_live_actor` (P3; F8's table passes because it grants nothing);
3. `anon` or PUBLIC can EXECUTE any `public` function outside an explicit allowlist (today the two trigger functions) (P2);
4. `anon` or `authenticated` hold TRUNCATE on any `public` relation;
5. a SECURITY DEFINER function in `public` or `monjez_private` has no fixed `search_path`.

Plus negative controls: each rule is shown failing on a deliberately broken temporary object inside a rolled-back transaction on the disposable stack.

**Not proposed now:** revoking the default table rights from `authenticated` (§3), and anything that needs `supabase_admin`.

## 5. Production confirmation (read-only, needs owner approval)

```sql
select pg_get_userbyid(defaclrole), defaclnamespace::regnamespace, defaclobjtype, defaclacl from pg_default_acl order by 1,2,3;
select relkind, pg_get_userbyid(relowner), count(*) from pg_class where relnamespace='public'::regnamespace group by 1,2;
select pg_get_userbyid(proowner), count(*) from pg_proc where pronamespace='public'::regnamespace group by 1;
select p.oid::regprocedure from pg_proc p where p.pronamespace='public'::regnamespace and has_function_privilege('anon',p.oid,'EXECUTE');
select c.oid::regclass from pg_class c where c.relnamespace='public'::regnamespace and c.relkind in ('r','p')
  and (has_table_privilege('anon',c.oid,'TRUNCATE') or has_table_privilege('authenticated',c.oid,'TRUNCATE'));
select current_setting('pgrst.db_schemas', true);  -- may be NULL; the exposed-schemas setting may live outside the DB
```

These read catalog metadata only: no business rows, no secrets.

## 6. Review round 2 (PR #90 at 773af30), 2026-11-10

The independent review of bacda16 found gaps in R2, R5 and R7. Each is closed with negative controls. The new controls fail on the bacda16 rules (22/35) and pass on the new rules (35/35, twice, local fresh stack).

- **R2:** the live-actor policy is now judged by substance:
  - RESTRICTIVE, for ALL commands;
  - it applies to every client role that holds a privilege on the table;
  - both USING and WITH CHECK are present;
  - each is one of PostgreSQL's own deparsed forms of `monjez_private.actor_is_active()`;
  - its dependencies are that function only.
  New R2c flags a constant open PERMISSIVE policy.
- **R5:** new R5b requires every `search_path` entry to be trusted.
  - New R5c ratchet: 45 SECURITY DEFINER functions do not list `pg_temp` last, so `pg_temp` is searched first for relations, and `anon` and `authenticated` hold TEMP. The exposure needs a client SQL session; PostgREST offers none. The list may only shrink. Rewriting the 45 functions is a separate scope.
- **R7 limits:**
  - `pg_depend` records only functions a policy calls directly.
  - New operational control: every policy expression that applies to `authenticated` (117) is evaluated as a real signed-in owner inside a rolled-back transaction, so nested helpers run even on empty tables.
  - Remaining limit: AND/OR short-circuiting with an all-NULL row can skip a branch, so a helper reached only through a skipped branch is not executed. The release suites' real data paths cover the sensitive tables.
- **New finding F11 (local, reproducible):**
  - **What crashes:** on the local Supabase PostgreSQL 17.6 image (`shared_preload_libraries` includes pgaudit, auto_explain, plan_filter, plpgsql_check, pg_tle, supabase_vault; supautils as a session library), calling a non-definer SQL-language function that calls a function the caller may not EXECUTE terminates the backend with **signal 11**. The postmaster then restarts all connections.
  - **Reproduced 8 times:** with volatile, stable, `SET search_path` and BEGIN ATOMIC bodies, for both `anon` and `authenticated`. With a plpgsql outer function, it raises 42501 cleanly. With the inner function granted, nothing happens.
  - **Current exposure:** a text scan of the 30 client-executable SQL functions found no such call.
  - **Unknown:** the root-cause component, and whether production's image behaves the same. Production was not tested.
  - **Guard:** R8 (static, never executes) flags the pattern. C-DEFPRIV-01 makes it more likely for new non-public helpers, which is why the rule exists.
  - **Action proposed:** report upstream after a minimal reproduction on a vanilla PostgreSQL 17.6, and confirm on production only with the owner's approval.
