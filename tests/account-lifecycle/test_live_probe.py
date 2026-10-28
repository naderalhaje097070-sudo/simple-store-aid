import copy
import os
import sys
import unittest
from unittest.mock import patch

from live_probe import HarnessFailure, EXPECTED_RED, Probe, NoRedirect, auth_ban_denial, denial, outcome


class LiveProbeSafetyTest(unittest.TestCase):
    def test_denial_distinguishes_empty_rows_from_server_errors(self):
        for status, body, expected in [(200, [], True), (200, [{}], False), (200, {}, False),
                                       (403, {'code': '42501'}, True), (401, {'code': 'PGRST301'}, True),
                                       (400, {'code': 'P0001'}, False), (500, {'code': '42501'}, False),
                                       (403, {'message': 'unknown'}, False), (302, [], False)]:
            with self.subTest(status=status, body=body):
                self.assertIs(denial(status, body), expected)

    def test_auth_ban_denial_requires_provider_reason(self):
        for status, body, expected in [(400, {'error_code': 'user_banned'}, True),
                                       (400, {'error_code': 'refresh_token_not_found'}, True),
                                       (400, {'error_code': 'invalid_credentials'}, False),
                                       (500, {'error_code': 'user_banned'}, False), (200, {}, False),
                                       (400, None, False)]:
            with self.subTest(status=status, body=body):
                self.assertIs(auth_ban_denial(status, body), expected)

    def test_named_red_requires_green_controls(self):
        controls = [{'name': 'active_own', 'passed': True}]
        targets = [{'name': 'banned_owner_old_jwt_own_tenant', 'passed': False, 'status': 200, 'visible_rows': 1}]
        self.assertEqual(outcome(controls, targets), EXPECTED_RED)
        mutations = [([], targets), ([{'name': 'active_own', 'passed': False}], targets),
                     (controls, []), (controls, [{'name': 'other_failure', 'passed': False}]),
                     (controls, targets + copy.deepcopy(targets)),
                     (controls, [dict(targets[0], status=500)]),
                     (controls, [dict(targets[0], visible_rows=0)]),
                     (controls, [dict(targets[0], passed=True)])]
        for c, t in mutations:
            with self.subTest(controls=c, targets=t):
                with self.assertRaises(HarnessFailure):
                    outcome(c, t)

    def test_no_redirect_following(self):
        self.assertIsNone(NoRedirect().redirect_request(None, None, 302, '', {}, 'https://external.example'))

    def test_guard_rejects_before_status_file_or_network(self):
        with patch.dict(os.environ, {}, clear=True), patch('pathlib.Path.read_text') as read, patch('urllib.request.build_opener') as network:
            with self.assertRaises(SystemExit) as error:
                Probe(None, None, 'source')
            self.assertEqual(error.exception.code, 2)
            read.assert_not_called()
            network.assert_not_called()


if __name__ == '__main__':
    unittest.main()
