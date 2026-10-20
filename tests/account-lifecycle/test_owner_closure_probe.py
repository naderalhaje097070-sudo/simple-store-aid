import unittest
from owner_closure_probe import explicit_inactive, expected_fixture


class ClosureEvidenceOracle(unittest.TestCase):
    def test_requires_named_permission_denial(self):
        self.assertTrue(explicit_inactive(403, {'code': '42501', 'message': 'account_inactive'}))
        for status, body in [(500, {'code': '42501', 'message': 'account_inactive'}),
                             (403, {'code': '42501', 'message': 'other'}), (200, []),
                             (401, {'code': 'PGRST301'}), (403, None)]:
            with self.subTest(status=status, body=body):
                self.assertFalse(explicit_inactive(status, body))

    def test_independent_financial_fixture_consistency(self):
        e = expected_fixture()
        self.assertEqual(e['total'], e['price'] * e['quantity'])
        self.assertEqual(e['remaining'], e['total'] - e['paid'])
        self.assertEqual(e['stock'], e['initial_stock'] - e['quantity'])
        self.assertEqual(e['margin'], e['total'] - e['cost'] * e['quantity'])


if __name__ == '__main__':
    unittest.main()
