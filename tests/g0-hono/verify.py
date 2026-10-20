"""Bounded Hono evidence; raw audit/lint failures remain visible, without project data."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

BASE = '89606268234724241065fdd0a8abe84467dd8b51'
MAIN = '43d6edbccb66fb06ce0fcb93734ad59532d1aeae'
OUT = Path('evidence/g0-hono')
OUT.mkdir(parents=True, exist_ok=True)
TARGETS = {'GHSA-' + suffix for suffix in [
    '8j4g-w8fx-2239', 'f23p-vx2j-j53r', '79qm-7rj5-m7r9', '54fx-42gc-7vw4',
    'gqvv-2mrq-wpjv', 'g6gw-c38x-mqfc', 'crvj-82cr-hjcx', 'hxh3-vqpv-xpqv',
]}


def save(name, value):
    (OUT / name).write_text(json.dumps(value, indent=2) + '\n')


def git_file(ref, path):
    return subprocess.check_output(['git', 'show', f'{ref}:{path}'])


def jsonc(data):
    return json.loads(re.sub(r',\s*([}\]])', r'\1', data.decode()))


def command(name, argv):
    result = subprocess.run(argv, capture_output=True, timeout=240)
    (OUT / (name + '.stdout')).write_bytes(result.stdout)
    (OUT / (name + '.stderr')).write_bytes(result.stderr)
    save(name + '.receipt.json', {'command': argv, 'exit_code': result.returncode,
         'stdout_sha256': hashlib.sha256(result.stdout).hexdigest(),
         'stderr_sha256': hashlib.sha256(result.stderr).hexdigest()})
    return result


def graph():
    before = jsonc(git_file(BASE, 'bun.lock'))
    after = jsonc(Path('bun.lock').read_bytes())
    changed = [k for k in before['packages'].keys() | after['packages'].keys()
               if before['packages'].get(k) != after['packages'].get(k)]
    assert changed == ['hono'], changed
    old, new = before['packages'].pop('hono'), after['packages'].pop('hono')
    assert old[0] == 'hono@4.12.27' and new[0] == 'hono@4.13.7'
    assert after['overrides'].pop('hono') == '4.13.7'
    assert before == after, 'Unrelated generated graph change'
    manifest = json.loads(Path('package.json').read_text())
    for key in ['overrides', 'resolutions']:
        assert manifest[key].pop('hono') == '4.13.7'
    assert manifest == json.loads(git_file(BASE, 'package.json'))
    assert Path('bunfig.toml').read_bytes() == git_file(BASE, 'bunfig.toml')
    save('graph.json', {'source': subprocess.check_output(['git', 'rev-parse', 'HEAD']).decode().strip(),
         'base': BASE, 'changed_packages': changed, 'old': old, 'new': new,
         'unrelated_graph_changes': False, 'lock_sha256': hashlib.sha256(Path('bun.lock').read_bytes()).hexdigest()})


def mutations():
    original = Path('bun.lock').read_text()
    source = Path('tests/unit/dependency-security.test.ts').read_text()
    cases = {
        'patched': original,
        'old': original.replace('hono@4.13.7', 'hono@4.13.6'),
        'prerelease': original.replace('hono@4.13.7', 'hono@4.13.7-rc.1'),
        'unreviewed-major': original.replace('hono@4.13.7', 'hono@5.0.0'),
        'nested-old': original.replace('"packages": {', '"packages": {\n "fixture/hono": ["hono@4.12.27", "", {}],', 1),
    }
    results = []
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        test = root / 'tests/unit/dependency-security.test.ts'
        test.parent.mkdir(parents=True)
        test.write_text(source)
        for name, lock in cases.items():
            (root / 'bun.lock').write_text(lock)
            result = command('guard-' + name, ['bun', 'test', str(test)])
            results.append({'case': name, 'exit_code': result.returncode})
            assert (result.returncode == 0) == (name == 'patched'), results
    save('guard-mutations.json', results)


def lint():
    cjs = command('lint-cjs', ['node_modules/.bin/eslint', 'tests/g01-acceptance/dns_trace.cjs',
                             'tests/g01-acceptance/test_cf_fetch.cjs', '--format', 'json'])
    assert cjs.returncode in (0, 1), 'Lint tooling failure'
    path = Path('src/routes/_authenticated/app.tsx')
    original = path.read_bytes()
    try:
        current = command('lint-app-candidate', ['node_modules/.bin/eslint', str(path), '--format', 'json'])
        path.write_bytes(git_file(MAIN, str(path)))
        main = command('lint-app-main', ['node_modules/.bin/eslint', str(path), '--format', 'json'])
    finally:
        path.write_bytes(original)
    assert current.returncode in (0, 1) and main.returncode in (0, 1), 'Lint tooling failure'
    rows = {}
    for name, result in [('cjs', cjs), ('app-candidate', current), ('app-main', main)]:
        parsed = json.loads(result.stdout)
        rows[name] = [{'path': str(Path(row['filePath']).relative_to(Path.cwd())),
                       'errors': row['errorCount'], 'warnings': row['warningCount'],
                       'messages': row['messages']} for row in parsed]
    save('lint-detail.json', rows)
    assert path.read_bytes() == original


def vendor():
    found = []
    for package in ['hono', '@modelcontextprotocol/sdk', '@hono/node-server', '@lovable.dev/mcp-js']:
        root = Path('node_modules') / package
        manifest = json.loads((root / 'package.json').read_text())
        save(package.replace('/', '_').replace('@', '') + '-installed.json', manifest)
        for path in sorted(root.rglob('*')):
            if path.suffix not in ('.js', '.mjs') or not path.is_file():
                continue
            data = path.read_text()
            imports = re.findall(r'(?:from\s*|import\s*\(|require\s*\()\s*[\"\']([^\"\']+)[\"\']', data)
            relevant = [x for x in imports if x == 'hono' or x.startswith(('hono/', '@modelcontextprotocol/sdk/'))]
            if relevant:
                found.append({'path': str(path), 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'imports': relevant})
    save('vendor-imports.json', found)


def audit():
    result = command('audit', ['bun', 'audit', '--json'])
    parsed = json.loads(result.stdout)
    assert isinstance(parsed, dict), 'Unrecognized audit result'
    records = []
    if 'advisories' in parsed:
        records = list(parsed['advisories'].values())
    elif all(isinstance(v, list) for v in parsed.values()):
        records = [dict(module_name=k, **v) for k, values in parsed.items() for v in values]
    else:
        raise AssertionError('Unsupported audit schema; inspect raw output')
    assert records or result.returncode == 0, 'Empty audit cannot hide a failed query'
    ids = set(re.findall(r'GHSA-[a-z0-9-]+', json.dumps(records)))
    counts = {}
    for record in records:
        severity = record['severity'].lower()
        counts[severity] = counts.get(severity, 0) + 1
    save('audit-summary.json', {'exit_code': result.returncode, 'counts': counts,
         'target_ids': sorted(TARGETS), 'target_ids_remaining': sorted(ids & TARGETS),
         'all_reported_ids': sorted(ids), 'records': records, 'g0_accepted': False})
    assert not ids & TARGETS, 'Targeted advisory remains'
    assert not counts.get('critical', 0) and not counts.get('high', 0), 'Critical/High blocker'
    # Preserve the complete scanner result as an actual failing G0 gate if findings remain.
    raise SystemExit(result.returncode)


if __name__ == '__main__':
    {'graph': graph, 'mutations': mutations, 'lint': lint, 'vendor': vendor, 'audit': audit}[sys.argv[1]]()
