"""Actual whole-graph baseline and adversarial unrelated-change controls."""
import copy
import json
from pathlib import Path
import sys
import unittest
import graph

root = Path(__file__).resolve().parents[2]
prepared = Path(sys.argv.pop(1)) if len(sys.argv) > 1 else None
if prepared:
    before_package = (prepared/'baseline-package.json').read_text()
    before_lock = (prepared/'baseline-bun.lock').read_text()
    after_package = (prepared/'package.json').read_text()
    after_lock = (prepared/'bun.lock').read_text()
else:
    before_package, before_lock = (graph.baseline(root,p) for p in ['package.json','bun.lock'])
    after_package, after_lock = ((root/p).read_text() for p in ['package.json','bun.lock'])


class Graph(unittest.TestCase):
    def deny(self, package=None, lock=None, before=None):
        with self.assertRaises(ValueError):
            graph.verify(before_package if before is None else before,before_lock,
                         after_package if package is None else json.dumps(package),after_lock if lock is None else lock)
    def test_actual_prepared_graph(self): self.assertEqual(graph.verify(before_package,before_lock,after_package,after_lock)['after_entries'],1086)
    def test_wrong_baseline(self): self.deny(before=before_package+' ')
    def test_old_consumer_lock(self): self.deny(lock=after_lock.replace('"lockfileVersion": 1','"lockfileVersion": 3'))
    def test_config_drift(self): self.deny(lock=after_lock.replace('"configVersion": 1','"configVersion": 0'))
    def test_unrelated_runtime_downgrade(self): self.deny(lock=after_lock.replace('@supabase/supabase-js@2.110.5','@supabase/supabase-js@2.110.4'))
    def test_unrelated_metadata(self): self.deny(lock=after_lock.replace('"@supabase/supabase-js": [','"unexpected-sdk-path": ['))
    def test_unrelated_locator(self):
        line=next(l for l in after_lock.splitlines() if l.strip().startswith('"@supabase/supabase-js": ['))
        row=json.loads('{'+line.strip().removesuffix(',')+'}')
        row['@supabase/supabase-js'][1]='https://unreviewed.invalid/archive.tgz'
        replacement=json.dumps(row)[1:-1]+','
        self.assertTrue(line != replacement,'Locator mutation must change bytes')
        self.deny(lock=after_lock.replace(line,replacement))
    def test_fixed_engine_integrity(self): self.deny(lock=after_lock.replace(graph.ADDED['minimatch@11.0.1'],'sha512-unreviewed'))
    def test_new_engine_dependency_metadata(self):
        original='"minimatch": "^11.0.0"'
        self.assertTrue(original in after_lock,'Expected official glob dependency')
        self.deny(lock=after_lock.replace(original,'"minimatch": "^11.1.0"'))
    def test_unapproved_modern_major(self): self.deny(lock=after_lock.replace('minimatch@11.0.1','minimatch@12.0.0'))
    def test_extra_legacy_copy(self): self.deny(lock=after_lock+'\n    "hidden/minimatch": ["minimatch@3.1.5", "", {}, "sha512-hidden"],\n')
    def test_duplicate_path(self):
        line=next(l for l in after_lock.splitlines() if '"glob": [' in l)
        self.deny(lock=after_lock+'\n'+line+'\n')
    def test_removed_patch(self):
        p=json.loads(after_package);p.pop('patchedDependencies');self.deny(package=p)
    def test_extra_override(self):
        p=json.loads(after_package);p['overrides']['unrelated']='1.0.0';self.deny(package=p)
    def test_resolution_disagrees(self):
        p=json.loads(after_package);p['resolutions']['glob']='14.0.3';self.deny(package=p)
    def test_removed_existing_security_floor(self):
        p=json.loads(after_package);p['overrides'].pop('esbuild');self.deny(package=p)


if __name__ == '__main__': unittest.main()
