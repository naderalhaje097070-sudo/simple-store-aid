"""Focused evidence-oracle tests, no DB, tokens or lifecycle actions."""
import copy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from owner_catalog_probe import CatalogProbe, HarnessFailure, reconcile, source_expectations, validated_inventory


def fixture():
    expected=dict(source_map=dict(public_fk_source_edges=[dict(child='public.tenants',column='owner_user_id',
        parent='auth.users',parent_column='id',on_delete='CASCADE',path='source.sql',line=1)],
        source_trigger_declarations=[],function_definition_chain={}),functions=[],checks=[])
    catalog=dict(fks=[dict(name='owner_fk',child='public.tenants',child_columns=['owner_user_id'],parent='auth.users',
        parent_columns=['id'],on_delete='CASCADE')],triggers=[],functions=[],constraints=[],relations=[],policies=[])
    return expected,catalog,dict(policies=[],table_grants=[])


class OracleTests(unittest.TestCase):
    def test_exact_reviewed_manifest(self):
        x=source_expectations()
        self.assertEqual(len(x['migration_sha256']),43)
        self.assertEqual(len(x['source_map']['public_fk_source_edges']),30)
        self.assertEqual(len(x['source_map']['source_trigger_declarations']),14)
        self.assertFalse(any(f['name']=='public.__test_force_delete_e2e_order' for f in x['functions']))

    def test_fk_match(self):
        self.assertEqual(reconcile(*fixture())[0]['status'],'MATCH')

    def test_missing_fk_not_pass(self):
        e,c,p=fixture();c['fks']=[]
        self.assertEqual(reconcile(e,c,p)[0]['status'],'DIFFERENCE')

    def test_wrong_delete_action(self):
        e,c,p=fixture();c['fks'][0]['on_delete']='RESTRICT'
        self.assertEqual(reconcile(e,c,p)[0]['status'],'DIFFERENCE')

    def test_wrong_composite_reference(self):
        e,c,p=fixture();c['fks'][0]['child_columns'].append('tenant_id')
        self.assertEqual(reconcile(e,c,p)[0]['status'],'DIFFERENCE')

    def test_extra_public_fk_visible(self):
        e,c,p=fixture();c['fks'].append(dict(child='public.orders',child_columns=['x'],name='extra'))
        self.assertEqual(reconcile(e,c,p)[1]['kind'],'FK_EXTRA')

    def test_missing_catalog_not_accepted(self):
        with self.assertRaises(HarnessFailure):validated_inventory({})

    def test_nonreadonly_catalog_not_accepted(self):
        c={k:[] for k in ('schemas','fks','constraints','columns','triggers','functions','relations','policies',
                         'roles','memberships','schema_privileges','default_acls','migration_versions')}
        c['settings']=dict(transaction_read_only='off')
        c['schemas']=['auth','public','storage','monjez_private']
        with self.assertRaises(HarnessFailure):validated_inventory(c)

    def test_disabled_trigger_visible(self):
        e,c,p=fixture()
        e['source_map']['source_trigger_declarations']=[dict(name='audit',declaration='AFTER DELETE ON public.orders FOR EACH ROW',function='public.audit',path='source.sql',line=2)]
        c['triggers']=[dict(name='audit',relation='public.orders',function='public.audit',internal=False,enabled='D',type_bits=9)]
        self.assertEqual(reconcile(e,c,p)[1]['status'],'DIFFERENCE')

    def test_wrong_function_body_visible(self):
        e,c,p=fixture();e['functions']=[dict(name='public.audit',body='BEGIN RETURN OLD; END',definer=True,path='source.sql',line=3)]
        c['functions']=[dict(name='public.audit',body='BEGIN RETURN NEW; END',definer=True,arguments='',config=[],execute={})]
        self.assertEqual(reconcile(e,c,p)[1]['status'],'DIFFERENCE')

    def test_http_calls_forbidden(self):
        with self.assertRaises(HarnessFailure):CatalogProbe.__new__(CatalogProbe).request('DELETE','/auth/v1/admin/users/x')

    def test_literal_whitespace_is_semantically_significant(self):
        e,c,p=fixture();e['functions']=[dict(name='public.audit',body="BEGIN RAISE EXCEPTION 'a b'; END",definer=True,path='source.sql',line=3)]
        c['functions']=[dict(name='public.audit',body="BEGIN RAISE EXCEPTION 'ab'; END",definer=True,arguments='',config=[],execute={})]
        self.assertEqual(reconcile(e,c,p)[1]['status'],'DIFFERENCE')

    def test_sql_uses_readonly_uid_boundary(self):
        from write_harness_guard import WriteHarnessConfig
        probe=CatalogProbe.__new__(CatalogProbe)
        probe.config=WriteHarnessConfig('ci','http://127.0.0.1:54321','placeholder','127.0.0.1','54322','postgres','postgres')
        with patch('owner_catalog_probe.subprocess.run') as run:
            run.return_value.returncode=0;run.return_value.stdout='{}'
            self.assertEqual(probe.sql('SELECT 1;'),'{}')
            args,kwargs=run.call_args
            self.assertEqual(args[0][:3],['sudo','-u','mcp-route'])
            self.assertIn('default_transaction_read_only=on',' '.join(args[0]))
            self.assertTrue(kwargs['input'].startswith('BEGIN READ ONLY;'))


if __name__=='__main__':unittest.main()
