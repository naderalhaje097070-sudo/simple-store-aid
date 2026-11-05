"""Safety boundaries, failure cleanup and bounded privacy; native proof is separate."""
import copy
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('independent_restore', Path(__file__).with_name('restore.py'))
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class RecoverySafety(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.patches = [patch.object(r,'ARCHIVE',root/'archive'),patch.object(r,'ROLES',root/'roles'),
                        patch.object(r,'ACL_BACKUP',root/'scoped-acl.json',create=True),
                        patch.object(r,'OUTDIR',root/'evidence'),patch.object(r,'CREATED_FILES',set()),
                        patch.object(r,'CHECKS',[]),patch.object(r,'DETAILS',{}),patch.object(r,'BEFORE',None),
                        patch.object(r,'TARGET_ID','b'*64),patch.object(r,'SECTION','none'),patch.dict(os.environ,{'EXPECTED_SOURCE':'a'*40})]
        for p in self.patches: p.start()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        self.tmp.cleanup()

    def info(self):
        return {'Id':'b'*64,'Name':'/'+r.TARGET,'Image':'sha256:'+'c'*64,
                'Config':{'Labels':{r.LABEL:'a'*40},'User':'postgres'},
                'HostConfig':{'NetworkMode':'none','PortBindings':{},'Binds':None,'ReadonlyRootfs':True},
                'NetworkSettings':{'Ports':{}},'Mounts':[]}

    def validate(self,info):
        return r.validate_target(info,'d'*64,'sha256:'+'c'*64,'a'*40)

    def test_distinct_bound_target(self): self.assertTrue(self.validate(self.info()))

    def test_reject_source_reuse_image_or_owner_change(self):
        for key,value in [('Id','d'*64),('Image','sha256:'+'e'*64),('Name','/'+r.SOURCE)]:
            i=self.info();i[key]=value;self.assertFalse(self.validate(i))
        i=self.info();i['Config']['Labels'][r.LABEL]='other';self.assertFalse(self.validate(i))

    def test_reject_network_ports_mounts_or_root(self):
        for section,key,value in [('HostConfig','NetworkMode','bridge'),('HostConfig','PortBindings',{'5432/tcp':[{}]}),
                                  ('HostConfig','Binds',['/source:/target']),('HostConfig','ReadonlyRootfs',False),
                                  ('NetworkSettings','Ports',{'5432/tcp':[{'HostPort':'5432'}]}),('Config','User','root')]:
            i=self.info();i[section][key]=value;self.assertFalse(self.validate(i))
        i=self.info();i['Mounts']=[{'Source':'/source'}];self.assertFalse(self.validate(i))

    def test_image_exposed_port_without_binding_is_not_published(self):
        i=self.info();i['NetworkSettings']['Ports']={'5432/tcp':None}
        self.assertTrue(self.validate(i))

    def test_only_private_tmpfs_mounts_allowed(self):
        i=self.info();i['Mounts']=[{'Type':'tmpfs','Destination':'/tmp'}, {'Type':'tmpfs','Destination':'/etc/postgresql-custom'}]
        self.assertTrue(self.validate(i))
        for mount in [{'Type':'bind','Destination':'/tmp'}, {'Type':'volume','Destination':'/etc/postgresql-custom'}, {'Type':'tmpfs','Destination':'/unreviewed'}]:
            i=self.info();i['Mounts']=[mount];self.assertFalse(self.validate(i))

    def test_private_exclusive_files(self):
        r.private_file(r.ARCHIVE,b'synthetic-private')
        self.assertEqual(r.ARCHIVE.stat().st_mode & 0o777,0o600)
        with self.assertRaises(FileExistsError): r.private_file(r.ARCHIVE,b'replace')
        self.assertEqual(r.ARCHIVE.read_bytes(),b'synthetic-private')

    def test_cleanup_wrong_identity_never_removes_target(self):
        i=self.info();i['Config']['Labels'][r.LABEL]='other'
        with patch.object(r,'target_info',return_value=i),patch.object(r,'run') as command:
            with self.assertRaises(RuntimeError): r.cleanup()
            command.assert_not_called()

    def test_cleanup_failure_keeps_false_receipt(self):
        with (patch.object(r,'main',side_effect=RuntimeError('injected_after_global_roles')),
              patch.object(r,'cleanup',side_effect=RuntimeError('resource_boundary'))):
            self.assertEqual(r.execute(),2)
        receipt=json.loads((r.OUTDIR/'independent-restore-result.json').read_text())
        self.assertFalse(receipt['restored']);self.assertFalse(receipt['cleanup']['verified'])

    def test_failure_removes_owned_files_and_target_checks_source(self):
        def failed():
            r.private_file(r.ARCHIVE,b'private');r.private_file(r.ROLES,b'private')
            r.BEFORE={'synthetic':'snapshot'}
            raise RuntimeError('injected_after_global_roles')
        with patch.object(r,'main',side_effect=failed),patch.object(r,'target_info',return_value=self.info()),patch.object(r,'snapshot',return_value={'synthetic':'snapshot'}),patch.object(r,'run',return_value=b'') as command:
            self.assertEqual(r.execute(),2)
            self.assertTrue(any(call.args[0][:3]==['docker','rm','-f'] for call in command.call_args_list))
        receipt=json.loads((r.OUTDIR/'independent-restore-result.json').read_text())
        self.assertFalse(receipt['restored']);self.assertTrue(all(receipt['cleanup'].values()))
        self.assertFalse(r.ARCHIVE.exists());self.assertFalse(r.ROLES.exists())

    def test_source_change_prevents_success(self):
        with patch.object(r,'main'),patch.object(r,'cleanup',return_value={'private_files_removed':True,'target_removed':True,'source_unchanged':False}):
            self.assertEqual(r.execute(),2)
        self.assertFalse(json.loads((r.OUTDIR/'independent-restore-result.json').read_text())['restored'])

    def test_nonruntime_exception_details_withheld(self):
        with (patch.object(r,'main',side_effect=ValueError('synthetic-secret-value')),
              patch.object(r,'cleanup',return_value={'private_files_removed':True,'target_removed':True,'source_unchanged':True})):
            self.assertEqual(r.execute(),2)
        raw=(r.OUTDIR/'independent-restore-result.json').read_text()
        self.assertNotIn('synthetic-secret-value',raw)

    def test_command_error_never_publishes_arbitrary_stderr(self):
        result=subprocess.CompletedProcess(['fake'],1,b'private-stdout',b'pg_restore: error: role synthetic_secret_value permission denied')
        with patch.object(r.subprocess,'run',return_value=result):
            with self.assertRaises(RuntimeError) as failure: r.run(['fake'],phase='pg_restore_full')
        self.assertNotIn('synthetic_secret_value',str(failure.exception))
        self.assertNotIn('private-stdout',str(failure.exception))
        self.assertIn('permission denied',str(failure.exception))

    def test_toc_partition_covers_every_entry_once(self):
        toc=b'''; private archive comment
1; 1262 1 DATABASE - postgres supabase_admin
2; 0 0 DATABASE PROPERTIES - postgres supabase_admin
3; 2615 2 SCHEMA - pgmq postgres
4; 0 0 ACL - DATABASE postgres supabase_admin
5; 0 0 ACL - SCHEMA pgmq postgres
6; 3079 3 EXTENSION - pgmq
7; 1259 4 TABLE public orders postgres
8; 0 4 TABLE DATA public orders postgres
9; 0 4 ACL public TABLE orders postgres
'''
        first,rest,counts=r.partition_toc(toc)
        self.assertEqual(counts,{'all':9,'bootstrap':4,'remainder':5})
        self.assertIn(b'EXTENSION - pgmq',rest)
        self.assertIn(b'ACL - SCHEMA pgmq',rest)
        self.assertIn(b'TABLE DATA',rest)
        self.assertNotIn(b'TABLE DATA',first)
        self.assertEqual(set(first.splitlines()+rest.splitlines()),set(toc.splitlines()[1:]))

    def test_restore_error_known_vendor_routine_without_raw_query(self):
        raw = b'pg_restore: from TOC entry 17; 0 0 EVENT TRIGGER issue_x supabase_admin\npg_restore: error: could not execute query: ERROR:  function extensions.grant_pg_net_access() does not exist\nCommand was: private SQL synthetic_secret_value;'
        result = r.restore_error_metadata(raw)
        self.assertEqual(result['known_vendor_routine'], 'extensions.grant_pg_net_access')
        self.assertEqual(result['object_kind'], 'EVENT TRIGGER')
        self.assertEqual(result['toc_entry'], 17)
        self.assertNotIn('synthetic_secret_value', json.dumps(result))

    def test_restore_error_unknown_identifiers_withheld(self):
        result = r.restore_error_metadata(b'ERROR:  function private.synthetic_secret_value(text) does not exist\nCommand was: private SQL;')
        self.assertEqual(result['known_vendor_routine'], 'unrecognized_withheld')
        self.assertNotIn('synthetic_secret_value', json.dumps(result))
        self.assertNotIn('private', json.dumps(result))

    def test_restore_error_does_not_extract_values_or_sql(self):
        for raw in (b'ERROR: password authentication failed for user secret', b'function extensions.grant_pg_net_access() secret', b'ERROR: function "private"."secret"(text) does not exist'):
            self.assertEqual(r.restore_error_metadata(raw), {'missing_function': False})

    def test_toc_duplicate_or_unknown_lines_rejected(self):
        for toc in [b'1; 0 0 DATABASE - postgres owner\n1; 0 0 TABLE public x owner\n',b'not a toc entry\n']:
            with self.assertRaises(RuntimeError):r.partition_toc(toc)

    def test_toc_requires_both_partitions(self):
        for toc in [b'1; 0 0 DATABASE - postgres owner\n',b'2; 0 0 TABLE public x owner\n']:
            with self.assertRaises(RuntimeError):r.partition_toc(toc)

    def test_only_known_bootstrap_create_is_prehandled(self):
        original=b'CREATE ROLE supabase_admin;\nALTER ROLE supabase_admin WITH SUPERUSER;\nCREATE ROLE postgres;\nGRANT postgres TO supabase_admin;\n'
        self.assertEqual(r.prepare_roles(original),b'ALTER ROLE supabase_admin WITH SUPERUSER;\nCREATE ROLE postgres;\nGRANT postgres TO supabase_admin;\n')

    def test_bootstrap_create_missing_or_duplicate_fails(self):
        for data in [b'CREATE ROLE postgres;\n',b'CREATE ROLE supabase_admin;\nCREATE ROLE supabase_admin;\n']:
            with self.assertRaises(RuntimeError):r.prepare_roles(data)

    def test_role_alterations_and_grants_preserved_exact(self):
        tail=b'ALTER ROLE supabase_admin WITH NOSUPERUSER;\nALTER ROLE postgres SET statement_timeout TO 10;\nGRANT pg_monitor TO postgres;\n'
        self.assertEqual(r.prepare_roles(b'CREATE ROLE supabase_admin;\n'+tail),tail)

    def graphql_toc(self):
        return b'''1; 3079 1 EXTENSION - pg_graphql
2; 1255 2 FUNCTION extensions grant_pg_graphql_access() supabase_admin
3; 0 0 COMMENT extensions FUNCTION grant_pg_graphql_access() supabase_admin
4; 0 0 ACL graphql_public FUNCTION graphql(text, text, jsonb, jsonb) supabase_admin
5; 3466 3 EVENT TRIGGER - issue_pg_graphql_access supabase_admin
6; 1259 4 TABLE public orders postgres
7; 0 4 TABLE DATA public orders postgres
8; 0 0 DEFAULT ACL graphql DEFAULT PRIVILEGES FOR FUNCTIONS supabase_admin
'''

    def test_graphql_prerequisites_move_only_original_function_and_trigger(self):
        first, rest, counts = r.split_graphql_prerequisites(self.graphql_toc())
        self.assertEqual(counts, {'prerequisites': 2, 'remainder': 6})
        self.assertIn(b'FUNCTION extensions grant_pg_graphql_access()', first)
        self.assertIn(b'EVENT TRIGGER - issue_pg_graphql_access', first)
        for item in (b'EXTENSION - pg_graphql', b'COMMENT', b'ACL graphql_public', b'TABLE DATA', b'DEFAULT ACL'):
            self.assertIn(item, rest)
        self.assertEqual(set(first.splitlines()) | set(rest.splitlines()), set(self.graphql_toc().splitlines()))
        self.assertFalse(set(first.splitlines()) & set(rest.splitlines()))

    def test_graphql_prerequisites_missing_or_duplicate_objects_fail(self):
        for excluded in (b'FUNCTION extensions grant_pg_graphql_access()', b'EVENT TRIGGER - issue_pg_graphql_access', b'EXTENSION - pg_graphql'):
            data=b'\n'.join(line for line in self.graphql_toc().splitlines() if excluded not in line)+b'\n'
            with self.assertRaises(RuntimeError): r.split_graphql_prerequisites(data)
        with self.assertRaises(RuntimeError):
            r.split_graphql_prerequisites(self.graphql_toc()+b'9; 3466 7 EVENT TRIGGER - issue_pg_graphql_access supabase_admin\n')

    def test_graphql_prerequisites_refuse_changed_owner_or_archive_wrapper(self):
        for data in (self.graphql_toc().replace(b'grant_pg_graphql_access() supabase_admin',b'grant_pg_graphql_access() postgres'),
                     self.graphql_toc().replace(b'issue_pg_graphql_access supabase_admin',b'issue_pg_graphql_access postgres'),
                     self.graphql_toc()+b'9; 1255 7 FUNCTION graphql_public graphql(text, text, jsonb, jsonb) supabase_admin\n'):
            with self.assertRaises(RuntimeError): r.split_graphql_prerequisites(data)

    def test_graphql_prerequisites_reject_duplicate_ids_or_malformed_input(self):
        for data in (self.graphql_toc()+b'1; 0 0 COMMENT - unrelated postgres\n', self.graphql_toc()+b'unrecognized private entry\n'):
            with self.assertRaises(RuntimeError): r.split_graphql_prerequisites(data)

    def test_graphql_toc_empty_owner_trailing_space_keeps_original_archive_line(self):
        toc=self.graphql_toc().replace(b'EXTENSION - pg_graphql\n',b'EXTENSION - pg_graphql \n')
        first,rest,counts=r.split_graphql_prerequisites(toc)
        self.assertEqual(counts, {'prerequisites':2,'remainder':6})
        self.assertIn(b'EXTENSION - pg_graphql \n',rest)
        self.assertEqual(set(first.splitlines()) | set(rest.splitlines()),set(toc.splitlines()))

    def catalog_fixture(self):
        return {'structure':{'prior_catalog':{
            'functions':[['public','synthetic_private_function','secret_argument text','private SQL body',True,['private_config=value'],'{owner=X/owner,user=X/owner}','private_owner']],
            'tables':[['public','synthetic_private_table',True,True,'{owner=arwdDxt/owner}','private_owner']],
            'policies':[{'schemaname':'public','tablename':'synthetic_private_table','policyname':'private_policy','permissive':'PERMISSIVE','roles':['private_role'],'cmd':'ALL','qual':'private SQL expression','with_check':'private check'}]},
            'extra':{'schemas':[['private_namespace','private_owner','private ACL']] }},
            'acl_semantics':{'functions':[['private grantor','private grantee','EXECUTE',False]],'tables':[['private grantor','private grantee','SELECT',False]]}}

    def test_catalog_diagnostic_equal_and_does_not_mutate_inputs(self):
        left=self.catalog_fixture();right=copy.deepcopy(left);saved=copy.deepcopy(left)
        result=r.catalog_diagnostics(left,right)
        self.assertTrue(result['literal_equal']);self.assertTrue(result['semantic_acl_equal'])
        self.assertEqual(left,saved);self.assertEqual(right,saved)

    def test_catalog_diagnostic_acl_representation_never_passes_literal_gate(self):
        left=self.catalog_fixture();right=copy.deepcopy(left)
        right['structure']['prior_catalog']['functions'][0][6]='{user=X/owner,owner=X/owner}'
        result=r.catalog_diagnostics(left,right)
        self.assertFalse(result['literal_equal']);self.assertTrue(result['semantic_acl_equal'])
        self.assertEqual(result['functions']['field_counts']['acl'],1)
        with self.assertRaises(RuntimeError):r.check('prior_functions_RLS_owners_ACLs_restored',result['literal_equal'])

    def test_catalog_diagnostic_owner_and_rls_differences_remain_visible(self):
        left=self.catalog_fixture();right=copy.deepcopy(left)
        right['structure']['prior_catalog']['functions'][0][7]='different_private_owner'
        right['structure']['prior_catalog']['tables'][0][2]=False
        result=r.catalog_diagnostics(left,right)
        self.assertFalse(result['literal_equal']);self.assertEqual(result['functions']['field_counts']['owner'],1)
        self.assertEqual(result['tables']['field_counts']['rls'],1)

    def test_catalog_diagnostic_grantor_grantee_privilege_and_option_retained(self):
        left=self.catalog_fixture()
        for index in range(4):
            right=copy.deepcopy(left);right['acl_semantics']['functions'][0][index]='different_private_value'
            result=r.catalog_diagnostics(left,right)
            self.assertFalse(result['semantic_acl_equal']);self.assertFalse(result['functions']['semantic_acl_equal'])

    def test_catalog_diagnostic_missing_added_and_order_only_objects(self):
        left=self.catalog_fixture();right=copy.deepcopy(left)
        extra=copy.deepcopy(left['structure']['prior_catalog']['functions'][0]);extra[1]='another_private_function'
        left['structure']['prior_catalog']['functions'].append(extra)
        right['structure']['prior_catalog']['functions']=[extra,right['structure']['prior_catalog']['functions'][0]]
        result=r.catalog_diagnostics(left,right)
        self.assertTrue(result['functions']['list_order_only']);self.assertFalse(result['literal_equal'])
        right['structure']['prior_catalog']['functions'].pop()
        result=r.catalog_diagnostics(left,right)
        self.assertEqual(result['functions']['missing_count'],1)

    def test_catalog_diagnostic_never_serializes_values_names_or_unknown_fields(self):
        left=self.catalog_fixture();right=copy.deepcopy(left)
        right['structure']['prior_catalog']['functions'][0][3]='another private SQL body'
        right['structure']['prior_catalog']['policies'][0]['qual']='another private expression'
        right['structure']['extra']['schemas']=[];right['structure']['extra']['unknown_private_section']='private value'
        result=r.catalog_diagnostics(left,right);serialized=json.dumps(result)
        for value in ('synthetic_private','private_owner','private SQL','private_policy','private expression','private_namespace','private_config','unknown_private'):
            self.assertNotIn(value,serialized)
        self.assertEqual(result['extra_different_sections'],['schemas'])
        self.assertTrue(all(len(h)==64 for h in result['functions']['changed_key_hashes']))

    def test_catalog_diagnostic_invalid_or_duplicate_shape_fails_closed(self):
        left=self.catalog_fixture();right=copy.deepcopy(left)
        right['structure']['prior_catalog']['functions'].append(copy.deepcopy(right['structure']['prior_catalog']['functions'][0]))
        with self.assertRaises(RuntimeError):r.catalog_diagnostics(left,right)
        right=copy.deepcopy(left);right['structure']['prior_catalog']['functions'][0].append('private unexpected')
        with self.assertRaises(RuntimeError):r.catalog_diagnostics(left,right)

    def logical_catalog_fixture(self):
        value=self.catalog_fixture()
        grant=['private_owner',{'public':False,'role':'private_role'},'SELECT',False]
        value['acl_semantics']={
            'functions':[['public','synthetic_private_function','secret_argument text',[['private_owner',{'public':False,'role':'private_role'},'EXECUTE',False]]]],
            'tables':[['public','synthetic_private_table',[grant]]],
            'schemas':[['private_namespace',[['private_owner',{'public':True,'role':None},'USAGE',False]]]],
            'database':[['postgres',[['private_owner',{'public':True,'role':None},'CONNECT',False]]]]}
        value['structure']['extra']['database']=['private_owner',6,'C.UTF-8','C.UTF-8','c',None,None,None,'private_database_acl']
        return value

    def test_logical_acl_representation_preserves_all_other_fields_and_raw_evidence(self):
        left=self.logical_catalog_fixture();right=copy.deepcopy(left)
        right['structure']['prior_catalog']['tables'][0][4]='another equivalent ACL representation'
        right['structure']['extra']['schemas'][0][2]='another equivalent schema ACL'
        right['structure']['extra']['database'][-1]='another equivalent database ACL'
        before=copy.deepcopy(left);after=copy.deepcopy(right)
        self.assertTrue(r.catalog_contract_equal(left,right))
        self.assertTrue(r.metadata_contract_equal(left,right,'schemas'))
        self.assertTrue(r.metadata_contract_equal(left,right,'database'))
        self.assertFalse(r.catalog_diagnostics(left,right)['literal_equal'])
        self.assertEqual(left,before);self.assertEqual(right,after)

    def test_logical_acl_owner_rls_and_forced_rls_changes_rejected(self):
        left=self.logical_catalog_fixture()
        for index,value in ((2,False),(3,False),(5,'another_private_owner')):
            right=copy.deepcopy(left);right['structure']['prior_catalog']['tables'][0][index]=value
            self.assertFalse(r.catalog_contract_equal(left,right))

    def test_logical_acl_function_and_policy_contracts_remain_exact(self):
        left=self.logical_catalog_fixture()
        for index in range(3,8):
            right=copy.deepcopy(left);right['structure']['prior_catalog']['functions'][0][index]='changed_private_value'
            self.assertFalse(r.catalog_contract_equal(left,right))
        for key in ('roles','cmd','qual','with_check','permissive'):
            right=copy.deepcopy(left);right['structure']['prior_catalog']['policies'][0][key]='changed_private_value'
            self.assertFalse(r.catalog_contract_equal(left,right))

    def test_logical_acl_grantor_grantee_privilege_and_option_changes_rejected(self):
        left=self.logical_catalog_fixture()
        for index,value in ((0,'another_private_grantor'),(1,{'public':False,'role':'another_private_role'}),(2,'UPDATE'),(3,True)):
            right=copy.deepcopy(left);right['acl_semantics']['tables'][0][-1][0][index]=value
            self.assertFalse(r.catalog_contract_equal(left,right))

    def test_logical_acl_public_is_distinct_from_a_role_named_like_public(self):
        left=self.logical_catalog_fixture();right=copy.deepcopy(left)
        left['acl_semantics']['tables'][0][-1][0][1]={'public':True,'role':None}
        right['acl_semantics']['tables'][0][-1][0][1]={'public':False,'role':'<PUBLIC>'}
        self.assertFalse(r.catalog_contract_equal(left,right))

    def test_logical_acl_schema_database_owner_locale_and_rights_remain_exact(self):
        left=self.logical_catalog_fixture()
        right=copy.deepcopy(left);right['structure']['extra']['schemas'][0][1]='another_private_owner'
        self.assertFalse(r.metadata_contract_equal(left,right,'schemas'))
        for index in range(8):
            right=copy.deepcopy(left);right['structure']['extra']['database'][index]='changed_private_value'
            self.assertFalse(r.metadata_contract_equal(left,right,'database'))
        for section in ('schemas','database'):
            right=copy.deepcopy(left);right['acl_semantics'][section][0][-1][0][3]=True
            self.assertFalse(r.metadata_contract_equal(left,right,section))

    def test_logical_acl_missing_duplicate_and_invalid_coverage_fail_closed(self):
        left=self.logical_catalog_fixture()
        for action in ('missing','duplicate','extra','invalid_public'):
            right=copy.deepcopy(left);rows=right['acl_semantics']['tables']
            if action=='missing':rows.clear()
            elif action=='duplicate':rows.append(copy.deepcopy(rows[0]))
            elif action=='extra':
                extra=copy.deepcopy(rows[0]);extra[1]='unmatched_private_table';rows.append(extra)
            else:rows[0][-1][0][1]={'public':1,'role':None}
            with self.assertRaises(RuntimeError):r.catalog_contract_equal(left,right)

    def test_logical_acl_order_preserved_as_multiset_and_no_rights_dropped(self):
        left=self.logical_catalog_fixture();right=copy.deepcopy(left)
        extra=['private_owner',{'public':False,'role':'other_private_role'},'UPDATE',True]
        left['acl_semantics']['tables'][0][-1].append(extra)
        right['acl_semantics']['tables'][0][-1].insert(0,copy.deepcopy(extra))
        self.assertTrue(r.catalog_contract_equal(left,right))
        right['acl_semantics']['tables'][0][-1].pop()
        self.assertFalse(r.catalog_contract_equal(left,right))

    def provenance_acl_fixture(self):
        return {'schemas':[['graphql_public',[['supabase_admin',{'public':False,'role':'postgres'},'USAGE',False]]]],
                'database':[['postgres',[['supabase_admin',{'public':False,'role':'authenticated'},'CONNECT',False]]]]}

    def test_scoped_grants_preserve_missing_extra_options_and_input_values(self):
        left=self.provenance_acl_fixture();right=copy.deepcopy(left)
        right['schemas'][0][-1][0][3]=True
        saved=copy.deepcopy(right);result=r.scoped_grant_delta(left,right)
        self.assertEqual(result['schemas']['missing_count'],1);self.assertEqual(result['schemas']['extra_count'],1)
        self.assertFalse(result['schemas']['missing'][0]['grant_option'])
        self.assertTrue(result['schemas']['extra'][0]['grant_option'])
        self.assertEqual(right,saved);self.assertEqual(result['database']['missing_count'],0)

    def test_scoped_grants_unknown_roles_and_privileges_never_exposed(self):
        left=self.provenance_acl_fixture();right=copy.deepcopy(left)
        right['schemas'][0][-1][0]=['private_secret_grantor',{'public':False,'role':'private_secret_role'},'PRIVATE_SECRET_PRIVILEGE',False]
        raw=json.dumps(r.scoped_grant_delta(left,right))
        for token in ('private_secret','PRIVATE_SECRET_PRIVILEGE'):
            self.assertNotIn(token,raw)
        self.assertIn('role_sha256',raw);self.assertIn('unknown_privilege_withheld',raw)

    def test_scoped_grants_public_and_named_role_are_distinct(self):
        left=self.provenance_acl_fixture();right=copy.deepcopy(left)
        right['database'][0][-1][0][1]={'public':True,'role':None}
        result=r.scoped_grant_delta(left,right)
        self.assertEqual(result['database']['extra'][0]['grantee'],{'public':True})
        self.assertEqual(result['database']['missing_count'],1)

    def test_scoped_grants_invalid_source_or_duplicate_target_fails(self):
        left=self.provenance_acl_fixture();right=copy.deepcopy(left)
        left['schemas']=[]
        with self.assertRaises(RuntimeError):r.scoped_grant_delta(left,right)
        left=self.provenance_acl_fixture();right=copy.deepcopy(left)
        right['schemas'].append(copy.deepcopy(right['schemas'][0]))
        with self.assertRaises(RuntimeError):r.scoped_grant_delta(left,right)

    def test_acl_stage_receipt_only_uses_fixed_stage_and_known_objects(self):
        acl=self.provenance_acl_fixture()
        with patch.object(r,'BEFORE',{'acl_semantics':acl}),patch.object(r,'acl_catalog') as query:
            r.note_acl_stage('full_archive',copy.deepcopy(acl));query.assert_not_called()
            with self.assertRaises(RuntimeError):r.note_acl_stage('unknown_private_stage',acl)
        self.assertEqual(set(r.DETAILS['grant_provenance']),{'full_archive'})

    def test_acl_archive_render_never_executes_or_emits_sql(self):
        toc=b'1; 0 0 ACL - SCHEMA graphql_public supabase_admin\n2; 0 0 ACL - DATABASE postgres supabase_admin\n3; 0 0 ACL public TABLE private_table postgres\n'
        commands=b'GRANT USAGE ON SCHEMA graphql_public TO private_secret_role WITH GRANT OPTION;\nREVOKE ALL ON DATABASE postgres FROM PUBLIC;\nGRANT CONNECT ON DATABASE postgres TO authenticated;\n'
        r.ARCHIVE.write_bytes(b'PGDMPsynthetic')
        with patch.object(r,'run',side_effect=[b'',commands]) as command:
            result=r.archive_acl_observations(toc)
        args=command.call_args_list[1].args[0]
        self.assertIn('--file=-',args);self.assertNotIn('-d',args)
        self.assertEqual(result['schemas']['with_grant_option'],1)
        self.assertEqual(result['database']['revoke_all'],1)
        self.assertNotIn('private_secret_role',json.dumps(result))
        self.assertNotIn('GRANT ',json.dumps(result))

    def test_acl_archive_no_entries_never_renders_unfiltered_archive(self):
        with patch.object(r,'run') as command:
            result=r.archive_acl_observations(b'1; 1259 1 TABLE public orders postgres\n')
            command.assert_not_called()
        self.assertEqual(result['schemas']['archive_entries'],0)
        with patch.object(r,'run') as command:
            with self.assertRaises(RuntimeError):
                r.archive_acl_observations(b'1; 0 0 ACL - DATABASE postgres owner\n2; 0 0 ACL - DATABASE postgres owner\n')
            command.assert_not_called()

    def recovery_acl_fixture(self):
        return {'schemas':[['graphql_public',[['supabase_admin',{'public':False,'role':'anon'},'USAGE',False]]]],
                'database':[['postgres',[['postgres',{'public':False,'role':'storage_role'},'CREATE',False]]]]}

    def test_scoped_recovery_only_adds_measured_grants_under_original_owners(self):
        left=self.recovery_acl_fixture();right=copy.deepcopy(left)
        for kind in right:right[kind][0][-1]=[]
        saved=copy.deepcopy(left)
        statement,count=r.missing_scoped_grants(left,right,{'anon','storage_role'})
        self.assertEqual(count,2);self.assertEqual(left,saved)
        self.assertIn('SET SESSION AUTHORIZATION "supabase_admin";',statement)
        self.assertIn('GRANT USAGE ON SCHEMA "graphql_public" TO "anon";',statement)
        self.assertIn('SET SESSION AUTHORIZATION "postgres";',statement)
        self.assertIn('GRANT CREATE ON DATABASE "postgres" TO "storage_role";',statement)
        self.assertTrue(statement.startswith('BEGIN;'));self.assertTrue(statement.endswith('COMMIT;'))
        self.assertNotIn('REVOKE',statement);self.assertNotIn('WITH GRANT OPTION',statement)
        self.assertEqual(r.missing_scoped_grants(left,left,{'anon','storage_role'}),('',0))

    def test_scoped_recovery_rejects_extra_duplicate_and_shifted_grant_options(self):
        left=self.recovery_acl_fixture()
        for mutation in ('extra','duplicate','option'):
            right=copy.deepcopy(left)
            if mutation=='extra':right['schemas'][0][-1].append(['supabase_admin',{'public':False,'role':'stranger'},'USAGE',False])
            elif mutation=='duplicate':right['schemas'][0][-1].append(copy.deepcopy(right['schemas'][0][-1][0]))
            else:right['schemas'][0][-1][0][3]=True
            with self.assertRaises(RuntimeError):r.missing_scoped_grants(left,right,{'anon','storage_role','stranger'})

    def test_scoped_recovery_rejects_public_delegated_missing_roles_and_unsupported_rights(self):
        for mutation in ('public','grantor','missing_role','privilege','option'):
            left=self.recovery_acl_fixture();right=copy.deepcopy(left);right['schemas'][0][-1]=[]
            grant=left['schemas'][0][-1][0]
            if mutation=='public':grant[1]={'public':True,'role':None}
            elif mutation=='grantor':grant[0]='delegate'
            elif mutation=='missing_role':grant[1]['role']='absent'
            elif mutation=='privilege':grant[2]='CREATE'
            else:grant[3]=True
            with self.assertRaises(RuntimeError):r.missing_scoped_grants(left,right,{'anon','storage_role'})

    def test_scoped_recovery_quotes_role_identifiers_and_never_interpolates_privileges(self):
        left=self.recovery_acl_fixture();right=copy.deepcopy(left);right['schemas'][0][-1]=[]
        name='role"; DROP SCHEMA public; --'
        left['schemas'][0][-1][0][1]['role']=name
        statement,count=r.missing_scoped_grants(left,right,{name,'storage_role'})
        self.assertEqual(count,1)
        self.assertIn('TO "role""; DROP SCHEMA public; --";',statement)
        for bad in ('','bad\x00role','r'*64):
            left['schemas'][0][-1][0][1]['role']=bad
            with self.assertRaises(RuntimeError):r.missing_scoped_grants(left,right,{bad,'storage_role'})

    def test_scoped_recovery_bounds_missing_grants_and_requires_both_objects(self):
        left=self.recovery_acl_fixture();right=copy.deepcopy(left);right['schemas'][0][-1]=[]
        names={'role'+str(n) for n in range(9)}
        left['schemas'][0][-1]=[['supabase_admin',{'public':False,'role':name},'USAGE',False] for name in names]
        with self.assertRaises(RuntimeError):r.missing_scoped_grants(left,right,names|{'storage_role'})
        for action in ('missing','duplicate'):
            left=self.recovery_acl_fixture();right=copy.deepcopy(left)
            if action=='missing':left['schemas']=[]
            else:left['database'].append(copy.deepcopy(left['database'][0]))
            with self.assertRaises(RuntimeError):r.missing_scoped_grants(left,right,{'anon','storage_role'})

    def save_acl_fixture(self):
        r.ARCHIVE.write_bytes(b'PGDMPsynthetic');r.ROLES.write_bytes(b'synthetic roles')
        r.CREATED_FILES.update({r.ARCHIVE,r.ROLES})
        r.BEFORE={'acl_semantics':self.recovery_acl_fixture()}
        r.save_scoped_acl_backup('a'*40)

    def test_scoped_backup_private_and_recovery_uses_backup_not_live_source(self):
        self.save_acl_fixture()
        self.assertEqual(r.ACL_BACKUP.stat().st_mode & 0o777,0o600)
        right=self.recovery_acl_fixture();right['schemas'][0][-1]=[]
        r.BEFORE=None
        inventory={'roles':[{'rolname':name} for name in ('anon','storage_role')]}
        with patch.object(r,'roles',return_value=inventory) as roles,patch.object(r,'sql') as sql,patch.object(r,'acl_catalog',return_value=self.recovery_acl_fixture()) as query:
            r.recover_scoped_acl_backup(right)
            roles.assert_called_once_with('recovery');query.assert_called_once_with('recovery')
            self.assertEqual(sql.call_count,1);self.assertEqual(sql.call_args.args[0],'recovery')
        self.assertEqual(r.DETAILS['scoped_acl_recovery']['missing_owner_grants_applied'],1)

    def test_scoped_backup_tampering_and_wrong_archive_roles_or_source_prevent_writes(self):
        for mutation in ('backup','archive','roles','source'):
            with self.subTest(mutation=mutation):
                r.ACL_BACKUP.unlink(missing_ok=True);r.CREATED_FILES.clear();self.save_acl_fixture()
                if mutation=='backup':r.ACL_BACKUP.write_bytes(r.ACL_BACKUP.read_bytes()+b' ')
                elif mutation=='archive':r.ARCHIVE.write_bytes(b'changed archive')
                elif mutation=='roles':r.ROLES.write_bytes(b'changed roles')
                else:os.environ['EXPECTED_SOURCE']='b'*40
                with patch.object(r,'sql') as sql,patch.object(r,'roles') as roles:
                    with self.assertRaises(RuntimeError):r.recover_scoped_acl_backup(self.recovery_acl_fixture())
                    sql.assert_not_called();roles.assert_not_called()
                os.environ['EXPECTED_SOURCE']='a'*40

    def test_scoped_backup_validation_finishes_before_any_grant(self):
        self.save_acl_fixture();right=self.recovery_acl_fixture()
        right['schemas'][0][-1]=[]
        right['database'][0][-1].append(['postgres',{'public':False,'role':'stranger'},'CONNECT',False])
        with patch.object(r,'roles',return_value={'roles':[{'rolname':'anon'},{'rolname':'storage_role'},{'rolname':'stranger'}]}),patch.object(r,'sql') as sql:
            with self.assertRaises(RuntimeError):r.recover_scoped_acl_backup(right)
            sql.assert_not_called()

    def test_scoped_backup_post_restore_mismatch_fails_and_cleanup_removes_sidecar(self):
        self.save_acl_fixture();right=self.recovery_acl_fixture();right['schemas'][0][-1]=[]
        with patch.object(r,'roles',return_value={'roles':[{'rolname':'anon'},{'rolname':'storage_role'}]}),patch.object(r,'sql'),patch.object(r,'acl_catalog',return_value=right):
            with self.assertRaises(RuntimeError):r.recover_scoped_acl_backup(right)
        with patch.object(r,'target_info',return_value=self.info()),patch.object(r,'run',return_value=b''),patch.object(r,'snapshot',return_value=r.BEFORE):
            clean=r.cleanup()
        self.assertTrue(clean['private_files_removed']);self.assertFalse(r.ACL_BACKUP.exists())


    def test_sql_failure_metadata_is_finite_and_withholds_raw_values(self):
        result=r.sql_error_metadata(b'ERROR:  42501: account_inactive\nCONTEXT: private_token secret SQL')
        self.assertEqual(result,{'sqlstate':'42501','domain_error':'account_inactive'})
        for raw in (b'ERROR: XX123: private_secret',b'ERROR: private_token secret',b'FATAL: private_token'):
            self.assertEqual(set(r.sql_error_metadata(raw).values()),{'unrecognized_withheld'})
        self.assertNotIn('private_',json.dumps(result))

    def test_replay_stage_rejects_arbitrary_identifiers(self):
        r.set_replay_stage('original_replay')
        self.assertEqual(r.DETAILS['replay_stage'],'original_replay');self.assertEqual(r.SECTION,'original_replay')
        with self.assertRaises(RuntimeError):r.set_replay_stage('private_customer_name')
        self.assertNotIn('private_customer_name',json.dumps(r.DETAILS))

    def test_sql_errors_capture_metadata_without_raw_stderr_or_sql(self):
        result=subprocess.CompletedProcess([],1,b'',b'ERROR:  P0001: idempotency_conflict\nprivate_token secret')
        with patch.object(r.subprocess,'run',return_value=result) as command:
            with self.assertRaises(RuntimeError):r.sql('recovery','private SQL payload')
        self.assertIn('VERBOSITY=verbose',command.call_args.args[0])
        self.assertEqual(r.DETAILS['sql_failure'],{'sqlstate':'P0001','domain_error':'idempotency_conflict'})
        self.assertNotIn('private',json.dumps(r.DETAILS))

    def test_sample_context_uses_real_guard_and_fixed_recovery_sql_role(self):
        subject='11111111-1111-4111-8111-111111111111'
        with patch.object(r.prior,'claims',return_value='synthetic_claims'),patch.object(r,'sql',return_value={'active':False,'subject_matches':True}) as sql:
            result=r.sample_actor_context({'uid':subject},{'actor':subject})
        self.assertFalse(result['active']);self.assertEqual(sql.call_args.args[0],'recovery')
        statement=sql.call_args.args[1]
        self.assertIn('set local role authenticated',statement);self.assertIn('monjez_private.actor_is_active()',statement)
        for word in ('update ','insert ','delete ','alter ','service_role'):
            self.assertNotIn(word,statement.lower())
        with patch.object(r,'sql') as sql:
            with self.assertRaises(ValueError):r.sample_actor_context({}, {'actor':'unsafe SQL'})
            sql.assert_not_called()

if __name__ == '__main__': unittest.main()

