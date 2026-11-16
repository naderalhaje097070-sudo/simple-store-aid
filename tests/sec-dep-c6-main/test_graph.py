"""Actual delta plus adversarial controls for SEC-DEP-C6-MAIN."""
import json
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import graph  # noqa: E402

root = Path(__file__).resolve().parents[2]
data = graph.inputs()
h_pkg, h_lock = data[(graph.HEAD16, 'package.json')], data[(graph.HEAD16, 'bun.lock')]
m_lock = data[(graph.MAIN, 'bun.lock')]
a_pkg, a_lock = graph.read(root / 'package.json'), graph.read(root / 'bun.lock')
ROW = '"@lovable.dev/vite-tanstack-config": ["@lovable.dev/vite-tanstack-config@2.26.5"'


class Graph(unittest.TestCase):
    def deny(self, pkg=None, lock=None, head_pkg=None, head_lock=None, main_lock=None):
        with self.assertRaises(ValueError):
            graph.verify(h_pkg if head_pkg is None else head_pkg, h_lock if head_lock is None else head_lock,
                         m_lock if main_lock is None else main_lock,
                         a_pkg if pkg is None else pkg, a_lock if lock is None else lock)

    def test_actual_delta(self):
        r = graph.verify(h_pkg, h_lock, m_lock, a_pkg, a_lock)
        self.assertEqual((r['entries'], r['added'], r['removed']), (1070, 13, 29))
        self.assertEqual(len(r['changed']), 13)

    def test_history_20261116_still_proven(self):
        h = graph.graph_20261116.verify(graph.show(graph.graph_20261116.BASE, 'package.json'),
                                        graph.show(graph.graph_20261116.BASE, 'bun.lock'), h_pkg, h_lock)
        self.assertEqual(h['changed_rows'], ['@hono/node-server', 'hono'])

    # Wrong inputs
    def test_wrong_head16_package(self): self.deny(head_pkg=h_pkg + ' ')
    def test_wrong_head16_lock(self): self.deny(head_lock=h_lock + ' ')
    def test_wrong_main_lock(self): self.deny(main_lock=m_lock.replace('"lockfileVersion": 1', '"lockfileVersion": 2'))
    def test_unchanged_head_is_not_this_delta(self): self.deny(pkg=h_pkg, lock=h_lock)

    # package.json
    def test_other_lovable_version(self): self.deny(pkg=a_pkg.replace('"2.26.5"', '"2.26.6"'))
    def test_extra_dependency(self):
        p = json.loads(a_pkg); p['dependencies']['left-pad'] = '1.3.0'
        self.deny(pkg=json.dumps(p, indent=2) + '\n')
    def test_hono_reverted_in_package(self): self.deny(pkg=a_pkg.replace('"hono": "4.13.16"', '"hono": "4.13.11"', 1))
    def test_package_whitespace(self): self.deny(pkg=a_pkg.replace('{\n', '{ \n', 1))
    def test_package_crlf(self): self.deny(pkg=a_pkg.replace('\n', '\r\n'))

    # bun.lock
    def test_main_lock_without_hono_fix(self): self.deny(lock=m_lock)
    def test_hono_rows_reverted(self):
        lock = a_lock
        for a, b in graph.graph_20261116.LINES:
            lock = lock.replace(b, a)
        self.deny(lock=lock)
    def test_one_hono_line_reverted(self):
        a, b = graph.graph_20261116.LINES[3]
        self.deny(lock=a_lock.replace(b, a))
    def test_lovable_integrity(self):
        i = a_lock.index(ROW); j = a_lock.index('sha512-', i)
        self.deny(lock=a_lock[:j] + 'sha512-unreviewed' + a_lock[j + 20:])
    def test_lightningcss_version(self): self.deny(lock=a_lock.replace('lightningcss@1.33.0', 'lightningcss@1.33.1', 1))
    def test_extra_hidden_copy(self): self.deny(lock=a_lock + '\n    "hidden/hono": ["hono@4.13.11", "", {}, "sha512-hidden"],\n')
    def test_removed_row(self):
        i = a_lock.index('    "zod": ['); j = a_lock.index('\n\n', i)
        self.deny(lock=a_lock[:i] + a_lock[j + 2:])
    def test_lock_whitespace(self): self.deny(lock=a_lock.replace('"workspaces": {', '"workspaces":  {'))
    def test_lock_crlf_single_line(self): self.deny(lock=a_lock.replace('\n', '\r\n', 1))
    def test_registry_swap(self):
        self.deny(lock=a_lock.replace('https://europe-west1-npm.pkg.dev/lovable-core-prod/sandbox-npm-cache/',
                                      'https://evil.example/', 1))

    # Row-delta pins are independent of the byte check
    def test_pinned_delta_is_enforced(self):
        saved = graph.ADDED
        try:
            graph.ADDED = saved[1:]
            self.deny()
        finally:
            graph.ADDED = saved

    def test_release_age_and_reviewed_files_unchanged(self):
        for name in graph.UNCHANGED:
            self.assertEqual((root / name).read_bytes(), graph.show(graph.HEAD16, name, binary=True), name)
        self.assertIn('minimumReleaseAge = 86400', (root / 'bunfig.toml').read_text())

    def test_recorded_publish_times_clear_release_age(self):
        # Recorded from the npm registry when this delta was reviewed (2026-11-16); both older than 24h.
        for when in graph.PUBLISHED.values():
            self.assertLess(when, '2026-11-15T00:00:00Z')


if __name__ == '__main__':
    unittest.main()
