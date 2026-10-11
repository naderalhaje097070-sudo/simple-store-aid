"""Build the unchanged application using Nitro's existing local Node preset."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'e2e'))
from write_harness_guard import require_write_harness


def app_environment(anon):
    env = dict(os.environ)
    for name in ('LOVABLE_API_KEY', 'SUPABASE_SERVICE_ROLE_KEY', 'NODE_OPTIONS'):
        env.pop(name, None)
    env.update(MONGEZZ_DEPLOY_TARGET='ci', CI_ISOLATED_SUPABASE='1',
               SUPABASE_URL='http://127.0.0.1:54321', VITE_SUPABASE_URL='http://127.0.0.1:54321',
               SUPABASE_PUBLISHABLE_KEY=anon, VITE_SUPABASE_PUBLISHABLE_KEY=anon,
               SUPABASE_PROJECT_ID='monjez-route-ci', VITE_SUPABASE_PROJECT_ID='monjez-route-ci')
    return env


if __name__ == '__main__':
    require_write_harness()
    root = Path(os.environ['RUNNER_TEMP'])
    evidence = root / 'route-evidence'
    evidence.mkdir(exist_ok=True)
    status = json.loads((root / 'route-status.json').read_text())
    assert status['API_URL'] == 'http://127.0.0.1:54321'
    env = app_environment(status['ANON_KEY'])
    env['NITRO_PRESET'] = 'node-server'
    with (root / 'route-build-private.log').open('w') as log:
        result = subprocess.run(['bun', 'run', 'build'], env=env, stdout=log,
                                stderr=subprocess.STDOUT, timeout=300)
    receipt = {'source_sha': os.environ['EXPECTED_SOURCE'], 'command': 'NITRO_PRESET=node-server bun run build',
               'exit_code': result.returncode, 'app_entry': 'src/server.ts', 'generated_files_edited': False}
    if result.returncode == 0:
        entry = Path('.output/server/index.mjs')
        assert entry.is_file(), 'Expected native Nitro Node entry absent'
        chunks = list(Path('.output/server').rglob('*.mjs'))
        source = '\n'.join(p.read_text() for p in chunks)
        markers = ['runtime Supabase configuration does not match baked build configuration',
                   '/.well-known/oauth-protected-resource', '/mcp', 'OAuth client claim is required']
        receipt['compiled_contract_markers'] = {m: m in source for m in markers}
        receipt['built_module_sha256'] = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in chunks}
        assert all(receipt['compiled_contract_markers'].values()), 'Actual app/adapter not in built bundle'
        receipt['tracked_source_unchanged'] = subprocess.run(['git', 'diff', '--quiet', 'HEAD', '--']).returncode == 0
    else:
        # Retain safe build diagnostic categories, never a log that may contain a key.
        private = (root / 'route-build-private.log').read_text()
        receipt['known_diagnostics'] = [s for s in ('Could not resolve', 'import-protection', 'SEC_ENV_CONFIG_ERROR',
                                                  'Build failed', 'error during build') if s in private]
    (evidence / 'build.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps({k: v for k, v in receipt.items() if k != 'built_module_sha256'}))
    raise SystemExit(result.returncode)
