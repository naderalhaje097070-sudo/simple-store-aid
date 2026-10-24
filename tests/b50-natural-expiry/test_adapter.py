"""No DB/app execution: validate actual adapter globals and inherited expiry oracles."""
import builtins
import dis
import importlib.util
from pathlib import Path
import types
import unittest


SPEC = importlib.util.spec_from_file_location('b50_expiry_adapter', Path(__file__).with_name('probe.py'))
adapter = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(adapter)


def require_resolved_globals(function, namespace=None):
    namespace = function.__globals__ if namespace is None else namespace
    pending = [function.__code__]
    missing = set()
    while pending:
        code = pending.pop()
        for instruction in dis.get_instructions(code):
            if instruction.opname == 'LOAD_GLOBAL':
                name = instruction.argval
                if name not in namespace and not hasattr(builtins, name):
                    missing.add(name)
        pending.extend(value for value in code.co_consts if isinstance(value, types.CodeType))
    if missing:
        raise AssertionError('unresolved adapter globals: ' + ', '.join(sorted(missing)))


class AdapterContractTests(unittest.TestCase):
    def test_actual_adapter_methods_resolve_all_runtime_globals(self):
        require_resolved_globals(adapter.B50NaturalExpiryProbe.run_expiry)
        require_resolved_globals(adapter.B50NaturalExpiryProbe.extra_snapshot)

    def test_missing_APP_is_detected_before_creating_any_fixture(self):
        namespace = dict(adapter.B50NaturalExpiryProbe.run_expiry.__globals__)
        del namespace['APP']
        with self.assertRaisesRegex(AssertionError, 'APP'):
            require_resolved_globals(adapter.B50NaturalExpiryProbe.run_expiry, namespace)

    def test_crypto_time_challenge_peers_and_no_refresh_remain_original_methods(self):
        for name in ['request', 'verify', 'active_state', 'positive', 'batch', 'fresh_oauth']:
            self.assertIs(getattr(adapter.B50NaturalExpiryProbe, name), getattr(adapter.NaturalExpiryProbe, name))
        self.assertEqual(adapter.TTL, 180)
        self.assertEqual(adapter.WAIT_MARGIN, 5)


if __name__ == '__main__':
    unittest.main()
