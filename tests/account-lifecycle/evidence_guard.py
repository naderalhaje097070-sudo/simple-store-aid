"""Offline regression oracle for the archived ENV-NATIVE-01 observation.

No network, credential input or database writes. Exit 1 is the recorded security
regression, exit 2 invalid/incomplete evidence, exit 0 only the bounded assertion.
Neither exit 0 nor unit tests constitute live lifecycle acceptance.
"""
import argparse
import json
import pathlib


class EvidenceError(ValueError):
    pass


class RegressionDetected(AssertionError):
    pass


def validate_archive(report, expected_source):
    if not isinstance(report, dict):
        raise EvidenceError('report must be an object')
    if report.get('source') != expected_source:
        raise EvidenceError('source mismatch')
    if report.get('scope') != 'nonfinancial_auth_and_tenant_metadata_only':
        raise EvidenceError('scope mismatch')
    checks = report.get('checks')
    if not isinstance(checks, list) or not checks:
        raise EvidenceError('missing checks')
    indexed = {}
    for check in checks:
        if not isinstance(check, dict):
            raise EvidenceError('invalid check')
        name = check.get('name')
        if not isinstance(name, str) or not name or name in indexed:
            raise EvidenceError('invalid or duplicate check name')
        if type(check.get('passed')) is not bool:
            raise EvidenceError('invalid boolean')
        if type(check.get('status')) is not int or not 100 <= check['status'] <= 599:
            raise EvidenceError('invalid HTTP status')
        indexed[name] = check
    passed = sum(c['passed'] for c in checks)
    for key, count in [('passed', passed), ('failed', len(checks) - passed)]:
        if type(report.get(key)) is not int or report[key] != count:
            raise EvidenceError('counter mismatch')
    # Named positive controls distinguish the reproduction from a dead stack.
    required = {'auth_login_B': 200, 'B_sees_only_own_tenant': 200,
                'ban_fixture_account': 200, 'banned_new_login_denied': 400}
    for name, status in required.items():
        check = indexed.get(name)
        if not check or check['passed'] is not True or check['status'] != status:
            raise EvidenceError('missing or failed prerequisite: ' + name)
    if type(indexed['B_sees_only_own_tenant'].get('visible_rows')) is not int or indexed['B_sees_only_own_tenant']['visible_rows'] != 1:
        raise EvidenceError('active own-tenant positive control missing')
    limitations = report.get('limitations')
    if not isinstance(limitations, dict):
        raise EvidenceError('missing limitations')
    for key in ['pre_ban_token_still_reads_own_tenant', 'disabled_user_strict_acceptance', 'full_tenant_coverage']:
        if type(limitations.get(key)) is not bool:
            raise EvidenceError('missing limitation: ' + key)
    status = limitations.get('status')
    if type(status) is not int or status not in (200, 401, 403):
        raise EvidenceError('unexpected old-token response, not security denial')
    visible = limitations['pre_ban_token_still_reads_own_tenant']
    if visible and status != 200:
        raise EvidenceError('contradictory old-token observation')
    if visible and limitations['disabled_user_strict_acceptance']:
        raise EvidenceError('contradictory acceptance')
    # Preserve failed fixtures. This archive cannot approve a future target suite.
    return {'passed': passed, 'failed': len(checks) - passed,
            'fixture_failures': [c['name'] for c in checks if not c['passed']],
            'pre_ban_token_visible': visible, 'integration_accepted': False}


def assert_disabled_access_denied(report, expected_source):
    result = validate_archive(report, expected_source)
    if result['pre_ban_token_visible']:
        raise RegressionDetected('ENV_NATIVE_01_PRE_BAN_JWT_STILL_READS_OWN_TENANT')
    if result['failed']:
        raise EvidenceError('fixture failures remain; bounded assertion not accepted')
    # A 200 can be empty RLS output, but the archived shape contains no row-level
    # post-ban observation. Do not infer a denial from an arbitrary success status.
    if report['limitations']['status'] not in (401, 403):
        raise EvidenceError('archive cannot prove empty-row denial')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=pathlib.Path)
    parser.add_argument('--expected-source', required=True)
    args = parser.parse_args()
    try:
        assert_disabled_access_denied(json.loads(args.archive.read_text()), args.expected_source)
    except RegressionDetected as error:
        print(str(error))
        return 1
    except (EvidenceError, OSError, json.JSONDecodeError):
        print('ENV_NATIVE_01_INVALID_OR_INCOMPLETE_EVIDENCE')
        return 2
    print('BOUNDED_ASSERTION_ONLY_NOT_INTEGRATION_ACCEPTANCE')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
