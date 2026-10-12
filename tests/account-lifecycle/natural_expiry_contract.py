"""Inspect installed SDK/jose and disposable Auth configuration without credentials."""
import hashlib
import json
import os
from pathlib import Path
import re
import sys
import tomllib


def configure(path):
    original = path.read_text()
    assert tomllib.loads(original)['auth']['jwt_expiry'] == 3600
    value, count = re.subn(r'^jwt_expiry = 3600$', 'jwt_expiry = 180', original, count=1, flags=re.M)
    assert count == 1
    path.write_text(value)
    assert tomllib.loads(path.read_text())['auth']['jwt_expiry'] == 180


def inspect():
    root = Path('node_modules/@lovable.dev/mcp-js')
    assert json.loads((root/'package.json').read_text())['version'] == '0.20.1'
    jose = Path('node_modules/jose')
    assert json.loads((jose/'package.json').read_text())['version'] == '6.2.3'
    sources = [(p, p.read_text()) for p in root.rglob('*') if p.suffix in ('.js', '.mjs', '.cjs')]
    # The actual verifier module must be present, and must use locked jose jwtVerify.
    # The TanStack/Nitro build consumes ESM exports. CJS bundles embed jose's own
    # implementation too, so their tolerance references are not SDK options.
    relevant = [(p, s) for p, s in sources if p.suffix == '.js' and 'jwtVerify' in s
                and 'OAuth client claim is required' in s]
    print(json.dumps({'sdk_verifier_candidates': [str(p.relative_to(root)) for p, s in sources
                      if 'jwtVerify' in s or 'OAuth client claim is required' in s]}))
    assert relevant, 'Installed SDK verifier source could not be reconciled'
    excerpts = []
    sdk_tolerance = []
    for p, s in relevant:
        snippets = [s[max(0, m.start()-100):m.end()+650] for m in re.finditer(r'jwtVerify\s*\(', s)]
        print(json.dumps({'verifier_file': str(p.relative_to(root)), 'calls': snippets,
                         'clock_context': [s[max(0, m.start()-120):m.end()+180]
                             for m in re.finditer('clockTolerance', s)]}))
        assert snippets and any('issuer' in x and 'audience' in x for x in snippets)
        # Only literal options on jwtVerify calls are accepted; dynamic policy
        # must be inspected separately, never silently assumed.
        for call in snippets:
            if 'clockTolerance' in call:
                value = re.search(r'clockTolerance:\s*(\d+)', call)
                assert value, 'Dynamic SDK leeway requires explicit source reconciliation'
                sdk_tolerance.append(int(value[1]))
            else:
                sdk_tolerance.append(0)
        excerpts.append({'file': str(p.relative_to(root)), 'sha256': hashlib.sha256(s.encode()).hexdigest(),
                         'jwtVerify_call_excerpts': snippets,
                         'auth_failure_excerpts': [s[max(0, m.start()-600):m.end()+400]
                             for m in re.finditer('unauthorized|invalid_token', s)]})
    claims = list(jose.rglob('jwt_claims_set.js'))
    assert claims
    source = claims[0].read_text()
    assert 'tolerance = 0' in source and 'JWTExpired' in source
    assert sdk_tolerance and max(sdk_tolerance) <= 120, 'SDK leeway outside bounded test budget'
    receipt = {'sdk_version': '0.20.1', 'jose_version': '6.2.3', 'sdk_clock_tolerance_seconds': max(sdk_tolerance),
               'postgrest_clock_skew_seconds': 30, 'auth_clock_leeway_seconds': 0,
               'disposable_jwt_expiry_seconds': 180, 'sdk_source': excerpts,
               'jose_claims_sha256': hashlib.sha256(source.encode()).hexdigest(),
               'no_clock_override': True}
    out = Path(os.environ['RUNNER_TEMP'])/'route-evidence'
    out.mkdir(exist_ok=True)
    (out/'expiry-contract.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    if len(sys.argv) == 2:
        configure(Path(sys.argv[1]))
    else:
        inspect()
