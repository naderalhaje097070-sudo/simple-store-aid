import json
import unittest
from mcp_probe import tool_success, account_tool_denial, protocol_body


class McpBoundaryTest(unittest.TestCase):
    def test_active_requires_real_successful_tool_payload(self):
        good = {'result': {'structuredContent': {'products': []}}}
        self.assertTrue(tool_success(200, good, 'list_products'))
        for status, body in [(401, good), (500, good), (200, {}), (200, {'error': {'code': -32000}}),
                             (200, {'result': {'isError': True, 'structuredContent': {'products': []}}})]:
            self.assertFalse(tool_success(status, body, 'list_products'))
        self.assertFalse(tool_success(200, good, 'today_summary'))

    def test_account_denial_cannot_accept_auth_or_generic_failures(self):
        good = {'result': {'isError': True, 'content': [{'type': 'text', 'text': 'account_inactive'}]}}
        self.assertTrue(account_tool_denial(200, good, 'today_summary'))
        for status, body in [(401, good), (403, good), (500, good),
                             (200, {'result': {'isError': True, 'content': [{'type': 'text', 'text': 'permission denied'}]}}),
                             (200, {'result': {'structuredContent': {'summary': {'sales': 0}}}})]:
            self.assertFalse(account_tool_denial(status, body, 'today_summary'))

    def test_real_protocol_json_and_sse_preserve_error_class(self):
        body = {'jsonrpc': '2.0', 'id': 2, 'result': {'structuredContent': {'products': []}}}
        self.assertEqual(protocol_body(json.dumps(body).encode()), body)
        self.assertEqual(protocol_body(('event: message\ndata: '+json.dumps(body)+'\n\n').encode()), body)
        with self.assertRaises(Exception): protocol_body(b'not-json')

    def test_empty_finance_rows_are_not_explicit_ban_denial(self):
        for name, field in [('list_products', 'products'), ('list_customers', 'customers'),
                            ('list_recent_orders', 'orders')]:
            body = {'result': {'structuredContent': {field: []}}}
            self.assertTrue(tool_success(200, body, name))
            self.assertFalse(account_tool_denial(200, body, name))

    def test_initialized_notification_empty_response(self):
        self.assertIsNone(protocol_body(b''))


if __name__ == '__main__': unittest.main()

