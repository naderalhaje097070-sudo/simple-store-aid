"""Fail-closed denial oracle: transport/server errors never become authorization."""
import unittest
from pathlib import Path
import tempfile
from scanner_auth_probe import explicit_denial
from scanner_evidence import PublicationBlocked, verify_publication


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


class PublicationSinkTests(unittest.TestCase):
    def test_detected_jwt_cannot_reach_always_upload_sink(self):
        with tempfile.TemporaryDirectory() as root:
            out, quarantine = Path(root)/'upload', Path(root)/'private'
            out.mkdir()
            secret = 'eyJabcdefghijk.abcdefghijk.abcdefghijk'
            (out/'unsafe.json').write_text(secret)
            (out/'sibling.json').write_text('ordinary evidence')
            with self.assertRaises(PublicationBlocked):
                verify_publication(out, quarantine)
            self.assertEqual([p.name for p in out.iterdir()], ['publication-blocked.json'])
            self.assertNotIn(secret, (out/'publication-blocked.json').read_text())
            self.assertEqual((quarantine/'unsafe.json').read_text(), secret)
            self.assertIn('sha256', (out/'publication-blocked.json').read_text())

    def test_known_password_is_quarantined_without_a_jwt_pattern(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root)/'upload'; out.mkdir()
            (out/'unsafe.txt').write_text('random-test-password-123456')
            with self.assertRaises(PublicationBlocked):
                verify_publication(out, Path(root)/'private', ['random-test-password-123456'])
            self.assertNotIn('random-test-password-123456', (out/'publication-blocked.json').read_text())

    def test_clean_receipts_stay_publishable(self):
        with tempfile.TemporaryDirectory() as root:
            out = Path(root)/'upload'; out.mkdir()
            (out/'clean.json').write_text('{"failed":0}')
            self.assertTrue(verify_publication(out, Path(root)/'private')['publication_allowed'])
