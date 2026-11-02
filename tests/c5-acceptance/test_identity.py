"""Adversarial C5 admission: never authorize financial/dependency/SQL drift."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import identity
from integrated_identity import IdentityError


class Identity(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='c5-identity-'))
        self.g('init', '-q')
        self.g('remote', 'add', 'origin', 'https://github.com/' + identity.REPOSITORY)
        self.write('.gitignore', '__pycache__/\n')
        for p in ['package.json', 'bun.lock', 'patches/minimatch@11.0.1.patch',
                  'src/domain/finance/core.ts', *identity.CHANGES]:
            self.write(p, '# old fixture\n')
        for i in range(54):
            self.write(f'supabase/migrations/{i:03}.sql', 'select 1;\n')
        frozen = {}
        for p in identity.FROZEN:
            self.write(p, '{}\n')
            frozen[p] = identity.blob((self.root / p).read_bytes())
        self.commit()
        base = self.g('rev-parse', 'HEAD').decode().strip()
        self.patches = [patch.object(identity, 'BASE', base), patch.object(identity, 'FROZEN', frozen),
                        patch.dict(os.environ, {'EXPECTED_SOURCE': ''})]
        for p in self.patches:
            p.start()
        self.before = self.snapshot()
        self.write('tests/g01-acceptance/runtime.py', '# verified target fixture\n')
        self.write('tests/c5-acceptance/target.py', '# target fixture\n')
        self.manifest = {'schema_version': 1, 'scope': 'C5-G1-SCHEMA-01',
                         'repository': identity.REPOSITORY, 'base_source': base,
                         'protected_blobs': self.snapshot(),
                         'intentional_changes': {'tests/g01-acceptance/runtime.py': {
                             'before': self.before_map()['tests/g01-acceptance/runtime.py'],
                             'after': identity.blob((self.root / 'tests/g01-acceptance/runtime.py').read_bytes()), 'mode': '100644'}},
                         'additions': {'tests/c5-acceptance/target.py': identity.blob((self.root / 'tests/c5-acceptance/target.py').read_bytes())}}
        self.save()
        self.commit()

    def tearDown(self):
        for p in reversed(self.patches):
            p.stop()
        shutil.rmtree(self.root)

    def g(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL)

    def commit(self):
        self.g('add', '.')
        self.g('-c', 'user.name=C5 Fixture', '-c', 'user.email=fixture@example.test', 'commit', '-qm', 'fixture')

    def write(self, path, data):
        file = self.root / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(data)

    def snapshot(self):
        return sorted([{'path': p.relative_to(self.root).as_posix(), 'sha': identity.blob(p.read_bytes()), 'mode': '100644'}
                       for p in self.root.rglob('*') if p.is_file() and '.git' not in p.parts
                       and identity.selected(p.relative_to(self.root).as_posix())], key=lambda r: r['path'])

    def before_map(self):
        return {r['path']: r['sha'] for r in self.before}

    def save(self):
        self.write(identity.MANIFEST, json.dumps(self.manifest, indent=2) + '\n')

    def deny(self):
        with self.assertRaises(IdentityError):
            identity.verify(self.root)

    def test_valid_explicit_admission(self):
        result = identity.verify(self.root)
        self.assertEqual(result['migration_count'], 54)
        self.assertFalse(result['financial_acceptance'])

    def test_financial_source_drift(self):
        self.write('src/domain/finance/core.ts', '# changed\n')
        self.deny()

    def test_self_adopted_financial_drift(self):
        self.write('src/domain/finance/core.ts', '# changed\n')
        self.manifest['protected_blobs'] = self.snapshot()
        self.save()
        self.commit()
        self.deny()

    def test_sql_drift(self):
        self.write('supabase/migrations/053.sql', 'select 2;\n')
        self.deny()

    def test_self_adopted_sql_drift(self):
        self.write('supabase/migrations/053.sql', 'select 2;\n')
        self.manifest['protected_blobs'] = self.snapshot()
        self.save()
        self.commit()
        self.deny()

    def test_package_lock_or_patch_drift(self):
        for p in ['package.json', 'bun.lock', 'patches/minimatch@11.0.1.patch']:
            old = (self.root / p).read_text()
            self.write(p, '# changed\n')
            self.deny()
            self.write(p, old)

    def test_frozen_manifests(self):
        for p in identity.FROZEN:
            old = (self.root / p).read_text()
            self.write(p, '# changed\n')
            self.deny()
            self.write(p, old)

    def test_uncommitted_c5_manifest(self):
        self.manifest['scope'] = 'forged'
        self.save()
        self.deny()

    def test_wrong_repository(self):
        self.g('remote', 'set-url', 'origin', 'https://github.com/other/repo')
        self.deny()

    def test_wrong_expected_source(self):
        with patch.dict(os.environ, {'EXPECTED_SOURCE': '0' * 40}):
            self.deny()

    def test_untracked_source_injection(self):
        self.write('src/injected.ts', 'malicious\n')
        self.deny()

    def test_undeclared_addition_self_adoption(self):
        self.write('src/injected.ts', 'malicious\n')
        self.manifest['protected_blobs'] = self.snapshot()
        self.save()
        self.commit()
        self.deny()

    def test_duplicate_path(self):
        self.manifest['protected_blobs'].append(self.manifest['protected_blobs'][0])
        self.save()
        self.commit()
        self.deny()

    def test_lost_baseline_path(self):
        self.manifest['protected_blobs'] = [r for r in self.manifest['protected_blobs'] if r['path'] != 'bun.lock']
        (self.root / 'bun.lock').unlink()
        self.save()
        self.commit()
        self.deny()

    def test_undeclared_before_provenance(self):
        self.manifest['intentional_changes']['tests/g01-acceptance/runtime.py']['before'] = '0' * 40
        self.save()
        self.commit()
        self.deny()

    def test_undeclared_addition_provenance(self):
        self.manifest['additions'] = {}
        self.save()
        self.commit()
        self.deny()

    def test_manifest_symlink(self):
        file = self.root / identity.MANIFEST
        file.unlink()
        file.symlink_to(self.root / 'package.json')
        self.deny()

    def test_manifest_mode(self):
        (self.root / identity.MANIFEST).chmod(0o755)
        self.deny()

    def test_worktree_source_mode(self):
        (self.root / 'tests/g01-acceptance/runtime.py').chmod(0o755)
        self.deny()

    def test_source_symlink(self):
        file = self.root / 'tests/g01-acceptance/runtime.py'
        file.unlink()
        file.symlink_to(self.root / 'package.json')
        self.deny()

    def test_documentation_is_not_executable_admission(self):
        self.write('changes/c5-g1-schema/RESULT.md', 'read-only evidence\n')
        self.assertTrue(identity.verify(self.root)['all_integrated_blobs_match'])


if __name__ == '__main__':
    unittest.main()
