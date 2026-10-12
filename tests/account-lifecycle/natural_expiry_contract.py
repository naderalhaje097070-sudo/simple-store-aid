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
    relevant = [(p, s) for p, s in sources if 'jwtVerify' in s and 'OAuth client claim is required' in s]
    print(json.dumps({'sdk_verifier_candidates': [str(p.relative_to(root)) for p, s in sources
                      if 'jwtVerify' in s or 'OAuth client claim is required' in s]}))
    assert relevant, 'Installed SDK verifier source could not be reconciled'
    excerpts = []
    for p, s in relevant:
        assert 'clockTolerance' not in s, 'Inspect new explicit SDK leeway before live testing'
        snippets = [s[max(0, m.start()-100):m.end()+650] for m in re.finditer(r'jwtVerify\s*\(', s)]
        assert snippets and any('issuer' in x and 'audience' in x for x in snippets)
        excerpts.append({'file': str(p.relative_to(root)), 'sha256': hashlib.sha256(s.encode()).hexdigest(),
                         'jwtVerify_call_excerpts': snippets})
    claims = list(jose.rglob('jwt_claims_set.js'))
    assert claims
    source = claims[0].read_text()
    assert 'tolerance = 0' in source and 'JWTExpired' in source
    receipt = {'sdk_version': '0.20.1', 'jose_version': '6.2.3', 'sdk_clock_tolerance_seconds': 0,
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
