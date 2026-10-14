"""Negative mutations prove new source/wiring checks cannot pass weakened guards."""
import importlib.util
from pathlib import Path
import unittest

from guard_receipt import EXPECTED, receipt

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('visual_contract', ROOT/'tests/gate4/sec-env/visual-runtime-contract.py')
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
VISUAL = (ROOT/'tests/visual/mobile-rtl-smoke.py').read_text()
HELPER = (ROOT/'tests/e2e/browser_network_guard.py').read_text()


class VisualContract(unittest.TestCase):
    def test_actual_contract(self):
        self.assertEqual(contract.verify(VISUAL, HELPER)['policy_cases'], 13)

    def reject_visual(self, old, new):
        self.assertIn(old, VISUAL)
        with self.assertRaises(contract.ContractFailure):
            contract.verify(VISUAL.replace(old, new), HELPER)

    def test_off_origin_navigation_mutation(self):
        self.reject_visual('if is_navigation and origin != BASE_ORIGIN:', 'if False:')

    def test_write_allowed_mutation(self):
        self.reject_visual('return method.upper() in {"GET", "HEAD", "OPTIONS"}', 'return True')

    def test_helper_wiring_mutation(self):
        self.reject_visual('ctx, browser_request_is_isolated, reject_browser_request',
                           'ctx, lambda *args: True, reject_browser_request')

    def test_missing_guard_mutation(self):
        self.reject_visual('await install_browser_network_guard(', 'await missing_guard(')

    def test_conditional_guard_suppression(self):
        self.reject_visual('            await install_browser_network_guard(\n                ctx, browser_request_is_isolated, reject_browser_request\n            )',
                           '            if False:\n                await install_browser_network_guard(\n                    ctx, browser_request_is_isolated, reject_browser_request\n                )')

    def test_swallowed_goto_mutation(self):
        self.reject_visual('raise RuntimeError(\n                        f"visual navigation failed for {name}: {error}"\n                    ) from error', 'pass')

    def test_origin_evidence_mutation(self):
        self.reject_visual('if network_origin(page.url) != BASE_ORIGIN:', 'if False:')

    def test_violation_evidence_mutation(self):
        self.reject_visual('if isolation_violations:', 'if False:')

    def test_navigation_flag_not_forwarded(self):
        changed = HELPER.replace('allowed(request.method, request.url, request.is_navigation_request())',
                                 'allowed(request.method, request.url, False)')
        self.assertNotEqual(changed, HELPER)
        with self.assertRaises(contract.ContractFailure):
            contract.verify(VISUAL, changed)


class NamedReceipt(unittest.TestCase):
    def test_exact_phrase(self):
        self.assertTrue(receipt(500, b'error page', EXPECTED)['passed'])

    def test_ansi_and_wrapping(self):
        log = '\x1b[31m'+EXPECTED.replace('configuration does', 'configuration\n  does')+'\x1b[0m'
        self.assertTrue(receipt(500, b'error page', log)['passed'])

    def test_generic_500_is_rejected(self):
        self.assertFalse(receipt(500, b'error page', 'unrelated failure')['passed'])

    def test_partial_phrase_is_rejected(self):
        self.assertFalse(receipt(500, b'error page', EXPECTED[:-20])['passed'])

    def test_different_named_guard_is_rejected(self):
        v = receipt(500, b'error page', 'SEC_ENV_BINDING_CONFLICT: VITE_SUPABASE_PROJECT_ID differs between runtime sources')
        self.assertFalse(v['passed'])
        self.assertEqual(v['known_guard_categories'], ['binding_conflict_VITE_SUPABASE_PROJECT_ID'])

    def test_matching_message_cannot_hide_wrong_status(self):
        self.assertFalse(receipt(200, b'html', EXPECTED)['passed'])

    def test_no_log_or_response_leak(self):
        v = receipt(500, b'private-response-needle', EXPECTED+' private-log-needle')
        self.assertNotIn('private-response-needle', str(v))
        self.assertNotIn('private-log-needle', str(v))


if __name__ == '__main__':
    unittest.main()
