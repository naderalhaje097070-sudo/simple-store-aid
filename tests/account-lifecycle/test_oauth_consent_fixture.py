"""Offline fixture control-flow tests; these are NOT live/signature/expiry proof."""
import base64
import hashlib
import json
import unittest
import urllib.error
import urllib.parse

from live_probe import HarnessFailure
from mcp_probe import McpProbe


class DummyAuthorize:
    def __init__(self, probe):
        self.probe = probe

    def open(self, request, timeout):
        self.probe.params = urllib.parse.parse_qs(urllib.parse.urlparse(request.full_url).query)
        raise urllib.error.HTTPError(request.full_url, 302, 'unit redirect',
            {'Location': 'http://127.0.0.1:3000/oauth/consent?authorization_id=' + 'a'*32}, None)


class FixtureFlow(McpProbe):
    def __init__(self, existing=False, invalid=None):
        self.base = 'http://127.0.0.1:54321'
        self.anon = 'unit-placeholder'
        self.existing, self.invalid, self.calls = existing, invalid, []
        self.opener = DummyAuthorize(self)

    def control(self, name, passed, **details):
        if not passed:
            raise HarnessFailure(name)

    def redirect(self):
        state = self.params['state'][0]
        if self.invalid == 'state':
            state = 'wrong-state'
        origin = 'https://foreign.example' if self.invalid == 'origin' else 'http://127.0.0.1:54325'
        return {'redirect_url': origin + '/test-oauth-callback?' + urllib.parse.urlencode({'state': state, 'code': 'offline-unit-code'})}

    def request(self, method, path, payload=None, token=None):
        self.calls.append((method, path))
        if method == 'GET':
            return 200, self.redirect() if self.existing else {'client': {'id': 'unit-client'}}
        if path.endswith('/consent'):
            return 200, self.redirect()
        assert path == '/auth/v1/oauth/token'
        assert payload['client_id'] == 'unit-client'
        assert payload['code'] == 'offline-unit-code'
        challenge = base64.urlsafe_b64encode(hashlib.sha256(payload['code_verifier'].encode()).digest()).decode().rstrip('=')
        assert self.params['code_challenge'] == [challenge]
        claims = {'sub': 'unit-actor', 'client_id': 'unit-client', 'iss': self.base + '/auth/v1', 'aud': 'authenticated'}
        # Unverified string only for this isolated helper unit; live proof uses
        # real provider tokens and a separate cryptographic verification helper.
        encoded = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip('=')
        return 200, {'access_token': 'unit.' + encoded + '.unverified'}


class ConsentFixtureTests(unittest.TestCase):
    def run_flow(self, existing, invalid=None):
        probe = FixtureFlow(existing, invalid)
        actor = {'uid': 'unit-actor', 'token': 'unit-session'}
        probe.oauth_token(actor, 'unit', 'unit-client')
        self.assertEqual(actor['session_token'], 'unit-session')
        return probe

    def test_initial_consent_uses_existing_explicit_path(self):
        probe = self.run_flow(False)
        self.assertTrue(any(path.endswith('/consent') for _, path in probe.calls))

    def test_existing_consent_reuses_provider_callback_and_pkce(self):
        probe = self.run_flow(True)
        self.assertFalse(any(path.endswith('/consent') for _, path in probe.calls))
        self.assertEqual(probe.calls[-1], ('POST', '/auth/v1/oauth/token'))

    def test_existing_consent_wrong_state_rejected_before_exchange(self):
        with self.assertRaises(HarnessFailure):
            self.run_flow(True, 'state')

    def test_existing_consent_foreign_callback_rejected_before_exchange(self):
        with self.assertRaises(HarnessFailure):
            self.run_flow(True, 'origin')


if __name__ == '__main__':
    unittest.main()
