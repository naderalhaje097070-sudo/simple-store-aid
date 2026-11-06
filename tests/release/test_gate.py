"""Negative and positive controls for the release gate, on throwaway git repos."""
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gate  # noqa: E402

M = 'supabase/migrations/'
REMOTE = f'https://github.com/{gate.REPOSITORY}.git'


def run(root, *args):
    return subprocess.run(['git', '-C', str(root), *args], check=True, capture_output=True).stdout.decode().strip()


class Repo:
    """origin/main with two migrations; tests then commit candidate changes on HEAD."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        run(self.root, 'init', '-q', '-b', 'main')
        run(self.root, 'config', 'user.email', 'gate@test')
        run(self.root, 'config', 'user.name', 'gate')
        run(self.root, 'remote', 'add', 'origin', REMOTE)
        self.write(M + '20261001000000_a.sql', 'select 1;\n')
        self.write(M + '20261021000000_b.sql', 'select 2;\n')
        self.commit('base')
        run(self.root, 'update-ref', 'refs/remotes/origin/main', 'HEAD')
        run(self.root, 'checkout', '-q', '-b', 'candidate')

    def write(self, path, text):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)

    def commit(self, message):
        run(self.root, 'add', '-A')
        run(self.root, 'commit', '-q', '-m', message)
        return run(self.root, 'rev-parse', 'HEAD')

    def verify(self, **kw):
        head = run(self.root, 'rev-parse', 'HEAD')
        kw.setdefault('expected', head)
        return gate.verify(self.root, **kw)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.addCleanup(self.repo.tmp.cleanup)

    def assertRejects(self, message, **kw):
        with self.assertRaises(gate.GateFailure) as ctx:
            self.repo.verify(**kw)
        self.assertIn(message, str(ctx.exception))

    # positive controls
    def test_new_migration_in_order_passes(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.repo.commit('c')
        receipt = self.repo.verify()
        self.assertEqual(receipt['migration_count'], 3)
        self.assertIn(M + '20261101000000_c.sql', receipt['review_sensitive_paths'])

    def test_unchanged_candidate_passes_in_objects_mode(self):
        self.repo.write('src/app.ts', 'x\n')
        self.repo.commit('code')
        self.assertEqual(self.repo.verify(mode='objects')['changed_file_count'], 1)

    def test_pinned_legacy_order_file_passes(self):
        self.repo.write(M + '20260815000000_old.sql', 'select 0;\n')
        sha = self.repo.commit('legacy')
        blob = run(self.repo.root, 'rev-parse', sha + ':' + M + '20260815000000_old.sql')
        legacy = {M + '20260815000000_old.sql': blob}
        self.assertEqual(gate.verify_migrations(self.repo.root, 'HEAD', 'origin/main', legacy)[0], '20260815000000')

    # negative controls: migrations
    def test_edited_base_migration_rejected(self):
        self.repo.write(M + '20261001000000_a.sql', 'select 1; -- edited\n')
        self.repo.commit('edit')
        self.assertRejects('Base migration changed')

    def test_deleted_base_migration_rejected(self):
        (self.repo.root / M / '20261001000000_a.sql').unlink()
        self.repo.commit('delete')
        self.assertRejects('Base migration removed or renamed')

    def test_renamed_base_migration_rejected(self):
        run(self.repo.root, 'mv', M + '20261001000000_a.sql', M + '20261001000000_renamed.sql')
        self.repo.commit('rename')
        self.assertRejects('Base migration removed or renamed')

    def test_new_migration_out_of_order_rejected(self):
        self.repo.write(M + '20261010000000_late.sql', 'select 9;\n')
        self.repo.commit('late')
        self.assertRejects('New migration out of order')

    def test_legacy_name_with_other_bytes_rejected(self):
        self.repo.write(M + '20260815000000_old.sql', 'select 0;\n')
        self.repo.commit('legacy')
        legacy = {M + '20260815000000_old.sql': '0' * 40}
        with self.assertRaises(gate.GateFailure) as ctx:
            gate.verify_migrations(self.repo.root, 'HEAD', 'origin/main', legacy)
        self.assertIn('New migration out of order', str(ctx.exception))

    def test_duplicate_version_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.repo.write(M + '20261101000000_d.sql', 'select 4;\n')
        self.repo.commit('dup')
        self.assertRejects('Duplicate migration version')

    def test_bad_migration_name_rejected(self):
        self.repo.write(M + 'latest.sql', 'select 5;\n')
        self.repo.commit('name')
        self.assertRejects('Invalid migration name')

    def test_executable_migration_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        (self.repo.root / M / '20261101000000_c.sql').chmod(0o755)
        self.repo.commit('mode')
        self.assertRejects('Invalid migration mode')

    # negative controls: identity and checkout
    def test_expected_source_mismatch_rejected(self):
        self.assertRejects('Tested commit differs', expected='0' * 40)

    def test_missing_expected_source_rejected(self):
        self.assertRejects('EXPECTED_SOURCE required', expected='')

    def test_dirty_checkout_rejected(self):
        self.repo.write('src/app.ts', 'uncommitted\n')
        self.assertRejects('Checkout not clean')

    def test_uncommitted_migration_rejected(self):
        self.repo.write(M + '20261101000000_c.sql', 'select 3;\n')
        self.assertRejects('Checkout not clean')

    def test_wrong_repository_rejected(self):
        run(self.repo.root, 'remote', 'set-url', 'origin', 'https://github.com/someone/fork.git')
        self.assertRejects('Repository mismatch')

    def test_missing_base_rejected(self):
        run(self.repo.root, 'update-ref', '-d', 'refs/remotes/origin/main')
        self.assertRejects('Base reference unavailable')


class CurrentRepository(unittest.TestCase):
    def test_candidate_migrations_pass_against_main(self):
        root = Path(__file__).resolve().parents[2]
        if subprocess.run(['git', '-C', str(root), 'rev-parse', '--verify', 'origin/main'],
                          capture_output=True).returncode:
            self.skipTest('origin/main not fetched')
        versions = gate.verify_migrations(root, 'HEAD', 'origin/main')
        self.assertEqual(len(versions), len({p.name for p in (root / M).glob('*.sql')}))


if __name__ == '__main__':
    unittest.main()
