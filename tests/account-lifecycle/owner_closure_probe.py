"""Bounded owner closure proof on disposable loopback Supabase and real app route."""
import argparse
import base64
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import time

from live_probe import HarnessFailure, FINANCE_TABLES
from mcp_probe import TOOLS, tool_success, account_tool_denial
from tanstack_route_probe import TanStackRouteProbe, publish_result

RPC = '/rest/v1/rpc/close_owner_account'


def explicit_inactive(status, body):
    return (status == 403 and isinstance(body, dict) and body.get('code') == '42501'
            and body.get('message') == 'account_inactive')


def claims(token):
    return json.loads(base64.urlsafe_b64decode(token.split('.')[1] + '=='))


def expected_fixture():
    # Independent constants, not derived from application totals or summaries.
    return {'price': 12.50, 'cost': 4.25, 'initial_stock': 10, 'quantity': 2,
            'total': 25, 'paid': 25, 'remaining': 0, 'stock': 8, 'line_cost': 8.50,
            'margin': 16.50, 'payment_count': 1, 'order_count': 1, 'item_count': 1}


class ClosureProbe(TanStackRouteProbe):
    def record(self, name, passed, **details):
        self.controls.append({'name': name, 'passed': bool(passed), **details})
        self.save_progress()
        if not passed:
            raise HarnessFailure('closure control failed: ' + name)

    def save_progress(self):
        # Every value in controls is deliberately allowlisted; never raw API bodies.
        (self.evidence_dir / 'closure-progress.json').write_text(json.dumps(
            {'source_sha': self.source, 'checks': self.controls}, indent=2) + '\n')

    def control(self, name, passed, **details):
        self.record(name, passed, **details)

    def state_snapshot(self):
        public = self.snapshot()
        rows = self.query("select coalesce(jsonb_agg(jsonb_build_object('id',id,'deleted_at',deleted_at,"
                          "'banned_until',banned_until) order by id),'[]'::jsonb) from auth.users;")
        counts = {t: int(self.sql('select count(*) from public.' + t + ';')) for t in public}
        return {'public': public, 'auth_identity_state': rows, 'counts': counts}

    def index_inventory(self):
        result = self.query("""select jsonb_agg(jsonb_build_object(
          'name',ic.relname,'unique',i.indisunique,'primary',i.indisprimary,
          'valid',i.indisvalid,'definition',pg_get_indexdef(i.indexrelid),
          'key_columns',(select jsonb_agg(a.attname order by k.pos)
            from unnest(i.indkey::smallint[]) with ordinality k(num,pos)
            left join pg_attribute a on a.attrelid=i.indrelid and a.attnum=k.num
            where k.pos<=i.indnkeyatts),
          'predicate',pg_get_expr(i.indpred,i.indrelid),
          'expressions',pg_get_expr(i.indexprs,i.indrelid)) order by ic.relname)
          from pg_index i join pg_class c on c.oid=i.indrelid
          join pg_namespace n on n.oid=c.relnamespace
          join pg_class ic on ic.oid=i.indexrelid
          where n.nspname='public' and c.relname='tenants';""")
        self.record('live_tenant_indexes_observed', isinstance(result, list) and bool(result))
        (self.evidence_dir / 'tenant-indexes.json').write_text(json.dumps(result, indent=2) + '\n')
        self.record('owner_not_uniquely_constrained', not any(
            x['unique'] and x['valid'] and x['key_columns'] == ['owner_user_id']
            and x['predicate'] is None and x['expressions'] is None for x in result))
        self.record('no_unresolved_unique_expression_index', not any(
            x['unique'] and x['expressions'] is not None for x in result))
        return result

    def no_truncate(self):
        result = self.query("""select jsonb_agg(jsonb_build_object('table',t.tablename,'role',r,
          'allowed',has_table_privilege(r,format('public.%I',t.tablename),'TRUNCATE'))
          order by t.tablename,r) from pg_tables t
          cross join unnest(array['anon','authenticated']) r where t.schemaname='public';""")
        self.record('client_truncate_denied_all22', len(result) == 44
                    and all(x['allowed'] is False for x in result))
        return result

    def financial_fixture(self, b):
        e = expected_fixture()
        status, rows = self.request('POST', '/rest/v1/products', {
            'tenant_id': b['tenant'], 'name': 'owner-closure synthetic product',
            'price': e['price'], 'cost': e['cost'], 'stock': e['initial_stock'],
            'is_discount': False}, token=b['token'])
        self.record('existing_owner_rest_product_created', status == 201 and isinstance(rows, list)
                    and len(rows) == 1, status=status)
        product = rows[0]['id']
        payload = {'p_customer_id': None, 'p_delivery': 'direct', 'p_courier_id': None,
                   'p_paid': e['paid'], 'p_method': 'cash',
                   'p_items': [{'productId': product, 'qty': e['quantity']}]}
        status, result = self.request('POST', '/rest/v1/rpc/create_sale_with_items', payload,
                                      token=b['token'])
        self.record('approved_sale_rpc_succeeded', status == 200 and isinstance(result, dict)
                    and result.get('success') is True and isinstance(result.get('order_id'), str), status=status)
        order = result['order_id']
        stored = self.query("""select jsonb_build_object(
          'product',(select to_jsonb(p) from public.products p where id='%s'),
          'order',(select to_jsonb(o) from public.orders o where id='%s'),
          'items',(select jsonb_agg(to_jsonb(i) order by id) from public.order_items i where order_id='%s'),
          'payments',(select jsonb_agg(to_jsonb(p) order by id) from public.payments p where order_id='%s'),
          'audit',(select jsonb_agg(to_jsonb(a) order by id) from public.financial_audit_log a where tenant_id='%s'),
          'counter',(select to_jsonb(c) from public.tenant_counters c where tenant_id='%s'));"""
          % (product, order, order, order, b['tenant'], b['tenant']))
        p, o, items, payments, audit = [stored[k] for k in ('product', 'order', 'items', 'payments', 'audit')]
        self.record('independent_product_values', p['price'] == e['price'] and p['cost'] == e['cost']
                    and p['stock'] == e['stock'] and p['tenant_id'] == b['tenant'])
        self.record('independent_direct_cash_order', o['total'] == e['total'] and o['paid'] == e['paid']
                    and o['status'] == 'paid' and o['delivery'] == 'direct' and o['created_by'] == b['uid']
                    and o['tenant_id'] == b['tenant'] and o['customer_id'] is None
                    and o['courier_id'] is None and o['collected_by_courier'] == 0)
        self.record('independent_item_values_and_links', len(items) == 1 and items[0]['product_id'] == product
                    and items[0]['qty'] == e['quantity'] and items[0]['unit_price'] == e['price']
                    and items[0]['unit_cost'] == e['cost'] and items[0]['tenant_id'] == b['tenant'])
        self.record('independent_payment_values_and_links', len(payments) == 1
                    and payments[0]['amount'] == e['paid'] and payments[0]['kind'] == 'sale'
                    and payments[0]['method'] == 'cash' and payments[0]['created_by'] == b['uid']
                    and payments[0]['tenant_id'] == b['tenant'])
        self.record('nonempty_actor_linked_financial_audit', isinstance(audit, list) and len(audit) == 1
                    and audit[0]['user_id'] == b['uid'] and audit[0]['entity_type'] == 'payments'
                    and audit[0]['entity_id'] == payments[0]['id'] and audit[0]['action'] == 'INSERT')
        self.record('counter_present_at_real_baseline', isinstance(stored['counter'], dict)
                    and stored['counter']['tenant_id'] == b['tenant'])
        (self.evidence_dir / 'financial-fixture.json').write_text(json.dumps(
            {'expected_independent': e, 'stored': stored, 'creation_surfaces':
             ['existing owner REST/RLS product insert', 'create_sale_with_items', 'existing payment audit trigger']},
            indent=2) + '\n')
        return payload, product, order

    def active_controls(self, a, b, phase):
        for label, actor in [('A', a), ('B', b)]:
            status, user = self.request('GET', '/auth/v1/user', token=actor['token'])
            self.record(phase + '_' + label + '_provider_valid', status == 200 and user.get('id') == actor['uid'])
            status, rows = self.own_rows(actor, 'tenants')
            self.record(phase + '_' + label + '_own_tenant', status == 200 and len(rows) == 1
                        and rows[0]['id'] == actor['tenant'])
            status, summary = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=actor['token'])
            self.record(phase + '_' + label + '_summary_rpc', status == 200 and isinstance(summary, dict)
                        and 'sales' in summary)
            self.initialize(actor, phase + '_' + label)
            for name in TOOLS:
                status, body = self.invoke(name, actor)
                success = tool_success(status, body, name)
                if label == 'B' and name in ('list_products', 'list_recent_orders'):
                    success = success and len(body['result']['structuredContent'][TOOLS[name]]) == 1
                self.record(phase + '_' + label + '_' + name, success, status=status)

    def marker(self):
        return self.query("select coalesce(jsonb_agg(to_jsonb(c) order by user_id),'[]'::jsonb) "
                          "from monjez_private.owner_account_closures c;")

    def closure_catalog(self):
        result = self.query("""select jsonb_build_object(
          'marker_rls',(select relrowsecurity from pg_class where oid='monjez_private.owner_account_closures'::regclass),
          'marker_client_rights',(select jsonb_agg(jsonb_build_object('role',r,'select',
            has_table_privilege(r,'monjez_private.owner_account_closures','SELECT'),'insert',
            has_table_privilege(r,'monjez_private.owner_account_closures','INSERT'),'update',
            has_table_privilege(r,'monjez_private.owner_account_closures','UPDATE'),'delete',
            has_table_privilege(r,'monjez_private.owner_account_closures','DELETE'),'truncate',
            has_table_privilege(r,'monjez_private.owner_account_closures','TRUNCATE')) order by r)
            from unnest(array['anon','authenticated','service_role']) r),
          'marker_fk',(select confdeltype::text from pg_constraint
            where conrelid='monjez_private.owner_account_closures'::regclass and contype='f'),
          'entry',(select jsonb_build_object('definer',prosecdef,'config',proconfig,'arguments',
             pg_get_function_identity_arguments(oid),'anon_execute',has_function_privilege('anon',oid,'EXECUTE'),
             'authenticated_execute',has_function_privilege('authenticated',oid,'EXECUTE'),
             'service_execute',has_function_privilege('service_role',oid,'EXECUTE'))
             from pg_proc where oid='public.close_owner_account()'::regprocedure),
          'active_guard_acl',(select proacl::text from pg_proc where oid='monjez_private.actor_is_active()'::regprocedure));""")
        self.record('private_marker_rls_and_restrict_reference', result['marker_rls'] is True and result['marker_fk'] == 'r')
        self.record('private_marker_clients_no_dml', all(not any(v for k,v in row.items() if k != 'role')
                    for row in result['marker_client_rights']))
        entry = result['entry']
        self.record('exact_self_entry_acl_and_search_path', entry['definer'] is True
                    and entry['arguments'] == '' and entry['authenticated_execute'] is True
                    and entry['anon_execute'] is False and entry['service_execute'] is False
                    and entry['config'] == ['search_path=""'])
        previous = json.loads(Path('changes/owner-retention-verify/evidence/native-9a5a/catalog.json').read_text())
        acl = next(x['acl'] for x in previous['functions'] if x['name'] == 'monjez_private.actor_is_active')
        self.record('existing_active_guard_acl_preserved', result['active_guard_acl'] == acl)
        (self.evidence_dir / 'closure-catalog.json').write_text(json.dumps(result, indent=2) + '\n')

    def negative_requests(self, a, b, staff):
        before = self.state_snapshot()
        for label, actor, payload in [('foreign_target', a, {'target_user_id': b['uid']}),
                                      ('malformed_parameter', b, {'confirmation': {'invalid': True}})]:
            status, body = self.request('POST', RPC, payload, token=actor['token'])
            self.record(label + '_rejected_by_exact_signature', status == 404 and body.get('code') == 'PGRST202')
        status, body = self.request('POST', RPC, {}, token=staff['token'])
        self.record('staff_cannot_close', status == 403 and body.get('code') == '42501'
                    and body.get('message') == 'owner_required')
        status, body = self.request('POST', RPC, {})
        self.record('unauthenticated_cannot_close', status in (401, 403) and body.get('code') == '42501')
        self.record('negative_requests_no_public_or_identity_effect', self.state_snapshot() == before)
        self.record('negative_requests_no_marker', self.marker() == [])

    def actor_sql(self, uid, query):
        uid = str(__import__('uuid').UUID(uid))
        return self.sql("begin; set local role authenticated; select set_config('request.jwt.claims',"
                        "'{\"sub\":\"" + uid + "\",\"role\":\"authenticated\"}',true); "
                        + query + '; rollback;').splitlines()[-1]

    def closed_controls(self, a, b, sale_payload, before):
        old_token = b['token']
        old_digest = hashlib.sha256(old_token.encode()).hexdigest()
        status, body = self.request('POST', RPC, {}, token=old_token)
        self.record('real_self_closure_success', status == 200 and body == {'status': 'closed'})
        marker = self.marker()
        self.record('one_private_closure_event', len(marker) == 1 and marker[0]['user_id'] == b['uid']
                    and bool(marker[0]['closed_at']))
        self.record('closure_only_private_delta', self.state_snapshot() == before)
        self.record('closed_live_predicate_false', self.actor_sql(b['uid'],
                    'select monjez_private.actor_is_active()::text') == 'false')
        self.record('active_control_live_predicate_true', self.actor_sql(a['uid'],
                    'select monjez_private.actor_is_active()::text') == 'true')
        original = copy.deepcopy(b)
        # Genuine new OAuth authorization/PKCE on the retained Auth identity.
        fresh = copy.deepcopy(b)
        fresh['token'] = fresh['session_token']
        self.oauth_token(fresh, 'B_after_closure', self.client_id)
        self.record('new_provider_token_distinct', fresh['token'] != old_token)
        for label, actor in [('old', original), ('new', fresh)]:
            token_claims = claims(actor['token'])
            self.record(label + '_jwt_unexpired_expected_identity', token_claims['sub'] == b['uid']
                        and token_claims['exp'] > time.time() and token_claims['iss'] == self.base + '/auth/v1')
            status, user = self.request('GET', '/auth/v1/user', token=actor['token'])
            self.record(label + '_retained_provider_identity_valid', status == 200 and user.get('id') == b['uid'])
            for name in ('current_tenant_id', 'get_tenant_today_estimate', 'create_sale_with_items'):
                status, body = self.request('POST', '/rest/v1/rpc/' + name,
                    sale_payload if name == 'create_sale_with_items' else {}, token=actor['token'])
                self.record(label + '_explicit_rpc_denial_' + name, explicit_inactive(status, body), status=status)
            for table in ('tenants', 'profiles', 'user_roles', 'products', 'orders', 'order_items',
                          'payments', 'financial_audit_log'):
                status, body = self.request('GET', '/rest/v1/' + table + '?select=*', token=actor['token'])
                # Empty rows alone never suffice: exact token/provider success and
                # named live RPC denial are established immediately before this read.
                self.record(label + '_rest_denial_' + table,
                    explicit_inactive(status, body) or (status == 200 and body == []), status=status,
                    corroborating_guard='named RPC 42501/account_inactive plus false live predicate')
            self.initialize(actor, 'closed_' + label)
            for name in TOOLS:
                status, body = self.invoke(name, actor)
                self.record(label + '_full_route_denial_' + name, account_tool_denial(status, body, name), status=status)
            status, body = self.request('POST', RPC, {}, token=actor['token'])
            self.record(label + '_narrow_idempotent_repeat', status == 200 and body == {'status': 'closed'})
            self.record(label + '_repeat_no_extra_event_or_history', self.marker() == marker
                        and self.state_snapshot() == before)
            for table, payload in [('profiles', {'display_name': 'reopen-attempt'}),
                                   ('tenants', {'owner_user_id': a['uid']})]:
                key, value = ('id', b['uid']) if table == 'profiles' else ('id', b['tenant'])
                status, body = self.request('PATCH', '/rest/v1/' + table + '?' + key + '=eq.' + value,
                                            payload, token=actor['token'])
                self.record(label + '_generic_write_cannot_reopen_' + table,
                            explicit_inactive(status, body) or (status == 200 and body == []), status=status)
            self.record(label + '_generic_writes_no_effect', self.marker() == marker
                        and self.state_snapshot() == before)
        self.record('exact_old_token_unchanged', hashlib.sha256(b['token'].encode()).hexdigest() == old_digest)
        # Private marker access is denied even to a still-active authenticated actor.
        permission = self.actor_sql(a['uid'], """do $t$ begin
          begin update monjez_private.owner_account_closures set closed_at=closed_at;
            raise exception 'marker_write_unexpectedly_allowed';
          exception when insufficient_privilege then raise notice 'MARKER_WRITE_DENIED'; end;
          end $t$; select 'private_denial_test_completed'""")
        self.record('private_marker_no_generic_authenticated_write', permission == 'private_denial_test_completed')
        # Repeat exception cannot override independent provider account invalidation.
        for field, value in [('banned_until', "statement_timestamp()+interval '1 day'"),
                             ('deleted_at', 'statement_timestamp()')]:
            uid = str(__import__('uuid').UUID(b['uid']))
            response = self.sql("begin; update auth.users set " + field + '=' + value + " where id='" + uid
                + "'; set local role authenticated; select set_config('request.jwt.claims',"
                + "'{\"sub\":\"" + uid + "\",\"role\":\"authenticated\"}',true); "
                + "do $t$ begin begin perform public.close_owner_account(); raise exception 'unexpected_repeat_allow';"
                  " exception when insufficient_privilege then if sqlerrm<>'account_inactive' then raise; end if; end;"
                  " end $t$; select 'inactive_repeat_denied'; rollback;").splitlines()[-1]
            self.record('repeat_does_not_override_' + field, response == 'inactive_repeat_denied')
        self.record('metadata_negative_transactions_rolled_back', self.state_snapshot() == before)
        self.initialize(a, 'A_unaffected_after_B_negatives')
        for name in TOOLS:
            status, body = self.invoke(name, a)
            self.record('A_unaffected_' + name, tool_success(status, body, name), status=status)
        status, rows = self.own_rows(a, 'tenants')
        self.record('A_unaffected_own_tenant', status == 200 and len(rows) == 1 and rows[0]['id'] == a['tenant'])
        status, summary = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=a['token'])
        self.record('A_unaffected_summary_rpc', status == 200 and isinstance(summary, dict) and 'sales' in summary)
        self.record('all_public_rows_and_identity_links_retained', self.state_snapshot() == before)
        self.record('one_immutable_closure_event_at_finish', self.marker() == marker)
        return {'marker': marker, 'old_token_sha256': old_digest,
                'old_expiry': claims(old_token)['exp'], 'new_expiry': claims(fresh['token'])['exp']}

    def run_closure(self, mode):
        self.mode = mode
        self.record('initial_empty_synthetic_stack', all(x == 0 for x in self.counts().values()))
        versions = self.query("select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;")
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        manifest = json.loads(Path('changes/owner-closure-implement-01/SOURCE_EVIDENCE.json').read_text())
        immutable = [x for x in manifest['verified_source_files']
                     if x['path'].startswith('supabase/migrations/')]
        self.record('all44_prior_migration_bytes_immutable', len(immutable) == 44 and all(
            hashlib.sha1(b'blob ' + str(len(Path(x['path']).read_bytes())).encode() + b'\0'
                         + Path(x['path']).read_bytes()).hexdigest() == x['git_blob_sha'] for x in immutable))
        expected = [p.name.split('_')[0] for p in files if not (mode in ('baseline', 'upgrade')
                     and p.name.endswith('_owner_closure_01.sql'))]
        self.record('initial_exact_migration_chain', versions == expected
                    and len(versions) == (45 if mode == 'fresh' else 44))
        indexes = self.index_inventory()
        self.no_truncate()
        a, b = self.fixture('closure_A'), self.fixture('closure_B')
        staff = self.fixture('closure_staff', tenant=a['tenant'], staff=True)
        self.secrets = [self.anon, self.admin] + [x[k] for x in (a, b, staff)
                       for k in ('password', 'token', 'refresh')]
        sale, product, order = self.financial_fixture(b)
        status, client = self.request('POST', '/auth/v1/admin/oauth/clients', {
            'redirect_uris': ['http://127.0.0.1:54325/test-oauth-callback'],
            'client_type': 'public', 'token_endpoint_auth_method': 'none',
            'grant_types': ['authorization_code', 'refresh_token'], 'client_name': 'isolated-owner-closure'}, admin=True)
        self.record('genuine_local_oauth_client', status == 201 and isinstance(client.get('client_id'), str))
        self.client_id = client['client_id']
        for label, actor in [('A', a), ('B', b)]:
            self.oauth_token(actor, 'closure_' + label, self.client_id)
            self.secrets.append(actor['token'])
        before = self.state_snapshot()
        result = {'source_sha': self.source, 'mode': mode, 'baseline': before,
                  'tenant_indexes': indexes, 'closure_verified': False, 'integration_accepted': False}
        try:
            self.start()
            self.active_controls(a, b, 'before')
            status, body = self.request('POST', RPC, {}, token=b['token']) if mode != 'fresh' else (None, None)
            if mode in ('baseline', 'upgrade'):
                self.record('named_missing_closure_expected_red', status == 404 and body.get('code') == 'PGRST202')
                self.record('expected_red_does_not_mutate_fixture', self.state_snapshot() == before)
            if mode == 'upgrade':
                stack = Path(os.environ['RUNNER_TEMP']) / 'monjez-tanstack-route'
                migration = list(Path('supabase/migrations').glob('*_owner_closure_01.sql'))
                self.record('one_new_migration_only', len(migration) == 1)
                __import__('shutil').copy2(migration[0], stack / 'supabase/migrations' / migration[0].name)
                log = Path(os.environ['RUNNER_TEMP']) / 'closure-upgrade-private.log'
                with log.open('w') as output:
                    code = subprocess.run(['supabase', '--workdir', str(stack), 'migration', 'up', '--local'],
                                          stdout=output, stderr=output).returncode
                self.record('populated44_to45_upgrade', code == 0)
                self.record('upgrade_preserves_populated_baseline', self.state_snapshot() == before)
                # PostgreSQL NOTIFY reload is asynchronous; retries here are discovery only.
                for _ in range(40):
                    if self.sql("select count(*) from pg_proc where proname='close_owner_account';") == '1':
                        time.sleep(.5)
                        break
                    time.sleep(.1)
            if mode != 'baseline':
                for _ in range(40):
                    status, body = self.request('POST', RPC, {}, token=staff['token'])
                    if status != 404 or body.get('code') != 'PGRST202':
                        break
                    time.sleep(.25)
                self.record('postgrest_new_entry_ready_staff_denied', status == 403
                            and body.get('code') == '42501' and body.get('message') == 'owner_required')
                self.closure_catalog()
                self.negative_requests(a, b, staff)
                result.update(self.closed_controls(a, b, sale, before))
                self.no_truncate()
            else:
                result['outcome'] = 'OWNER_CLOSURE_EXPECTED_RED_MISSING_ENTRY'
            self.firewall_after('app')
            result['after'] = self.state_snapshot()
            result['checks'] = self.controls
            result['process_containment'] = self.state()
            result['firewall'] = self.firewall_observations
            result['migration_versions'] = self.query("select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;")
            self.record('exact_final_migration_chain', result['migration_versions'] ==
                        [p.name.split('_')[0] for p in files] and len(files) == (44 if mode == 'baseline' else 45))
            result['closure_verified'] = mode != 'baseline'
            result['migration_sha256'] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in files}
            result['not_verified'] = ['concurrency/in-flight operations', 'Cloudflare/production',
                'broader financial contracts', 'provider sign-in blocking', 'retention duration/erasure',
                'full provider-service egress audit', 'release acceptance']
            result['not_verified'].append('same-tenant staff access continuity after owner closure')
            self.record('tracked_source_unchanged', subprocess.run(['git','diff','--quiet','HEAD','--']).returncode == 0)
            result['checks'] = self.controls
            result = publish_result(self.evidence_dir, result, self.secrets + self.oauth_refresh_tokens)
            # Reuse quarantine logic, rename result rather than altering shared harness.
            (self.evidence_dir / 'route-result.json').rename(self.evidence_dir / 'closure-result.json')
            if not result.get('evidence_no_credentials'):
                raise HarnessFailure('closure evidence quarantined')
            print(json.dumps({'mode': mode, 'checks': len(self.controls),
                              'closure_verified': result['closure_verified'], 'source_sha': self.source}))
        finally:
            self.stop()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--status-file', type=Path, required=True)
    parser.add_argument('--evidence-dir', type=Path, required=True)
    parser.add_argument('--expected-source', required=True)
    parser.add_argument('--mode', choices=['baseline', 'fresh', 'upgrade'], required=True)
    args = parser.parse_args()
    try:
        probe = ClosureProbe(args.status_file, args.evidence_dir, args.expected_source)
        probe.run_closure(args.mode)
    except (HarnessFailure, ValueError, KeyError, TypeError, subprocess.SubprocessError) as error:
        args.evidence_dir.mkdir(exist_ok=True)
        safe = {'source_sha': args.expected_source, 'mode': args.mode, 'closure_verified': False,
                'integration_accepted': False, 'failure_type': type(error).__name__}
        if isinstance(error, HarnessFailure):
            safe['reason'] = str(error)
        (args.evidence_dir / 'closure-failure.json').write_text(json.dumps(safe, indent=2) + '\n')
        print(json.dumps(safe))
        raise SystemExit(2)
