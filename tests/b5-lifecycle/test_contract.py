"""Negative acceptance controls; no application/database execution."""
import unittest
from inventory import applied
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'account-lifecycle'))
from owner_closure_probe import explicit_inactive
from mcp_probe import account_tool_denial

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

if __name__=='__main__':unittest.main()
