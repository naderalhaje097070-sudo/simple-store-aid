"""Adversarial receipt tests: no causal/time/identity shortcut is accepted."""
import copy
import unittest

from natural_expiry_probe import expiry_accepted, expired_mcp, expired_rest, PHASES, PATHS, APP, METADATA


def good_receipt():
    timing = {'iat': 1000, 'exp': 1180, 'positive_finished': 1010,
              'negative_started': 1215, 'real_wait_seconds': 205,
              'monotonic_wait_seconds': 205, 'clock_drift_seconds': 0, 'max_verifier_leeway': 30}
    continuity = {key: True for key in ('accounts_active', 'old_session_exists',
                  'no_auto_refresh', 'same_old_token', 'new_token_distinct')}
    observations = []
    for actor, phase in PHASES:
        negative = phase in ('expired', 'old_again')
        for path in PATHS:
            observations.append({'actor': actor, 'phase': phase, 'path': path, 'passed': True,
                'token_role': 'old_B' if actor == 'B' and phase != 'new' else 'fresh_' + actor,
                'status': 401 if negative else 200, 'checked_at': 1215 if phase != 'before' else 1005,
                'token_exp': 1180 if actor == 'B' and phase != 'new' else 1400,
                'same_old_token': negative, 'expiration_proven': negative})
    return observations, timing, continuity


class NaturalExpiryTests(unittest.TestCase):
    def test_complete_receipt(self):
        self.assertTrue(expiry_accepted(*good_receipt()))

    def test_refreshed_substitution_or_wrong_identity(self):
        for key, value in [('same_old_token', False), ('token_role', 'fresh_B')]:
            data = good_receipt()
            data[0][7][key] = value
            self.assertFalse(expiry_accepted(*data))

    def test_early_check_not_expiry(self):
        data = good_receipt()
        data[1]['negative_started'] = 1200
        self.assertFalse(expiry_accepted(*data))

    def test_sdk_leeway_requires_wait_beyond_provider_skew(self):
        data = good_receipt()
        data[1]['max_verifier_leeway'] = 60
        self.assertFalse(expiry_accepted(*data))
        data[1]['negative_started'] = 1245
        data[1]['real_wait_seconds'] = data[1]['monotonic_wait_seconds'] = 235
        for item in data[0]:
            if item['phase'] in ('expired', 'old_again'):
                item['checked_at'] = 1245
        self.assertTrue(expiry_accepted(*data))
        data = good_receipt()
        data[0][7]['checked_at'] = 1210
        self.assertFalse(expiry_accepted(*data))

    def test_missing_previous_success(self):
        data = good_receipt()
        data[0].pop(0)
        self.assertFalse(expiry_accepted(*data))
        data = good_receipt()
        data[0][0]['passed'] = False
        self.assertFalse(expiry_accepted(*data))

    def test_blanket_denial_not_expiry_proof(self):
        for phase in ('fresh', 'new'):
            data = good_receipt()
            for item in data[0]:
                if item['phase'] == phase:
                    item['status'] = 401
            self.assertFalse(expiry_accepted(*data))

    def test_generic_failure_not_expiry(self):
        for status in (200, 403, 500, 504):
            self.assertFalse(expired_rest(status, {'code': 'PGRST303', 'message': 'JWT expired'}))
        for body in ({}, [], {'code': 'PGRST301', 'message': 'JWT expired'},
                     {'code': 'PGRST303', 'message': 'account_inactive'}):
            self.assertFalse(expired_rest(401, body))

    def test_mcp_generic_challenge_needs_expired_signed_identity(self):
        challenge = f'Bearer error="invalid_token", resource_metadata="{APP}{METADATA}"'
        proof = {'signature_verified': True, 'identity_verified': True, 'expired': True,
                 'error_code': 'ERR_JWT_EXPIRED'}
        self.assertTrue(expired_mcp(401, {'error': 'unauthorized'}, challenge, proof))
        for key in ('signature_verified', 'identity_verified', 'expired', 'error_code'):
            changed = copy.deepcopy(proof)
            changed[key] = False
            self.assertFalse(expired_mcp(401, {'error': 'unauthorized'}, challenge, changed))
        for status in (200, 403, 500, 504):
            self.assertFalse(expired_mcp(status, {'error': 'unauthorized'}, challenge, proof))
        self.assertFalse(expired_mcp(401, {'error': 'unauthorized'}, '', proof))

    def test_auth_session_continuity_required(self):
        for key in good_receipt()[2]:
            data = good_receipt()
            data[2][key] = False
            self.assertFalse(expiry_accepted(*data))

    def test_actual_ttl_and_real_elapsed_time_required(self):
        for key, value in [('iat', 900), ('positive_finished', 1181),
                           ('real_wait_seconds', 0), ('monotonic_wait_seconds', 0),
                           ('clock_drift_seconds', 5)]:
            data = good_receipt()
            data[1][key] = value
            self.assertFalse(expiry_accepted(*data))

    def test_expiration_cause_mandatory_on_every_replay(self):
        data = good_receipt()
        data[0][-1]['expiration_proven'] = False
        self.assertFalse(expiry_accepted(*data))


if __name__ == '__main__':
    unittest.main()
