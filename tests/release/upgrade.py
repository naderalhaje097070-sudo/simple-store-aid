"""Production-shaped upgrade check: seed on main's schema, upgrade, compare meaning.

seed   runs against a stack built only from origin/main's migrations, using only
       RPCs that exist on main (legacy create_sale_with_items, collect_order_debt,
       close_day). It records independent expected financial facts.
verify runs after `migration up --include-all` to the candidate. It checks the
       same facts by value (types may legitimately widen, e.g. integer stock to
       numeric), that the saved close reads correctly through the new report view,
       and that the remaining debt can be settled exactly once with the keyed RPC.
       Before acting it also checks that the database history is exactly the
       candidate's migrations (seed checks it is exactly main's) and that every
       row of every pre-upgrade table is unchanged on its pre-upgrade columns.

Seed tenant is separate from the suites' tenants so their oracles are unaffected.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import re
import sys
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release_collection_probe', ROOT / 'tests/c5-collection/native.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
sys.path.insert(0, str(ROOT / 'tests/release'))
import gate  # noqa: E402

SCHEMAS = "('public','monjez_private')"
IDENT = re.compile(r'[a-z_][a-z0-9_]{0,62}')

# price 100, cost 40, qty 2 -> total 200, margin 120. Paid 100 at sale, 40 later.
EXPECTED = {
    'order': {'total': 200, 'paid': 140, 'status': 'partial'},
    'payments': {'count': 2, 'sum': 140},
    'stock': 8,
    'close': {'sales': 200, 'collected': 140, 'expenses': 5, 'realized_profit': 84, 'customer_debts': 60},
}


def facts(p, seed):
    order = p.query(f"select jsonb_build_object('total',total,'paid',paid,'status',status) from public.orders where id='{seed['order']}';")
    payments = p.query(f"select jsonb_build_object('count',count(*),'sum',coalesce(sum(amount),0)) from public.payments where order_id='{seed['order']}';")
    stock = p.query(f"select to_jsonb(stock) from public.products where id='{seed['product']}';")
    close = p.query(f"select jsonb_build_object('sales',sales,'collected',collected,'expenses',expenses,'realized_profit',realized_profit,'customer_debts',customer_debts) from public.day_closes where tenant_id='{seed['tenant']}';")
    return {'order': order, 'payments': payments, 'stock': stock, 'close': close}


def history(p):
    return p.query('select coalesce(jsonb_agg(version order by version),\'[]\'::jsonb) from supabase_migrations.schema_migrations;')


def relation_columns(p):
    """{schema.table: sorted column names} for every base table of the app schemas."""
    data = p.query("select coalesce(jsonb_object_agg(name, cols),'{}'::jsonb) from (select c.table_schema||'.'||c.table_name name,"
                   " jsonb_agg(c.column_name::text order by c.column_name) cols from information_schema.columns c"
                   " join information_schema.tables t on t.table_schema=c.table_schema and t.table_name=c.table_name"
                   f" where t.table_type='BASE TABLE' and c.table_schema in {SCHEMAS} group by 1) s;")
    for name, cols in data.items():
        if not (all(IDENT.fullmatch(x) for x in name.split('.', 1)) and all(IDENT.fullmatch(c) for c in cols)):
            raise ValueError('unexpected relation or column name')
    return data


def relation_digest(p, name, cols):
    """Row count and digest of the table projected onto cols; by value, so a
    widened type (integer -> numeric) with the same values keeps its digest."""
    schema, table = name.split('.', 1)
    keys = ','.join("'" + c + "'" for c in cols)
    return p.query(f"select jsonb_build_object('count',count(*),'digest',md5(coalesce(string_agg(x::text,'' order by x::text),'')))"
                   f" from (select (select coalesce(jsonb_object_agg(k,v),'{{}}'::jsonb) from jsonb_each(to_jsonb(t)) e(k,v)"
                   f" where k = any(array[{keys}]::text[])) x from \"{schema}\".\"{table}\" t) s;")


def relations(p):
    return {name: {'columns': cols, **relation_digest(p, name, cols)} for name, cols in sorted(relation_columns(p).items())}


def seed(p, private):
    p.stage = 'upgrade_seed_main'
    main_versions = gate.verify_migrations(ROOT, 'origin/main', 'origin/main')
    observed_history = history(p)
    p.control('upgrade_starts_exactly_at_main_history', observed_history == main_versions,
              observed={'applied': len(observed_history), 'main': len(main_versions)})
    state = p.actors_state(private)  # suite actors, created now so later phases reuse them
    owner = p.fixture('Upgrade_owner')
    state['actors']['upgrade_owner'] = owner
    p.save(private, state)
    pid = p.seed_product(owner)
    customer, _ = p.customer_courier(owner)
    code, sale = p.rpc(owner, 'create_sale_with_items', {
        'p_customer_id': customer, 'p_delivery': 'direct', 'p_courier_id': None, 'p_paid': 100,
        'p_method': 'cash', 'p_items': [{'productId': pid, 'qty': 2}]})
    p.control('main_legacy_sale', code == 200 and sale.get('success') is True)
    order = str(uuid.UUID(sale['order_id']))
    code, _ = p.rpc(owner, 'collect_order_debt', {'p_order_id': order, 'p_amount': 40, 'p_method': 'cash'})
    p.control('main_legacy_collection', code == 200)
    p.sql(f"insert into public.expenses(tenant_id,type,amount,method,created_by) values ('{owner['tenant']}','upgrade-seed',5,'cash','{owner['uid']}');")
    code, _ = p.rpc(owner, 'close_day', {'p_note': 'main-before-upgrade'})
    p.control('main_close_day', code == 200)
    state['upgrade_seed'] = {'tenant': owner['tenant'], 'order': order, 'product': pid}
    observed = facts(p, state['upgrade_seed'])
    p.control('main_seed_matches_independent_oracle', observed == EXPECTED, observed=observed, expected=EXPECTED)
    state['upgrade_relations'] = relations(p)
    p.control('main_seed_relations_recorded', len(state['upgrade_relations']) > 0
              and any(v['count'] > 0 for v in state['upgrade_relations'].values()),
              observed={'relations': len(state['upgrade_relations'])})
    state['upgrade_checks'] = p.controls
    p.save(private, state)
    return {'source_sha': p.source, 'phase': 'seed_main', 'controls': p.controls}


def verify_upgrade(p, private):
    p.stage = 'upgrade_verify_candidate'
    state = json.loads(private.read_text())
    s, owner = state['upgrade_seed'], state['actors']['upgrade_owner']
    p.controls = state['upgrade_checks'] + p.controls
    candidate = gate.verify_migrations(ROOT, 'HEAD', 'origin/main')
    observed_history = history(p)
    p.control('upgraded_history_is_exactly_candidate', observed_history == candidate,
              observed={'applied': len(observed_history), 'candidate': len(candidate)})
    # Before any new action: nothing the upgrade touched may alter an existing row.
    before, columns = state['upgrade_relations'], relation_columns(p)
    changed = sorted(name for name, old in before.items()
                     if name not in columns or not set(old['columns']) <= set(columns[name])
                     or relation_digest(p, name, old['columns']) != {'count': old['count'], 'digest': old['digest']})
    p.control('upgraded_all_base_relations_preserved', not changed,
              observed={'relations': len(before), 'changed': len(changed)}, changed_relations=changed)
    p.control('upgraded_financial_facts_preserved', facts(p, s) == EXPECTED, observed=facts(p, s), expected=EXPECTED)
    report = p.query(f"select jsonb_build_object('margin',realized_margin_before_expenses,'net',realized_net_profit) from public.day_close_profit_report where tenant_id='{s['tenant']}';")
    p.control('upgraded_saved_close_reads_margin84_net79', report == {'margin': 84, 'net': 79}, observed=report)
    request = {'p_idempotency_key': str(uuid.uuid4()), 'p_order_id': s['order'], 'p_amount': 60, 'p_method': 'cash'}
    first = p.rpc(owner, 'collect_order_debt_idempotent', request)
    replay = p.rpc(owner, 'collect_order_debt_idempotent', request)
    after = facts(p, s)
    p.control('upgraded_old_debt_settles_exactly_once',
              first[0] == 200 and replay == first and after['order'] == {'total': 200, 'paid': 200, 'status': 'paid'}
              and after['payments'] == {'count': 3, 'sum': 200}, observed=after)
    state['upgrade_seed_final'] = after
    p.save(private, state)
    return {'source_sha': p.source, 'phase': 'verify_candidate', 'controls': p.controls}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['seed', 'verify'])
    for name in ('status-file', 'evidence-dir', 'private-state'):
        parser.add_argument('--' + name, type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    p = prior.FinanceProbe(args.status_file, args.evidence_dir, args.expected_source)
    try:
        result = (seed if args.phase == 'seed' else verify_upgrade)(p, args.private_state)
        (args.evidence_dir / f'upgrade-{args.phase}.json').write_text(json.dumps(result, indent=2) + '\n')
        print('RELEASE_UPGRADE_' + args.phase.upper() + ' ' + json.dumps({'source': p.source, 'controls': len(p.controls)}))
        return 0
    except Exception as error:
        failed = next((c['name'] for c in p.controls if not c.get('passed')), None)
        print('RELEASE_UPGRADE_FAILED ' + json.dumps({'phase': args.phase, 'stage': getattr(p, 'stage', None),
                                                     'failure_type': type(error).__name__,
                                                     'controls_completed': len(p.controls),
                                                     'first_failed_control': failed}))
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
