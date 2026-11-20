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
from write_harness_guard import require_write_harness
from live_probe import NoRedirect, HarnessFailure
from owner_closure_probe import explicit_inactive
import composed, candidate_surface as surface
import importlib.util
spec = importlib.util.spec_from_file_location('b50probe', repo / 'tests/b50-natural-expiry/probe.py'); b50 = importlib.util.module_from_spec(spec); spec.loader.exec_module(b50)
import billing_probe


def bare(cls, evidence):
    p = object.__new__(cls)
    p.config = require_write_harness()
    st = json.loads(status_file.read_text())
    p.status, p.base, p.anon, p.admin = st, st['API_URL'], st['ANON_KEY'], st['SERVICE_ROLE_KEY']
    p.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
    p.evidence_dir = evidence; evidence.mkdir(parents=True, exist_ok=True)
    p.controls, p.targets, p.secrets, p.issued, p.source = [], [], [], {}, 'local-3.4'
    return p


ev = out.parent / 'evidence'
r = {}
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
# Keyed replay of one request with one key returns the same order (one ledger row), a different body is a conflict.
keyed = c.sale_body(sale)
s1, o1 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, keyed, token=b['token'])
s2, o2 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, keyed, token=b['token'])
s3, o3 = c.request('POST', '/rest/v1/rpc/' + c.sale_rpc, {**keyed, 'p_paid': 1}, token=b['token'])
r['keyed_replay'] = {'first': s1, 'same_order': s2 == 200 and o1 == o2, 'conflict_status': s3, 'conflict': (o3 or {}).get('message')}
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
