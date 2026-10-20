"""Fail-closed denial oracle: transport/server errors never become authorization."""
import unittest
from scanner_auth_probe import explicit_denial


class DenialOracleTests(unittest.TestCase):
    def test_requires_permission_status_code_and_message(self):
        for status in (401, 403):
            self.assertTrue(explicit_denial(status, {'code':'42501','message':'forbidden_platform_admin'}, 'forbidden_platform_admin'))
        for status in (200, 400, 404, 429, 500, 503):
            self.assertFalse(explicit_denial(status, {'code':'42501','message':'forbidden_platform_admin'}, 'forbidden_platform_admin'))
        for body in ({}, [], None, {'code':'P0001'}, {'code':'42501','message':'unrelated'}):
            self.assertFalse(explicit_denial(403, body, 'forbidden_platform_admin'))

    def test_inactive_is_distinct_and_anon_requires_permission_code(self):
        self.assertTrue(explicit_denial(403, {'code':'42501','message':'account_inactive'}, 'account_inactive'))
        self.assertFalse(explicit_denial(403, {'code':'42501','message':'account_inactive'}, 'forbidden_platform_admin'))
        self.assertTrue(explicit_denial(401, {'code':'42501'}))
        self.assertFalse(explicit_denial(401, {'code':'PGRST301'}))
