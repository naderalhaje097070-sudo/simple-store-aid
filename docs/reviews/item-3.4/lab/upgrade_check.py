#!/usr/bin/env python3
"""Item 3.4 local check of the composed UPGRADE path: original41 seed (legacy sale) -> real `supabase migration up`
to the reviewed candidate63 -> preservation, stage-exact surface, keyed sale and inactive denials.
Uses the REAL ComposedProbe methods; __init__ (CI containment preflight) is bypassed. No app/OAuth/MCP/price route.
usage: python3 upgrade_check.py REPO STATUS_JSON STACK_DIR SUPABASE_BIN OUT_JSON
"""
import json, shutil, subprocess, sys, urllib.request
from pathlib import Path

repo, status_file, stack, sb, out = Path(sys.argv[1]), Path(sys.argv[2]), Path(sys.argv[3]), sys.argv[4], Path(sys.argv[5])
for d in ('tests/account-lifecycle', 'tests/b5-lifecycle', 'tests/e2e'):
    sys.path.insert(0, str(repo / d))
from write_harness_guard import require_write_harness
from live_probe import NoRedirect
from owner_closure_probe import explicit_inactive
from inventory import inventory
import composed, candidate_surface as surface

c = object.__new__(composed.ComposedProbe)
c.config = require_write_harness()
st = json.loads(status_file.read_text())
c.status, c.base, c.anon, c.admin = st, st['API_URL'], st['ANON_KEY'], st['SERVICE_ROLE_KEY']
c.opener = urllib.request.build_opener(urllib.request.ProxyHandler({}), NoRedirect())
c.evidence_dir = out.parent / 'evidence' / 'upgrade'; c.evidence_dir.mkdir(parents=True, exist_ok=True)
c.controls, c.targets, c.secrets, c.issued, c.source = [], [], [], {}, 'local-3.4-upgrade'

inv = inventory(repo)
c.chain(inv['original_versions'], 'exact_initial_chain_upgrade')
c.select_sale('initial')
a, b = c.fixture('U_A'), c.fixture('U_B')
sale, product, order = c.financial_fixture(b)
for label, actor in [('A', a), ('B', b)]:
    code, rows = c.request('POST', '/rest/v1/customers', {'tenant_id': actor['tenant'], 'name': 'U customer ' + label}, token=actor['token'])
    c.record(label + '_real_owned_customer', code == 201 and len(rows) == 1)
before = c.state_snapshot()
for path in inv['all_paths']:
    shutil.copy2(repo / path, stack / 'supabase/migrations' / Path(path).name)
with (out.parent / 'upgrade-private.log').open('w') as log:
    rc = subprocess.run([sb, '--workdir', str(stack), 'migration', 'up', '--local'], stdout=log, stderr=log, timeout=300).returncode
c.record('real_populated41_to' + str(inv['count']) + '_migration', rc == 0)
after = c.state_snapshot()
c.record('all_original22_public_and_auth_identity_preserved',
         after['auth_identity_state'] == before['auth_identity_state']
         and all(after['relations'][k] == v for k, v in before['relations'].items()))
c.chain(inv['full_versions'], 'exact_effective' + str(inv['count']) + '_chain')
c.select_sale('effective')
snap = c.snapshot()
c.record('all_three_new_private_tables_empty', all(snap['private.' + n]['count'] == 0 for n in composed.PRIVATE))
c.record('financial_idempotency_empty_after_upgrade', snap['financial_idempotency']['count'] == 0)
c.no_truncate()
c.record('financial_idempotency_rls_no_policy_no_client_rights', surface.idempotency_locked(c.query(surface.IDEMPOTENCY_SQL)))
c.record('legacy_unkeyed_sales_not_client_executable_keyed_sale_authenticated_only',
         c.query(surface.SALE_SURFACE_SQL) == surface.EXPECTED_SALE_SURFACE[63])
# Historical (legacy-shape) seed payload replayed through the keyed adapter by a fresh active owner on candidate63.
cc = c.fixture('U_C')
# financial_fixture's exact-one-audit oracle is per tenant: the keyed fixture uses a fresh owner C and its own
# probe instance (same config/keys), because ComposedProbe refuses duplicate check names.
import copy
k = copy.copy(c); k.controls = []
k.financial_fixture(cc)
keyed_checks = [x['name'] for x in k.controls]; keyed_ok = all(x['passed'] for x in k.controls)
code, _ = c.request('PUT', '/auth/v1/admin/users/' + b['uid'], {'ban_duration': '24h'}, admin=True)
c.record('real_provider_ban_B', code == 200)
pre = c.state_snapshot()
for name in ('current_tenant_id', 'get_tenant_today_estimate', c.sale_rpc):
    code, body = c.request('POST', '/rest/v1/rpc/' + name, c.sale_body(sale) if name == c.sale_rpc else {}, token=b['token'])
    c.record('banned_B_named_RPC_' + name, explicit_inactive(code, body), status=code)
c.record('banned_B_denials_state_unchanged', c.state_snapshot() == pre)
r = {'rc': rc, 'checks': [x['name'] for x in c.controls], 'all_passed': all(x['passed'] for x in c.controls),
     'keyed_fixture_checks': keyed_checks, 'keyed_fixture_all_passed': keyed_ok,
     'sale_rpc_before': surface.LEGACY_SALE, 'sale_rpc_after': c.sale_rpc,
     'relations_before': len(before['relations']), 'relations_after': len(after['relations'])}
out.write_text(json.dumps(r, indent=1) + '\n')
print(json.dumps(r, indent=1))
