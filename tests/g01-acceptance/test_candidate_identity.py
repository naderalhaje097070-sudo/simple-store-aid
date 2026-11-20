"""Synthetic mutation oracles for the candidate63 identity (item 3.4). No network, no database.

Each fixture is a throwaway git repository: a B50 base commit (50 migrations, frozen A41/B50
manifests), a candidate base commit (+13 migrations) and a reviewed candidate manifest. Every
rejection is tried in its strongest form: committed, with the candidate manifest regenerated so
that it agrees with the tampered tree, where that is possible.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch

import candidate_identity as cand
import integrated_identity as frozen
from integrated_identity import IdentityError, REPOSITORY


def blob(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def name(i):
    """Mirrors the real interleaving: original41 (Jan-Feb), B50-only 9 (Oct), new 13 = 2 in Aug + 11 in Nov."""
    if i < 41:
        stamp = f"2026{i // 28 + 1:02}{i % 28 + 1:02}"
    elif i < 50:
        stamp = f"202610{i - 40:02}"
    elif i < 52:
        stamp = f"202608{i - 49:02}"
    else:
        stamp = f"202611{i - 51:02}"
    return f"supabase/migrations/{stamp}100000_m{i:02}.sql"


class CandidateIdentity(unittest.TestCase):
    def setUp(self):
        self.root = Path(tempfile.mkdtemp(prefix="monjez-candidate-identity-"))
        self.git("init", "-q")
        self.git("remote", "add", "origin", f"https://github.com/{REPOSITORY}")
        for path, body in {"package.json": "{}\n", "src/server.ts": "export const x = 1;\n",
                           ".gitignore": "node_modules/\n__pycache__/\n"}.items():
            self.write(path, body)
        for i in range(50):
            self.write(name(i), f"select {i};\n")
        migrations = {name(i): blob(f"select {i};\n".encode()) for i in range(50)}
        original = {k: migrations[k] for k in sorted(migrations)[:41]}
        a = json.dumps({"schema_version": 1, "original54_migrations": original}) + "\n"
        b = json.dumps({"schema_version": 2, "integrated_migrations": migrations, "original54_migrations": original}) + "\n"
        self.write(frozen.A_MANIFEST, a)
        self.write(frozen.MANIFEST, b)
        self.commit()
        b_base = self.head()
        for i in range(50, 63):
            self.write(name(i), f"select {i};\n")
        self.commit()
        c_base = self.head()
        self.patches = [patch.object(frozen, "B_BASE_SHA", b_base), patch.object(frozen, "A_MANIFEST_SHA", blob(a.encode())),
                        patch.object(cand, "B_MANIFEST_SHA", blob(b.encode())), patch.object(cand, "CANDIDATE_BASE_SHA", c_base)]
        for p in self.patches:
            p.start()
        self.regenerate()

    def tearDown(self):
        for p in self.patches:
            p.stop()
        shutil.rmtree(self.root)

    def git(self, *args):
        return subprocess.check_output(["git", "-C", str(self.root), *args], stderr=subprocess.DEVNULL)

    def head(self):
        return self.git("rev-parse", "HEAD").decode().strip()

    def commit(self):
        self.git("add", "-A")
        self.git("-c", "user.name=Identity Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "--no-gpg-sign", "-qm", "fixture")

    def write(self, path, body):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(body)

    def regenerate(self):
        """The strongest forger: a candidate manifest that agrees with the current tree, committed."""
        self.commit()
        self.write(cand.CANDIDATE_MANIFEST, json.dumps(cand.build_manifest(self.root), indent=1) + "\n")
        self.commit()

    def manifest(self):
        return json.loads((self.root / cand.CANDIDATE_MANIFEST).read_text())

    def save(self, manifest):
        self.write(cand.CANDIDATE_MANIFEST, json.dumps(manifest, indent=1) + "\n")
        self.commit()

    def deny(self, message):
        with self.assertRaisesRegex(IdentityError, message):
            cand.verify(self.root)

    # Positive control
    def test_reviewed_candidate_accepted(self):
        result = cand.verify(self.root)
        self.assertEqual(result["migration_count"], 63)
        self.assertEqual(result["new_migration_count"], 13)
        self.assertTrue(result["b50_migrations_preserved"] and result["original41_migrations_preserved"])
        self.assertEqual(result["new_migrations_sorting_before_b50_max"], [name(50), name(51)])

    # Old (B50) file corrupted
    def test_old_migration_corrupted_in_worktree(self):
        self.write(name(7), "select 'tampered';\n")
        self.deny("Unreviewed source mutation")

    def test_old_migration_corrupted_committed_with_regenerated_manifest(self):
        self.write(name(7), "select 'tampered';\n")
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    def test_original41_migration_corrupted_committed_with_regenerated_manifest(self):
        self.write(name(0), "select 'tampered';\n")
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    def test_old_migration_whitespace_only_change(self):
        self.write(name(45), "select 45; \n")
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    # Old file deleted
    def test_old_migration_deleted_in_worktree(self):
        (self.root / name(12)).unlink()
        self.deny("Nonregular or missing source")

    def test_old_migration_deleted_committed_with_regenerated_manifest(self):
        (self.root / name(12)).unlink()
        self.regenerate()
        self.deny("Candidate63 ledger size changed")

    # Different ledger, same count
    def test_same_count_old_file_replaced_by_new_file(self):
        (self.root / name(12)).unlink()
        self.write("supabase/migrations/20261231100000_swap.sql", "select 'swap';\n")
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    def test_same_count_old_file_renamed(self):
        os.rename(self.root / name(30), self.root / name(30).replace("_m30", "_renamed"))
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    def test_ledger_blob_forged_in_manifest_only(self):
        m = self.manifest()
        m["migration_ledger"][3]["sha"] = "0" * 40
        self.save(m)
        self.deny("Ledger differs from protected snapshot")

    def test_ledger_reordered_in_manifest(self):
        m = self.manifest()
        m["migration_ledger"][41], m["migration_ledger"][42] = m["migration_ledger"][42], m["migration_ledger"][41]
        self.save(m)
        self.deny("Migration ledger order changed")

    def test_new_migration_sorting_inside_original41(self):
        os.rename(self.root / name(55), self.root / "supabase/migrations/20260101000000_early.sql")
        self.regenerate()
        self.deny("ledger differs from fixed candidate base")

    # Extra path
    def test_extra_untracked_path(self):
        self.write("src/extra.ts", "export const y = 1;\n")
        self.deny("Protected source path set changed")

    def test_extra_untracked_migration(self):
        self.write("supabase/migrations/20261231100000_extra.sql", "select 1;\n")
        self.deny("Protected source path set changed")

    def test_extra_committed_migration_with_regenerated_manifest(self):
        self.write("supabase/migrations/20261231100000_extra.sql", "select 1;\n")
        self.regenerate()
        self.deny("Candidate63 ledger size changed")

    def test_extra_nonsql_file_in_migration_directory(self):
        self.write("supabase/migrations/README.txt", "x\n")
        self.regenerate()
        self.deny("Candidate63 ledger size changed")

    def test_same_count_nonsql_file_replaces_migration(self):
        (self.root / name(62)).unlink()
        self.write("supabase/migrations/README.txt", "x\n")
        self.regenerate()
        self.deny("Invalid migration ledger path")

    # Mode
    def test_old_migration_mode_in_worktree(self):
        os.chmod(self.root / name(20), 0o755)
        self.deny("Unreviewed worktree source mode")

    def test_old_migration_mode_committed_with_regenerated_manifest(self):
        os.chmod(self.root / name(20), 0o755)
        self.git("update-index", "--chmod=+x", name(20))
        self.regenerate()
        self.deny("Executable migration|ledger differs from fixed candidate base")

    def test_source_mode_in_index_only(self):
        self.git("update-index", "--chmod=+x", "src/server.ts")
        self.deny("Unreviewed tracked source mode/blob")

    # Frozen manifests and the candidate manifest itself
    def test_b50_manifest_changed(self):
        self.write(frozen.MANIFEST, '{"forged": true}\n')
        self.regenerate()
        self.deny("Frozen manifest identity changed")

    def test_a41_manifest_changed(self):
        self.write(frozen.A_MANIFEST, '{"forged": true}\n')
        self.regenerate()
        self.deny("Frozen manifest identity changed")

    def test_uncommitted_candidate_manifest(self):
        m = self.manifest()
        m["migration_count"] = 63
        self.write(cand.CANDIDATE_MANIFEST, json.dumps(m) + "\n")
        self.deny("Uncommitted candidate manifest mutation")

    def test_wrong_base_in_manifest(self):
        m = self.manifest()
        m["base_source"] = frozen.B_BASE_SHA
        self.save(m)
        self.deny("Invalid reviewed candidate base")

    def test_candidate_base_not_ancestor(self):
        self.git("checkout", "-q", "--orphan", "other")
        self.commit()
        self.deny("Reviewed base is not an ancestor")

    # Commit binding: index and worktree agree with the committed manifest, the HEAD commit does not
    def commit_index(self):
        """Commit the index exactly as staged (no `git add`)."""
        self.git("-c", "user.name=Identity Fixture", "-c", "user.email=fixture@example.invalid",
                 "commit", "--allow-empty", "--no-gpg-sign", "-qm", "index-only")

    def store(self, text):
        return subprocess.run(["git", "-C", str(self.root), "hash-object", "-w", "--stdin"], input=text.encode(),
                              capture_output=True, check=True).stdout.decode().strip()

    def stage_manifest(self):
        self.write(cand.CANDIDATE_MANIFEST, json.dumps(cand.build_manifest(self.root), indent=1) + "\n")
        self.git("add", cand.CANDIDATE_MANIFEST)

    def test_head_blob_differs_while_index_and_worktree_match_manifest(self):
        path, committed = "src/server.ts", "export const x = 1;\n"
        self.write(path, "export const x = 99;\n")
        self.git("add", path)
        staged = self.git("rev-parse", ":" + path).decode().strip()
        self.stage_manifest()
        self.git("update-index", "--cacheinfo", "100644," + self.store(committed) + "," + path)
        self.commit_index()
        self.git("update-index", "--cacheinfo", "100644," + staged + "," + path)
        # Precondition: the old checks (manifest==HEAD manifest, index==worktree==manifest) all hold.
        self.assertEqual(self.git("diff", "--cached", "--name-only").decode().split(), [path])
        self.assertEqual(self.git("diff", "--name-only").decode().split(), [])
        self.deny("Protected HEAD tree differs from reviewed snapshot")

    def test_head_lacks_file_held_by_index_worktree_and_manifest(self):
        path = "src/staged_only.ts"
        self.write(path, "export const s = 1;\n")
        self.git("add", path)
        self.stage_manifest()
        self.git("rm", "-q", "--cached", path)
        self.commit_index()
        self.git("add", path)
        self.deny("Protected HEAD tree differs from reviewed snapshot")

    def test_head_holds_file_absent_from_index_worktree_and_manifest(self):
        path = "src/server.ts"
        sha = self.git("rev-parse", "HEAD:" + path).decode().strip()
        self.git("rm", "-q", path)
        self.stage_manifest()
        self.git("update-index", "--add", "--cacheinfo", "100644," + sha + "," + path)
        self.commit_index()
        self.git("update-index", "--force-remove", path)
        self.assertFalse((self.root / path).exists())
        self.deny("Protected HEAD tree differs from reviewed snapshot")

    def test_head_mode_differs_while_index_and_worktree_match(self):
        path = name(60)
        sha = self.git("rev-parse", "HEAD:" + path).decode().strip()
        self.git("update-index", "--cacheinfo", "100755," + sha + "," + path)
        self.commit_index()
        self.git("update-index", "--cacheinfo", "100644," + sha + "," + path)
        self.deny("Protected HEAD tree differs from reviewed snapshot")

    def test_head_manifest_differs_from_index_manifest(self):
        m = self.manifest()
        self.write(cand.CANDIDATE_MANIFEST, json.dumps(m) + "\n")
        self.git("add", cand.CANDIDATE_MANIFEST)
        self.deny("Uncommitted candidate manifest mutation|Manifest differs between HEAD and index")

    # Other protected source
    def test_protected_source_mutation(self):
        self.write("src/server.ts", "export const x = 2;\n")
        self.deny("Unreviewed source mutation")

    def test_protected_source_committed_without_review(self):
        self.write("src/server.ts", "export const x = 2;\n")
        self.commit()
        self.deny("Protected HEAD tree differs from reviewed snapshot")

    def test_real_repository_manifest_is_current(self):
        """The checked-in manifest equals a regeneration from the real committed tree (CI checkout)."""
        for p in self.patches:
            p.stop()
        try:
            real = Path(__file__).resolve().parents[2]
            committed = json.loads(subprocess.check_output(["git", "-C", str(real), "show", f"HEAD:{cand.CANDIDATE_MANIFEST}"]))
            self.assertEqual(committed, cand.build_manifest(real))
            self.assertEqual(cand.verify(real)["migration_count"], 63)
        finally:
            for p in self.patches:
                p.start()


if __name__ == "__main__":
    unittest.main()
