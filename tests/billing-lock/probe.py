"""C-PADDLE-01: the Paddle webhook must not wait on a concurrent sale's FK lock.

Two real sessions on the isolated local stack only:
  A holds the tenant row lock a sale or collection takes (FK KEY SHARE through an
    uncommitted child insert), or a real tenant write (UPDATE tenants);
  B applies a synthetic sandbox subscription event as service_role, inside a
    transaction that is always rolled back.
Expected: B succeeds while A holds KEY SHARE, and still times out (55P03) while A
holds a real tenant write, so the webhook keeps excluding other tenant writers.
The synthetic user and tenant are removed at the end. No network beyond loopback.
"""
import json, os, subprocess, sys, time
from pathlib import Path

USER = '00000000-0000-4000-8000-0000000c0a01'
TENANT = '00000000-0000-4000-8000-0000000c0a02'
SUB = 'sub_' + 'c' * 26
EVENT = 'evt_' + 'c' * 26


def guard():
    bad = []
    if os.environ.get('CI_ISOLATED_SUPABASE') != '1': bad.append('CI_ISOLATED_SUPABASE must equal 1')
    if os.environ.get('PGHOST') not in ('127.0.0.1', 'localhost'): bad.append('PGHOST must be loopback')
    if os.environ.get('PGPORT') != '54322': bad.append('PGPORT must equal 54322')
    if os.environ.get('PGUSER') != 'postgres' or os.environ.get('PGDATABASE') != 'postgres':
        bad.append('PGUSER/PGDATABASE must equal postgres')
    if os.environ.get('PGSERVICE') or os.environ.get('PGSERVICEFILE') or os.environ.get('PGHOSTADDR'):
        bad.append('PGSERVICE/PGSERVICEFILE/PGHOSTADDR not allowed')
    if bad:
        sys.exit('BILLING_LOCK_PROBE_BLOCKED: ' + '; '.join(bad))


PSQL = ['psql', '-X', '-q', '-At', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose']


def sql(text, timeout=30):
    return subprocess.run(PSQL, input=text, capture_output=True, text=True, timeout=timeout)


def webhook_call(env='sandbox', sub_id=SUB, event_id=EVENT):
    """The webhook call itself, as service_role (inside a caller-provided transaction)."""
    sub = json.dumps({'id': sub_id, 'created_at': '2026-11-10T12:00:00Z', 'customer_id': 'ctm_' + 'c' * 26,
                      'tenant_id': TENANT, 'user_id': USER, 'product_id': 'pro_c_paddle_01',
                      'price_id': 'pri_c_paddle_01', 'status': 'active'})
    return f"""SELECT set_config('request.jwt.claims','{{"role":"service_role"}}',true);
SET LOCAL ROLE service_role;
SELECT public.apply_subscription_webhook('{env}','{event_id}','subscription.created',
  '2026-11-10T12:00:01Z'::timestamptz,'{sub}'::jsonb)->>'status';
RESET ROLE;"""


def webhook_txn(env='sandbox'):
    """Session B: one event as service_role, always rolled back."""
    sub = json.dumps({'id': SUB, 'created_at': '2026-11-10T12:00:00Z', 'customer_id': 'ctm_' + 'c' * 26,
                      'tenant_id': TENANT, 'user_id': USER, 'product_id': 'pro_c_paddle_01',
                      'price_id': 'pri_c_paddle_01', 'status': 'active'})
    return f"""\\set VERBOSITY verbose
BEGIN;
SELECT set_config('request.jwt.claims','{{"role":"service_role"}}',true);
SET LOCAL ROLE service_role;
SELECT public.apply_subscription_webhook('{env}','{EVENT}','subscription.created',
  '2026-11-10T12:00:01Z'::timestamptz,'{sub}'::jsonb)->>'status';
RESET ROLE;
SELECT 'rows_in_txn', (SELECT count(*) FROM public.subscriptions WHERE tenant_id='{TENANT}'),
  (SELECT count(*) FROM monjez_private.billing_webhook_receipts WHERE tenant_id='{TENANT}'),
  (SELECT subscription_status FROM public.tenants WHERE id='{TENANT}');
ROLLBACK;
"""


def with_holder(hold_sql, env='sandbox', b_script=None):
    """Session A takes a lock and keeps its transaction open while B runs."""
    a = subprocess.Popen(PSQL, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    a.stdin.write('BEGIN;\n' + hold_sql + "\n\\echo HOLDER_READY\n"); a.stdin.flush()
    seen = []
    while True:  # the holder's own statements may print rows before the marker
        line = a.stdout.readline()
        if not line or line.strip() == 'HOLDER_READY':
            break
        seen.append(line.strip())
    if line.strip() != 'HOLDER_READY':
        a.kill(); raise SystemExit('BILLING_LOCK_HOLDER_FAILED ' + ' '.join(seen)[:200] + ' ' + a.stderr.read()[:300])
    t0 = time.monotonic(); b = sql(b_script or webhook_txn(env)); elapsed = time.monotonic() - t0
    a.stdin.write('ROLLBACK;\n\\q\n'); a.stdin.flush(); a.wait(timeout=30)
    return b, elapsed


def main():
    guard()
    evidence = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    controls = []

    def control(name, ok, detail=None):
        controls.append({'name': name, 'passed': bool(ok), **({'detail': detail} if detail is not None else {})})

    setup = sql(f"""BEGIN;
INSERT INTO auth.users(id, instance_id, aud, role, email, created_at, updated_at)
  VALUES ('{USER}','00000000-0000-0000-0000-000000000000','authenticated','authenticated',
          'c-paddle-01@mongezz.test', now(), now()) ON CONFLICT (id) DO NOTHING;
INSERT INTO public.tenants(id, name, owner_user_id) VALUES ('{TENANT}','C-PADDLE-01 synthetic','{USER}')
  ON CONFLICT (id) DO NOTHING;
COMMIT;""")
    if setup.returncode != 0:
        raise SystemExit('BILLING_LOCK_SETUP_FAILED ' + setup.stderr[:400])
    try:
        src = sql("SELECT prosrc FROM pg_proc WHERE oid='public.apply_subscription_webhook(text,text,text,timestamptz,jsonb)'::regprocedure").stdout
        control('catalog_tenant_lock_is_no_key_update',
                'FROM public.tenants WHERE id=v_tenant_id FOR NO KEY UPDATE;' in src
                and 'FROM public.tenants WHERE id=v_tenant_id FOR UPDATE;' not in src)

        # A sale or collection on the same tenant: an uncommitted child row takes FK KEY SHARE.
        b, elapsed = with_holder(
            f"INSERT INTO public.customers(tenant_id, name) VALUES ('{TENANT}','C-PADDLE-01 holder');")
        out = b.stdout.split()
        control('webhook_not_blocked_by_concurrent_sale_key_share',
                b.returncode == 0 and 'applied' in out and elapsed < 2.0,
                {'rc': b.returncode, 'elapsed_s': round(elapsed, 2), 'sqlstate_55P03': '55P03' in b.stderr})
        control('webhook_effect_visible_inside_its_txn', 'rows_in_txn|1|1|' in b.stdout)

        # live projects onto the tenant row itself (UPDATE of non-key columns) under the same holder.
        b, elapsed = with_holder(
            f"INSERT INTO public.customers(tenant_id, name) VALUES ('{TENANT}','C-PADDLE-01 holder');", 'live')
        control('live_webhook_projects_tenant_while_sale_holds_key_share',
                b.returncode == 0 and 'applied' in b.stdout.split() and 'rows_in_txn|1|1|active' in b.stdout
                and elapsed < 2.0,
                {'rc': b.returncode, 'elapsed_s': round(elapsed, 2), 'sqlstate_55P03': '55P03' in b.stderr})

        # A real tenant write must still be excluded: the webhook waits, then lock_timeout 2s.
        b, elapsed = with_holder(f"UPDATE public.tenants SET name=name WHERE id='{TENANT}';")
        control('webhook_still_excludes_concurrent_tenant_writer',
                b.returncode != 0 and '55P03' in b.stderr and elapsed >= 1.9,
                {'rc': b.returncode, 'elapsed_s': round(elapsed, 2)})

        # Review of #87 (concurrency invariants FOR UPDATE gave, which NO KEY UPDATE must keep):
        sub2, evt2 = 'sub_' + 'd' * 26, 'evt_' + 'd' * 26
        timed = "\\set VERBOSITY verbose\nBEGIN;\nSET LOCAL lock_timeout = '2s';\n"
        # (a) two events for different subscriptions of the same tenant are serialized.
        b, elapsed = with_holder(webhook_call(), b_script=timed + webhook_call(sub_id=sub2, event_id=evt2) + "\nROLLBACK;\n")
        control('concurrent_webhooks_same_tenant_serialized',
                b.returncode != 0 and '55P03' in b.stderr and elapsed >= 1.9, {'rc': b.returncode, 'elapsed_s': round(elapsed, 2)})
        # (b) an owner's tenant write waits while a webhook holds the tenant row.
        b, elapsed = with_holder(webhook_call(), b_script=timed + f"UPDATE public.tenants SET name='x' WHERE id='{TENANT}';\nROLLBACK;\n")
        control('tenant_writer_waits_for_inflight_webhook',
                b.returncode != 0 and '55P03' in b.stderr and elapsed >= 1.9, {'rc': b.returncode, 'elapsed_s': round(elapsed, 2)})
        # (c) the same event cannot be applied concurrently (event advisory lock).
        b, elapsed = with_holder(webhook_call(), b_script=timed + webhook_call() + "\nROLLBACK;\n")
        control('same_event_concurrent_second_waits',
                b.returncode != 0 and '55P03' in b.stderr and elapsed >= 1.9, {'rc': b.returncode, 'elapsed_s': round(elapsed, 2)})
        # (d) the same event twice in sequence: applied, then duplicate, one subscription row.
        r = sql("\\set VERBOSITY verbose\nBEGIN;\n" + webhook_call() + "\n" + webhook_call() +
                f"\nSELECT 'subs', count(*) FROM public.subscriptions WHERE tenant_id='{TENANT}';\nROLLBACK;\n")
        outs = [x for x in r.stdout.split() if not x.startswith('{')]  # drop set_config echoes
        control('same_event_sequential_applied_then_duplicate_one_row',
                r.returncode == 0 and outs[:2] == ['applied', 'duplicate'] and 'subs|1' in outs, outs[:4])

        left = sql(f"SELECT (SELECT count(*) FROM public.subscriptions WHERE tenant_id='{TENANT}'),"
                   f"(SELECT count(*) FROM monjez_private.billing_webhook_receipts WHERE tenant_id='{TENANT}'),"
                   f"(SELECT count(*) FROM monjez_private.billing_tenant_bindings WHERE tenant_id='{TENANT}'),"
                   f"(SELECT count(*) FROM public.customers WHERE tenant_id='{TENANT}');").stdout.strip()
        control('no_billing_or_customer_rows_persisted', left == '0|0|0|0', left)
    finally:
        sql(f"""BEGIN;
DELETE FROM public.tenants WHERE id='{TENANT}';
DELETE FROM auth.users WHERE id='{USER}';
COMMIT;""")
    gone = sql(f"SELECT (SELECT count(*) FROM public.tenants WHERE id='{TENANT}')+(SELECT count(*) FROM auth.users WHERE id='{USER}');").stdout.strip()
    control('synthetic_tenant_and_user_removed', gone == '0', gone)

    result = {'probe': 'c-paddle-01', 'controls': controls}
    print('BILLING_LOCK_RESULT ' + json.dumps(result))
    if evidence:
        evidence.mkdir(parents=True, exist_ok=True)
        (evidence / 'billing-lock.json').write_text(json.dumps(result, indent=2) + '\n')
    failed = [c['name'] for c in controls if not c['passed']]
    if failed:
        raise SystemExit('BILLING_LOCK_FAILED ' + ','.join(failed))


if __name__ == '__main__':
    main()
