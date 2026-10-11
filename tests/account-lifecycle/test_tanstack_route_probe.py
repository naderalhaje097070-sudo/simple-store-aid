"""Adversarial acceptance checks for the route runner; no live-path auth stubs."""
import copy
import unittest
from tanstack_route_probe import lifecycle_accepted, exact_catalog, contains_credentials
from mcp_probe import TOOLS, tool_success, account_tool_denial


class RouteAcceptanceTest(unittest.TestCase):
    def setUp(self):
        self.rows = [{'actor': actor, 'phase': phase, 'tool': tool, 'passed': True}
                     for actor, phase in [('A', 'active'), ('B', 'active'),
                                          ('B', 'banned_old_jwt'), ('A', 'unaffected_active')]
                     for tool in TOOLS]

    def test_complete_exact_sequence(self):
        self.assertTrue(lifecycle_accepted(self.rows))

    def test_missing_duplicate_extra_and_reordered_observation(self):
        for rows in [[], self.rows[:-1], self.rows + self.rows[:1],
                     self.rows[:4] + self.rows[8:12] + self.rows[4:8] + self.rows[12:]]:
            with self.subTest(rows=rows):
                self.assertFalse(lifecycle_accepted(rows))
        duplicate = copy.deepcopy(self.rows)
        duplicate[9] = duplicate[8]
        self.assertFalse(lifecycle_accepted(duplicate))

    def test_false_missing_and_truthy_pass_never_accepted(self):
        for value in [False, None, 1, 'true']:
            rows = copy.deepcopy(self.rows)
            rows[0]['passed'] = value
            self.assertFalse(lifecycle_accepted(rows))

    def test_http_200_with_mcp_error_not_success(self):
        for name in TOOLS:
            body = {'result': {'isError': True, 'content': [{'type': 'text', 'text': 'account_inactive'}]}}
            self.assertFalse(tool_success(200, body, name))
            self.assertTrue(account_tool_denial(200, body, name))

    def test_empty_and_generic_failures_not_ban_proof(self):
        for status, body in [(500, None), (401, {'error': 'unauthorized'}),
                             (200, {'result': {'structuredContent': {'products': []}}}),
                             (200, {'result': {'isError': True, 'content': [{'type': 'text', 'text': 'timeout'}]}})]:
            for name in TOOLS:
                self.assertFalse(account_tool_denial(status, body, name))

    def test_catalog_rejects_duplicate_missing_and_error(self):
        tools = [{'name': name} for name in TOOLS]
        self.assertTrue(exact_catalog({'result': {'tools': tools}}))
        for items in [[], tools[:-1], tools + tools[:1], tools[:3] + tools[:1]]:
            self.assertFalse(exact_catalog({'result': {'tools': items}}))
        self.assertFalse(exact_catalog({'error': 'failed'}))

    def test_unknown_jwt_key_and_known_oauth_refresh_are_detected(self):
        for text, secrets in [('eyJabcdefghijk.abcdefghijkl.abcdefghijkl', []),
                              ('sb_secret_unknownvalue', []), ('oauth-refresh-sensitive', ['oauth-refresh-sensitive'])]:
            self.assertTrue(contains_credentials(text, secrets))
        self.assertFalse(contains_credentials('{"outcome":"passed","sha":"abc"}', ['sensitive']))


if __name__ == '__main__':
    unittest.main()
