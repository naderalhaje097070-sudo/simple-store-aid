import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import integrated_identity as identity

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
        for i in range(50):
            self.write(f"supabase/migrations/{i:03}.sql", "select 1;\n")
        self.commit()
        base = self.run_git("rev-parse", "HEAD").decode().strip()
        self.base_patch = patch.object(identity, "B_BASE_SHA", base)
        self.base_patch.start()
        blobs = []
        for p in self.root.rglob("*"):
            if p.is_file() and ".git" not in p.parts:
                name = p.relative_to(self.root).as_posix()
                if protected(name):
                    data = p.read_bytes()
                    sha = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
                    blobs.append({"path": name, "sha": sha, "mode": "100644"})
        migrations = {x["path"]: x["sha"] for x in blobs if x["path"].endswith(".sql")}
        original = dict(list(sorted(migrations.items()))[:41])
        archive = json.dumps({"schema_version": 1, "original54_migrations": original}) + "\n"
        self.write(identity.A_MANIFEST, archive)
        archive_bytes = archive.encode()
        digest = hashlib.sha1(b"blob " + str(len(archive_bytes)).encode() + b"\0" + archive_bytes).hexdigest()
        self.archive_patch = patch.object(identity, "A_MANIFEST_SHA", digest)
        self.archive_patch.start()
        self.manifest = {"schema_version": 2, "repository": REPOSITORY, "base_source": base,
                         "protected_blobs": blobs, "original54_migrations": original,
                         "integrated_migrations": migrations}
        self.save_manifest()
        self.commit()

    def tearDown(self):
        self.archive_patch.stop()
        self.base_patch.stop()
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
        self.assertEqual(result["migration_count"], 50)
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
        self.write("supabase/migrations/050.sql", "select 2;\n")
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

    def test_worktree_executable_bit_only_mutation(self):
        (self.root / "src/server.ts").chmod(0o755)
        with self.assertRaisesRegex(IdentityError, "worktree source mode"):
            verify(self.root)

    def test_tracked_executable_bit_only_mutation(self):
        self.run_git("update-index", "--chmod=+x", "src/server.ts")
        with self.assertRaisesRegex(IdentityError, "tracked source mode/blob"):
            verify(self.root)

    def test_unsupported_manifest_mode(self):
        self.manifest["protected_blobs"][0]["mode"] = "120000"
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Invalid source mode"):
            verify(self.root)

    def test_frozen_A_manifest_cannot_be_replaced(self):
        self.write(identity.A_MANIFEST, "{}\n")
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Frozen A manifest identity"):
            verify(self.root)

    def test_original41_map_cannot_be_redeclared_by_B(self):
        self.manifest["original54_migrations"].pop("supabase/migrations/000.sql")
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Original41 migration map"):
            verify(self.root)

    def test_integrated50_map_cannot_omit_an_added_B_migration(self):
        self.manifest["integrated_migrations"].pop("supabase/migrations/049.sql")
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Integrated50 migration identity"):
            verify(self.root)

    def test_added_B_migration_bytes_are_protected(self):
        self.write("supabase/migrations/049.sql", "select 999;\n")
        with self.assertRaisesRegex(IdentityError, "Unreviewed source mutation"):
            verify(self.root)

    def test_B_base_cannot_be_replaced_with_an_arbitrary_ancestor(self):
        self.manifest["base_source"] = self.run_git("rev-parse", "HEAD").decode().strip()
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "reviewed B base"):
            verify(self.root)

    def test_source_entry_requires_explicit_mode(self):
        self.manifest["protected_blobs"][0].pop("mode")
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Invalid source mode"):
            verify(self.root)

    def test_staged_A_manifest_must_match_frozen_worktree(self):
        original = (self.root / identity.A_MANIFEST).read_text()
        self.write(identity.A_MANIFEST, "{}\n")
        self.run_git("add", identity.A_MANIFEST)
        self.write(identity.A_MANIFEST, original)
        with self.assertRaisesRegex(IdentityError, "manifest index/mode"):
            verify(self.root)

    def test_active_manifest_executable_mode_is_rejected(self):
        (self.root / MANIFEST).chmod(0o755)
        with self.assertRaisesRegex(IdentityError, "manifest index/mode"):
            verify(self.root)

    def test_B_SQL_cannot_change_even_if_new_snapshot_is_redeclared(self):
        path = "supabase/migrations/049.sql"
        self.write(path, "select 999;\n")
        raw = (self.root / path).read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()
        self.manifest["integrated_migrations"][path] = digest
        next(x for x in self.manifest["protected_blobs"] if x["path"] == path)["sha"] = digest
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Applied B50 migration"):
            verify(self.root)

    def test_B_SQL_mode_cannot_change_even_if_new_snapshot_is_redeclared(self):
        path = "supabase/migrations/049.sql"
        (self.root / path).chmod(0o755)
        next(x for x in self.manifest["protected_blobs"] if x["path"] == path)["mode"] = "100755"
        self.save_manifest()
        self.commit()
        with self.assertRaisesRegex(IdentityError, "Applied B50 migration"):
            verify(self.root)


if __name__ == "__main__":
    unittest.main()

