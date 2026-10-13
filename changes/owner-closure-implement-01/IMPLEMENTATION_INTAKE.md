# OWNER-CLOSURE-IMPLEMENT-01 — resumed authorized intake

Owner said «استمر» after the concrete product REST/RLS fixture amendment in the final
handoff. #55/6151753298 records this narrow continuation and sole implementer /root.
OC-FIXTURE-01 is resolved for this batch: one fake product via the existing owner
REST/RLS path; sale/order/items/payment/audit only through existing create_sale_with_items
and its triggers. No direct financial SQL, new productRPC or PR49/50 borrowing.

Source: existing PR69/f8361ac62d48de9047475f79d378b1448c696f21 above PR68/00923287.
The same additive branch/PR will be used. PR69 is temporarily closed to avoid historical
PR workflows activated by its state paths. Dedicated push workflow only; reopen after
final docs/evidence with skip-ci. Main is not updated; no production/merge/deploy/new cost.
Local Supabase runs on one disposable GitHub runner per focused mode, matching the
existing project runner approach; every target is loopback, fake data only, no backup.

## Contract design before implementation

The existing policy says account closure stops owner's application access while retaining
stores/identity/history. Interpret this as account-wide: every token for that identity
loses application access, including all owned stores and existing memberships. It does
not close any store, change rights/ownership/obligations or affect other identities.
No assumption of one store per owner is allowed. Observe actual pg_index on baseline44
before implementing; source only suggests no unique owner index. If inconsistent stop.

Proposed entry: public.close_owner_account(), zero arguments. Caller must be authenticated,
Auth identity exists/not deleted/not currently banned, and on first call must actually own
at least one tenant with existing owner role. No arbitrary target ID/profile metadata role.
Return only {"status":"closed"}, also on repeat. Invalid/foreign extra parameters cannot
resolve the zero-argument PostgREST contract. anon has no EXECUTE. Staff/non-owner raises
42501/owner_required; invalid Auth state raises42501/account_inactive; missing caller raises
42501/authentication_required. Only connection role authenticated may call this entry.

Persistent event: private owner_account_closures(user_id primary key reference Auth user
ON DELETE RESTRICT, closed_at not null). No email/name copy, new public table, tenant links,
financial audit append, data backfill, re-open or clearing path. Private table RLS enabled,
no client/service DML grants/policies; definer entry/predicate with empty search_path.
The event is its own closure audit. Existing financial/public audit rows remain byte-identical.
FK RESTRICT deliberately prevents closed user's later hard-delete from erasing the marker;
future explicit erasure needs separately authorized forward compensation.

Replace only actor_is_active body to retain Auth checks and additionally reject an existing
private marker. Keep its signature/volatility/owner/ACL and assert_active_actor/financial
RPC statements unchanged. Existing restrictive RLS and RPC callers consume it.

One transaction/function call locks the Auth row then inserts one event; primary key and
same row lock prevent repeated effects. Repeat exception checks independent live Auth state
first and returns constant closed result from own marker only. It does not bypass bans/deletion,
return protected public data, reopen, regrant or confer rights. Race/in-flight promises outside
card are not claimed; sequential old/new-token repeats are in scope.

## Gates and stop

First run unmodified44 source/schema with populated fixture, live index inventory, active
REST/RPC and full Nitro/TanStack MCP route, and expected-red PGRST202 missing closure entry.
Fresh45 and populated44→45 upgrade will follow only after this baseline/design check.
If approved-source fixture or actual index assumptions fail, save failure without financial repair.
Independent design/source/runtime-evidence review and final-source equivalence remain required.
