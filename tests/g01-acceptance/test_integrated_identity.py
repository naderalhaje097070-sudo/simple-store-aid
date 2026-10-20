import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from integrated_identity import IdentityError, MANIFEST, REPOSITORY, protected, verify


class IntegratedIdentity(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="monjez-identity-"))
        self.run_git("init", "-q")
        self.run_git("remote", "add", "origin", f"https://github.com/{REPOSITORY}")
        for name, body in {"package.json": "{}\n", "src/server.ts": "export const x = 1;\n",
                           "config/env.ts": "export const target = 'ci';\n",
                           ".gitignore": "node_modules/\n__pycache__/\n"}.items():
            self.write(name, body)
        for i in range(41):
            self.write(f"supabase/migrations/{i:03}.sql", "select 1;\n")
        self.commit()
        base = self.run_git("rev-parse", "HEAD").decode().strip()
        blobs = []
        for p in self.root.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                name = p.relative_to(self.root).as_posix()
                if protected(name):
                    data = p.read_bytes()
                    sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                    blobs.append({"path": name, "sha": sha})
        self.manifest = {"schema_version": 1, "repository": REPOSITORY, "base_source": base,
                         "protected_blobs": blobs,
                         "original54_migrations": {x["path"]: x["sha"] for x in blobs if x["path"].endswith(".sql")}}
        self.save_manifest()
        self.commit()

    def tearDown(self):
        shutil.rmtree(self.root)

    def run_git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL)

    def commit(self):
        self.run_git("add", ".")
        self.run_git("-c", "user.name=Identity Fixture", "-c", "user.email=fixture@example.invalid",
                     "commit", "-qm", "fixture")

    def write(self, name, body):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def save_manifest(self):
        self.write(MANIFEST, json.dumps(self.manifest, indent=2) + "\n")

    def test_actual_fixture(self):
        result = verify(self.root)
        self.assertTrue(result["all_integrated_blobs_match"])
        self.assertEqual(result["migration_count"], 41)
        self.assertFalse(result["legacy383_unchanged_claim"])

    def test_source_byte_mutation(self):
        self.write("src/server.ts", "export const x = 2;\n")
        with self.assertRaisesRegex(IdentityError, "Unreviewed source mutation"):
            verify(self.root)

    def test_environment_mutation(self):
        self.write("config/env.ts", "export const target = 'production';\n")
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_lock_or_manifest_source_mutation(self):
        self.write("package.json", '{"dependencies":{"unknown":"*"}}\n')
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_added_untracked_source(self):
        self.write("src/unreviewed.cjs", "console.log('unreviewed');\n")
        with self.assertRaisesRegex(IdentityError, "path set changed"):
            verify(self.root)

    def test_added_evidence_code(self):
        self.write("docs/evidence/unreviewed.py", "print('unreviewed')\n")
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_missing_migration(self):
        (self.root / "supabase/migrations/000.sql").unlink()
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_added_migration(self):
        self.write("supabase/migrations/041.sql", "select 2;\n")
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_mutated_migration(self):
        self.write("supabase/migrations/000.sql", "select 2;\n")
        with self.assertRaises(IdentityError):
            verify(self.root)

    def test_uncommitted_identity_manifest(self):
        self.manifest["protected_blobs"] = []
        self.save_manifest()
        with self.assertRaisesRegex(IdentityError, "Uncommitted"):
            verify(self.root)

    def test_duplicate_manifest_path(self):
        self.manifest["protected_blobs"].append(dict(self.manifest["protected_blobs"][0]))
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Duplicate"):
            verify(self.root)

    def test_traversal_manifest_path(self):
        self.manifest["protected_blobs"][0]["path"] = "../private"
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Invalid protected"):
            verify(self.root)

    def test_boolean_schema_is_not_version_one(self):
        self.manifest["schema_version"] = True
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "schema"):
            verify(self.root)

    def test_symlink_source_rejected(self):
        p = self.root / "src/server.ts"
        raw = p.read_bytes()
        p.unlink()
        target = self.root / "same-bytes"
        target.write_bytes(raw)
        p.symlink_to(target)
        # Keep the target outside the observed source set so mode alone must fail.
        self.write(".git/info/exclude", "same-bytes\n")
        with self.assertRaisesRegex(IdentityError, "Nonregular"):
            verify(self.root)

    def test_repository_remote_mismatch(self):
        self.run_git("remote", "set-url", "origin", "https://github.com/other/repository")
        with self.assertRaisesRegex(IdentityError, "repository remote"):
            verify(self.root)

    def test_readonly_documents_can_change(self):
        self.write("docs/new-receipt.md", "read-only report\n")
        self.write("PROJECT_STATE.md", "checkpoint\n")
        self.assertTrue(verify(self.root)["all_integrated_blobs_match"])


if __name__ == "__main__":
    unittest.main()
