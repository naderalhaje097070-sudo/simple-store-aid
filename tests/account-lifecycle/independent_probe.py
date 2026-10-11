"""Reviewer-owned, loopback-only replay with independently defined expectations.

Shares transport, source/target safety and fixture plumbing, not the implementer's
result oracle. Auth keys and JWTs stay in memory; all output contains booleans,
dummy fixture counts and stored-row digests only. No financial writes or hard delete.
"""
import argparse
import base64
import binascii
import hashlib
import hmac
import json
from pathlib import Path
import subprocess
import time

from correction_probe import CorrectionProbe, HarnessFailure, FINANCE_TABLES

SUCCESS = 'ENV_NATIVE_01_INDEPENDENT_REPLAY_GREEN'


def encoded(raw):
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def decoded(value):
    return base64.b64decode(value + '=' * (-len(value) % 4), altchars=b'-_', validate=True)


def signed_twins(token, secret, expected_uid, clock):
    """Verify real local Auth signature before changing only its expiry claim."""
    if not isinstance(secret, str) or len(secret) < 32:
        raise HarnessFailure('independent local JWT secret unavailable')
    try:
        head, body, signature = token.split('.')
        header, claims = json.loads(decoded(head)), json.loads(decoded(body))
        actual = decoded(signature)
    except (ValueError, TypeError, binascii.Error, json.JSONDecodeError) as exc:
        raise HarnessFailure('independent issued JWT shape') from exc
    if not isinstance(header, dict) or header.get('alg') != 'HS256':
        raise HarnessFailure('independent issued JWT algorithm unsupported')
    expected = hmac.new(secret.encode(), (head + '.' + body).encode('ascii'), hashlib.sha256).digest()
    if not hmac.compare_digest(actual, expected):
        raise HarnessFailure('independent issued JWT signature mismatch')
    if (not isinstance(claims, dict) or claims.get('sub') != expected_uid
            or claims.get('role') != 'authenticated' or type(claims.get('exp')) is not int
            or claims['exp'] <= clock):
        raise HarnessFailure('independent issued JWT identity or expiry mismatch')

    def twin(expiry):
        payload = encoded(json.dumps(dict(claims, exp=expiry), separators=(',', ':')).encode())
        unsigned = head + '.' + payload
        sig = hmac.new(secret.encode(), unsigned.encode('ascii'), hashlib.sha256).digest()
        return unsigned + '.' + encoded(sig)

    future, expired = twin(clock + 600), twin(clock - 300)
    head, body, signature = future.split('.')
    invalid = bytearray(decoded(signature)); invalid[0] ^= 1
    return future, expired, head + '.' + body + '.' + encoded(bytes(invalid))


def account_denial(status, body):
    return status == 403 and isinstance(body, dict) and body.get('code') == '42501' and body.get('message') == 'account_inactive'


def metadata_denial(status, body):
    # A valid old JWT must reach the account gate or yield empty RLS rows.
    # Expired/invalid JWT errors do NOT prove lifecycle enforcement.
    return (status == 200 and body == []) or account_denial(status, body)


def foreign_denial(status, body):
    # Active callers reach existing tenant policies. WITH CHECK may report a
    # generic42501 rather than account_inactive; trusted hashes prove no effect.
    return ((status == 200 and body == []) or
            (status == 403 and isinstance(body, dict) and body.get('code') == '42501'))


def expiry_denial(status, body):
    # PostgREST14.10 separates claims validation (303) from decoding (301).
    return (status == 401 and isinstance(body, dict) and body.get('code') == 'PGRST303'
            and body.get('message') == 'JWT expired')


def signature_denial(status, body):
    return (status == 401 and isinstance(body, dict) and body.get('code') == 'PGRST301'
            and body.get('message') == 'JWT cryptographic operation failed')


class IndependentProbe(CorrectionProbe):
    def control(self, name, passed, **details):
        if any(c['name'] == name for c in self.controls):
            raise HarnessFailure('duplicate independent assertion')
        self.controls.append({'name': name, 'passed': passed is True, **details})
        (self.evidence_dir / 'independent-progress.json').write_text(json.dumps(
            {'source_sha': self.source, 'checks': self.controls}, indent=2) + '\n')
        if passed is not True:
            raise HarnessFailure('independent assertion failed: ' + name)

    def snapshot(self, tables):
        return {table: self.query("select to_jsonb(md5(coalesce(jsonb_agg(to_jsonb(t) order by to_jsonb(t)::text)::text,'[]'))) from public." + table + ' t;') for table in tables}

    def direct_denial(self, actor):
        # Authenticated SQL role, no superuser/definer bypass; exact account error
        # or zero visible rows across each of the three previously exposed relations.
        self.sql(f'''begin; set local role authenticated;
        select set_config('request.jwt.claim.sub','{actor['uid']}',true) is not null;
        do $review$ declare n bigint; begin
          begin
            select (select count(*) from public.tenants where id='{actor['tenant']}'::uuid)
                 + (select count(*) from public.profiles where id='{actor['uid']}'::uuid)
                 + (select count(*) from public.user_roles where user_id='{actor['uid']}'::uuid)
              into n;
            if n <> 0 then raise exception 'independent SQL leaked rows'; end if;
          exception when insufficient_privilege then
            if SQLERRM <> 'account_inactive' then raise; end if;
          end;
        end $review$; rollback;''')
        return True

    def denied_actor(self, label, actor):
        for table in ('tenants', 'profiles', 'user_roles'):
            status, rows = self.own_rows(actor, table)
            self.control(label + '_old_jwt_' + table, metadata_denial(status, rows), status=status)
        status, body = self.request('POST', '/rest/v1/rpc/get_tenant_today_estimate', {}, token=actor['token'])
        self.control(label + '_old_jwt_summary', account_denial(status, body), status=status)
        self.control(label + '_authenticated_direct_sql', self.direct_denial(actor))

    def run_review(self):
        files = sorted(Path('supabase/migrations').glob('*.sql'))
        versions = self.query("select coalesce(jsonb_agg(version order by version),'[]'::jsonb) from supabase_migrations.schema_migrations;")
        self.control('independent_exact_final_43_migrations', len(files) == 43 and versions == [p.name.split('_')[0] for p in files])
        roles = self.query("select jsonb_build_object('current',current_user,'session',session_user,'role',current_setting('role',true));")
        self.control('independent_trusted_connection_boundary', roles == {'current': 'postgres', 'session': 'postgres', 'role': 'none'})
        initial = self.counts()
        self.control('independent_inherited_dummy_counts', {k: initial[k] for k in ('users','tenants','profiles','roles')} == {'users':4,'tenants':2,'profiles':4,'roles':4})
        self.control('independent_initial_financial_zero', all(initial[t] == 0 for t in FINANCE_TABLES))
        tables = self.query("select jsonb_agg(tablename order by tablename) from pg_tables where schemaname='public';")
        self.control('independent_exact_public_table_surface', isinstance(tables,list) and len(tables) == 22)

        deleted = self.fixture('review_deleted_owner')
        b = self.fixture('review_banned_owner')
        staff = self.fixture('review_banned_staff', b['tenant'], True)
        a = self.fixture('review_active_staff', deleted['tenant'], True)
        for label, actor in [('active',a),('owner',b),('staff',staff),('deleted',deleted)]:
            status, rows = self.own_rows(actor, 'tenants')
            self.control('independent_' + label + '_initial_own_tenant', status == 200 and isinstance(rows,list) and len(rows) == 1 and rows[0]['id'] == actor['tenant'], status=status)
            status, body = self.request('POST','/rest/v1/rpc/get_tenant_today_estimate',{},token=actor['token'])
            self.control('independent_' + label + '_initial_summary', status == 200 and isinstance(body,dict) and 'sales' in body, status=status)

        # Stored baseline precedes every malicious mutation; expected identities
        # are checked independently rather than only comparing arbitrary digests.
        before_foreign = self.snapshot(tables)
        expected = self.query("select jsonb_build_object('tenants',(select jsonb_object_agg(id,owner_user_id) from public.tenants),'profiles',(select jsonb_object_agg(id,tenant_id) from public.profiles));")
        self.control('independent_expected_stored_fixture_links', all(expected['tenants'][x['tenant']] == x['uid'] for x in (b,deleted)) and all(expected['profiles'][x['uid']] == x['tenant'] for x in (a,b,staff,deleted)))
        for label, actor in [('active',a),('owner',b),('staff',staff)]:
            foreign = b['tenant'] if actor['tenant'] == a['tenant'] else a['tenant']
            for method, payload in [('GET',None),('PATCH',{'name':'INDEPENDENT_FORBIDDEN'})]:
                status, body = self.request(method,'/rest/v1/tenants?id=eq.'+foreign,payload,token=actor['token'])
                self.control('independent_'+label+'_foreign_'+method, foreign_denial(status,body),status=status)
            status, body = self.request('PATCH','/rest/v1/profiles?id=eq.'+actor['uid'],{'tenant_id':foreign},token=actor['token'])
            self.control('independent_'+label+'_reassignment',foreign_denial(status,body),status=status)
        self.control('independent_foreign_mutations_stored_no_effect', self.snapshot(tables) == before_foreign)

        # Expiry is measured with a real signed token and signature negative
        # control, before disabling any of these independent actors.
        twins = signed_twins(a['token'], self.status.get('JWT_SECRET'), a['uid'], int(time.time()))
        self.control('independent_original_hs256_signature_verified', True)
        status, rows = self.request('GET','/rest/v1/tenants?id=eq.'+a['tenant'],token=twins[0])
        self.control('independent_future_signed_twin_active',status == 200 and isinstance(rows,list) and len(rows) == 1 and rows[0]['id'] == a['tenant'],status=status)
        for label, token, classifier in [('expired',twins[1],expiry_denial),('tampered',twins[2],signature_denial)]:
            status, body = self.request('GET','/rest/v1/tenants?id=eq.'+a['tenant'],token=token)
            self.control('independent_'+label+'_jwt_reason',classifier(status,body),status=status)

        # Delete a separate unbanned actor, keeping all public rows and IDs.
        self.control('independent_deleted_actor_initially_unbanned', self.sql(f"select (deleted_at is null and (banned_until is null or banned_until<=now()))::text from auth.users where id='{deleted['uid']}';") == 'true')
        before_lifecycle = self.snapshot(tables)
        status, _ = self.request('DELETE','/auth/v1/admin/users/'+deleted['uid'],{'should_soft_delete':True},admin=True)
        self.control('independent_auth_admin_soft_delete_succeeded',status == 200,status=status)
        self.control('independent_deleted_row_retained_without_ban', self.sql(f"select (deleted_at is not null and (banned_until is null or banned_until<=now()))::text from auth.users where id='{deleted['uid']}';") == 'true')
        self.control('independent_soft_delete_public_history_preserved',self.snapshot(tables) == before_lifecycle)
        self.denied_actor('independent_deleted',deleted)

        for label, actor in [('owner',b),('staff',staff)]:
            status, _ = self.request('PUT','/auth/v1/admin/users/'+actor['uid'],{'ban_duration':'24h'},admin=True)
            self.control('independent_'+label+'_auth_ban_saved',status == 200,status=status)
            self.control('independent_'+label+'_stored_live_ban', self.sql(f"select (deleted_at is null and banned_until>now())::text from auth.users where id='{actor['uid']}';") == 'true')
            self.denied_actor('independent_banned_'+label,actor)
        status, rows = self.own_rows(a,'tenants')
        self.control('independent_unaffected_active_tenant',status == 200 and isinstance(rows,list) and len(rows) == 1 and rows[0]['id'] == a['tenant'],status=status)
        status, body = self.request('POST','/rest/v1/rpc/get_tenant_today_estimate',{},token=a['token'])
        self.control('independent_unaffected_active_summary',status == 200 and isinstance(body,dict) and 'sales' in body,status=status)
        self.control('independent_lifecycle_public_history_preserved',self.snapshot(tables) == before_lifecycle)
        final = self.counts()
        self.control('independent_final_financial_zero',all(final[t] == 0 for t in FINANCE_TABLES))
        self.control('independent_exact_final_dummy_counts',{k:final[k] for k in ('users','tenants','profiles','roles')} == {'users':8,'tenants':4,'profiles':8,'roles':8})
        self.control('independent_tracked_source_unchanged',subprocess.run(['git','diff','--quiet','HEAD','--']).returncode == 0)
        result = {'outcome':SUCCESS,'source_sha':self.source,'reviewer_owned_oracle':True,'checks':self.controls,'migration_versions':versions,'initial_counts':initial,'final_counts':final,'history_before':before_lifecycle,'history_after':self.snapshot(tables),'integration_accepted':False,'missing_coverage':['MCP transport','nonempty financial history','active financial writes','concurrent/in-flight transactions','production-scale performance','hard-delete cascade/history semantics','naturally elapsed Auth-issued token; expiry twins are locally minted from verified issued claims']}
        (self.evidence_dir/'independent-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps({'outcome':SUCCESS,'checks_passed':len(self.controls),'integration_accepted':False}))


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--status-file',type=Path,required=True)
    p.add_argument('--evidence-dir',type=Path,required=True)
    p.add_argument('--expected-source',required=True)
    args = p.parse_args()
    try:
        IndependentProbe(args.status_file,args.evidence_dir,args.expected_source).run_review()
    except (HarnessFailure,OSError,ValueError,subprocess.SubprocessError) as error:
        args.evidence_dir.mkdir(parents=True,exist_ok=True)
        reason = str(error) if isinstance(error,HarnessFailure) else 'independent local harness failure'
        (args.evidence_dir/'independent-failure.json').write_text(json.dumps({'outcome':'ENV_NATIVE_01_INDEPENDENT_REPLAY_FAILURE','reason':reason,'integration_accepted':False})+'\n')
        print('ENV_NATIVE_01_INDEPENDENT_REPLAY_FAILURE: '+reason)
        raise SystemExit(2)
