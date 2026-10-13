"""Focused privilege-delta regressions; no database, data DML or client identity switch."""
import copy
import unittest
from truncate_probe import TABLES, TEMPLATE, HarnessFailure, validate_privilege_delta, validate_sql, remove_client_truncate


def fixture():
    b={'identity':{'current_user':'postgres','session_user':'postgres'},'table_acl':[],
       'table_matrix':[],'default_acl':[]}
    for table in TABLES:
        for role in ('anon','authenticated','postgres','service_role'):
            truncate=role in ('postgres','service_role') or (role=='authenticated' and table!='public.tenant_counters')
            b['table_matrix'].append(dict(relation=table,role=role,rights={'SELECT':True,'DELETE':False,'TRUNCATE':truncate}))
            if truncate:b['table_acl'].append(dict(relation=table,grantee=role,privilege='TRUNCATE'))
    b['default_acl']=[dict(creator='postgres',schema='public',object_type='r',grantee='authenticated',privilege='TRUNCATE'),
                      dict(creator='postgres',schema='storage',object_type='r',grantee='authenticated',privilege='TRUNCATE')]
    a=copy.deepcopy(b)
    a['table_acl']=[r for r in a['table_acl'] if r['grantee'] not in ('anon','authenticated','PUBLIC')]
    a['default_acl']=a['default_acl'][1:]
    for r in a['table_matrix']:
        if r['role'] in ('anon','authenticated'):r['rights']['TRUNCATE']=False
    return b,a


class PermissionOracle(unittest.TestCase):
    def test_only_target_privilege_delta(self):self.assertTrue(validate_privilege_delta(*fixture()))
    def test_missing_target_table_pair_fails(self):
        b,a=fixture();a['table_matrix'].pop()
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_inherited_client_permission_fails(self):
        b,a=fixture();next(r for r in a['table_matrix'] if r['role']=='authenticated')['rights']['TRUNCATE']=True
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_service_permission_change_fails(self):
        b,a=fixture();next(r for r in a['table_matrix'] if r['role']=='service_role')['rights']['TRUNCATE']=False
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_owner_permission_change_fails(self):
        b,a=fixture();next(r for r in a['table_matrix'] if r['role']=='postgres')['rights']['TRUNCATE']=False
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_nontruncate_permission_change_fails(self):
        b,a=fixture();a['table_matrix'][0]['rights']['DELETE']=True
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_public_grant_remaining_fails(self):
        b,a=fixture();a['table_acl'].append(dict(relation=TABLES[0],grantee='PUBLIC',privilege='TRUNCATE'))
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_provider_default_acl_change_fails(self):
        b,a=fixture();a['default_acl']=[]
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_global_default_acl_change_fails(self):
        b,a=fixture();a['default_acl'].append(dict(creator='postgres',schema='<global>',object_type='r',grantee='authenticated',privilege='TRUNCATE'))
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_creator_identity_switch_fails(self):
        b,a=fixture();a['identity']['current_user']='service_role'
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_empty_matrix_fails(self):
        b,a=fixture();b['table_matrix']=a['table_matrix']=[]
        with self.assertRaises(HarnessFailure):validate_privilege_delta(b,a)
    def test_explicit_source_scope(self):self.assertTrue(validate_sql(TEMPLATE.read_text()))
    def test_destructive_statement_rejected(self):
        with self.assertRaises(HarnessFailure):validate_sql(TEMPLATE.read_text()+'\nTRUNCATE public.orders;')
    def test_revoke_all_rejected(self):
        with self.assertRaises(HarnessFailure):validate_sql(TEMPLATE.read_text().replace('REVOKE TRUNCATE','REVOKE ALL'))
    def test_global_default_change_rejected(self):
        with self.assertRaises(HarnessFailure):validate_sql(TEMPLATE.read_text().replace('FOR ROLE postgres IN SCHEMA public','FOR ROLE postgres'))
    def test_raw_acl_only_clients_lose_truncate(self):
        self.assertEqual(remove_client_truncate('{postgres=arwdDxtm/postgres,authenticated=arwdDxtm/postgres,service_role=arwdDxtm/postgres}'),
            '{postgres=arwdDxtm/postgres,authenticated=arwdxtm/postgres,service_role=arwdDxtm/postgres}')


if __name__=='__main__':unittest.main()
