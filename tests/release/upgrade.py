"""Production-shaped upgrade check: seed on main's schema, upgrade, compare meaning.

seed   runs against a stack built only from origin/main's migrations, using only
       RPCs that exist on main (legacy create_sale_with_items, collect_order_debt,
       close_day). It records independent expected financial facts.
verify runs after `migration up --include-all` to the candidate. It checks the
       same facts by value (types may legitimately widen, e.g. integer stock to
       numeric), that the saved close reads correctly through the new report view,
       and that the remaining debt can be settled exactly once with the keyed RPC.

Seed tenant is separate from the suites' tenants so their oracles are unaffected.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('release_collection_probe', ROOT / 'tests/c5-collection/native.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)

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


def seed(p, private):
    p.stage = 'upgrade_seed_main'
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
    state['upgrade_checks'] = p.controls
    p.save(private, state)
    return {'source_sha': p.source, 'phase': 'seed_main', 'controls': p.controls}


def verify_upgrade(p, private):
    p.stage = 'upgrade_verify_candidate'
    state = json.loads(private.read_text())
    s, owner = state['upgrade_seed'], state['actors']['upgrade_owner']
    p.controls = state['upgrade_checks'] + p.controls
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
