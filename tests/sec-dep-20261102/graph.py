"""Independent whole-lock delta: four official versions; no unrelated graph drift."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

BASE = '50530716ab3163199de4187d3776356a49813dda'
PATCH = 'patches/minimatch@11.0.1.patch'
BEFORE = {'package.json':'2b01ba68ea30be3e801cf75c256fb199849d4044','bun.lock':'6d017ff0e72d9dbde3d4e3c88ce6b3adc2c0c320'}
ADDED = {
    'glob@14.0.2':'sha512-vfMgTR2djMHPUchsJMLpZlYQvtjVL+mHpEr5wPpoCbQs2vr/FBNK+3Gnl9Ara1DSs4Aeg4eG9HiADb5/rkY/ZA==',
    'minimatch@11.0.1':'sha512-t+Vn6DX4wPCxS23y03C0uhF7S1jpi1GfqPrnlEipCJaA2ykiNbMkVlDutZtmvLfRcUN6R8AYVlzTsQrT4RZoLQ==',
    'path-scurry@3.0.0':'sha512-1pTbQqH1wIwMi/eleQ5leFTTCkzFsPcgXNjwOA8YGGW/W4/kHT3dssE7Z6NH+zuqNLOzOB0uaD61yl7cAcVhgg==',
    '@isaacs/nonrecursive-glob-match@1.0.3':'sha512-SI7kyKHq4XXDRozw+r9GlRZkia1ZkFrpLW98r2IC2Bpr8YkFGE3fvjzmxCG0x78A++69HmDNrDvSMYBZmHGpKA==',
}
ADDED_METADATA = {
    'glob@14.0.2': {'dependencies': {'minimatch':'^11.0.0','minipass':'^7.1.3','path-scurry':'^3.0.0'}},
    'minimatch@11.0.1': {'dependencies': {'@isaacs/nonrecursive-glob-match':'^1.0.1','brace-expansion':'^5.0.12'}},
    'path-scurry@3.0.0': {'dependencies': {'lru-cache':'^11.0.0','minipass':'^7.1.2'}},
    '@isaacs/nonrecursive-glob-match@1.0.3': {},
}
REMOVED = {'@isaacs/cliui@9.0.0','balanced-match@1.0.2','brace-expansion@1.1.21','brace-expansion@2.1.7',
           'concat-map@0.0.1','foreground-child@3.3.1','glob@11.1.0','jackspeak@4.2.3',
           'minimatch@10.2.5','minimatch@3.1.5','minimatch@5.1.9','package-json-from-dist@1.0.1',
           'path-scurry@2.0.2','signal-exit@4.1.0'}
REMOVED_PATHS = {'@typescript-eslint/typescript-estree/minimatch/brace-expansion/balanced-match',
                 'filelist/minimatch/brace-expansion','foreground-child','glob/minimatch',
                 '@typescript-eslint/typescript-estree/minimatch/brace-expansion','jackspeak','signal-exit',
                 '@typescript-eslint/typescript-estree/minimatch','glob/minimatch/brace-expansion','@isaacs/cliui',
                 'glob/minimatch/brace-expansion/balanced-match','filelist/minimatch','package-json-from-dist','concat-map'}


def require(ok, message):
    if not ok: raise ValueError(message)


def rows(text):
    result = {}
    for line in text.splitlines():
        if re.match(r'^\s*"[^"]+": \[', line):
            entry = json.loads('{' + line.strip().removesuffix(',') + '}')
            require(not set(entry) & set(result), 'Duplicate locked physical path')
            result.update(entry)
    require(bool(result), 'Missing lock rows')
    return result


def blob(text):
    raw = text.encode()
    return hashlib.sha1(b'blob ' + str(len(raw)).encode() + b'\0' + raw).hexdigest()


def verify(before_package, before_lock, after_package, after_lock):
    require(blob(before_package) == BEFORE['package.json'] and blob(before_lock) == BEFORE['bun.lock'], 'Wrong exact graph baseline')
    original = json.loads(before_package)
    for group in ['overrides','resolutions']:
        original[group].update({'glob':'14.0.2','minimatch':'11.0.1'})
    original['patchedDependencies'] = {'minimatch@11.0.1':PATCH}
    require(json.loads(after_package) == original, 'Undeclared package contract change')
    require(re.search(r'"lockfileVersion":\s*1\s*,',after_lock) is not None, 'Old consumer lock version changed')
    require(re.search(r'"configVersion":\s*1\s*,',after_lock) is not None, 'Existing project lock config changed')
    old, new = rows(before_lock), rows(after_lock)
    require(len(old) == 1099 and len(new) == 1086, 'Unreviewed physical graph count')
    require(set(old)-set(new) == REMOVED_PATHS and set(new)-set(old) == {'@isaacs/nonrecursive-glob-match'}, 'Unreviewed physical dependency path change')
    canonical = lambda row: json.dumps(row,sort_keys=True,separators=(',',':'))
    a, b = {canonical(r) for r in old.values()}, {canonical(r) for r in new.values()}
    added, removed = [json.loads(r) for r in sorted(b-a)], [json.loads(r) for r in sorted(a-b)]
    require(len(added) == 4 and {r[0] for r in added} == set(ADDED), 'Unrelated new version or retained metadata mutation')
    require({r[0] for r in removed} == REMOVED and len(removed) == 14, 'Unrelated version removal or retained metadata mutation')
    for row in added:
        require(row[-1] == ADDED[row[0]], 'Official package integrity changed')
        require(row[1] == '' and row[2] == ADDED_METADATA[row[0]], 'Official new package metadata changed')
    # Three apparent root version changes are reviewed; brace5/balanced4 merely
    # move from old nested locations. Every other retained row stays exact.
    changed = [p for p in old.keys() & new.keys() if old[p] != new[p]]
    require(set(changed) == {'glob','minimatch','path-scurry','brace-expansion','balanced-match'}, 'Unreviewed hoist/path mutation')
    return {'before_entries':len(old),'after_entries':len(new),'new_official_versions':sorted(ADDED),
            'removed_old_versions':sorted(REMOVED),'all_other_retained_package_metadata_exact':True,
            'changed_physical_rows':sorted(changed),'manual_lock_edits':False,'financial_acceptance':False}


def baseline(root, name):
    return subprocess.check_output(['git','-C',str(root),'show',f'{BASE}:{name}'],text=True)


if __name__ == '__main__':
    root = Path(__file__).resolve().parents[2]
    receipt = verify(baseline(root,'package.json'),baseline(root,'bun.lock'),(root/'package.json').read_text(),(root/'bun.lock').read_text())
    require((root/'bunfig.toml').read_text() == baseline(root,'bunfig.toml'), 'Release-age rule changed')
    name = 'vendor/rollup-plugin-node-resolve-16.0.3-b7.tgz'
    before = subprocess.check_output(['git','-C',str(root),'show',f'{BASE}:{name}'])
    require((root/name).read_bytes() == before, 'Previously reviewed vendor changed')
    print(json.dumps(receipt,indent=2))
