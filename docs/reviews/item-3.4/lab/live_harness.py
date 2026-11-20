#!/usr/bin/env python3
"""Item 3.4 local live check of the changed harness paths on the disposable 63-migration stack (127.0.0.1 only).

Runs the REAL ComposedProbe / B50NaturalExpiryProbe / CandidateWebhookProbe methods that this change touches,
against the local stack, with synthetic actors. It does NOT run the app, OAuth, MCP, the price route, the
firewall/UID containment or the 41->63 upgrade: __init__ (which requires the CI containment preflight) is
bypassed and only the attributes those methods read are set.
usage: python3 live_harness.py REPO_WORKTREE STATUS_JSON OUT_JSON
"""
import json, sys, urllib.request
from pathlib import Path

repo, status_file, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3])
for d in ('tests/account-lifecycle', 'tests/b5-lifecycle', 'tests/b50-natural-expiry', 'tests/e2e'):
    sys.path.insert(0, str(repo / d))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from lab_guard import guarded_target
# Target identity (live_probe.Probe.__init__ rules) and synthetic-only check, before anything can write.
CONFIG, STATUS, BASE, PRIOR_IDENTITIES = guarded_target(status_file)
from live_probe import NoRedirect, HarnessFailure
from owner_closure_probe import explicit_inactive
import composed, candidate_surface as surface
import importlib.util
spec = importlib.util.spec_from_file_location('b50probe', repo / 'tests/b50-natural-expiry/probe.py'); b50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b50)
import billing_probe


def bare(cls, evidence):
    p = object.__new__(cls)
    p.config, st = CONFIG, STATUS
    p.status, p.base, p.anon, p.admin = st, BASE, st['ANON_KEY'], st['SERVICE_ROLE_KEY']
    p.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    p.evidence_dir = evidence; evidence.mkdir(parents=True, exist_ok=True)
    p.controls, p.targets, p.secrets, p.issued, p.source = [], [], [], {}, 'local-3.4'
    return p


ev = out.parent / 'evidence'
r = {'target': {'api': BASE, 'prior_identities_all_synthetic': PRIOR_IDENTITIES}}
c = bare(composed.ComposedProbe, ev / 'composed')
names = c.snapshot()
r['ledger_count'] = c.query(surface.LEDGER_SQL)
r['composed_snapshot_relations'] = sorted(names)
c.no_truncate()
c.select_sale('initial')
a, b = c.fixture('L34_A'), c.fixture('L34_B')
sale, product, order = c.financial_fixture(b)
c.record('financial_idempotency_rls_no_policy_no_client_rights', surface.idempotency_locked(c.query(surface.IDEMPOTENCY_SQL)))
c.record('legacy_unkeyed_sales_not_client_executable_keyed_sale_authenticated_only',
         c.query(surface.SALE_SURFACE_SQL) == surface.EXPECTED_SALE_SURFACE[63])
# Negative: the historical legacy call (what the unadapted harness made) is refused on candidate63, not account_inactive.
code, body = c.request('POST', '/rest/v1/rpc/create_sale_with_items', sale, token=a['token'])
r['legacy_call_on_candidate'] = {'status': code, 'code': (body or {}).get('code'), 'explicit_inactive': explicit_inactive(code, body)}
# Keyed replay, asserted on the stored rows (not only the response): the first call writes exactly one order, one
# item, one payment, one completed ledger row and moves stock by the sold quantity; the exact replay and the
# conflicting body change nothing at all.
def rows(tenant):
    return c.query("""select jsonb_build_object(
      'orders',(select coalesce(jsonb_agg(jsonb_build_object('id',id,'total',total,'paid',paid,'status',status) order by id),'[]') from public.orders where tenant_id='%(t)s'),
      'items',(select count(*) from public.order_items where tenant_id='%(t)s'),
      'payments',(select coalesce(jsonb_agg(jsonb_build_object('id',id,'amount',amount,'kind',kind) order by id),'[]') from public.payments where tenant_id='%(t)s'),
      'stock',(select stock from public.products where id='%(p)s'),
      'ledger',(select coalesce(jsonb_agg(jsonb_build_object('key',idempotency_key,'op',operation,'done',completed_at is not null,'result',result) order by idempotency_key),'[]') from public.financial_idempotency where tenant_id='%(t)s'));""" % {'t': b['tenant'], 'p': product})
keyed = c.sale_body(sale)
r0 = rows(b['tenant'])
s1, o1 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, keyed, token=b['token'])
r1 = rows(b['tenant'])
s2, o2 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, keyed, token=b['token'])
r2 = rows(b['tenant'])
s3, o3 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, {**keyed, 'p_paid': 1}, token=b['token'])
r3 = rows(b['tenant'])
new_ledger = [x for x in r1['ledger'] if x not in r0['ledger']]
qty = sale['p_items'][0]['qty']
first_ok = (s1 == 200 and o1.get('success') is True and len(r1['orders']) == len(r0['orders']) + 1
            and r1['items'] == r0['items'] + 1 and len(r1['payments']) == len(r0['payments']) + 1
            and r1['stock'] == r0['stock'] - qty and len(new_ledger) == 1
            and new_ledger[0]['key'] == keyed['p_idempotency_key'] and new_ledger[0]['done'] is True
            and new_ledger[0]['result'] == o1)
replay_ok = s2 == 200 and o2 == o1 and r2 == r1
conflict_ok = s3 == 400 and (o3 or {}).get('message') == 'idempotency_conflict' and r3 == r1
c.record('keyed_first_call_writes_exactly_one_sale_and_one_completed_ledger_row', first_ok)
c.record('keyed_exact_replay_same_result_and_no_row_change', replay_ok)
c.record('keyed_conflicting_body_refused_and_no_row_change', conflict_ok)
r['keyed_replay'] = {'first_status': s1, 'replay_status': s2, 'conflict_status': s3,
                     'conflict_message': (o3 or {}).get('message'),
                     'delta_first': {'orders': len(r1['orders']) - len(r0['orders']), 'items': r1['items'] - r0['items'],
                                     'payments': len(r1['payments']) - len(r0['payments']),
                                     'stock': r1['stock'] - r0['stock'], 'ledger_rows': len(new_ledger)},
                     'replay_rows_unchanged': r2 == r1, 'conflict_rows_unchanged': r3 == r1}
# Inactive actor: provider ban, then the denial loop's exact call shape (denied_state / closed_controls).
code, _ = c.request('PUT', '/auth/v1/admin/users/' + b['uid'], {'ban_duration': '24h'}, admin=True)
before = c.state_snapshot()
denials = {}
for name in ('current_tenant_id', 'get_tenant_today_estimate', c.sale_rpc):
    code, body = c.request('POST', '/rest/v1/rpc/' + name, c.sale_body(sale) if name == c.sale_rpc else {}, token=b['token'])
    denials[name] = {'status': code, 'explicit_inactive': explicit_inactive(code, body)}
r['banned_rpc_denials'] = denials
r['banned_denials_left_state_unchanged'] = c.state_snapshot() == before
r['composed_checks'] = [x['name'] for x in c.controls]
r['composed_all_passed'] = all(x['passed'] for x in c.controls)
# B50 natural-expiry snapshot override on the same stage.
n = bare(b50.B50NaturalExpiryProbe, ev / 'b50')
r['b50_snapshot_tables'] = len(n.snapshot())
# Billing adapter's disk/ledger source check on this worktree.
r['billing_candidate_source'] = billing_probe.candidate_source(repo)[0]
out.write_text(json.dumps(r, indent=1) + '\n')
print(json.dumps({k: v for k, v in r.items() if k not in ('composed_checks', 'composed_snapshot_relations')}, indent=1))
print('checks:', len(r['composed_checks']), 'all passed:', r['composed_all_passed'])
