"""Negative acceptance controls; no application/database execution."""
import unittest
from inventory import applied
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'account-lifecycle'))
from owner_closure_probe import explicit_inactive
from mcp_probe import account_tool_denial
import candidate_surface as surface

class StrictEvidence(unittest.TestCase):
    def test_exact_ordered_versions_required(self):
        expected=[str(x) for x in range(50)]
        self.assertTrue(applied(expected,expected.copy()))
        for actual in (expected[:-1],expected[::-1],expected[:-1]+['foreign'],expected+['extra'],None,tuple(expected)):
            with self.subTest(actual_type=type(actual).__name__):
                with self.assertRaises(RuntimeError):applied(expected,actual)

    def test_generic_errors_expiry_and_empty_are_not_named_account_denial(self):
        self.assertTrue(explicit_inactive(403,{'code':'42501','message':'account_inactive'}))
        for code,body in [(500,{'code':'42501','message':'account_inactive'}),(401,{'code':'PGRST301'}),(200,[]),(403,{'code':'42501','message':'other'})]:
            self.assertFalse(explicit_inactive(code,body))

    def test_mcp_denial_requires_explicit_protocol_account_error(self):
        good={'result':{'isError':True,'content':[{'type':'text','text':'account_inactive'}]}}
        self.assertTrue(account_tool_denial(200,good,'list_products'))
        for code,body in [(500,good),(200,{'result':{'isError':False,'structuredContent':{'products':[]}}}),(401,{'error':'unauthorized'}),(200,{'result':{'isError':True,'content':[{'type':'text','text':'other'}]}})]:
            self.assertFalse(account_tool_denial(code,body,'list_products'))

    def test_stage_exact_public_surface(self):
        self.assertTrue(surface.public_matches(63,list(surface.PUBLIC23)))
        for names in (list(surface.PUBLIC22),sorted(surface.PUBLIC22+('foreign',)),sorted(surface.PUBLIC23+('extra',)),list(surface.PUBLIC23)[::-1]):
            self.assertFalse(surface.public_matches(63,names))
        self.assertTrue(surface.public_matches(41,list(surface.PUBLIC22)) and surface.public_matches(50,list(surface.PUBLIC22)))
        self.assertFalse(surface.public_matches(50,list(surface.PUBLIC23)))
        self.assertEqual(surface.public_count(63),23)
        for count in (0,49,51,62,64):
            with self.assertRaises(RuntimeError):surface.public_matches(count,list(surface.PUBLIC23))

    def test_sale_surface_and_keyed_body(self):
        good=surface.EXPECTED_SALE_SURFACE[63]
        self.assertTrue(surface.sale_surface_ok(63,dict(good)))
        for key,value in [('legacy',{'anon':False,'authenticated':True}),('v2',{'anon':False,'authenticated':True}),
                          ('keyed',{'anon':True,'authenticated':True}),('keyed','absent'),('legacy','absent')]:
            self.assertFalse(surface.sale_surface_ok(63,{**good,key:value}))
        self.assertTrue(surface.sale_surface_ok(41,{'legacy':{'anon':False,'authenticated':True},'v2':'absent','keyed':'absent'}))
        self.assertFalse(surface.sale_surface_ok(41,{'legacy':{'anon':False,'authenticated':True},'v2':'absent','keyed':good['keyed']}))
        self.assertEqual((surface.sale_rpc(41),surface.sale_rpc(63)),(surface.LEGACY_SALE,surface.KEYED_SALE))
        payload={'p_customer_id':None,'p_paid':25}
        a,b=surface.sale_body(surface.KEYED_SALE,payload),surface.sale_body(surface.KEYED_SALE,payload)
        self.assertNotEqual(a['p_idempotency_key'],b['p_idempotency_key'])
        self.assertEqual(set(a)-set(payload),{'p_idempotency_key','p_courier_state'})
        self.assertEqual(surface.sale_body(surface.LEGACY_SALE,payload),payload)
        with self.assertRaises(RuntimeError):surface.sale_body('create_sale_with_items_v2',payload)

    def test_idempotency_ledger_locked(self):
        rights={r+':'+x:False for r in ('anon','authenticated') for x in ('SELECT','INSERT','UPDATE','DELETE','TRUNCATE','REFERENCES','TRIGGER')}
        self.assertTrue(surface.idempotency_locked({'rls':True,'policies':0,'client_rights':rights}))
        for bad in [{'rls':False,'policies':0,'client_rights':rights},{'rls':True,'policies':1,'client_rights':rights},
                    {'rls':True,'policies':0,'client_rights':{**rights,'authenticated:SELECT':True}},
                    {'rls':True,'policies':0,'client_rights':{k:v for k,v in list(rights.items())[:13]}},None]:
            self.assertFalse(surface.idempotency_locked(bad))

if __name__=='__main__':unittest.main()
