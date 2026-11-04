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
                        patch.object(r,'OUTDIR',root/'evidence'),patch.object(r,'CREATED_FILES',set()),
                        patch.object(r,'CHECKS',[]),patch.object(r,'DETAILS',{}),patch.object(r,'BEFORE',None),
                        patch.object(r,'TARGET_ID','b'*64),patch.dict(os.environ,{'EXPECTED_SOURCE':'a'*40})]
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


if __name__ == '__main__': unittest.main()

