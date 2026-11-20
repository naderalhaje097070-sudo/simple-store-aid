"""Exact reviewed identity of the 63-migration candidate (item 3.4).

Additive to the frozen A41 (integrated-source.json) and B50 (integrated-b-source.json)
identities, which stay byte-identical and keep their own verifier and tests. This
verifier pins, for the checked-out candidate:
  * every protected path with its blob and mode (index and worktree), and the exact path set;
  * the full ordered 63-migration ledger (path, blob, mode), equal to the fixed candidate base;
  * the 50 B50 migrations preserved byte- and mode-identical, as the ledger's first 50 entries;
  * the frozen original41 as the ledger's first 41 entries;
  * the frozen A41 and B50 manifests by blob, and the B50 base ledger at its fixed commit.
No per-path override and no fallback: any difference is a refusal.
"""
import hashlib
import json
from pathlib import Path
import re
import stat
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import integrated_identity as frozen
from integrated_identity import IdentityError, REPOSITORY, check, git, valid_path

CANDIDATE_MANIFEST = "tests/g01-acceptance/candidate-63-source.json"
CANDIDATE_BASE_SHA = "09089be291a56fd2a76ba8c0943564c30e5a4eb8"
B_MANIFEST_SHA = "71895f740a9519b0d2399ed0c55c9f7d3b44f05e"
CANDIDATE_COUNT = 63
B50_COUNT = 50
ORIGINAL_COUNT = 41
MIGRATION_DIR = "supabase/migrations/"
MIGRATION_NAME = re.compile(r"supabase/migrations/([0-9]{14})_[A-Za-z0-9_-]+\.sql")


def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def protected(path):
    return path != CANDIDATE_MANIFEST and frozen.protected(path)


def tree_migrations(root, commit):
    found = []
    for entry in git(root, "ls-tree", "-r", "-z", commit, "--", "supabase/migrations").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, kind, sha = metadata.decode().split()
        check(kind == "blob", "Nonblob migration entry at fixed commit")
        found.append({"path": path.decode(), "sha": sha, "mode": mode})
    return sorted(found, key=lambda x: x["path"])


def index_entries(root):
    index = {}
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, sha, stage = metadata.decode().split()
        check(stage == "0", "Unmerged source index")
        index[path.decode()] = (sha, mode)
    return index


def build_manifest(root):
    """Regeneration helper for review; verify() never trusts its output."""
    root = Path(root)
    index = index_entries(root)
    blobs = [{"path": p, "sha": s, "mode": m} for p, (s, m) in sorted(index.items()) if protected(p)]
    ledger = [x for x in blobs if x["path"].startswith(MIGRATION_DIR)]
    return {"schema_version": 1, "repository": REPOSITORY, "base_source": CANDIDATE_BASE_SHA,
            "b50_manifest_sha": B_MANIFEST_SHA, "a41_manifest_sha": frozen.A_MANIFEST_SHA,
            "b50_base_source": frozen.B_BASE_SHA, "migration_count": len(ledger),
            "migration_ledger": ledger, "protected_blobs": blobs}


def verify(root):
    root = Path(root)
    data = (root / CANDIDATE_MANIFEST).read_bytes()
    check(data == git(root, "show", f"HEAD:{CANDIDATE_MANIFEST}"), "Uncommitted candidate manifest mutation")
    manifest = json.loads(data)
    check(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
          "Unreviewed candidate manifest schema")
    check(manifest.get("repository") == REPOSITORY, "Unexpected source repository")
    remote = git(root, "config", "--get", "remote.origin.url").decode().strip()
    check(remote in {f"https://github.com/{REPOSITORY}", f"https://github.com/{REPOSITORY}.git"},
          "Unexpected repository remote")
    check(manifest.get("base_source") == CANDIDATE_BASE_SHA, "Invalid reviewed candidate base")
    check(manifest.get("b50_base_source") == frozen.B_BASE_SHA, "Invalid reviewed B50 base")
    check(manifest.get("b50_manifest_sha") == B_MANIFEST_SHA and manifest.get("a41_manifest_sha") == frozen.A_MANIFEST_SHA,
          "Frozen manifest pin changed")
    for base in (frozen.B_BASE_SHA, CANDIDATE_BASE_SHA):
        status = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", base, "HEAD"],
                                timeout=15, capture_output=True)
        check(status.returncode == 0, "Reviewed base is not an ancestor")

    # Frozen A41 and B50 manifests: exact blob, regular, tracked 100644, not executable.
    index = index_entries(root)
    frozen_files = {frozen.A_MANIFEST: frozen.A_MANIFEST_SHA, frozen.MANIFEST: B_MANIFEST_SHA}
    for path, pinned in frozen_files.items():
        file = root / path
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), "Nonregular frozen manifest")
        digest = blob_sha(file.read_bytes())
        check(digest == pinned, "Frozen manifest identity changed")
        check(index.get(path) == (digest, "100644") and not file.stat().st_mode & 0o111,
              "Unreviewed frozen manifest index/mode")
    file = root / CANDIDATE_MANIFEST
    check(stat.S_ISREG(file.lstat().st_mode) and index.get(CANDIDATE_MANIFEST) == (blob_sha(data), "100644")
          and not file.stat().st_mode & 0o111, "Unreviewed candidate manifest index/mode")
    original = json.loads((root / frozen.A_MANIFEST).read_bytes()).get("original54_migrations")
    b50 = json.loads((root / frozen.MANIFEST).read_bytes())
    b50_migrations = b50.get("integrated_migrations")
    check(isinstance(original, dict) and len(original) == ORIGINAL_COUNT, "Frozen original41 map invalid")
    check(isinstance(b50_migrations, dict) and len(b50_migrations) == B50_COUNT
          and b50.get("original54_migrations") == original, "Frozen B50 map invalid")

    # Protected snapshot: exact path set, blob and mode in index and worktree.
    entries = manifest.get("protected_blobs")
    check(isinstance(entries, list) and bool(entries), "Empty source snapshot")
    expected = {}
    for item in entries:
        check(isinstance(item, dict) and set(item) == {"path", "sha", "mode"}, "Invalid source snapshot entry")
        path = item["path"]
        check(valid_path(path) and protected(path), "Invalid protected snapshot path")
        check(path not in expected, "Duplicate source snapshot path")
        check(isinstance(item["sha"], str) and re.fullmatch(r"[0-9a-f]{40}", item["sha"]), "Invalid source blob identity")
        check(item["mode"] in {"100644", "100755"}, "Invalid source mode")
        expected[path] = (item["sha"], item["mode"])
    check([x["path"] for x in entries] == sorted(expected), "Unordered source snapshot")
    observed = {p.decode() for p in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    check({p for p in observed if protected(p)} == set(expected), "Protected source path set changed")
    check({p for p in index if protected(p)} == set(expected), "Protected index path set changed")
    for path, (sha, mode) in expected.items():
        file = root / path
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), f"Nonregular or missing source: {path}")
        check(blob_sha(file.read_bytes()) == sha, f"Unreviewed source mutation: {path}")
        check(index.get(path) == (sha, mode), f"Unreviewed tracked source mode/blob: {path}")
        worktree_mode = "100755" if file.stat().st_mode & 0o111 else "100644"
        check(worktree_mode == mode, f"Unreviewed worktree source mode: {path}")

    # Full ordered ledger: exactly the protected migration files, strictly ordered, unique versions.
    ledger = manifest.get("migration_ledger")
    check(isinstance(ledger, list) and len(ledger) == CANDIDATE_COUNT and manifest.get("migration_count") == CANDIDATE_COUNT,
          "Candidate63 ledger size changed")
    check(all(isinstance(x, dict) and set(x) == {"path", "sha", "mode"} for x in ledger), "Invalid ledger entry")
    paths = [x["path"] for x in ledger]
    check(all(MIGRATION_NAME.fullmatch(p) for p in paths), "Invalid migration ledger path")
    check(paths == sorted(paths) and len(set(paths)) == len(paths), "Migration ledger order changed")
    versions = [MIGRATION_NAME.fullmatch(p).group(1) for p in paths]
    check(len(set(versions)) == len(versions), "Duplicate migration version")
    in_dir = {p for p in expected if p.startswith(MIGRATION_DIR)}
    check(in_dir == set(paths), "Migration directory differs from ledger")
    check(all(expected[x["path"]] == (x["sha"], x["mode"]) for x in ledger), "Ledger differs from protected snapshot")
    check(all(x["mode"] == "100644" for x in ledger), "Executable migration")
    # Fixed candidate base: the applied ledger is exactly the reviewed commit's, byte and mode.
    check(tree_migrations(root, CANDIDATE_BASE_SHA) == ledger, "Candidate63 ledger differs from fixed candidate base")

    # B50 and original41 preserved, as the ordered prefix; new migrations sort after B50.
    prefix = ledger[:B50_COUNT]
    check([x["path"] for x in prefix] == sorted(b50_migrations)
          and all(b50_migrations[x["path"]] == x["sha"] for x in prefix), "B50 migration identity changed")
    check(tree_migrations(root, frozen.B_BASE_SHA) == prefix, "B50 migration identity/mode changed from fixed B base")
    check([x["path"] for x in ledger[:ORIGINAL_COUNT]] == sorted(original)
          and all(original[x["path"]] == x["sha"] for x in ledger[:ORIGINAL_COUNT]), "Original41 migration identity changed")
    check(versions[B50_COUNT] > versions[B50_COUNT - 1], "New migrations do not sort after B50")
    return {"scope": "reviewed_candidate63_source", "base_source": CANDIDATE_BASE_SHA,
            "b50_base_source": frozen.B_BASE_SHA,
            "head_sha": git(root, "rev-parse", "HEAD").decode().strip(),
            "protected_blob_count": len(expected), "all_protected_blobs_match": True,
            "migration_count": len(ledger), "b50_migrations_preserved": True,
            "original41_migrations_preserved": True, "new_migration_count": CANDIDATE_COUNT - B50_COUNT}


if __name__ == "__main__":
    if sys.argv[1:] == ["--print-manifest"]:
        print(json.dumps(build_manifest(Path.cwd()), indent=1))
    else:
        print(json.dumps(verify(Path.cwd()), indent=2))
