"""Distinguish setup absence, real leak, and an unreadable process table."""
import subprocess
from types import SimpleNamespace
import unittest
from cleanup import process_state


class ProcessEvidence(unittest.TestCase):
    def lookup(self, name):
        self.assertEqual(name, 'g01-app')
        return SimpleNamespace(pw_uid=12345)

    def runner(self, code):
        def command(args, **kwargs):
            self.assertEqual(args, ['pgrep', '-u', '12345'])
            return SimpleNamespace(returncode=code)
        return command

    def test_user_never_created(self):
        def absent(name): raise KeyError(name)
        def forbidden(*args, **kwargs): self.fail('pgrep must not run for absent user')
        self.assertEqual(process_state(absent, forbidden), {'state': 'user_absent', 'removed': True})

    def test_existing_user_no_processes(self):
        self.assertEqual(process_state(self.lookup, self.runner(1)), {'state': 'no_processes', 'removed': True})

    def test_actual_remaining_processes(self):
        self.assertEqual(process_state(self.lookup, self.runner(0)), {'state': 'processes_remaining', 'removed': False})

    def test_process_table_errors(self):
        for code in (2, 3, 127, -9):
            with self.subTest(code=code):
                self.assertEqual(process_state(self.lookup, self.runner(code)), {'state': 'process_read_failed', 'removed': False})

    def test_lookup_error_is_not_absence(self):
        def broken(name): raise OSError('unreadable user database')
        self.assertEqual(process_state(broken, self.runner(1)), {'state': 'user_lookup_failed', 'removed': False})

    def test_process_command_unavailable_or_timeout(self):
        for error in (OSError('missing pgrep'), subprocess.TimeoutExpired('pgrep', 10)):
            def broken(*args, **kwargs): raise error
            self.assertEqual(process_state(self.lookup, broken), {'state': 'process_read_failed', 'removed': False})


if __name__ == '__main__':
    unittest.main()
