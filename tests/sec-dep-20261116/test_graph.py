"""Actual delta plus adversarial controls for SEC-DEP-HONO-01."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graph  # noqa: E402

root = Path(__file__).resolve().parents[2]
before_package, before_lock = graph.show(graph.BASE, 'package.json'), graph.show(graph.BASE, 'bun.lock')
after_package, after_lock = (root / 'package.json').read_text(), (root / 'bun.lock').read_text()


class Graph(unittest.TestCase):
    def deny(self, package=None, lock=None, before=None):
        with self.assertRaises(ValueError):
            graph.verify(before_package if before is None else before, before_lock,
                         after_package if package is None else json.dumps(package, indent=2) + '\n',
                         after_lock if lock is None else lock)

    def test_actual_delta(self):
        r = graph.verify(before_package, before_lock, after_package, after_lock)
        self.assertEqual((r['entries'], r['changed_rows']), (1086, ['@hono/node-server', 'hono']))

    def test_historical_20261102_contract_still_proven(self):
        h = graph.graph_20261102.verify(graph.graph_20261102.baseline(root, 'package.json'),
                                        graph.graph_20261102.baseline(root, 'bun.lock'), before_package, before_lock)
        self.assertEqual(h['after_entries'], 1086)

    def test_unchanged_head_is_not_this_delta(self): self.deny(package=json.loads(before_package), lock=before_lock)
    def test_wrong_baseline(self): self.deny(before=before_package + ' ')
    def test_old_consumer_lock(self): self.deny(lock=after_lock.replace('"lockfileVersion": 1', '"lockfileVersion": 3'))
    def test_config_drift(self): self.deny(lock=after_lock.replace('"configVersion": 1', '"configVersion": 0'))
    def test_other_hono_version(self): self.deny(lock=after_lock.replace('hono@4.13.16', 'hono@4.13.17'))
    def test_hono_integrity(self): self.deny(lock=after_lock.replace(graph.NEW_ROWS['hono'][3], 'sha512-unreviewed'))
    def test_node_server_integrity(self):
        self.deny(lock=after_lock.replace(graph.NEW_ROWS['@hono/node-server'][3], 'sha512-unreviewed'))
    def test_node_server_peer_metadata(self): self.deny(lock=after_lock.replace('"^4 || ^5.0.0-0"', '"*"'))
    def test_hono_locator(self):
        self.deny(lock=after_lock.replace('"hono": ["hono@4.13.16", ""', '"hono": ["hono@4.13.16", "https://unreviewed.invalid/h.tgz"'))
    def test_unrelated_runtime_downgrade(self): self.deny(lock=after_lock.replace('@supabase/supabase-js@2.110.5', '@supabase/supabase-js@2.110.4'))
    def test_extra_hidden_copy(self): self.deny(lock=after_lock + '\n    "hidden/hono": ["hono@4.13.11", "", {}, "sha512-hidden"],\n')
    def test_lock_pin_disagrees(self): self.deny(lock=after_lock.replace('"hono": "4.13.16",', '"hono": "4.13.11",'))
    def test_whitespace_drift(self): self.deny(lock=after_lock.replace('"workspaces": {', '"workspaces":  {'))
    def test_resolution_disagrees(self):
        p = json.loads(after_package); p['resolutions']['hono'] = '4.13.17'; self.deny(package=p)
    def test_override_reverted(self):
        p = json.loads(after_package); p['overrides']['@hono/node-server'] = '2.1.3'; self.deny(package=p)
    def test_extra_override(self):
        p = json.loads(after_package); p['overrides']['unrelated'] = '1.0.0'; self.deny(package=p)
    def test_removed_existing_security_floor(self):
        p = json.loads(after_package); p['overrides'].pop('esbuild'); self.deny(package=p)
    def test_removed_patch(self):
        p = json.loads(after_package); p.pop('patchedDependencies'); self.deny(package=p)
    def test_release_age_rule_and_reviewed_files_unchanged(self):
        for name in graph.UNCHANGED:
            self.assertEqual((root / name).read_bytes(), graph.show(graph.BASE, name, binary=True), name)

    def test_published_older_than_release_age(self):
        import datetime
        for name, ts in graph.PUBLISHED.items():
            t = datetime.datetime.fromisoformat(ts.replace('Z', '+00:00'))
            self.assertGreaterEqual((datetime.datetime(2026, 11, 16, tzinfo=datetime.timezone.utc) - t).total_seconds(), 86400, name)
        self.assertIn('minimumReleaseAge = 86400', (root / 'bunfig.toml').read_text())


if __name__ == '__main__':
    unittest.main()
