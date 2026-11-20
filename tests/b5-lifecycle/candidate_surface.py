"""Stage-exact database surface expectations for the B5/B50 harness on the candidate63 chain.

The stage is the live applied ledger size: 41 (historical A41 seed before upgrade), 50 (frozen B50)
or 63 (reviewed candidate). Each stage has one exact expectation; any other size is refused.
Candidate63 values below were measured on a disposable local stack built from the 63 reviewed
migrations (catalog reads only); 41/50 keep the historical count-only public rule unchanged.
"""
import uuid

PUBLIC22 = ('couriers', 'customers', 'day_closes', 'email_send_log', 'email_send_state',
            'email_unsubscribe_tokens', 'expenses', 'financial_audit_log', 'order_items', 'orders',
            'payments', 'platform_admin_audit_log', 'platform_admins', 'products', 'profiles',
            'security_scan_findings', 'security_scan_runs', 'subscriptions', 'suppressed_emails',
            'tenant_counters', 'tenants', 'user_roles')
IDEMPOTENCY = 'financial_idempotency'
PUBLIC23 = tuple(sorted(PUBLIC22 + (IDEMPOTENCY,)))
LEGACY_SALE = 'create_sale_with_items'
KEYED_SALE = 'create_sale_with_items_idempotent'
SIGNATURES = {
    'legacy': 'public.create_sale_with_items(uuid,delivery_kind,uuid,numeric,payment_method,jsonb)',
    'v2': 'public.create_sale_with_items_v2(uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)',
    'keyed': 'public.create_sale_with_items_idempotent(uuid,uuid,delivery_kind,uuid,numeric,payment_method,jsonb,courier_state)',
}
LEDGER_SQL = 'select to_jsonb(count(*)) from supabase_migrations.schema_migrations;'
# A missing function (or argument type) yields null from to_regprocedure, reported as absent.
SALE_SURFACE_SQL = 'select jsonb_build_object(' + ','.join(
    "'{k}',(select case when to_regprocedure('{s}') is null then to_jsonb('absent'::text) else jsonb_build_object("
    "'anon',has_function_privilege('anon',to_regprocedure('{s}'),'EXECUTE'),"
    "'authenticated',has_function_privilege('authenticated',to_regprocedure('{s}'),'EXECUTE')) end)".format(k=k, s=s)
    for k, s in SIGNATURES.items()) + ');'
IDEMPOTENCY_SQL = """select jsonb_build_object(
  'rls',c.relrowsecurity,
  'policies',(select count(*) from pg_policy p where p.polrelid=c.oid),
  'client_rights',(select jsonb_object_agg(r||':'||x,has_table_privilege(r,c.oid,x))
    from unnest(array['anon','authenticated']) r
    cross join unnest(array['SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER']) x))
  from pg_class c where c.oid=to_regclass('public.financial_idempotency');"""
DENIED = {'anon': False, 'authenticated': False}
EXPECTED_SALE_SURFACE = {
    63: {'legacy': DENIED, 'v2': DENIED, 'keyed': {'anon': False, 'authenticated': True}},
}


def stage(count):
    if count not in (41, 50, 63):
        raise RuntimeError('unreviewed_migration_stage')
    return count


def public_matches(count, names):
    if stage(count) == 63:
        return list(names) == list(PUBLIC23)
    # Historical A41/B50 rule, unchanged: exactly 22 public tables, and no candidate table.
    return len(names) == 22 and IDEMPOTENCY not in names


def public_count(count):
    return 23 if stage(count) == 63 else 22


def sale_surface_ok(count, surface):
    if stage(count) == 63:
        return surface == EXPECTED_SALE_SURFACE[63]
    # Historical seed: the keyed sale does not exist yet and the legacy sale is the approved path.
    legacy = surface.get('legacy')
    return surface.get('keyed') == 'absent' and isinstance(legacy, dict) and legacy.get('authenticated') is True


def sale_rpc(count):
    return KEYED_SALE if stage(count) == 63 else LEGACY_SALE


def sale_body(rpc, payload):
    """Legacy payload for the historical sale; the keyed sale also takes a fresh key and courier state."""
    if rpc == KEYED_SALE:
        return {'p_idempotency_key': str(uuid.uuid4()), **payload, 'p_courier_state': None}
    if rpc == LEGACY_SALE:
        return dict(payload)
    raise RuntimeError('unreviewed_sale_rpc')


def idempotency_locked(surface):
    """RLS on, no policy, and no client privilege of any kind on the idempotency ledger."""
    return (isinstance(surface, dict) and surface.get('rls') is True and surface.get('policies') == 0
            and isinstance(surface.get('client_rights'), dict) and len(surface['client_rights']) == 14
            and not any(surface['client_rights'].values()))
