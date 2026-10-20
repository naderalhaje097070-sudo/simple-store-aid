"""AC-01: disposable full-chain scanner authorization; no financial writes."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from live_probe import Probe, HarnessFailure
from write_harness_guard import _psql_command, _psql_env

ROOT = Path(__file__).resolve().parents[2]


def explicit_denial(status, body, message=None):
    return (status in (401, 403) and isinstance(body, dict)
            and body.get('code') == '42501'
            and (message is None or body.get('message') == message))


class ScannerProbe(Probe):
    def snapshot(self):
        names = self.query("select jsonb_agg(tablename order by tablename) from pg_tables where schemaname='public';")
        if not names or any(not re.fullmatch('[a-z_]+', n) for n in names):
            raise HarnessFailure('public inventory invalid')
        result = {}
        for name in names:
            result[name] = self.query("select jsonb_build_object('count',count(*),'digest',md5(coalesce("
                "string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),''))) from public." + name + ' t;')
        result['private_closures'] = self.query("select jsonb_build_object('count',count(*),'digest',"
            "md5(coalesce(string_agg(to_jsonb(t)::text,'' order by to_jsonb(t)::text),''))) "
            "from monjez_private.owner_account_closures t;")
        return result

    def catalog(self):
        return self.query("""select jsonb_build_object(
          'scanner',(select jsonb_build_object('oid',p.oid,'owner',pg_get_userbyid(p.proowner),
            'acl',p.proacl,'args',pg_get_function_arguments(p.oid),'returns',pg_get_function_result(p.oid),
            'definer',p.prosecdef,'settings',p.proconfig,'body',p.prosrc)
            from pg_proc p where p.oid='public.run_security_scan(text)'::regprocedure),
          'other_functions',(select md5(string_agg(pg_get_functiondef(p.oid),'' order by n.nspname,p.proname,p.oid))
            from pg_proc p join pg_namespace n on n.oid=p.pronamespace
            where n.nspname in ('public','monjez_private') and p.prokind='f'
              and p.oid<>'public.run_security_scan(text)'::regprocedure),
          'relations',(select md5(string_agg(jsonb_build_object('name',c.oid::regclass::text,
            'owner',c.relowner,'acl',c.relacl,'rls',c.relrowsecurity,'force_rls',c.relforcerowsecurity)::text,'' order by c.oid))
            from pg_class c join pg_namespace n on n.oid=c.relnamespace
            where n.nspname in ('public','monjez_private') and c.relkind in ('r','p')),
          'policies',(select md5(coalesce(string_agg(row_to_json(p)::text,'' order by p.oid),'')) from pg_policy p),
          'cron',(select jsonb_agg(jsonb_build_object('name',jobname,'schedule',schedule,'command',command,
            'username',username,'active',active) order by jobname) from cron.job),
          'execute',(select jsonb_object_agg(r,has_function_privilege(r,'public.run_security_scan(text)','EXECUTE'))
            from unnest(array['anon','authenticated','service_role']) r),
          'public_execute',(select exists(select 1 from pg_proc p,
            lateral aclexplode(coalesce(p.proacl,acldefault('f',p.proowner))) a
            where p.oid='public.run_security_scan(text)'::regprocedure and a.grantee=0 and a.privilege_type='EXECUTE'))
        );""")

    def scan(self, actor=None, service=False, trigger='manual'):
        return self.request('POST', '/rest/v1/rpc/run_security_scan',
                            {'p_triggered_by': trigger}, token=actor['token'] if actor else None, admin=service)

    def positive(self, name, actor=None, service=False):
        before = self.snapshot()
        code, body = self.scan(actor, service)
        self.control(name, code == 200 and isinstance(body, dict)
                     and set(body) == {'run_id', 'new_count', 'total_count'}, status=code)
        rows = self.query("select jsonb_build_object('status',status,'trigger',triggered_by) "
                          "from public.security_scan_runs where id='" + str(__import__('uuid').UUID(body['run_id'])) + "';")
        self.control(name + '_durable_success', rows == {'status': 'success', 'trigger': 'manual'})
        after = self.snapshot()
        self.control(name + '_only_scanner_data_changed',
            all(after[k] == v for k, v in before.items() if k not in ('security_scan_runs', 'security_scan_findings')))

    def deny(self, name, actor, admin_control, message='forbidden_platform_admin', trigger='manual'):
        before = self.snapshot()
        code, body = self.scan(actor, trigger=trigger)
        self.control(name, explicit_denial(code, body, message), status=code, sqlstate=body.get('code') if isinstance(body, dict) else None)
        self.control(name + '_all_data_unchanged', self.snapshot() == before)
        code, rows = self.own_rows(admin_control, 'tenants')
        self.control(name + '_unaffected_positive', code == 200 and len(rows) == 1, status=code)

    def seed(self):
        self.control('empty_financial_fixture', all(self.counts()[t] == 0 for t in
            ('orders', 'order_items', 'products', 'customers', 'payments', 'expenses', 'day_closes')))
        a = self.fixture('ordinary_owner_A')
        admin = self.fixture('platform_admin_B')
        staff_a = self.fixture('employee_A', a['tenant'], True)
        staff_b = self.fixture('employee_B', admin['tenant'], True)
        banned = self.fixture('future_banned_admin')
        closed = self.fixture('future_closed_admin')
        for actor in (admin, banned, closed):
            self.sql("insert into public.platform_admins(user_id,note) values ('" + actor['uid'] + "','AC01 disposable fixture');")
        code, body = self.request('PUT', '/auth/v1/admin/users/' + a['uid'],
            {'user_metadata': {'role': 'service_role', 'is_platform_admin': True}}, admin=True)
        self.control('untrusted_user_metadata_seeded', code == 200, status=code)
        code, session = self.request('POST', '/auth/v1/token?grant_type=password',
            {'email': a['email'], 'password': a['password']})
        self.control('metadata_actor_real_login', code == 200 and bool(session.get('access_token')), status=code)
        a['token'] = session['access_token']
        return {'ordinary': a, 'admin': admin, 'staff_a': staff_a, 'staff_b': staff_b, 'banned': banned, 'closed': closed}

    def run(self, phase, state_file):
        files = sorted((ROOT / 'supabase/migrations').glob('*.sql'))
        self.control('expected46_source_migrations', len(files) == 46)
        versions = self.query("select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;")
        expected = files[:-1] if phase == 'before' else files
        self.control('exact_applied_chain_' + phase, versions == [p.name.split('_')[0] for p in expected])
        if phase == 'before' or not state_file.exists():
            actors = self.seed()
        else:
            saved = json.loads(state_file.read_text())
            self.control('populated_upgrade_all_data_preserved', self.snapshot() == saved['snapshot'])
            old, current = saved['catalog'], self.catalog()
            self.control('only_scanner_body_and_search_path_changed',
                {k:v for k,v in old.items() if k != 'scanner'} == {k:v for k,v in current.items() if k != 'scanner'}
                and {k:v for k,v in old['scanner'].items() if k not in ('body','settings')} ==
                    {k:v for k,v in current['scanner'].items() if k not in ('body','settings')})
            actors = saved['actors']
        admin = actors['admin']
        self.positive(phase + '_active_admin_positive', admin)
        self.positive(phase + '_service_positive', service=True)
        if phase == 'before':
            before = self.snapshot()
            code, body = self.scan(actors['ordinary'], trigger='cron')
            after = self.snapshot()
            self.control('AC01_BASELINE_UNAUTHORIZED_SCAN_REPRODUCED', code == 200 and isinstance(body, dict)
                and after['security_scan_runs']['count'] == before['security_scan_runs']['count'] + 1, status=code,
                expected_denial_assertion=False)
            self.control('baseline_denial_assertion_is_red', not explicit_denial(code, body, 'forbidden_platform_admin'))
            state_file.write_text(json.dumps({'actors': actors, 'snapshot': after, 'catalog': self.catalog()}))
            state_file.chmod(0o600)
        else:
            catalog = self.catalog()
            self.control('execute_acl_preserved_and_not_public', catalog['execute'] ==
                {'anon': False, 'authenticated': True, 'service_role': True} and catalog['public_execute'] is False)
            self.control('scanner_stays_definer_with_safe_path', catalog['scanner']['definer'] is True
                and catalog['scanner']['settings'] == ['search_path=pg_catalog, pg_temp'])
            payload = (ROOT / 'changes/b2-ac01/SCANNER_AUTH.sql').read_text().split('$function$')[1]
            self.control('actual_function_matches_reviewed_body', catalog['scanner']['body'] == payload)
            for label in ('ordinary', 'staff_a', 'staff_b'):
                self.deny(label + '_denied', actors[label], admin)
            self.deny('trigger_cron_spoof_denied', actors['ordinary'], admin, trigger='cron')
            self.deny('trigger_service_spoof_denied', actors['ordinary'], admin, trigger='service_role')
            self.deny('anonymous_denied', None, admin, message=None)
            before = self.snapshot()
            claims = json.dumps({'sub': actors['ordinary']['uid'], 'role': 'service_role',
                                 'user_metadata': {'is_platform_admin': True}})
            sql = "BEGIN; SET LOCAL ROLE authenticated; SELECT set_config('request.jwt.claims','" + claims + "',true); SELECT public.run_security_scan('cron'); ROLLBACK;"
            r = subprocess.run(_psql_command(self.config, '-Atq', '-v', 'ON_ERROR_STOP=1', '-v', 'VERBOSITY=verbose'),
                input=sql, capture_output=True, text=True, env=_psql_env(self.config), timeout=30)
            self.control('jwt_claim_cannot_override_invoker_role', r.returncode != 0
                and '42501' in r.stderr and 'forbidden_platform_admin' in r.stderr)
            self.control('sql_denial_all_data_unchanged', self.snapshot() == before)
            self.positive('banned_admin_before_ban_positive', actors['banned'])
            code, _ = self.request('PUT', '/auth/v1/admin/users/' + actors['banned']['uid'],
                                   {'ban_duration': '24h'}, admin=True)
            self.control('ban_transition_confirmed', code == 200, status=code)
            self.deny('banned_admin_old_jwt_denied', actors['banned'], admin, message='account_inactive')
            self.positive('closed_admin_before_closure_positive', actors['closed'])
            code, body = self.request('POST', '/rest/v1/rpc/close_owner_account', {}, token=actors['closed']['token'])
            self.control('real_owner_closure_confirmed', code == 200 and body == {'status':'closed'}, status=code)
            self.deny('closed_admin_old_jwt_denied', actors['closed'], admin, message='account_inactive')
            self.positive('admin_after_denials_positive', admin)
            self.positive('service_after_denials_positive', service=True)
            cron = [r for r in catalog['cron'] if r['name'] == 'mongezz-weekly-security-scan']
            self.control('cron_schedule_and_sql_identity_preserved', len(cron) == 1 and cron[0]['username'] == 'postgres'
                and cron[0]['command'].strip() == "SELECT public.run_security_scan('cron');")
            before = self.snapshot()
            cron_result = self.query("select public.run_security_scan('cron');")
            after = self.snapshot()
            self.control('actual_trusted_sql_cron_identity_positive', isinstance(cron_result, dict)
                and after['security_scan_runs']['count'] == before['security_scan_runs']['count'] + 1)
            self.control('cron_only_scanner_data_changed', all(after[k] == v for k,v in before.items()
                if k not in ('security_scan_runs','security_scan_findings')))
        report = {'source': self.source, 'phase': phase, 'checks': self.controls,
                  'passed': len(self.controls), 'failed': 0, 'b2_runtime_accepted': phase == 'after',
                  'independent_review': 'pending', 'package_B_accepted': False,
                  'schema_versions': versions, 'all_data_fingerprints': self.snapshot(),
                  'scope': 'synthetic loopback scanner authorization; not B5 lifecycle acceptance'}
        serialized = json.dumps(report, indent=2) + '\n'
        for actor in actors.values():
            for key in ('token','refresh','password','email'):
                if actor.get(key) and actor[key] in serialized:
                    raise HarnessFailure('credential or unnecessary identity in evidence')
        if self.admin in serialized or self.anon in serialized:
            raise HarnessFailure('local key in evidence')
        (self.evidence_dir / ('scanner-' + phase + '.json')).write_text(serialized)
        (self.evidence_dir / ('catalog-' + phase + '.json')).write_text(json.dumps(self.catalog(), indent=2) + '\n')
        print('AC01_RECEIPT ' + json.dumps({k:v for k,v in report.items() if k not in ('checks','all_data_fingerprints')}))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--status-file', type=Path, required=True)
    p.add_argument('--evidence-dir', type=Path, required=True)
    p.add_argument('--private-state', type=Path, required=True)
    p.add_argument('--expected-source', required=True)
    p.add_argument('--phase', choices=('before','after'), required=True)
    a = p.parse_args()
    try:
        ScannerProbe(a.status_file, a.evidence_dir, a.expected_source).run(a.phase, a.private_state)
    except (HarnessFailure, ValueError, OSError, subprocess.SubprocessError) as error:
        a.evidence_dir.mkdir(parents=True, exist_ok=True)
        # Only controlled assertion names enter exception text; never export raw I/O.
        safe = str(error) if isinstance(error, HarnessFailure) else type(error).__name__
        (a.evidence_dir/'failure.json').write_text(json.dumps({'source': a.expected_source, 'phase': a.phase, 'failure': safe}))
        print('AC01_HARNESS_FAILURE: ' + safe)
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
