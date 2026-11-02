"""Independent synthetic mutation oracles for the bounded C source inventory."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import sec_identity as identity


class CIdentity(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix='monjez-c-identity-'))
        self.g('init', '-q')
        self.g('remote', 'add', 'origin', 'https://github.com/' + identity.REPOSITORY)
        self.write('.gitignore', '__pycache__/\n')
        self.write('package.json', '{}\n')
        self.write('src/server.ts', 'export const x = 1;\n')
        for i in range(54): self.write(f'supabase/migrations/{i:03}.sql', 'select 1;\n')
        frozen = {}
        for p in identity.FROZEN:
            self.write(p, '{}\n'); frozen[p] = identity.blob((self.root / p).read_bytes())
        self.commit()
        base = self.g('rev-parse', 'HEAD').decode().strip()
        self.patches = [patch.object(identity, 'C_BASE', base), patch.object(identity, 'FROZEN', frozen), patch.dict(os.environ, {'EXPECTED_SOURCE': ''})]
        for p in self.patches: p.start()
        before = identity.blob((self.root / 'package.json').read_bytes())
        self.write('package.json', '{"patched":true}\n')
        self.write('tests/sec-dep-20261102/sec_identity.py', '# fixture\n')
        self.write(identity.PATCH, (Path(__file__).resolve().parents[2] / identity.PATCH).read_text())
        self.manifest = {'schema_version': 1, 'scope': 'SEC-DEP-20261102', 'repository': identity.REPOSITORY,
                         'base_source': base, 'protected_blobs': self.snapshot(),
                         'intentional_changes': {'package.json': {'before': before, 'after': identity.blob((self.root / 'package.json').read_bytes()), 'mode': '100644'}},
                         'additions': {p: identity.blob((self.root / p).read_bytes()) for p in ['tests/sec-dep-20261102/sec_identity.py', identity.PATCH]}}
        self.save(); self.commit()

    def tearDown(self):
        for p in reversed(self.patches): p.stop()
        shutil.rmtree(self.root)

    def g(self, *args): return subprocess.check_output(['git', '-C', str(self.root), *args], stderr=subprocess.DEVNULL)
    def write(self, p, s):
        f = self.root / p; f.parent.mkdir(parents=True, exist_ok=True); f.write_text(s)
    def commit(self):
        self.g('add', '.'); self.g('-c', 'user.name=C Identity Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
    def snapshot(self):
        return [{'path': p.relative_to(self.root).as_posix(), 'sha': identity.blob(p.read_bytes()), 'mode': '100644'}
                for p in sorted(self.root.rglob('*')) if p.is_file() and '.git' not in p.parts
                and identity.c_protected(p.relative_to(self.root).as_posix())]
    def save(self): self.write(identity.MANIFEST, json.dumps(self.manifest, indent=2) + '\n')
    def deny(self):
        with self.assertRaises(identity.IdentityError): identity.verify(self.root)
    def test_valid(self): self.assertEqual(identity.verify(self.root)['migration_count'], 54)
    def test_source_bytes(self): self.write('src/server.ts', 'changed\n'); self.deny()
    def test_unknown_untracked(self): self.write('src/new.ts', 'new\n'); self.deny()
    def test_uncommitted_manifest(self): self.manifest['scope'] = 'other'; self.save(); self.deny()
    def test_redeclared_base(self): self.manifest['base_source'] = self.g('rev-parse', 'HEAD').decode().strip(); self.save(); self.commit(); self.deny()
    def test_boolean_schema(self): self.manifest['schema_version'] = True; self.save(); self.commit(); self.deny()
    def test_duplicate(self): self.manifest['protected_blobs'].append(self.manifest['protected_blobs'][0]); self.save(); self.commit(); self.deny()
    def test_traversal(self): self.manifest['protected_blobs'][0]['path'] = '../secret'; self.save(); self.commit(); self.deny()
    def test_redeclared_sql(self):
        self.write('supabase/migrations/053.sql', 'select 999;\n')
        for row in self.manifest['protected_blobs']:
            if row['path'] == 'supabase/migrations/053.sql': row['sha'] = identity.blob((self.root / row['path']).read_bytes())
        self.save(); self.commit(); self.deny()
    def test_redeclared_financial_source(self): self.write('src/server.ts', 'new\n'); self.manifest['protected_blobs'] = self.snapshot(); self.save(); self.commit(); self.deny()
    def test_worktree_mode(self): (self.root / 'src/server.ts').chmod(0o755); self.deny()
    def test_staged_mode(self): self.g('update-index', '--chmod=+x', 'src/server.ts'); self.deny()
    def test_symlink(self):
        p = self.root / 'src/server.ts'; p.unlink(); p.symlink_to('/dev/null'); self.deny()
    def test_frozen_B(self): self.write('tests/g01-acceptance/integrated-b-source.json', '{"forged":true}\n'); self.commit(); self.deny()
    def test_manifest_mode(self): (self.root / identity.MANIFEST).chmod(0o755); self.deny()
    def test_remote(self): self.g('remote', 'set-url', 'origin', 'https://github.com/other/repo'); self.deny()
    def test_readonly_docs(self): self.write('docs/receipt.md', 'receipt\n'); self.assertTrue(identity.verify(self.root)['all_integrated_blobs_match'])
    def test_evidence_code(self): self.write('changes/new/unreviewed.py', 'print(1)\n'); self.deny()

    def test_missing_patch(self): (self.root / identity.PATCH).unlink(); self.deny()
    def test_redeclared_patch_is_not_owner_approval(self):
        self.write(identity.PATCH, 'unapproved replacement\n')
        self.manifest['protected_blobs'] = self.snapshot()
        self.manifest['additions'][identity.PATCH] = identity.blob((self.root / identity.PATCH).read_bytes())
        self.save(); self.commit(); self.deny()
    def test_frozen_C4(self): self.write('tests/c4-sale/source.json', '{"changed":true}\n'); self.commit(); self.deny()
    def test_missing_manifest(self): (self.root / identity.MANIFEST).unlink(); self.deny()
    def test_patch_mode(self): (self.root / identity.PATCH).chmod(0o755); self.deny()


if __name__ == '__main__': unittest.main()
