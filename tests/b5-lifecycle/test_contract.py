"""Negative acceptance controls; no application/database execution."""
import unittest
from inventory import applied
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'account-lifecycle'))
from owner_closure_probe import explicit_inactive
from mcp_probe import account_tool_denial
import candidate_surface as surface
import shutil,tempfile,json as _json
import billing_probe
import candidate_evidence as evidence
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'g01-acceptance'))
import egress_trace
from live_probe import HarnessFailure

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

    def billing_root(self):
        root=Path(tempfile.mkdtemp(prefix='b5-billing-ref-'));self.addCleanup(shutil.rmtree,root)
        repo=Path(__file__).resolve().parents[2]
        for rel in ('supabase/migrations','changes/b4-app02'):
            shutil.copytree(repo/rel,root/rel)
        (root/'tests/g01-acceptance').mkdir(parents=True)
        shutil.copy2(repo/'tests/g01-acceptance/candidate-63-source.json',root/'tests/g01-acceptance/candidate-63-source.json')
        return root

    def test_billing_reference_is_pinned_final_definition(self):
        body=billing_probe.reviewed_final_body(self.billing_root())
        self.assertIn('FOR NO KEY UPDATE',body)
        self.assertEqual(len(billing_probe.REVIEWED_DELTA),5)

    def test_billing_reference_refuses_tampering(self):
        final=billing_probe.FINAL_DEFINITION
        cases={
          'final_body_extra_change':(final,lambda t:t.replace("ERRCODE='P0001'","ERRCODE='P0002'",1)),
          'final_bytes_unpinned':(final,lambda t:t+'\n-- trailing\n'),
          'b4_reference_drift':(billing_probe.B4_REFERENCE,lambda t:t.replace('FOR UPDATE','FOR SHARE',1)),
          'october_definition_drift':(billing_probe.OCTOBER_DEFINITION,lambda t:t.replace('FOR UPDATE','FOR SHARE',1)),
        }
        for name,(rel,mutate) in cases.items():
            with self.subTest(name):
                root=self.billing_root();f=root/rel;f.write_text(mutate(f.read_text()))
                with self.assertRaises(HarnessFailure):billing_probe.reviewed_final_body(root)

    def test_billing_delta_is_exact(self):
        repo=Path(__file__).resolve().parents[2]
        ref=billing_probe.function_body((repo/billing_probe.B4_REFERENCE).read_text())
        final=billing_probe.function_body((repo/billing_probe.FINAL_DEFINITION).read_text())
        self.assertEqual(billing_probe.body_delta(ref,final),billing_probe.REVIEWED_DELTA)
        for changed in (final.replace("ERRCODE='P0001'","ERRCODE='P0002'",1),final.replace('FOR NO KEY UPDATE','FOR UPDATE'),
                        final.replace('-- The UPDATE below','-- The update below'),final+'\nPERFORM 1;'):
            self.assertNotEqual(billing_probe.body_delta(ref,changed),billing_probe.REVIEWED_DELTA)

    def test_billing_reference_refuses_a_later_redefinition(self):
        root=self.billing_root()
        m=_json.loads((root/'tests/g01-acceptance/candidate-63-source.json').read_text())
        last=root/m['migration_ledger'][-1]['path']
        last.write_text(last.read_text()+'\n-- CREATE OR REPLACE FUNCTION public.apply_subscription_webhook(\n')
        with self.assertRaises(HarnessFailure):billing_probe.reviewed_final_body(root)

    def test_tool_response_outline_is_allowlisted_and_textless(self):
        secret='needle-'+'x'*24
        cases=[((200,{'result':{'isError':True,'content':[{'type':'text','text':'account_inactive'}]}},'list_products'),{'class':'tool_error_account_inactive','items':None}),
               ((200,{'result':{'isError':True,'content':[{'type':'text','text':secret}]}},'list_products'),{'class':'tool_error_other','items':None}),
               ((200,{'result':{'structuredContent':{'products':[{'name':secret},{'name':secret}]}}},'list_products'),{'class':'tool_success','items':2}),
               ((200,{'result':{'structuredContent':{'summary':{'sales':1}}}},'today_summary'),{'class':'tool_success','items':None}),
               ((200,{'error':{'code':-32000,'message':secret}},'list_products'),{'class':'protocol_error','items':None}),
               ((200,[secret],'list_products'),{'class':'unexpected_shape','items':None}),
               ((401,{'error':secret},'list_products'),{'class':'non_200','items':None})]
        for args,expected in cases:
            with self.subTest(expected['class']):
                outline=evidence.tool_response_outline(*args)
                self.assertEqual(outline,expected);self.assertIn(outline['class'],evidence.RESPONSE_CLASSES)
                self.assertNotIn(secret,_json.dumps(outline))
        empty={'result':{'structuredContent':{'products':[]}}}
        self.assertFalse(account_tool_denial(200,empty,'list_products'))
        self.assertEqual(evidence.tool_response_outline(200,empty,'list_products'),{'class':'tool_success','items':0})

    def test_tool_response_outline_malformed_success_is_unexpected_shape(self):
        secret='needle-'+'y'*24
        malformed=[
            ('result_missing',{'jsonrpc':'2.0','id':1},'list_products'),
            ('result_null',{'result':None},'list_products'),
            ('result_list',{'result':[{'products':[]}]},'list_products'),
            ('result_string',{'result':secret},'list_products'),
            ('structured_missing',{'result':{'content':[{'type':'text','text':secret}]}},'list_products'),
            ('structured_null',{'result':{'structuredContent':None}},'list_products'),
            ('structured_list',{'result':{'structuredContent':[{'name':secret}]}},'list_products'),
            ('structured_wrong_key',{'result':{'structuredContent':{'customers':[]}}},'list_products'),
            ('structured_wrong_type',{'result':{'structuredContent':{'products':{'name':secret}}}},'list_products'),
            ('summary_without_sales',{'result':{'structuredContent':{'summary':{'total':1}}}},'today_summary'),
            ('summary_list',{'result':{'structuredContent':{'summary':[1]}}},'today_summary'),
            ('isError_truthy_non_bool',{'result':{'isError':'true','structuredContent':{'products':[]}}},'list_products'),
            ('isError_one',{'result':{'isError':1,'content':[{'type':'text','text':'account_inactive'}]}},'list_products'),
            ('unknown_tool',{'result':{'structuredContent':{'products':[]}}},'drop_tables'),
        ]
        for label,body,name in malformed:
            with self.subTest(label):
                outline=evidence.tool_response_outline(200,body,name)
                self.assertEqual(outline,{'class':'unexpected_shape','items':None})
                self.assertNotIn(secret,_json.dumps(outline))
                self.assertFalse(account_tool_denial(200,body,name))
        # Well-formed successes still classify, with isError absent or explicitly false.
        for body,name,items in [({'result':{'structuredContent':{'products':[{},{}]}}},'list_products',2),
                                ({'result':{'isError':False,'structuredContent':{'orders':[]}}},'list_recent_orders',0),
                                ({'result':{'structuredContent':{'summary':{'sales':0}}}},'today_summary',None)]:
            self.assertEqual(evidence.tool_response_outline(200,body,name),{'class':'tool_success','items':items})

    def test_unfinished_outline_matches_historical_count_without_detail(self):
        self.assertEqual(set(evidence.TRACED_CALLS),egress_trace.CALLS)
        texts={'killed_mid_connect':('12<node> 1700000000.1 connect(21, {sa_family=AF_INET, sin_port=htons(443), sin_addr=inet_addr("192.0.2.7")}, 16 <unfinished ...>\n'
                                     '13<node> 1700000000.2 recvfrom_like(5, 0x1 <unfinished ...>\n12<node> 1700000000.3 +++ killed by SIGTERM +++\n'),
               'resumed':'12<node> 1700000000.1 connect(21, 0x1 <unfinished ...>\n12<node> 1700000000.2 <... connect resumed>) = -1 EINPROGRESS (x)\n',
               'none':'12<node> 1700000000.1 sendto(21, "x", 1, 0, NULL, 0) = 1\n'}
        expected={'killed_mid_connect':{'unfinished_calls':2,'unfinished_call_names':{'connect':1,'other':1},'unfinished_calls_then_thread_exited':1},
                  'resumed':{'unfinished_calls':0,'unfinished_call_names':{},'unfinished_calls_then_thread_exited':0},
                  'none':{'unfinished_calls':0,'unfinished_call_names':{},'unfinished_calls_then_thread_exited':0}}
        for name,text in texts.items():
            with self.subTest(name):
                outline=evidence.unfinished_outline(text)
                self.assertEqual(outline,expected[name])
                self.assertEqual(outline['unfinished_calls'],egress_trace.sanitize_syscalls(text)['unfinished_calls'])
                self.assertNotIn('192.0.2.7',_json.dumps(outline))

    def test_composed_attaches_outline_only_to_closure_denials(self):
        import composed
        probe=object.__new__(composed.ComposedProbe)
        probe.controls=[];probe.source='x'*40
        probe.evidence_dir=Path(tempfile.mkdtemp(prefix='b5-outline-'));self.addCleanup(shutil.rmtree,probe.evidence_dir)
        outline={'class':'tool_success','items':0}
        probe._last_tool_outline=dict(outline)
        with self.assertRaises(HarnessFailure):probe.record('old_full_route_denial_list_products',False,status=200)
        self.assertEqual(probe.controls[-1]['response'],outline)
        self.assertFalse(probe.controls[-1]['passed'])
        probe._last_tool_outline=dict(outline);probe.record('owner_ban_before_list_products',True,status=200)
        self.assertNotIn('response',probe.controls[-1])
        probe.record('old_full_route_denial_list_customers',True,status=200)
        self.assertNotIn('response',probe.controls[-1])

if __name__=='__main__':unittest.main()
