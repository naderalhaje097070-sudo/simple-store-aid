import copy
import json
import pathlib
import subprocess
import sys
import unittest

from evidence_guard import EvidenceError, RegressionDetected, assert_disabled_access_denied, validate_archive

ROOT = pathlib.Path(__file__).resolve().parents[2]
ARCHIVE = ROOT / 'changes/primary-env-001/native-runner/auth-tenant-probe.json'
SOURCE = '84c3444fcdf5fa2825809192cda5b15561c950cf'


class EvidenceGuardTest(unittest.TestCase):
    def setUp(self):
        self.report = json.loads(ARCHIVE.read_text())

    def test_archive_keeps_real_fixture_failures(self):
        result = validate_archive(self.report, SOURCE)
        self.assertEqual((result['passed'], result['failed']), (22, 2))
        self.assertEqual(result['fixture_failures'], ['seed_role_A', 'seed_role_B'])
        self.assertFalse(result['integration_accepted'])

    def test_login_ban_does_not_hide_preissued_token_regression(self):
        with self.assertRaisesRegex(RegressionDetected, '^ENV_NATIVE_01_PRE_BAN_JWT_STILL_READS_OWN_TENANT$'):
            assert_disabled_access_denied(self.report, SOURCE)

    def test_corrupt_evidence_cannot_be_expected_red(self):
        mutations = [
            lambda r: r.update(source='wrong-head'),
            lambda r: r.update(scope='production'),
            lambda r: r.update(checks=[]),
            lambda r: r['checks'].append(copy.deepcopy(r['checks'][0])),
            lambda r: r.update(passed=24),
            lambda r: r.update(failed=False),
            lambda r: r['checks'][0].update(passed='true'),
            lambda r: r['checks'][0].update(status=True),
            lambda r: r['checks'][0].update(status=700),
            lambda r: r['checks'][0].update(name=None),
            lambda r: r.update(limitations=None),
            lambda r: r['limitations'].pop('full_tenant_coverage'),
            lambda r: r['limitations'].update(status=500),
            lambda r: r['limitations'].update(status=401),
            lambda r: r['limitations'].update(disabled_user_strict_acceptance=True),
        ]
        for n, mutate in enumerate(mutations):
            with self.subTest(case=n):
                report = copy.deepcopy(self.report)
                mutate(report)
                with self.assertRaises(EvidenceError):
                    assert_disabled_access_denied(report, SOURCE)

    def test_every_reproduction_prerequisite_is_required(self):
        for name in ['auth_login_B', 'B_sees_only_own_tenant', 'ban_fixture_account', 'banned_new_login_denied']:
            for field, value in [('status', 500), ('passed', False)]:
                with self.subTest(name=name, field=field):
                    report = copy.deepcopy(self.report)
                    next(c for c in report['checks'] if c['name'] == name)[field] = value
                    report['passed'] = sum(c['passed'] for c in report['checks'])
                    report['failed'] = len(report['checks']) - report['passed']
                    with self.assertRaises(EvidenceError):
                        assert_disabled_access_denied(report, SOURCE)

    def test_positive_control_requires_one_own_row(self):
        next(c for c in self.report['checks'] if c['name'] == 'B_sees_only_own_tenant')['visible_rows'] = 0
        with self.assertRaises(EvidenceError):
            assert_disabled_access_denied(self.report, SOURCE)

    def test_zero_visible_marker_does_not_approve_fixture_failures(self):
        self.report['limitations'].update(pre_ban_token_still_reads_own_tenant=False, status=403)
        with self.assertRaises(EvidenceError):
            assert_disabled_access_denied(self.report, SOURCE)

    def test_http_200_without_postban_rows_is_incomplete(self):
        for c in self.report['checks']:
            c['passed'] = True
        self.report.update(passed=24, failed=0)
        self.report['limitations']['pre_ban_token_still_reads_own_tenant'] = False
        with self.assertRaises(EvidenceError):
            assert_disabled_access_denied(self.report, SOURCE)

    def test_bounded_denial_still_never_approves_integration(self):
        for c in self.report['checks']:
            c['passed'] = True
        self.report.update(passed=24, failed=0)
        self.report['limitations'].update(pre_ban_token_still_reads_own_tenant=False, status=403)
        self.assertFalse(assert_disabled_access_denied(self.report, SOURCE)['integration_accepted'])

    def test_cli_separates_regression_from_source_error(self):
        script = ROOT / 'tests/account-lifecycle/evidence_guard.py'
        for source, code, sentinel in [(SOURCE, 1, 'ENV_NATIVE_01_PRE_BAN_JWT_STILL_READS_OWN_TENANT'),
                                      ('wrong', 2, 'ENV_NATIVE_01_INVALID_OR_INCOMPLETE_EVIDENCE')]:
            with self.subTest(source=source):
                result = subprocess.run([sys.executable, str(script), str(ARCHIVE), '--expected-source', source], capture_output=True, text=True)
                self.assertEqual(result.returncode, code)
                self.assertEqual(result.stdout.strip(), sentinel)
                self.assertEqual(result.stderr, '')


if __name__ == '__main__':
    unittest.main()
