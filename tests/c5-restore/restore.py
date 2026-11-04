"""Logical restore on the exact disposable Docker database; no remote API or archive publication."""
import base64
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import uuid

CONTAINER = 'supabase_db_monjez-c5sale-stack'
TARGET = 'monjez_c5_restore'
PRIVATE = Path('/tmp/monjez-c5sale/private-state.json')
OUT = Path('/tmp/monjez-c5sale/evidence/restore-result.json')
ARCHIVE = Path('/tmp/monjez-c5-restore-private.dump')


def command(args, data=None):
    result = subprocess.run(args, input=data, capture_output=True, timeout=180)
    if result.returncode:
        raise RuntimeError('local_restore_command_failed:' + args[0])
    return result.stdout


def sql(database, statement, denied=None):
    assert database in ('postgres', TARGET)
    args = ['docker', 'exec', '-i', CONTAINER, 'psql', '-X', '-U', 'postgres', '-d', database,
            '-Atq', '-v', 'ON_ERROR_STOP=1']
    result = subprocess.run(args, input=statement.encode(), capture_output=True, timeout=90)
    if denied:
        assert result.returncode != 0 and denied.encode() in result.stderr
        return None
    if result.returncode:
        raise RuntimeError('local_restore_SQL_failed')
    return json.loads(result.stdout)


def rows(database):
    tables = sql(database, "select jsonb_agg(jsonb_build_array(schemaname,tablename) order by schemaname,tablename) from pg_tables where schemaname in ('public','monjez_private','auth','supabase_migrations');")
    result = {}
    for schema, table in tables:
        assert re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', schema)
        assert re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', table)
        result[schema + '.' + table] = sql(database, 'select jsonb_build_object(\'count\',count(*),\'digest\',md5(coalesce(string_agg(to_jsonb(t)::text,\'\' order by to_jsonb(t)::text),\'\'))) from "' + schema + '"."' + table + '" t;')
    return result


def catalog(database):
    return sql(database, """select jsonb_build_object(
      'functions',(select jsonb_agg(jsonb_build_array(n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),p.prosrc,p.prosecdef,p.proconfig,p.proacl::text,pg_get_userbyid(p.proowner)) order by n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('public','monjez_private')),
      'tables',(select jsonb_agg(jsonb_build_array(n.nspname,c.relname,c.relrowsecurity,c.relforcerowsecurity,c.relacl::text,pg_get_userbyid(c.relowner)) order by n.nspname,c.relname) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private') and c.relkind in ('r','p')),
      'policies',(select jsonb_agg(to_jsonb(p) order by schemaname,tablename,policyname) from pg_policies p where schemaname in ('public','monjez_private')));""")


def claims(actor):
    # Claims from the actual isolated Auth-issued token; this is a SQL role test,
    # not proof of JWT signature verification or a restored API deployment.
    part = actor['token'].split('.')[1]
    value = json.loads(base64.urlsafe_b64decode(part + '=' * (-len(part) % 4)))
    assert str(uuid.UUID(value['sub'])) == actor['uid']
    return json.dumps(value, separators=(',', ':')).replace("'", "''")


def rpc(actor, request, denied=None):
    key = str(uuid.UUID(request['key']))
    order = str(uuid.UUID(request['order_id']))
    amount = request['amount']
    assert isinstance(amount, (int, float)) and 0 < amount <= 100
    method = request['method']
    assert method in ('cash', 'transfer')
    return sql(TARGET, "begin; set local role authenticated; set local request.jwt.claims = '" + claims(actor) + "'; select public.collect_order_debt_idempotent('" + key + "','" + order + "'," + str(amount) + ",'" + method + "'); commit;", denied)


def main():
    checks = []
    def check(name, passed):
        checks.append({'name': name, 'passed': bool(passed)})
        if not passed:
            raise RuntimeError(name)
    source = command(['git', 'rev-parse', 'HEAD']).decode().strip()
    check('exact_source_and_isolation', source == os.environ['EXPECTED_SOURCE'] and os.environ.get('CI_ISOLATED_SUPABASE') == '1')
    check('tracked_source_clean', subprocess.run(['git','diff','--quiet','HEAD','--']).returncode == 0)
    check('fixed_local_container', command(['docker','inspect','--format','{{.Name}}',CONTAINER]).decode().strip() == '/' + CONTAINER)
    check('separate_target_absent', sql('postgres', "select count(*) from pg_database where datname='" + TARGET + "';") == 0)
    state = json.loads(PRIVATE.read_text())
    before, structure = rows('postgres'), catalog('postgres')
    check('nonempty_finance_and_auth', all(before[t]['count'] > 0 for t in ('public.orders','public.order_items','public.payments','public.financial_idempotency','public.products','auth.users')))
    sample = sql('postgres', "select jsonb_build_object('key',i.idempotency_key,'order_id',o.id,'amount',(i.request_payload->>'amount')::numeric,'method',i.request_payload->>'method','result',i.result,'actor',i.created_by,'paid',o.paid,'payments',(select count(*) from public.payments where order_id=o.id)) from public.financial_idempotency i join public.orders o on o.id=(i.request_payload->>'order_id')::uuid where i.operation='order.debt.collect.v1' and i.result is not null and o.total-o.paid>=20 order by i.created_at limit 1;")
    actor = next(a for a in state['actors'].values() if a['uid'] == sample['actor'])
    foreign = next(a for a in state['actors'].values() if a['tenant'] != actor['tenant'])
    archive = command(['docker','exec',CONTAINER,'pg_dump','-U','postgres','-d','postgres','-Fc'])
    check('nonempty_custom_archive', archive.startswith(b'PGDMP') and len(archive) > 1000)
    fd = os.open(ARCHIVE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(archive)
    digest = hashlib.sha256(archive).hexdigest()
    command(['docker','exec',CONTAINER,'createdb','-U','postgres','-T','template0',TARGET])
    command(['docker','exec','-i',CONTAINER,'pg_restore','-U','postgres','-d',TARGET,'--exit-on-error'], ARCHIVE.read_bytes())
    check('all_selected_relations_restored_exactly', rows(TARGET) == before)
    check('functions_RLS_policies_owners_ACLs_restored', catalog(TARGET) == structure)
    check('restored_original_key_returns_original_result', rpc(actor, sample) == sample['result'])
    check('restored_replay_changes_no_relation', rows(TARGET) == before)
    rpc(foreign, sample, 'forbidden_tenant')
    check('foreign_replay_atomic_denial', rows(TARGET) == before)
    altered = {**sample, 'amount': sample['amount'] + 1}
    rpc(actor, altered, 'idempotency_conflict')
    check('changed_payload_atomic_denial', rows(TARGET) == before)
    fresh = {**sample, 'key': str(uuid.uuid4()), 'amount': 20}
    rpc(actor, fresh)
    effect = sql(TARGET, "select jsonb_build_object('paid',paid,'payments',(select count(*) from public.payments where order_id=o.id)) from public.orders o where id='" + sample['order_id'] + "';")
    check('new_intentional_payment_after_restore', effect == {'paid': sample['paid'] + 20, 'payments': sample['payments'] + 1})
    check('original_database_unchanged', rows('postgres') == before and catalog('postgres') == structure)
    ARCHIVE.unlink()
    check('private_archive_removed', not ARCHIVE.exists())
    OUT.write_text(json.dumps({'source':source,'mode':os.environ['CONTRACT_MODE'],'checks':checks,'archive_sha256':digest,'restored':True,'scope':'local logical database plus SQL authenticated-role replay; not restored HTTP/Auth deployment or managed backup/PITR','full_C5_acceptance':False},indent=2)+'\n')
    print(json.dumps({'restore_checks':len(checks),'passed':True}))


if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        OUT.write_text(json.dumps({'source':os.environ.get('EXPECTED_SOURCE'),'restored':False,'failure_type':type(error).__name__})+'\n')
        print('C5_RESTORE_FAILED_PRIVATE_DETAILS_WITHHELD')
        raise SystemExit(2)
    finally:
        ARCHIVE.unlink(missing_ok=True)
