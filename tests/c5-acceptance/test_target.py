"""Source/history mismatches must fail even when an attacker keeps the count at54."""
import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest

import target


class MigrationTarget(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='c5-target-'))
        directory = self.root / 'supabase/migrations'
        directory.mkdir(parents=True)
        self.rows = []
        for i in range(54):
            name = f'20260101{i:06}_fixture.sql'
            path = directory / name
            path.write_text(f'select {i};\n')
            self.rows.append({'path': 'supabase/migrations/' + name, 'sha': target.blob(path.read_bytes()), 'mode': '100644'})
        self.manifest = {'schema_version': 1, 'scope': 'C5-G1-SCHEMA-01',
                         'repository': target.REPOSITORY, 'base_source': target.BASE, 'migrations': copy.deepcopy(self.rows)}
        self.original = {r['path']: r['sha'] for r in self.rows[:41]}
        self.versions = [Path(r['path']).name.split('_')[0] for r in self.rows]

    def tearDown(self):
        shutil.rmtree(self.root)

    def verify(self):
        return target.verify_files(self.root, self.manifest, self.rows, self.original)

    def deny(self):
        with self.assertRaises(target.TargetError):
            self.verify()

    def test_exact_source_and_history(self):
        self.assertEqual(self.verify(), self.versions)
        target.verify_history(self.versions, self.versions)

    def test_original41_database_history_is_rejected(self):
        with self.assertRaises(target.TargetError):
            target.verify_history(self.versions, self.versions[:41])

    def test_same_count_different_database_version(self):
        with self.assertRaises(target.TargetError):
            target.verify_history(self.versions, self.versions[:-1] + ['29990101000000'])

    def test_reordered_or_duplicate_database_history(self):
        for value in [self.versions[::-1], self.versions[:-1] + self.versions[:1]]:
            with self.assertRaises(target.TargetError):
                target.verify_history(self.versions, value)

    def test_history_null_object_and_nonstring(self):
        for value in [None, {}, '54', [int(v) for v in self.versions]]:
            with self.assertRaises(target.TargetError):
                target.verify_history(self.versions, value)

    def test_changed_sql_body(self):
        (self.root / self.rows[-1]['path']).write_text('select 999;\n')
        self.deny()

    def test_self_adopted_sql_body(self):
        file = self.root / self.rows[-1]['path']
        file.write_text('select 999;\n')
        self.manifest['migrations'][-1]['sha'] = target.blob(file.read_bytes())
        self.deny()

    def test_missing_sql(self):
        (self.root / self.rows[-1]['path']).unlink()
        self.deny()

    def test_extra_sql(self):
        (self.root / 'supabase/migrations/29990101000000_extra.sql').write_text('select 1;')
        self.deny()

    def test_same_count_renamed_sql(self):
        file = self.root / self.rows[-1]['path']
        file.rename(file.with_name('29990101000000_renamed.sql'))
        self.deny()

    def test_duplicate_version_in_pinned_candidate(self):
        self.rows[-1]['path'] = self.rows[0]['path'].replace('_fixture', '_duplicate')
        self.manifest['migrations'] = copy.deepcopy(self.rows)
        self.deny()

    def test_noncanonical_manifest_path(self):
        self.rows[-1]['path'] = 'supabase/migrations/../bad.sql'
        self.manifest['migrations'] = copy.deepcopy(self.rows)
        self.deny()

    def test_symlink_sql(self):
        file = self.root / self.rows[-1]['path']
        body = file.read_bytes()
        file.unlink()
        other = self.root / 'copied.sql'
        other.write_bytes(body)
        file.symlink_to(other)
        self.deny()

    def test_symlink_migration_directory(self):
        directory = self.root / 'supabase/migrations'
        moved = self.root / 'copied-migrations'
        directory.rename(moved)
        directory.symlink_to(moved)
        self.deny()

    def test_executable_sql(self):
        (self.root / self.rows[-1]['path']).chmod(0o755)
        self.deny()

    def test_extra_directory_or_non_sql_entry(self):
        (self.root / 'supabase/migrations/injected').mkdir()
        self.deny()

    def test_lost_original41(self):
        self.original[self.rows[0]['path']] = '0' * 40
        self.deny()

    def test_manifest_authority_or_empty(self):
        for key, value in [('schema_version', True), ('base_source', '0' * 40), ('scope', 'legacy41'),
                           ('repository', 'other/repository'), ('migrations', [])]:
            changed = copy.deepcopy(self.manifest)
            changed[key] = value
            with self.assertRaises(target.TargetError):
                target.verify_files(self.root, changed, self.rows, self.original)


class RuntimeWiring(unittest.TestCase):
    def test_runtime_validates_source_before_status_then_real_db_history(self):
        source = (Path(__file__).resolve().parents[1] / 'g01-acceptance/runtime.py').read_text()
        self.assertIn('verify_source(Path.cwd())', source)
        self.assertIn('verify_history(pinned_versions, versions)', source)
        self.assertLess(source.index('verify_source(Path.cwd())'), source.index("status=json.loads"))
        self.assertLess(source.index('verify_history(pinned_versions, versions)'), source.index("check('initial_empty_finance_auth'"))
        self.assertNotIn("check('exact41_migrations'", source)
        self.assertIn("check('native_unexpected_outbound_zero'", source)
        self.assertIn("check('bounded_egress_trace_collected'", source)
        self.assertIn("record['financial_flow_executed']=False", source)


if __name__ == '__main__':
    unittest.main()
