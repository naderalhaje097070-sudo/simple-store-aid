"""Nonempty logical recovery in a distinct, network-less disposable PG cluster.

The frozen prior helpers retain their data/catalog and SQL-role RPC assertions.
No restored HTTP/Auth, password, encryption-key or managed-PITR claim is made.
"""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import re
import subprocess
import time
import uuid

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen_restore', ROOT / 'tests/c5-restore/restore.py')
prior = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prior)
SOURCE = prior.CONTAINER
TARGET = 'monjez-c5-independent-recovery'
BOOTSTRAP = 'supabase_admin'
LABEL = 'monjez.c5-recovery.source'
PRIVATE = prior.PRIVATE
ARCHIVE = Path('/tmp/monjez-c5-independent.dump')
ROLES = Path('/tmp/monjez-c5-independent.roles')
OUTDIR = Path('/tmp/monjez-c5sale/evidence')
CHECKS = []
PHASE = 'preflight'
SECTION = 'none'
DETAILS = {}
CREATED_FILES = set()
TARGET_ID = None
BEFORE = None
SEQUENCE_REGRESSION_PROVED = False
ADMIN = 'test -n "${POSTGRES_PASSWORD:-}"; export PGPASSWORD="$POSTGRES_PASSWORD"; '


def check(name, passed):
    CHECKS.append({'name': name, 'passed': bool(passed)})
    if not passed:
        raise RuntimeError(name)


def run(args, data=None, phase='command', timeout=180):
    global PHASE
    PHASE = phase
    result = subprocess.run(args, input=data, capture_output=True, timeout=timeout)
    if result.returncode:
        # Never serialize raw stdout/stderr, SQL, roles or Docker environment.
        raise RuntimeError('command_failed:' + phase + ':' + ','.join(prior.classify(result.stderr)) + ':' + prior.error_words(result.stderr))
    return result.stdout


def source_command(command, data=None, phase='source'):
    # Existing disposable admin credentials stay entirely inside source container.
    return run(['docker','exec','--user','postgres','-i',SOURCE,'sh','-ec',ADMIN + 'exec ' + command], data, phase)


def sql(database, statement, denied=None):
    global PHASE
    assert database in ('source','recovery','template1','template0')
    PHASE = 'sql_' + database + '_' + SECTION
    if database == 'source':
        args = ['docker','exec','--user','postgres','-i',SOURCE,'sh','-ec',
                ADMIN + 'exec psql -X -U supabase_admin -d postgres -Atq -v ON_ERROR_STOP=1']
    else:
        assert TARGET_ID is not None
        args = ['docker','exec','--user','postgres','-i',TARGET_ID,'psql','-X',
                '-h','/tmp','-U','supabase_admin' if database == 'recovery' else BOOTSTRAP,
                '-d',database if database in ('template0','template1') else 'postgres',
                '-Atq','-v','ON_ERROR_STOP=1']
    result = subprocess.run(args, input=statement.encode(), capture_output=True, timeout=90)
    if denied:
        check('explicit_denial_' + denied, result.returncode != 0 and denied.encode() in result.stderr)
        return None
    if result.returncode:
        raise RuntimeError('SQL_failed:' + PHASE + ':' + ','.join(prior.classify(result.stderr)) + ':' + prior.error_words(result.stderr))
    return json.loads(result.stdout) if result.stdout.strip() else None


prior.sql = sql
prior.TARGET = 'recovery'


def structure(database):
    global SEQUENCE_REGRESSION_PROVED
    # Stable identities rather than cluster-local OIDs; private values never published.
    extra = sql(database, """select jsonb_build_object(
      'schemas',(select jsonb_agg(jsonb_build_array(nspname,pg_get_userbyid(nspowner),nspacl::text) order by nspname) from pg_namespace where nspname !~ '^pg_' and nspname <> 'information_schema'),
      'extensions',(select jsonb_agg(jsonb_build_array(e.extname,e.extversion,n.nspname,pg_get_userbyid(e.extowner)) order by e.extname) from pg_extension e join pg_namespace n on n.oid=e.extnamespace),
      'constraints',(select jsonb_agg(jsonb_build_array(n.nspname,c.relname,k.conname,k.contype,k.convalidated,pg_get_constraintdef(k.oid,true)) order by n.nspname,c.relname,k.conname) from pg_constraint k join pg_class c on c.oid=k.conrelid join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private','auth')),
      'indexes',(select jsonb_agg(to_jsonb(i) order by schemaname,tablename,indexname) from pg_indexes i where schemaname in ('public','monjez_private','auth')),
      'triggers',(select jsonb_agg(jsonb_build_array(n.nspname,c.relname,t.tgname,t.tgenabled,pg_get_triggerdef(t.oid,true)) order by n.nspname,c.relname,t.tgname) from pg_trigger t join pg_class c on c.oid=t.tgrelid join pg_namespace n on n.oid=c.relnamespace where not t.tgisinternal and n.nspname in ('public','monjez_private','auth')),
      'sequences',(select jsonb_agg(to_jsonb(s) order by schemaname,sequencename) from pg_sequences s where schemaname in ('public','monjez_private','auth')),
      'database',(select jsonb_build_array(pg_get_userbyid(datdba),encoding,datcollate,datctype,datlocprovider,datlocale,daticurules,datcollversion,datacl::text) from pg_database where datname=current_database()),
      'settings',(select jsonb_agg(jsonb_build_array(coalesce(d.datname,''),r.rolname,s.setconfig) order by d.datname,r.rolname) from pg_db_role_setting s left join pg_database d on d.oid=s.setdatabase left join pg_roles r on r.oid=s.setrole where s.setdatabase in (0,(select oid from pg_database where datname=current_database())))
      );""")
    # pg_sequences does not contain is_called; preserve it explicitly as well.
    sequences = sql(database, "select coalesce(jsonb_agg(jsonb_build_array(schemaname,sequencename) order by schemaname,sequencename),'[]') from pg_sequences where schemaname in ('public','monjez_private','auth');")
    extra['sequence_positions'] = {}
    for schema, name in sequences:
        assert re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', schema) and re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*', name)
        relation = '"'+schema+'"."'+name+'"'
        if database == 'source' and not SEQUENCE_REGRESSION_PROVED:
            # Read-only regression: sequence relations have no composite row type.
            # Explicit position fields are the logical setval state restored by pg_dump;
            # internal WAL log_cnt is not logical recovery state.
            sql(database, 'select to_jsonb(s) from '+relation+' s;', 'does not have a composite type')
            SEQUENCE_REGRESSION_PROVED = True
        extra['sequence_positions'][schema+'.'+name] = sql(database, "select jsonb_build_object('last_value',last_value,'is_called',is_called) from "+relation+';')
    return {'prior_catalog': prior.catalog(database), 'extra': extra}


def roles(database):
    return sql(database, """select jsonb_build_object(
      'roles',(select jsonb_agg(to_jsonb(r)-'oid'-'rolpassword' order by rolname) from pg_roles r),
      'memberships',(select jsonb_agg(jsonb_build_array(r.rolname,m.rolname,g.rolname,a.admin_option,a.inherit_option,a.set_option) order by r.rolname,m.rolname,g.rolname) from pg_auth_members a join pg_roles r on r.oid=a.roleid join pg_roles m on m.oid=a.member join pg_roles g on g.oid=a.grantor));""")


def snapshot(database):
    global SECTION
    result = {}
    try:
        SECTION = 'rows'
        result['rows'] = prior.rows(database)
        SECTION = 'structure'
        result['structure'] = structure(database)
        SECTION = 'roles'
        result['roles'] = roles(database)
        SECTION = 'cron_jobs'
        result['cron_jobs'] = sql(database, "select coalesce(jsonb_agg(to_jsonb(j) order by jobid),'[]') from cron.job j;")
        return result
    finally:
        SECTION = 'none'


def private_file(path, value):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    CREATED_FILES.add(path)
    with os.fdopen(fd, 'wb') as stream:
        stream.write(value)
    check('private_mode_' + ('archive' if path == ARCHIVE else 'roles'), path.stat().st_mode & 0o777 == 0o600)


def partition_toc(toc):
    """Partition execution, never discard an archive entry or an extension.

    DB/schema/database-ACL creation precedes mixed-owner extension bootstrap;
    every other TOC entry is subsequently restored, with errors fatal in both.
    """
    first, rest, all_ids = [], [], set()
    for line in toc.decode().splitlines():
        if not line or line.startswith(';'):
            continue
        match = re.fullmatch(r'(\d+);\s+\d+\s+\d+\s+(.+)',line)
        if not match:
            raise RuntimeError('invalid_archive_toc_entry')
        entry, description = int(match[1]), match[2]
        if entry in all_ids:
            raise RuntimeError('duplicate_archive_toc_entry')
        all_ids.add(entry)
        bootstrap = (re.match(r'(DATABASE(?: PROPERTIES)?|SCHEMA) ',description) is not None
                     or description.startswith('ACL - DATABASE '))
        (first if bootstrap else rest).append((entry,line))
    if not first or not rest:
        raise RuntimeError('empty_archive_toc_partition')
    assert not ({i for i,_ in first} & {i for i,_ in rest})
    assert {i for i,_ in first+rest} == all_ids
    encode = lambda values: ('\n'.join(line for _,line in values)+'\n').encode()
    return encode(first), encode(rest), {'all':len(all_ids),'bootstrap':len(first),'remainder':len(rest)}


def prepare_roles(role_dump):
    # Supabase's patched server requires its real bootstrap administrator for
    # reserved-role management. initdb has already created precisely that role.
    # Remove only the one expected CREATE; all ALTER/config/grants remain fatal.
    declaration = b'CREATE ROLE supabase_admin;'
    lines = role_dump.splitlines(keepends=True)
    if sum(line.rstrip(b'\r\n') == declaration for line in lines) != 1:
        raise RuntimeError('bootstrap_role_declaration_count')
    return b''.join(line for line in lines if line.rstrip(b'\r\n') != declaration)


def target_info():
    return json.loads(run(['docker','inspect',TARGET_ID],phase='target_identity'))[0]


def validate_target(info, source_id, image, expected_source):
    return (info['Id'] == TARGET_ID and info['Id'] != source_id and info['Image'] == image
            and info['Name'] == '/'+TARGET and info['Config']['Labels'].get(LABEL) == expected_source
            and info['HostConfig']['NetworkMode'] == 'none' and not info['HostConfig']['PortBindings']
            and all(not bindings for bindings in (info['NetworkSettings']['Ports'] or {}).values()) and not info['HostConfig']['Binds']
            and all(m.get('Type') == 'tmpfs' and m.get('Destination') in ('/tmp','/etc/postgresql-custom') for m in info['Mounts'])
            and info['HostConfig']['ReadonlyRootfs']
            and info['Config']['User'] == 'postgres')


def cleanup():
    result = {'private_files_removed': False, 'target_removed': False, 'source_unchanged': None}
    for path in CREATED_FILES:
        path.unlink(missing_ok=True)
    result['private_files_removed'] = not ARCHIVE.exists() and not ROLES.exists()
    if TARGET_ID is not None:
        info = target_info()
        # Never remove an unowned resource or the source, even if a name is reused.
        check('cleanup_target_identity', info['Id'] == TARGET_ID and info['Name'] == '/'+TARGET
              and info['Config']['Labels'].get(LABEL) == os.environ['EXPECTED_SOURCE'] and TARGET != SOURCE)
        run(['docker','rm','-f','-v',TARGET_ID],phase='remove_target')
    names = run(['docker','ps','-a','--format','{{.Names}}'],phase='verify_cleanup').decode().splitlines()
    result['target_removed'] = TARGET not in names
    if BEFORE is not None:
        result['source_unchanged'] = snapshot('source') == BEFORE
    return result


def main():
    global TARGET_ID, BEFORE
    source = os.environ['EXPECTED_SOURCE']
    git = ['git','-c','safe.directory=/tmp/monjez-c5sale/repo']
    check('exact_source_and_isolation', run([*git,'rev-parse','HEAD'],phase='git').decode().strip() == source and os.environ.get('CI_ISOLATED_SUPABASE') == '1')
    run([*git,'diff','--exit-code','HEAD','--'],phase='clean_source')
    check('private_paths_absent', not ARCHIVE.exists() and not ROLES.exists())
    names = run(['docker','ps','-a','--format','{{.Names}}'],phase='inventory').decode().splitlines()
    check('source_present_target_absent', SOURCE in names and TARGET not in names)
    src = json.loads(run(['docker','inspect',SOURCE],phase='source_identity'))[0]
    image = src['Image']
    check('exact_source_image', re.fullmatch('sha256:[0-9a-f]{64}',image) and src['Name'] == '/'+SOURCE)
    image_meta = json.loads(run(['docker','image','inspect',image],phase='image_identity'))[0]
    check('image_has_no_automatic_volumes', not image_meta['Config'].get('Volumes'))
    check('original_vendor_bootstrap_identity', sql('source',"select to_jsonb(rolsuper and rolcanlogin) from pg_roles where rolname='supabase_admin';") is True)
    settings = sql('source', "select jsonb_object_agg(name,setting) from pg_settings where name in ('shared_preload_libraries','cron.database_name','pgsodium.getkey_script','vault.getkey_script','server_version_num');")
    check('original_database_and_cron_name', settings.get('cron.database_name') == 'postgres' and 'pg_cron' in [x.strip() for x in settings['shared_preload_libraries'].split(',')])
    check('preload_setting_safe', re.fullmatch('[a-zA-Z0-9_, $/.-]+', settings['shared_preload_libraries']) is not None)
    versions = {t: source_command(t+' --version',phase='tool_version').decode().strip() for t in ('pg_dump','pg_restore','initdb')}
    for name in ('pg_dump','pg_restore'):
        check('pinned_tool_version_'+name, re.fullmatch(r'[a-z_]+ \(PostgreSQL\) [0-9.]+(?: \([^\n]*\))?', versions[name]) is not None)
    # Discover flags in this installed binary rather than assuming CLI structure.
    check('initdb_required_flags', all(flag.encode() in source_command('initdb --help',phase='tool_help') for flag in ('--auth-local','--auth-host','--username')))
    check('restore_required_flags', all(flag.encode() in source_command('pg_restore --help',phase='tool_help') for flag in ('--create','--exit-on-error')))
    check('role_dump_required_flags', b'--no-role-passwords' in source_command('pg_dumpall --help',phase='tool_help'))
    DETAILS.update({'image_id':image,'image_repo_digests':image_meta.get('RepoDigests',[]),'tools':versions,
                    'server_version_num':settings['server_version_num'],'shared_preload_libraries':settings['shared_preload_libraries'],
                    'cron_database':'postgres','scheduler_execution':'requested disabled; target attestation pending',
                    'target_created_and_contained':False,'network_mode':'none','host_ports':False})
    BEFORE = snapshot('source')
    check('native_sequence_regression_and_position_read', SEQUENCE_REGRESSION_PROVED)
    DETAILS['extensions'] = BEFORE['structure']['extra']['extensions']
    # This drill does not recover provider master keys. Fail closed if the fixture
    # contains Vault/pgsodium key-dependent records rather than claiming they work.
    for schema, table in (('vault','secrets'),('pgsodium','key')):
        if sql('source', "select to_jsonb(to_regclass('"+schema+'.'+table+"') is not null);"):
            check('no_master_key_dependent_fixture_'+schema, sql('source','select count(*) from "'+schema+'"."'+table+'";') == 0)
    check('nonempty_finance_and_auth', all(BEFORE['rows'][t]['count'] > 0 for t in ('public.orders','public.order_items','public.payments','public.financial_idempotency','public.products','auth.users')))
    archive = source_command('pg_dump -U supabase_admin -d postgres -Fc',phase='full_dump')
    check('full_custom_archive', archive.startswith(b'PGDMP') and len(archive) > 1000)
    private_file(ARCHIVE,archive)
    role_dump = prepare_roles(source_command('pg_dumpall -U supabase_admin --roles-only --no-role-passwords',phase='global_roles_dump'))
    check('only_expected_bootstrap_create_prehandled', b'CREATE ROLE' in role_dump and b'ALTER ROLE supabase_admin ' in role_dump)
    private_file(ROLES,role_dump)
    DETAILS['archive_sha256'] = hashlib.sha256(archive).hexdigest()
    # A private tmpfs cluster bypasses the image's service bootstrap scripts.
    # No source mounts, source credentials, host ports or network connectivity.
    script = ('set -eu; initdb -D /tmp/c5pg -U '+BOOTSTRAP+' --auth-local=trust --auth-host=reject --encoding=UTF8; '
              'exec postgres -D /tmp/c5pg -c listen_addresses= -c unix_socket_directories=/tmp -c unix_socket_permissions=0700 '
              '-c cron.database_name=postgres -c cron.launch_active_jobs=off -c wal_level=logical "$@"')
    config = ['-c','shared_preload_libraries='+settings['shared_preload_libraries']]
    for name in ('pgsodium.getkey_script','vault.getkey_script'):
        if settings.get(name):
            check('key_script_path_'+name, re.fullmatch('/[a-zA-Z0-9_/.-]+',settings[name]) is not None)
            config += ['-c',name+'='+settings[name]]
    operator_uid = int(run(['docker','exec','--user','postgres',SOURCE,'id','-u'],phase='operator_uid'))
    operator_gid = int(run(['docker','exec','--user','postgres',SOURCE,'id','-g'],phase='operator_gid'))
    check('nonroot_operator_uid_gid', 0 < operator_uid < 65536 and 0 < operator_gid < 65536)
    TARGET_ID = run(['docker','create','--name',TARGET,'--label',LABEL+'='+source,'--network','none',
                    '--read-only','--tmpfs','/tmp:rw,mode=1777,size=1073741824','--shm-size','256m',
                    '--tmpfs','/etc/postgresql-custom:rw,mode=0700,uid='+str(operator_uid)+',gid='+str(operator_gid),
                    '--user','postgres','--cap-drop','ALL','--security-opt','no-new-privileges',
                    '--no-healthcheck','--entrypoint','sh',image,'-ec',script,'c5-recovery',*config],phase='create_target').decode().strip()
    check('created_target_id', re.fullmatch('[0-9a-f]{64}',TARGET_ID) is not None)
    run(['docker','start',TARGET_ID],phase='start_target')
    check('distinct_no_network_no_host_mount_target', validate_target(target_info(),src['Id'],image,source))
    DETAILS['target_created_and_contained'] = True
    for _ in range(50):
        ready = subprocess.run(['docker','exec','--user','postgres',TARGET_ID,'pg_isready','-h','/tmp','-U',BOOTSTRAP,'-d','template1'],capture_output=True,timeout=5)
        if ready.returncode == 0:
            break
        time.sleep(.2)
    else:
        # Fixed vocabulary only; underlying startup log stays private.
        output = subprocess.run(['docker','logs',TARGET_ID],stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=15)
        logs = output.stdout.decode(errors='replace').lower()
        DETAILS['startup_labels'] = [label for label in ('read-only file system','permission denied','invalid locale','initdb','could not load library','fatal','pgsodium','no such file or directory') if label in logs]
        DETAILS['target_running'] = bool(target_info()['State']['Running'])
        raise RuntimeError('target_readiness_failed')
    check('target_cron_disabled_before_role_restore', sql('template1',"select to_jsonb(current_setting('cron.launch_active_jobs')='off' and current_setting('listen_addresses')='');") is True)
    DETAILS['scheduler_execution'] = 'disabled before role/archive restore; scheduler execution not accepted'
    source_system = sql('source',"select system_identifier::text::jsonb from pg_control_system();")
    target_system = sql('template1',"select system_identifier::text::jsonb from pg_control_system();")
    check('distinct_cluster_system_identifier', source_system != target_system)
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'psql','-X','-h','/tmp','-U',BOOTSTRAP,'-d','template1','-v','ON_ERROR_STOP=1'],ROLES.read_bytes(),phase='restore_global_roles')
    check('global_roles_memberships_restored_without_passwords', roles('template1') == BEFORE['roles'])
    if os.environ.get('C5_RECOVERY_FAILURE_CANARY') == '1':
        raise RuntimeError('injected_after_global_roles')
    # Only the attested independent target's default empty postgres DB is dropped.
    # --create restores the original name, database settings/owner/ACL from archive.
    extensions = BEFORE['structure']['extra']['extensions']
    builtin_owner = next(e[3] for e in extensions if e[0] == 'plpgsql')
    mixed = [e for e in extensions if e[0] != 'plpgsql' and e[3] != 'supabase_admin']
    check('known_mixed_extension_bootstrap', all(e == ['pgmq','1.5.1','pgmq','postgres'] for e in mixed))
    check('builtin_owner_safe', re.fullmatch('[a-zA-Z_][a-zA-Z_0-9]*',builtin_owner) is not None)
    # Standard pg_dump intentionally does not encode extension owners. Its CREATE
    # EXTENSION runs as the restore user; template0 supplies builtin plpgsql.
    # initdb's actual vendor identity matches the measured builtin owner.
    check('builtin_template_extension_owner_matches', builtin_owner == BOOTSTRAP)
    sql('template1','drop database postgres with (force);')
    first, remainder, counts = partition_toc(source_command('pg_restore --list',ARCHIVE.read_bytes(),phase='archive_toc'))
    check('archive_toc_full_disjoint_coverage', counts['all'] == counts['bootstrap']+counts['remainder'])
    DETAILS['archive_toc_coverage'] = counts
    for name, content in (('bootstrap',first),('remainder',remainder)):
        run(['docker','exec','--user','postgres','-i',TARGET_ID,'sh','-ec','umask 077; cat > /tmp/c5-'+name+'.list'],content,phase='private_toc_'+name)
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','-h','/tmp','-U','supabase_admin','-d','template1','--create','--exit-on-error','--use-list=/tmp/c5-bootstrap.list'],ARCHIVE.read_bytes(),phase='pg_restore_database_schemas')
    for name, version, schema, owner in mixed:
        # pgmq is an explicitly measured non-superuser extension. Install under
        # its original role after source database/schema ACLs exist, then keep
        # its normal IF NOT EXISTS archive entry in the full remainder restore.
        check('pgmq_non_superuser_extension', sql('source',"select to_jsonb(not superuser) from pg_available_extension_versions where name='pgmq' and version='1.5.1';") is True)
        check('source_owner_has_database_create', sql('source',"select to_jsonb(has_database_privilege('postgres','postgres','CREATE'));") is True)
        check('recovered_owner_has_database_create', sql('recovery',"select to_jsonb(has_database_privilege('postgres','postgres','CREATE'));") is True)
        check('recovered_owner_has_schema_create', sql('recovery',"select to_jsonb(has_schema_privilege('postgres','pgmq','CREATE'));") is True)
        sql('recovery',"set session authorization postgres; create extension pgmq with schema pgmq version '1.5.1'; reset session authorization;")
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','-h','/tmp','-U','supabase_admin','-d','postgres','--exit-on-error','--use-list=/tmp/c5-remainder.list'],ARCHIVE.read_bytes(),phase='pg_restore_all_remaining_entries')
    check('scheduler_stays_disabled', sql('recovery',"select to_jsonb(current_setting('cron.launch_active_jobs')='off' and current_setting('listen_addresses')='');") is True)
    recovered = snapshot('recovery')
    check('all_selected_rows_restored', recovered['rows'] == BEFORE['rows'])
    check('prior_functions_RLS_owners_ACLs_restored', recovered['structure']['prior_catalog'] == BEFORE['structure']['prior_catalog'])
    for section in BEFORE['structure']['extra']:
        check('metadata_restored_' + section, recovered['structure']['extra'][section] == BEFORE['structure']['extra'][section])
    check('roles_restored', recovered['roles'] == BEFORE['roles'])
    check('cron_definitions_restored', recovered['cron_jobs'] == BEFORE['cron_jobs'])
    state = json.loads(PRIVATE.read_text())
    sample = sql('recovery',"select jsonb_build_object('key',i.idempotency_key,'order_id',o.id,'amount',(i.request_payload->>'amount')::numeric,'method',i.request_payload->>'method','result',i.result,'actor',i.created_by,'paid',o.paid,'payments',(select count(*) from public.payments where order_id=o.id)) from public.financial_idempotency i join public.orders o on o.id=(i.request_payload->>'order_id')::uuid where i.operation='order.debt.collect.v1' and i.result is not null and o.total-o.paid>=20 order by i.created_at limit 1;")
    actor = next(a for a in state['actors'].values() if a['uid'] == sample['actor'])
    foreign = next(a for a in state['actors'].values() if a['tenant'] != actor['tenant'])
    check('restored_original_key_returns_original_result', prior.rpc(actor,sample) == sample['result'])
    check('replay_no_effect_on_relations', prior.rows('recovery') == BEFORE['rows'])
    prior.rpc(foreign,sample,'forbidden_tenant')
    check('foreign_denial_atomic', prior.rows('recovery') == BEFORE['rows'])
    prior.rpc(actor,{**sample,'amount':sample['amount']+1},'idempotency_conflict')
    check('payload_conflict_atomic', prior.rows('recovery') == BEFORE['rows'])
    fresh = {**sample,'key':str(uuid.uuid4()),'amount':20}
    first = prior.rpc(actor,fresh)
    check('new_payment_replay_same_result', prior.rpc(actor,fresh) == first)
    effect = sql('recovery',"select jsonb_build_object('paid',paid,'payments',(select count(*) from public.payments where order_id=o.id)) from public.orders o where id='"+sample['order_id']+"';")
    check('intentional_new_payment_exactly_once', effect == {'paid':sample['paid']+20,'payments':sample['payments']+1})
    check('source_unchanged_after_recovery', snapshot('source') == BEFORE)


def execute():
    canary = os.environ.get('C5_RECOVERY_FAILURE_CANARY') == '1'
    result = {'source':os.environ.get('EXPECTED_SOURCE'),'mode':os.environ.get('CONTRACT_MODE'),
              'restored':False,'full_C5_acceptance':False,'failure_canary':canary,
              'scope':'isolated logical postgres restore and SQL authenticated-role replay; not restored HTTP/Auth, role-password/encryption-key recovery or managed backup/PITR'}
    exit_code = 0
    try:
        main()
        result['restored'] = True
    except Exception as error:
        exit_code = 2
        result.update({'failure_type':type(error).__name__,'phase':PHASE,
                       'reason':str(error) if type(error) is RuntimeError else 'private_details_withheld'})
    finally:
        try:
            clean = cleanup()
            result['cleanup'] = clean
            if not (clean['private_files_removed'] and clean['target_removed'] and clean['source_unchanged'] is True):
                exit_code = 2
                result['restored'] = False
        except Exception:
            exit_code = 2
            result['restored'] = False
            result['cleanup'] = {'verified':False,'private_details_withheld':True}
        result['checks'] = CHECKS
        result['discovery'] = DETAILS
        OUTDIR.mkdir(parents=True,exist_ok=True)
        (OUTDIR/('independent-restore-failure-canary.json' if canary else 'independent-restore-result.json')).write_text(json.dumps(result,indent=2)+'\n')
    # Result contains only fixed checks/booleans/public image metadata; never snapshots, SQL, claims or credentials.
    print('C5_INDEPENDENT_RECEIPT ' + json.dumps(result,separators=(',',':')))
    return exit_code


if __name__ == '__main__':
    raise SystemExit(execute())
