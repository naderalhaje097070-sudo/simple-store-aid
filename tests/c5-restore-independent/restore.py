"""Nonempty logical recovery in a distinct, network-less disposable PG cluster.

The frozen prior helpers retain their data/catalog and SQL-role RPC assertions.
No restored HTTP/Auth, password, encryption-key or managed-PITR claim is made.
"""
import hashlib
from collections import Counter
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
ACL_BACKUP = Path('/tmp/monjez-c5-independent.scoped-acl.json')
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
        if phase.startswith('pg_restore_'):
            DETAILS['restore_error'] = restore_error_metadata(result.stderr)
        # Never serialize raw stdout/stderr, SQL, roles or Docker environment.
        raise RuntimeError('command_failed:' + phase + ':' + ','.join(prior.classify(result.stderr)) + ':' + prior.error_words(result.stderr))
    return result.stdout


def restore_error_metadata(stderr):
    """Finite vendor vocabulary only; never emit raw SQL or arbitrary names."""
    message = stderr.decode(errors='replace')
    known_routines = (
        'extensions.grant_pg_graphql_access', 'extensions.grant_pg_cron_access',
        'extensions.grant_pg_net_access', 'extensions.set_graphql_placeholder',
        'extensions.notify_api_restart', 'extensions.pgrst_ddl_watch',
        'extensions.pgrst_drop_watch', 'graphql_public.graphql',
        'graphql.resolve', 'net.http_collect_response', 'net.http_get',
        'net.http_post', 'pgsodium.get_key_by_id', 'vault.create_secret',
    )
    missing = re.search(r'ERROR:\s+function ([a-z_][a-z_0-9]*\.[a-z_][a-z_0-9]*)\([^\n]*?\) does not exist', message)
    result = {'missing_function': bool(missing)}
    if missing:
        routine = missing[1]
        result['known_vendor_routine'] = routine if routine in known_routines else 'unrecognized_withheld'
        result['routine_name_sha256'] = hashlib.sha256(routine.encode()).hexdigest()
    # Object kind is a bounded diagnostic, not the TOC description or object name.
    match = re.search(r'from TOC entry (\d+); \d+ \d+ ([A-Z][A-Z ]*) ', message)
    kinds = ('FUNCTION', 'EVENT TRIGGER', 'EXTENSION', 'ACL', 'COMMENT', 'TABLE', 'TABLE DATA', 'TRIGGER', 'DEFAULT ACL')
    if match:
        result['toc_entry'] = int(match[1])
        result['object_kind'] = next((kind for kind in kinds if match[2].strip() == kind), 'unrecognized_withheld')
    return result


def source_command(command, data=None, phase='source'):
    # Existing disposable admin credentials stay entirely inside source container.
    return run(['docker','exec','--user','postgres','-i',SOURCE,'sh','-ec',ADMIN + 'exec ' + command], data, phase)


def sql(database, statement, denied=None):
    global PHASE
    assert database in ('source','recovery','template1','template0')
    PHASE = 'sql_' + database + '_' + SECTION
    if database == 'source':
        args = ['docker','exec','--user','postgres','-i',SOURCE,'sh','-ec',
                ADMIN + 'exec psql -X -U supabase_admin -d postgres -Atq -v ON_ERROR_STOP=1 -v VERBOSITY=verbose']
    else:
        assert TARGET_ID is not None
        args = ['docker','exec','--user','postgres','-i',TARGET_ID,'psql','-X',
                '-h','/tmp','-U','supabase_admin' if database == 'recovery' else BOOTSTRAP,
                '-d',database if database in ('template0','template1') else 'postgres',
                '-Atq','-v','ON_ERROR_STOP=1','-v','VERBOSITY=verbose']
    result = subprocess.run(args, input=statement.encode(), capture_output=True, timeout=90)
    if denied:
        check('explicit_denial_' + denied, result.returncode != 0 and denied.encode() in result.stderr)
        return None
    if result.returncode:
        DETAILS['sql_failure'] = sql_error_metadata(result.stderr)
        raise RuntimeError('SQL_failed:' + PHASE + ':' + ','.join(prior.classify(result.stderr)) + ':' + prior.error_words(result.stderr))
    return json.loads(result.stdout) if result.stdout.strip() else None


def sql_error_metadata(stderr):
    # Verbose psql stderr remains private. Emit finite code/domain labels only.
    match = re.search(r'ERROR:\s+([0-9A-Z]{5}):\s*([a-z_]+)',stderr.decode(errors='replace'))
    codes = {'42501','P0001','22P02','42883','42P01','42703','42601','23505','23503','23514',
             '25P02','08006','08001','57014','0A000','XX000'}
    labels = {'account_inactive','authentication_required','unauthenticated','forbidden_tenant',
              'forbidden_role','order_not_found','idempotency_conflict','idempotency_key_required',
              'idempotency_state_missing','idempotency_incomplete','invalid_amount',
              'cannot_collect_returned_order','settle_courier_first','amount_exceeds_remaining'}
    return {'sqlstate':match[1] if match and match[1] in codes else 'unrecognized_withheld',
            'domain_error':match[2] if match and match[2] in labels else 'unrecognized_withheld'}


def set_replay_stage(stage):
    global SECTION
    allowed = {'sample_select','sample_actor_context','inactive_replay','inactive_replay_rows','original_replay','original_replay_rows',
               'foreign_replay','foreign_replay_rows','conflicting_replay','conflicting_replay_rows',
               'new_payment','new_payment_replay','new_payment_effect'}
    if stage not in allowed:
        raise RuntimeError('invalid_replay_stage')
    SECTION = stage
    DETAILS['replay_stage'] = stage


def sample_actor_context(actor, sample):
    subject = str(uuid.UUID(sample['actor']))
    return sql('recovery',"begin; set local role authenticated; set local request.jwt.claims = '"+
        prior.claims(actor)+"'; select jsonb_build_object('active',monjez_private.actor_is_active(),"+
        "'subject_matches',auth.uid()='"+subject+"'::uuid); commit;")


def select_replay_samples(samples, actors):
    """Keep blocked saved requests as negative controls, active ones as positives.

    Do not alter account state or use administrator authority for a replay.
    Every actor check runs the already restored canonical live-account guard.
    """
    if not isinstance(samples,list) or not 1 <= len(samples) <= 128 or not isinstance(actors,dict):
        raise RuntimeError('invalid_restored_sample_inventory')
    by_id = {}
    for actor in actors.values():
        if not isinstance(actor,dict) or not all(key in actor for key in ('uid','tenant','token')):
            raise RuntimeError('invalid_saved_actor_inventory')
        uid = str(uuid.UUID(actor['uid']))
        if uid in by_id:
            raise RuntimeError('duplicate_saved_actor')
        by_id[uid] = actor
    seen = set()
    for sample in samples:
        if not isinstance(sample,dict) or set(sample) != {'key','order_id','amount','method','result','actor','paid','payments'}:
            raise RuntimeError('invalid_saved_request_shape')
        for key in ('key','order_id','actor'):
            if str(uuid.UUID(sample[key])) != sample[key]:
                raise RuntimeError('invalid_saved_request_identity')
        identity = (sample['actor'],sample['key'])
        if identity in seen or sample['actor'] not in by_id:
            raise RuntimeError('duplicate_or_unowned_saved_request')
        seen.add(identity)
        if (type(sample['amount']) not in (int,float) or not 0 < sample['amount'] <= 100
                or sample['method'] not in ('cash','transfer') or not isinstance(sample['result'],dict)
                or type(sample['paid']) not in (int,float) or not 0 <= sample['paid'] < float('inf')
                or type(sample['payments']) is not int or sample['payments'] < 0):
            raise RuntimeError('invalid_saved_request_values')
    contexts = {}
    def context(actor):
        if actor['uid'] not in contexts:
            value = sample_actor_context(actor,{'actor':actor['uid']})
            if (not isinstance(value,dict) or set(value) != {'active','subject_matches'}
                    or not all(type(v) is bool for v in value.values()) or not value['subject_matches']):
                raise RuntimeError('invalid_saved_actor_context')
            contexts[actor['uid']] = value
        return contexts[actor['uid']]
    active, inactive = [], []
    for sample in samples:
        actor = by_id[sample['actor']]
        (active if context(actor)['active'] else inactive).append((sample,actor))
    if not active or not inactive:
        raise RuntimeError('missing_active_or_inactive_saved_request')
    foreign = next((actor for actor in actors.values()
        if actor['tenant'] != active[0][1]['tenant'] and context(actor)['active']),None)
    if foreign is None:
        raise RuntimeError('missing_active_foreign_actor')
    return {'active':active[0],'inactive':inactive[0],'foreign':foreign,
        'active_context':context(active[0][1]),
        'summary':{'eligible_saved_requests':len(samples),'active_saved_requests':len(active),
            'inactive_saved_requests':len(inactive),
            'oldest_saved_actor_active':context(by_id[samples[0]['actor']])['active'],
            'oldest_saved_request_selected_for_denial':inactive[0][0] == samples[0]}}


prior.sql = sql
prior.TARGET = 'recovery'


def structure(database):
    global SEQUENCE_REGRESSION_PROVED
    # Stable identities rather than cluster-local OIDs; private values never published.
    extra = sql(database, """select jsonb_build_object(
      'schemas',(select jsonb_agg(jsonb_build_array(nspname,pg_get_userbyid(nspowner),nspacl::text) order by nspname) from pg_namespace where nspname !~ '^pg_' and nspname <> 'information_schema'),
      'extensions',(select jsonb_agg(jsonb_build_array(e.extname,e.extversion,n.nspname,pg_get_userbyid(e.extowner)) order by e.extname) from pg_extension e join pg_namespace n on n.oid=e.extnamespace),
      'vendor_functions',(select jsonb_agg(jsonb_build_array(n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),pg_get_functiondef(p.oid),p.prosecdef,p.proconfig,p.proacl::text,pg_get_userbyid(p.proowner),(select e.extname from pg_depend d join pg_extension e on e.oid=d.refobjid where d.classid='pg_proc'::regclass and d.objid=p.oid and d.deptype='e')) order by n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('extensions','graphql','graphql_public') and p.prokind in ('f','p')),
      'event_triggers',(select jsonb_agg(jsonb_build_array(t.evtname,t.evtevent,t.evtenabled,t.evttags,pg_get_userbyid(t.evtowner),n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)) order by t.evtname) from pg_event_trigger t join pg_proc p on p.oid=t.evtfoid join pg_namespace n on n.oid=p.pronamespace),
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


def acl_catalog(database):
    # Stable identities rather than local OIDs; PUBLIC has a separate type tag.
    # NULL is PostgreSQL's object default; an explicit empty ACL stays empty.
    def grants(expression):
        # All expressions are fixed below, never identifiers from a snapshot.
        return """(select coalesce(jsonb_agg(jsonb_build_array(pg_get_userbyid(a.grantor),
          jsonb_build_object('public',a.grantee=0,'role',case when a.grantee=0 then null else pg_get_userbyid(a.grantee) end),
          a.privilege_type,a.is_grantable) order by pg_get_userbyid(a.grantor),a.grantee=0,
          case when a.grantee=0 then null else pg_get_userbyid(a.grantee) end,a.privilege_type,a.is_grantable),'[]'::jsonb)
          from aclexplode(""" + expression + ") a)"
    function_acl = grants("coalesce(p.proacl,acldefault('f',p.proowner))")
    table_acl = grants("coalesce(c.relacl,acldefault('r',c.relowner))")
    schema_acl = grants("coalesce(n.nspacl,acldefault('n',n.nspowner))")
    database_acl = grants("coalesce(d.datacl,acldefault('d',d.datdba))")
    return sql(database, f"""select jsonb_build_object(
      'functions',(select jsonb_agg(jsonb_build_array(n.nspname,p.proname,pg_get_function_identity_arguments(p.oid),
        {function_acl})
        order by n.nspname,p.proname,pg_get_function_identity_arguments(p.oid)) from pg_proc p join pg_namespace n on n.oid=p.pronamespace where n.nspname in ('public','monjez_private')),
      'tables',(select jsonb_agg(jsonb_build_array(n.nspname,c.relname,
        {table_acl})
        order by n.nspname,c.relname) from pg_class c join pg_namespace n on n.oid=c.relnamespace where n.nspname in ('public','monjez_private') and c.relkind in ('r','p')),
      'schemas',(select jsonb_agg(jsonb_build_array(n.nspname,{schema_acl}) order by n.nspname) from pg_namespace n where n.nspname !~ '^pg_' and n.nspname <> 'information_schema'),
      'database',(select jsonb_agg(jsonb_build_array(d.datname,{database_acl}) order by d.datname) from pg_database d where d.datname=current_database())
      );""")


def rows_with_logical_acl(rows, acl_rows, key_columns, acl_column, width):
    """Replace only textual ACL representation in a new comparison copy.

    Coverage, grantors, typed grantees, privileges, duplicates and grant options
    are preserved. Owners/RLS/definitions and all other values stay exact.
    """
    rights = {}
    for row in acl_rows or []:
        if len(row) != key_columns+1 or not all(isinstance(v,str) for v in row[:key_columns]):
            raise RuntimeError('unexpected_acl_identity_shape')
        key = tuple(row[:key_columns])
        if key in rights or not isinstance(row[-1],list):
            raise RuntimeError('duplicate_or_invalid_acl_identity')
        normalized = []
        for grant in row[-1]:
            if (not isinstance(grant,list) or len(grant) != 4 or not isinstance(grant[0],str)
                or not isinstance(grant[1],dict) or set(grant[1]) != {'public','role'}
                or type(grant[1]['public']) is not bool
                or (grant[1]['role'] is not None if grant[1]['public'] else not isinstance(grant[1]['role'],str))
                or not isinstance(grant[2],str) or type(grant[3]) is not bool):
                raise RuntimeError('unexpected_acl_grant_shape')
            normalized.append(json.dumps(grant,separators=(',',':'),sort_keys=True))
        rights[key] = sorted(normalized)
    result, seen = [], set()
    for row in rows or []:
        if len(row) != width or not all(isinstance(v,str) for v in row[:key_columns]):
            raise RuntimeError('unexpected_catalog_acl_shape')
        key = tuple(row[:key_columns])
        if key in seen or key not in rights:
            raise RuntimeError('catalog_acl_coverage_mismatch')
        seen.add(key)
        value = list(row)
        value[acl_column] = rights[key]
        result.append(value)
    if seen != rights.keys():
        raise RuntimeError('catalog_acl_coverage_mismatch')
    return result


def catalog_contract_equal(before, after):
    left, right = before['structure']['prior_catalog'], after['structure']['prior_catalog']
    if set(left) != {'functions','tables','policies'} or set(right) != set(left):
        return False
    return (left['functions'] == right['functions'] and left['policies'] == right['policies']
        and rows_with_logical_acl(left['tables'],before['acl_semantics']['tables'],2,4,6)
         == rows_with_logical_acl(right['tables'],after['acl_semantics']['tables'],2,4,6))


def metadata_contract_equal(before, after, section):
    left, right = before['structure']['extra'][section], after['structure']['extra'][section]
    if section == 'schemas':
        return (rows_with_logical_acl(left,before['acl_semantics']['schemas'],1,2,3)
             == rows_with_logical_acl(right,after['acl_semantics']['schemas'],1,2,3))
    if section == 'database':
        # Both fixed routes address postgres; all nine original attributes stay.
        return (rows_with_logical_acl([['postgres',*left]],before['acl_semantics']['database'],1,9,10)
             == rows_with_logical_acl([['postgres',*right]],after['acl_semantics']['database'],1,9,10))
    return left == right


def catalog_field_differences(before, after, fields, key_columns):
    def indexed(rows):
        result = {}
        for row in rows or []:
            key = json.dumps(row[:key_columns],separators=(',',':'),ensure_ascii=True)
            if key in result or len(row) != len(fields):
                raise RuntimeError('unexpected_catalog_diagnostic_shape')
            result[key] = row
        return result
    left, right = indexed(before), indexed(after)
    common = left.keys() & right.keys()
    changed = [key for key in common if left[key] != right[key]]
    return {'source_count':len(left),'recovered_count':len(right),
            'missing_count':len(left.keys()-right.keys()),'added_count':len(right.keys()-left.keys()),
            'changed_count':len(changed),'literal_equal':before == after,
            'list_order_only':before != after and left == right,
            'field_counts':{field:sum(left[key][index] != right[key][index] for key in common)
                            for index,field in enumerate(fields)},
            'changed_key_hashes':sorted(hashlib.sha256(key.encode()).hexdigest() for key in changed)[:4]}


def catalog_diagnostics(before, after):
    """Publish fixed field labels/counts/key hashes; never values or raw identities.

    This function does not mutate snapshots or decide whether a restore passes.
    """
    left, right = before['structure']['prior_catalog'], after['structure']['prior_catalog']
    policy_fields = ('schema','table','name','permissive','roles','command','using','with_check')
    def policies(rows):
        return [[p.get(key) for key in ('schemaname','tablename','policyname','permissive','roles','cmd','qual','with_check')]
                for p in rows or []]
    result = {'literal_equal':left == right,
        'functions':catalog_field_differences(left['functions'],right['functions'],
            ('schema','name','arguments','body','security_definer','config','acl','owner'),3),
        'tables':catalog_field_differences(left['tables'],right['tables'],
            ('schema','name','rls','forced_rls','acl','owner'),2),
        'policies':catalog_field_differences(policies(left['policies']),policies(right['policies']),policy_fields,3),
        'semantic_acl_equal':before['acl_semantics'] == after['acl_semantics']}
    for kind in ('functions','tables'):
        result[kind]['semantic_acl_equal'] = before['acl_semantics'][kind] == after['acl_semantics'][kind]
    sections = ('schemas','extensions','vendor_functions','event_triggers','constraints','indexes','triggers',
                'sequences','database','settings','sequence_positions')
    result['extra_different_sections'] = [s for s in sections
        if before['structure']['extra'].get(s) != after['structure']['extra'].get(s)]
    if 'schemas' in before['acl_semantics'] and 'schemas' in after['acl_semantics']:
        result['schemas'] = catalog_field_differences(before['structure']['extra']['schemas'],after['structure']['extra']['schemas'],('schema','owner','acl'),1)
        result['schemas']['semantic_acl_equal'] = before['acl_semantics']['schemas'] == after['acl_semantics']['schemas']
        result['database'] = catalog_field_differences([['postgres',*before['structure']['extra']['database']]],[['postgres',*after['structure']['extra']['database']]],
            ('database','owner','encoding','collate','ctype','locale_provider','locale','icu_rules','collation_version','acl'),1)
        result['database']['semantic_acl_equal'] = before['acl_semantics']['database'] == after['acl_semantics']['database']
    return result


def scoped_grant_delta(source_acls, recovered_acls):
    """Only fixed vendor objects, known role labels and bounded grant deltas."""
    known_roles = {'postgres','supabase_admin','anon','authenticated','service_role','pg_database_owner',
                   'supabase_auth_admin','supabase_storage_admin','supabase_functions_admin','pgbouncer',
                   'supabase_read_only_user','supabase_replication_admin'}
    def role(value):
        return {'known_role':value} if value in known_roles else {'role_sha256':hashlib.sha256(value.encode()).hexdigest()}
    def public_grant(value):
        recipient = {'public':True} if value[1]['public'] else role(value[1]['role'])
        privilege = value[2] if value[2] in {'CREATE','USAGE','CONNECT','TEMPORARY'} else 'unknown_privilege_withheld'
        return {'grantor':role(value[0]),'grantee':recipient,'privilege':privilege,'grant_option':value[3]}
    result = {}
    for kind,name in (('schemas','graphql_public'),('database','postgres')):
        source = [row for row in source_acls[kind] or [] if row[0] == name]
        restored = [row for row in recovered_acls[kind] or [] if row[0] == name]
        if len(source) != 1 or len(restored) > 1:
            raise RuntimeError('scoped_acl_inventory_invalid')
        left = rows_with_logical_acl([[name,None]],source,1,1,2)[0][1]
        right = rows_with_logical_acl([[name,None]],restored,1,1,2)[0][1] if restored else []
        missing = Counter(left)-Counter(right); extra = Counter(right)-Counter(left)
        result[kind] = {'source_present':True,'target_present':bool(restored),
            'source_grants':len(left),'target_grants':len(right),
            'missing_count':sum(missing.values()),'extra_count':sum(extra.values()),
            'missing':[public_grant(json.loads(g)) for g in sorted(missing.elements())[:8]],
            'extra':[public_grant(json.loads(g)) for g in sorted(extra.elements())[:8]]}
    return result


def note_acl_stage(stage, recovered_acls=None):
    if stage not in ('database_schemas','graphql_hook','pgmq_bootstrap','full_archive'):
        raise RuntimeError('invalid_acl_stage')
    observed = acl_catalog('recovery') if recovered_acls is None else recovered_acls
    DETAILS.setdefault('grant_provenance',{})[stage] = scoped_grant_delta(BEFORE['acl_semantics'],observed)


def archive_acl_observations(toc):
    selected, counts = [], {'schemas':0,'database':0}
    for line in toc.decode().splitlines():
        match = re.fullmatch(r'(\d+);\s+\d+\s+\d+\s+(.+)',line)
        if not match:
            continue
        description = match[2].rstrip()
        for kind,prefix in (('schemas','ACL - SCHEMA graphql_public '),('database','ACL - DATABASE postgres ')):
            if description.startswith(prefix):
                selected.append(line);counts[kind] += 1
    if any(v > 1 for v in counts.values()):
        raise RuntimeError('duplicate_scoped_acl_archive_entry')
    output = b''
    if selected:
        run(['docker','exec','--user','postgres','-i',TARGET_ID,'sh','-ec','umask 077; cat > /tmp/c5-acl-observe.list'],
            ('\n'.join(selected)+'\n').encode(),phase='private_acl_observation_list')
        # No -d: this renders text into private memory, never executes SQL.
        output = run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','--create','--exit-on-error',
            '--use-list=/tmp/c5-acl-observe.list','--file=-'],ARCHIVE.read_bytes(),phase='pg_restore_acl_observation')
    result = {}
    for kind,clause in (('schemas','ON SCHEMA graphql_public '),('database','ON DATABASE postgres ')):
        commands = [line.strip() for line in output.decode().splitlines()
                    if line.lstrip().startswith(('GRANT ','REVOKE ')) and clause in line]
        result[kind] = {'archive_entries':counts[kind],'grant_statements':sum(c.startswith('GRANT ') for c in commands),
            'revoke_statements':sum(c.startswith('REVOKE ') for c in commands),
            'with_grant_option':sum('WITH GRANT OPTION' in c for c in commands),
            'revoke_grant_option':sum(c.startswith('REVOKE GRANT OPTION FOR ') for c in commands),
            'revoke_all':sum(c.startswith('REVOKE ALL ') for c in commands),
            'statement_hashes':[hashlib.sha256(c.encode()).hexdigest() for c in commands[:8]]}
    return result


def scoped_acl_inventory(acls):
    result = {}
    for kind,name in (('schemas','graphql_public'),('database','postgres')):
        selected = [row for row in acls[kind] or [] if row[0] == name]
        # Reuse the strict typed ACL validator, including identity uniqueness.
        rows_with_logical_acl([[name,None]],selected,1,1,2)
        result[kind] = selected
    return result


def missing_scoped_grants(backup_acls, recovered_acls, role_names):
    """Add only missing, owner-issued named-role grants on two fixed objects.

    Extra grants, grant-option changes, PUBLIC additions or delegated grantors
    are outside this measured recovery correction and fail before any write.
    """
    expected = scoped_acl_inventory(backup_acls)
    current = scoped_acl_inventory(recovered_acls)
    statements, count = [], 0
    def identifier(value):
        if not isinstance(value,str) or not value or '\x00' in value or len(value.encode()) > 63:
            raise RuntimeError('invalid_scoped_acl_role')
        return '"'+value.replace('"','""')+'"'
    for kind,name,owner,privileges,object_type in (
            ('schemas','graphql_public','supabase_admin',{'USAGE'},'SCHEMA'),
            ('database','postgres','postgres',{'CONNECT','CREATE','TEMPORARY'},'DATABASE')):
        left = rows_with_logical_acl([[name,None]],expected[kind],1,1,2)[0][1]
        right = rows_with_logical_acl([[name,None]],current[kind],1,1,2)[0][1]
        if len(left) != len(set(left)) or len(right) != len(set(right)) or Counter(right)-Counter(left):
            raise RuntimeError('scoped_acl_not_additive')
        for value in sorted((Counter(left)-Counter(right)).elements()):
            grantor,recipient,privilege,grant_option = json.loads(value)
            if (grantor != owner or recipient['public'] or recipient['role'] not in role_names
                    or privilege not in privileges or grant_option is not False):
                raise RuntimeError('unapproved_scoped_acl_delta')
            statements += ['SET SESSION AUTHORIZATION '+identifier(owner)+';',
                'GRANT '+privilege+' ON '+object_type+' '+identifier(name)+' TO '+identifier(recipient['role'])+';',
                'RESET SESSION AUTHORIZATION;']
            count += 1
    if count > 8:
        raise RuntimeError('scoped_acl_delta_bound')
    return ('BEGIN;\n'+'\n'.join(statements)+'\nCOMMIT;' if count else ''),count


def save_scoped_acl_backup(source):
    payload = {'schema_version':1,'source':source,
        'archive_sha256':hashlib.sha256(ARCHIVE.read_bytes()).hexdigest(),
        'roles_sha256':hashlib.sha256(ROLES.read_bytes()).hexdigest(),
        'acls':scoped_acl_inventory(BEFORE['acl_semantics'])}
    content = (json.dumps(payload,sort_keys=True,separators=(',',':'))+'\n').encode()
    private_file(ACL_BACKUP,content)
    DETAILS['scoped_acl_backup_sha256'] = hashlib.sha256(content).hexdigest()


def recover_scoped_acl_backup(recovered_acls):
    content = ACL_BACKUP.read_bytes()
    check('scoped_acl_backup_digest',hashlib.sha256(content).hexdigest() == DETAILS['scoped_acl_backup_sha256'])
    payload = json.loads(content)
    check('scoped_acl_backup_binding',set(payload) == {'schema_version','source','archive_sha256','roles_sha256','acls'}
        and payload['schema_version'] == 1 and payload['source'] == os.environ['EXPECTED_SOURCE']
        and payload['archive_sha256'] == hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
        and payload['roles_sha256'] == hashlib.sha256(ROLES.read_bytes()).hexdigest())
    statement,count = missing_scoped_grants(payload['acls'],recovered_acls,
        {role['rolname'] for role in roles('recovery')['roles']})
    # Validation covers the entire plan before the first write. sql's target
    # route is fixed to the already attested independent cluster, never source.
    if statement:
        sql('recovery',statement)
    DETAILS['scoped_acl_recovery'] = {'scope':'graphql_public schema and postgres database',
        'missing_owner_grants_applied':count,'extra_grants_removed':0,'grant_options_changed':0}
    check('scoped_acl_backup_restored',scoped_acl_inventory(acl_catalog('recovery')) == payload['acls'])


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
        SECTION = 'acl_semantics'
        result['acl_semantics'] = acl_catalog(database)
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
    check('private_mode_' + ('archive' if path == ARCHIVE else 'scoped_acl' if path == ACL_BACKUP else 'roles'), path.stat().st_mode & 0o777 == 0o600)


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


def split_graphql_prerequisites(toc):
    """Replay the archived vendor hook before extension creation; never omit IDs."""
    entries, ids = [], set()
    helper = 'FUNCTION extensions grant_pg_graphql_access() supabase_admin'
    trigger = 'EVENT TRIGGER - issue_pg_graphql_access supabase_admin'
    for line in toc.decode().splitlines():
        if not line or line.startswith(';'):
            continue
        match = re.fullmatch(r'(\d+);\s+\d+\s+\d+\s+(.+)',line)
        if not match or int(match[1]) in ids:
            raise RuntimeError('invalid_graphql_toc_entry')
        # An empty archive owner leaves a trailing separator (not an identifier).
        # Normalize comparison only; retain the exact original execution line.
        ids.add(int(match[1])); entries.append((int(match[1]),match[2].rstrip(),line))
    descriptions = [d for _,d,_ in entries]
    DETAILS['graphql_archive'] = {'helper_entries':descriptions.count(helper),
        'trigger_entries':descriptions.count(trigger),
        'extension_entries':descriptions.count('EXTENSION - pg_graphql'),
        'wrapper_declarations':sum(d.startswith('FUNCTION graphql_public graphql(') for d in descriptions),
        'trailing_separator_entries':sum(line != line.rstrip() for _,_,line in entries)}
    if (descriptions.count(helper) != 1 or descriptions.count(trigger) != 1
        or descriptions.count('EXTENSION - pg_graphql') != 1
        or any(d.startswith('FUNCTION graphql_public graphql(') for d in descriptions)):
        raise RuntimeError('unmeasured_graphql_archive_dependencies')
    # Preserve the original owner/definition via pg_restore, not handwritten SQL.
    before = [next(e for e in entries if e[1] == d) for d in (helper,trigger)]
    rest = [e for e in entries if e[1] not in (helper,trigger)]
    assert not ({i for i,_,_ in before} & {i for i,_,_ in rest})
    assert {i for i,_,_ in before+rest} == ids
    encode = lambda values: ('\n'.join(line for _,_,line in values)+'\n').encode()
    return encode(before), encode(rest), {'prerequisites':len(before),'remainder':len(rest)}


def graphql_source_contract():
    """Read source membership/owner/hook evidence before selecting this repair."""
    measured = sql('source', """select jsonb_build_object(
      'wrapper_extension',(select e.extname from pg_depend d join pg_extension e on e.oid=d.refobjid where d.classid='pg_proc'::regclass and d.objid=to_regprocedure('graphql_public.graphql(text,text,jsonb,jsonb)') and d.deptype='e'),
      'wrapper_owner',(select pg_get_userbyid(proowner) from pg_proc where oid=to_regprocedure('graphql_public.graphql(text,text,jsonb,jsonb)')),
      'helper_owner',(select pg_get_userbyid(proowner) from pg_proc where oid=to_regprocedure('extensions.grant_pg_graphql_access()')),
      'helper_definition',(select pg_get_functiondef(to_regprocedure('extensions.grant_pg_graphql_access()'))),
      'trigger_matches',(select evtfoid=to_regprocedure('extensions.grant_pg_graphql_access()') and evtevent='ddl_command_end' and evtenabled='O' and evttags=ARRAY['CREATE FUNCTION']::text[] and evtowner=(select oid from pg_roles where rolname='supabase_admin') from pg_event_trigger where evtname='issue_pg_graphql_access')
      );""")
    check('source_graphql_wrapper_is_extension_member', measured['wrapper_extension'] == 'pg_graphql')
    check('source_graphql_owners_and_hook_match', measured['wrapper_owner'] == BOOTSTRAP
          and measured['helper_owner'] == BOOTSTRAP and measured['trigger_matches'] is True
          and isinstance(measured['helper_definition'],str))
    DETAILS['graphql_bootstrap'] = {'source_extension_member':True,'source_owners_and_hook_match':True,
        'source_helper_definition_sha256':hashlib.sha256(measured['helper_definition'].encode()).hexdigest()}
    return measured


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
    result['private_files_removed'] = not ARCHIVE.exists() and not ROLES.exists() and not ACL_BACKUP.exists()
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
    check('private_paths_absent', not ARCHIVE.exists() and not ROLES.exists() and not ACL_BACKUP.exists())
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
    graphql_contract = graphql_source_contract()
    archive_toc = source_command('pg_restore --list',archive,phase='archive_toc')
    first, remaining, counts = partition_toc(archive_toc)
    graphql_prerequisites, remainder, graphql_counts = split_graphql_prerequisites(remaining)
    counts.update({'graphql_prerequisites':graphql_counts['prerequisites'],'remainder':graphql_counts['remainder']})
    check('archive_toc_full_disjoint_coverage', counts['all'] == counts['bootstrap']+counts['graphql_prerequisites']+counts['remainder'])
    DETAILS['archive_toc_coverage'] = counts
    DETAILS['graphql_bootstrap']['archive_wrapper_declaration_absent'] = True
    DETAILS['graphql_bootstrap']['archived_function_and_hook_reordered'] = True
    role_dump = prepare_roles(source_command('pg_dumpall -U supabase_admin --roles-only --no-role-passwords',phase='global_roles_dump'))
    check('only_expected_bootstrap_create_prehandled', b'CREATE ROLE' in role_dump and b'ALTER ROLE supabase_admin ' in role_dump)
    private_file(ROLES,role_dump)
    save_scoped_acl_backup(source)
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
    for name, content in (('bootstrap',first),('graphql-prerequisites',graphql_prerequisites),('remainder',remainder)):
        run(['docker','exec','--user','postgres','-i',TARGET_ID,'sh','-ec','umask 077; cat > /tmp/c5-'+name+'.list'],content,phase='private_toc_'+name)
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','-h','/tmp','-U','supabase_admin','-d','template1','--create','--exit-on-error','--use-list=/tmp/c5-bootstrap.list'],ARCHIVE.read_bytes(),phase='pg_restore_database_schemas')
    note_acl_stage('database_schemas')
    DETAILS['archive_acl_observations'] = archive_acl_observations(archive_toc)
    check('no_dummy_graphql_wrapper_before_extension', sql('recovery',"select to_jsonb(to_regprocedure('graphql_public.graphql(text,text,jsonb,jsonb)') is null);") is True)
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','-h','/tmp','-U','supabase_admin','-d','postgres','--exit-on-error','--use-list=/tmp/c5-graphql-prerequisites.list'],ARCHIVE.read_bytes(),phase='pg_restore_graphql_prerequisites')
    check('archived_graphql_hook_definition_exact', sql('recovery',"select to_jsonb(pg_get_functiondef(to_regprocedure('extensions.grant_pg_graphql_access()')));") == graphql_contract['helper_definition'])
    note_acl_stage('graphql_hook')
    for name, version, schema, owner in mixed:
        # pgmq is an explicitly measured non-superuser extension. Install under
        # its original role after source database/schema ACLs exist, then keep
        # its normal IF NOT EXISTS archive entry in the full remainder restore.
        check('pgmq_non_superuser_extension', sql('source',"select to_jsonb(not superuser) from pg_available_extension_versions where name='pgmq' and version='1.5.1';") is True)
        check('source_owner_has_database_create', sql('source',"select to_jsonb(has_database_privilege('postgres','postgres','CREATE'));") is True)
        check('recovered_owner_has_database_create', sql('recovery',"select to_jsonb(has_database_privilege('postgres','postgres','CREATE'));") is True)
        check('recovered_owner_has_schema_create', sql('recovery',"select to_jsonb(has_schema_privilege('postgres','pgmq','CREATE'));") is True)
        sql('recovery',"set session authorization postgres; create extension pgmq with schema pgmq version '1.5.1'; reset session authorization;")
    note_acl_stage('pgmq_bootstrap')
    run(['docker','exec','--user','postgres','-i',TARGET_ID,'pg_restore','-h','/tmp','-U','supabase_admin','-d','postgres','--exit-on-error','--use-list=/tmp/c5-remainder.list'],ARCHIVE.read_bytes(),phase='pg_restore_all_remaining_entries')
    check('scheduler_stays_disabled', sql('recovery',"select to_jsonb(current_setting('cron.launch_active_jobs')='off' and current_setting('listen_addresses')='');") is True)
    recovered = snapshot('recovery')
    note_acl_stage('full_archive',recovered['acl_semantics'])
    recover_scoped_acl_backup(recovered['acl_semantics'])
    recovered = snapshot('recovery')
    DETAILS['catalog_diagnostics'] = catalog_diagnostics(BEFORE,recovered)
    check('all_selected_rows_restored', recovered['rows'] == BEFORE['rows'])
    check('prior_functions_RLS_owners_ACLs_restored', catalog_contract_equal(BEFORE,recovered))
    for section in BEFORE['structure']['extra']:
        check('metadata_restored_' + section, metadata_contract_equal(BEFORE,recovered,section))
    check('roles_restored', recovered['roles'] == BEFORE['roles'])
    check('cron_definitions_restored', recovered['cron_jobs'] == BEFORE['cron_jobs'])
    state = json.loads(PRIVATE.read_text())
    set_replay_stage('sample_select')
    samples = sql('recovery',"select coalesce(jsonb_agg(s.request order by s.created_at,s.key),'[]'::jsonb) from (select jsonb_build_object('key',i.idempotency_key,'order_id',o.id,'amount',(i.request_payload->>'amount')::numeric,'method',i.request_payload->>'method','result',i.result,'actor',i.created_by,'paid',o.paid,'payments',(select count(*) from public.payments where order_id=o.id)) as request,i.created_at,i.idempotency_key as key from public.financial_idempotency i join public.orders o on o.id=(i.request_payload->>'order_id')::uuid where i.operation='order.debt.collect.v1' and i.result is not null and o.total-o.paid>=20 order by i.created_at,i.idempotency_key limit 129) s;")
    set_replay_stage('sample_actor_context')
    selected = select_replay_samples(samples,state['actors'])
    sample,actor = selected['active']
    blocked_sample,blocked_actor = selected['inactive']
    foreign = selected['foreign']
    DETAILS['sample_selection'] = selected['summary']
    check('restored_sample_found',isinstance(sample,dict))
    context = selected['active_context']
    check('restored_sample_context_shape',isinstance(context,dict) and set(context) == {'active','subject_matches'}
          and all(type(value) is bool for value in context.values()))
    DETAILS['sample_actor_context'] = context
    check('restored_sample_subject_matches',context['subject_matches'])
    check('restored_positive_actor_active',context['active'])
    set_replay_stage('inactive_replay')
    prior.rpc(blocked_actor,blocked_sample,'account_inactive')
    set_replay_stage('inactive_replay_rows')
    check('inactive_saved_replay_denial_atomic',prior.rows('recovery') == BEFORE['rows'])
    set_replay_stage('original_replay')
    check('restored_original_key_returns_original_result', prior.rpc(actor,sample) == sample['result'])
    set_replay_stage('original_replay_rows')
    check('replay_no_effect_on_relations', prior.rows('recovery') == BEFORE['rows'])
    set_replay_stage('foreign_replay')
    prior.rpc(foreign,sample,'forbidden_tenant')
    set_replay_stage('foreign_replay_rows')
    check('foreign_denial_atomic', prior.rows('recovery') == BEFORE['rows'])
    set_replay_stage('conflicting_replay')
    prior.rpc(actor,{**sample,'amount':sample['amount']+1},'idempotency_conflict')
    set_replay_stage('conflicting_replay_rows')
    check('payload_conflict_atomic', prior.rows('recovery') == BEFORE['rows'])
    fresh = {**sample,'key':str(uuid.uuid4()),'amount':20}
    set_replay_stage('new_payment')
    first = prior.rpc(actor,fresh)
    set_replay_stage('new_payment_replay')
    check('new_payment_replay_same_result', prior.rpc(actor,fresh) == first)
    set_replay_stage('new_payment_effect')
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

