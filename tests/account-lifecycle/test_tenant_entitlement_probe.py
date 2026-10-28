"""Fail-closed denial oracle regressions: malformed errors are never security proof."""
import unittest
from tenant_entitlement_probe import safe_denial


class DenialOracle(unittest.TestCase):
    def test_permission_denial(self):
        self.assertTrue(safe_denial(403,{'code':'42501'}))
        self.assertTrue(safe_denial(401,{'code':'42501'}))

    def test_generic_failures_are_not_denial(self):
        for code,body in ((500,{'code':'42501'}),(400,{'code':'22P02'}),
                          (409,{'code':'23505'}),(403,{'code':'OTHER'}),(302,{}),(0,None)):
            with self.subTest(code=code):self.assertFalse(safe_denial(code,body,rls=True))

    def test_empty_requires_known_rls_path(self):
        self.assertFalse(safe_denial(200,[]))
        self.assertTrue(safe_denial(200,[],rls=True))

    def test_success_is_not_security_denial(self):
        for body in ([{'id':'known'}],True,{},None):
            self.assertFalse(safe_denial(200,body,rls=True))

    def test_invalid_error_shapes_fail_closed(self):
        for body in (None,[],True,'42501',{'message':'permission denied'}):
            self.assertFalse(safe_denial(403,body))


if __name__=='__main__':unittest.main()
