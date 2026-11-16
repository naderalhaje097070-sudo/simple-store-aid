"""SEC-DEP-C6-MAIN: admit main's reviewed Lovable dependency sync into integration.

Layered on the earlier admissions, which stay unchanged and keep proving their own deltas:
  20261102: 50530716 -> 2e4c8cc (tests/sec-dep-20261102)
  20261116: 2e4c8cc  -> HEAD16  (tests/sec-dep-20261116, hono 4.13.16, @hono/node-server 2.1.6)
This verifier admits exactly one further delta, HEAD16 -> working tree, created by merging main
(MAIN, which carries the owner-merged Lovable sync #80) into integration:
  package.json: HEAD16 with only devDependencies/@lovable.dev/vite-tanstack-config 2.9.1 -> 2.26.5.
  bun.lock:     main's lock, byte-exact, with only the four reviewed 20261116 hono lines replaced.
                So no lock byte comes from anywhere other than reviewed main or reviewed SEC-DEP-HONO-01.
The resulting row delta against HEAD16 is pinned name by name below, as review evidence and as a
second, independent check.
"""
import hashlib
import importlib.util
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# Both earlier verifiers are named graph.py, so load them by exact path.
graph_20261102 = _load('graph_20261102', 'tests/sec-dep-20261102/graph.py')
graph_20261116 = _load('graph_20261116', 'tests/sec-dep-20261116/graph.py')

HEAD16 = 'b32d59165941f8b09555fa646c206dc41a6fc192'  # integration tip proven by the 20261116 verifier
MAIN = '1c5276fae77cb71f49d868fe71d17d84c5d3c6b3'    # main: Lovable sync #80, owner-merged
BLOBS = {  # git blob ids of the exact inputs
    (HEAD16, 'package.json'): '2f947205918bf15e51b1a114d467c9422305bf5b',
    (HEAD16, 'bun.lock'): '42b1f8ceee8b5094e4debbb01910768a1dd2e3c2',
    (MAIN, 'package.json'): '5af207153da9176f31ae1de1baa0b642d44c0fbc',
    (MAIN, 'bun.lock'): 'b5aa3b7645c80e80b64ada92ea0c39c95a83f5c8',
}
PKG = ('devDependencies', '@lovable.dev/vite-tanstack-config', '2.9.1', '2.26.5')
UNCHANGED = ['bunfig.toml', 'patches/minimatch@11.0.1.patch', 'vendor/rollup-plugin-node-resolve-16.0.3-b7.tgz']
ENTRIES_BEFORE, ENTRIES_AFTER = 1086, 1070

_LC = ['android-arm64', 'darwin-arm64', 'darwin-x64', 'freebsd-x64', 'linux-arm-gnueabihf', 'linux-arm64-gnu',
       'linux-arm64-musl', 'linux-x64-gnu', 'linux-x64-musl', 'win32-arm64-msvc', 'win32-x64-msvc']
_lc = ['lightningcss'] + ['lightningcss-' + p for p in _LC]
# Row-path delta HEAD16 -> head (Bun's hoisting of lightningcss 1.32/1.33 and of workbox's ajv helper).
ADDED = sorted(['@tailwindcss/node/lightningcss'] + ['@tailwindcss/node/lightningcss/' + n for n in _lc[1:]]
               + ['workbox-build/@apideck/better-ajv-errors'])
REMOVED = sorted(['@apideck/better-ajv-errors', '@apideck/better-ajv-errors/ajv',
                  '@apideck/better-ajv-errors/ajv/json-schema-traverse',
                  '@lovable.dev/vite-plugin-dev-server-bridge', '@lovable.dev/vite-plugin-hmr-gate']
                 + [pre + n for pre in ['@tanstack/start-plugin-core/', 'vite/'] for n in ['lightningcss'] +
                    ['lightningcss/' + m for m in _lc[1:]]])
CHANGED = {'@lovable.dev/vite-tanstack-config': ('2.9.1', '2.26.5'), **{n: ('1.32.0', '1.33.0') for n in _lc}}
# npm publish times (registry "time" field) for the bunfig 24h minimumReleaseAge review.
PUBLISHED = {'@lovable.dev/vite-tanstack-config@2.26.5': '2026-10-09T11:31:33.870Z',
             'lightningcss@1.33.0': '2026-07-20T05:11:09.509Z'}
INSTALLED = {'@lovable.dev/vite-tanstack-config': '2.26.5', 'lightningcss': '1.33.0'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def blob(text):
    raw = text.encode()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


show, read = graph_20261116.show, graph_20261116.read


def inputs():
    data = {k: show(*k) for k in BLOBS}
    for k, want in BLOBS.items():
        require(blob(data[k]) == want, 'Wrong exact input: ' + '@'.join(k))
    return data


def expected_lock(main_lock):
    lock = main_lock
    for a, b in graph_20261116.LINES:
        require(lock.count(a) == 1, 'Main line not unique: ' + a[:60])
        lock = lock.replace(a, b)
    return lock


def verify(head16_package, head16_lock, main_lock, after_package, after_lock):
    for text, key in [(head16_package, (HEAD16, 'package.json')), (head16_lock, (HEAD16, 'bun.lock')),
                      (main_lock, (MAIN, 'bun.lock'))]:
        require(blob(text) == BLOBS[key], 'Wrong exact baseline: ' + '@'.join(key))
    group, name, old, new = PKG
    # package.json: semantic and byte-exact single-pin delta on HEAD16.
    want = json.loads(head16_package)
    require(want[group].get(name) == old, 'Baseline pin missing: ' + name)
    want[group][name] = new
    require(json.loads(after_package) == want, 'Undeclared package contract change')
    line = f'"{name}": "{old}"'
    require(head16_package.count(line) == 1, 'Baseline package line not unique: ' + name)
    require(head16_package.replace(line, f'"{name}": "{new}"') == after_package,
            'package.json differs from the reviewed one-pin delta')
    # bun.lock: byte-exact main lock plus the reviewed hono lines.
    require(after_lock == expected_lock(main_lock), 'Lock differs from reviewed main plus the reviewed hono lines')
    # Independent check: the row delta against HEAD16 is exactly the reviewed one.
    old_rows, new_rows = graph_20261102.rows(head16_lock), graph_20261102.rows(after_lock)
    require((len(old_rows), len(new_rows)) == (ENTRIES_BEFORE, ENTRIES_AFTER), 'Unreviewed lock entry count')
    require(sorted(set(new_rows) - set(old_rows)) == ADDED, 'Unreviewed added lock path')
    require(sorted(set(old_rows) - set(new_rows)) == REMOVED, 'Unreviewed removed lock path')
    changed = sorted(p for p in set(old_rows) & set(new_rows) if old_rows[p] != new_rows[p])
    require(changed == sorted(CHANGED), 'Unreviewed changed lock row: ' + ','.join(changed))
    for p, (a, b) in CHANGED.items():
        require(old_rows[p][0] == f'{p}@{a}' and new_rows[p][0] == f'{p}@{b}', 'Unreviewed version: ' + p)
    # Hoisting only: every added or changed row (except the Lovable package itself, whose bytes come
    # from reviewed main) must be identical to a row that already existed at HEAD16.
    known = [json.dumps(v, sort_keys=True) for v in old_rows.values()]
    for p in ADDED + [c for c in changed if c != PKG[1]]:
        require(json.dumps(new_rows[p], sort_keys=True) in known, 'Row is not a copy of a reviewed row: ' + p)
    # The hono pins from 20261116 are still exactly in place.
    for n in graph_20261116.PINS:
        require(new_rows[n] == graph_20261116.NEW_ROWS[n], 'Hono admission lost: ' + n)
    return {'head16': HEAD16, 'main': MAIN, 'entries': len(new_rows), 'added': len(ADDED), 'removed': len(REMOVED),
            'changed': changed, 'published': PUBLISHED, 'lock_bytes_from': 'main + 20261116 LINES'}


def installed(root=ROOT):
    seen = graph_20261116.installed(root)
    for name, version in INSTALLED.items():
        meta = json.loads((Path(root) / 'node_modules' / name / 'package.json').read_text())
        require(meta['name'] == name and meta['version'] == version, 'Installed version drift: ' + name)
        seen[name] = version
    return seen


def main():
    data = inputs()
    # 1. History: the unchanged 20261116 verifier still proves 2e4c8cc -> HEAD16 (and 20261102 inside it).
    h16 = graph_20261116.verify(show(graph_20261116.BASE, 'package.json'), show(graph_20261116.BASE, 'bun.lock'),
                                data[(HEAD16, 'package.json')], data[(HEAD16, 'bun.lock')])
    # 2. This change: HEAD16 -> working tree.
    receipt = verify(data[(HEAD16, 'package.json')], data[(HEAD16, 'bun.lock')], data[(MAIN, 'bun.lock')],
                     read(ROOT / 'package.json'), read(ROOT / 'bun.lock'))
    for name in UNCHANGED:
        require((ROOT / name).read_bytes() == show(HEAD16, name, binary=True), 'Reviewed file changed: ' + name)
    receipt['unchanged'] = UNCHANGED
    receipt['history_20261116_changed_rows'] = h16['changed_rows']
    if '--installed' in sys.argv:
        receipt['installed'] = installed()
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
