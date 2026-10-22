"""Exact, reviewed integrated-source snapshot; no per-path override fallback."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

REPOSITORY = "naderalhaje097070-sudo/simple-store-aid"
MANIFEST = "tests/g01-acceptance/integrated-b-source.json"
A_MANIFEST = "tests/g01-acceptance/integrated-source.json"
A_MANIFEST_SHA = "b79640f400a32924f114e19ec51a728be94b6afd"
B_BASE_SHA = "59c8a0c7920e58a02cb885b382f6ac5f1cb168f1"
STATE_DOCUMENTS = {"PROJECT_STATE.md", "TASKS.md", "DECISIONS.md"}
EVIDENCE_CODE = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".sh", ".c"}


class IdentityError(RuntimeError):
    pass


def protected(path):
    if path in {MANIFEST, A_MANIFEST} or path in STATE_DOCUMENTS or path.endswith(".md"):
        return False
    if path.startswith(("docs/", "changes/")):
        return PurePosixPath(path).suffix in EVIDENCE_CODE
    return True


def git(root, *args):
    return subprocess.check_output(["git", "-C", str(root), *args], timeout=15)


def check(condition, message):
    if not condition:
        raise IdentityError(message)


def valid_path(path):
    return (
        isinstance(path, str)
        and bool(path)
        and not path.startswith("/")
        and "\\" not in path
        and ".." not in path.split("/")
        and "." not in path.split("/")
        and str(PurePosixPath(path)) == path
    )


def verify(root):
    root = Path(root)
    data = (root / MANIFEST).read_bytes()
    check(data == git(root, "show", f"HEAD:{MANIFEST}"), "Uncommitted source manifest mutation")
    manifest = json.loads(data)
    check(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 2,
          "Unreviewed source manifest schema")
    check(manifest.get("repository") == REPOSITORY, "Unexpected source repository")
    remote = git(root, "config", "--get", "remote.origin.url").decode().strip()
    check(remote in {f"https://github.com/{REPOSITORY}", f"https://github.com/{REPOSITORY}.git"},
          "Unexpected repository remote")
    base = manifest.get("base_source", "")
    check(base == B_BASE_SHA, "Invalid reviewed B base")
    status = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", base, "HEAD"],
                            timeout=15, capture_output=True)
    check(status.returncode == 0, "Reviewed base is not an ancestor")
    archive = (root / A_MANIFEST).read_bytes()
    archive_sha = hashlib.sha1(b"blob " + str(len(archive)).encode() + b"\0" + archive).hexdigest()
    check(archive_sha == A_MANIFEST_SHA, "Frozen A manifest identity changed")
    original = json.loads(archive).get("original54_migrations")
    check(isinstance(original, dict) and len(original) == 41, "Frozen original41 map invalid")
    check(manifest.get("original54_migrations") == original, "Original41 migration map changed")
    entries = manifest.get("protected_blobs")
    check(isinstance(entries, list) and bool(entries), "Empty source snapshot")
    expected = {}
    for item in entries:
        check(isinstance(item, dict), "Invalid source snapshot entry")
        path = item.get("path")
        check(valid_path(path) and protected(path), "Invalid protected snapshot path")
        check(path not in expected, "Duplicate source snapshot path")
        sha = item.get("sha")
        check(isinstance(sha, str) and re.fullmatch(r"[0-9a-f]{40}", sha), "Invalid source blob identity")
        mode = item.get("mode")
        check(mode in {"100644", "100755"}, "Invalid source mode")
        expected[path] = (sha, mode)
    observed = {p.decode() for p in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    check({p for p in observed if protected(p)} == set(expected), "Protected source path set changed")
    index = {}
    for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, sha, stage = metadata.decode().split()
        check(stage == "0", "Unmerged source index")
        index[path.decode()] = (sha, mode)
    for path in (MANIFEST, A_MANIFEST):
        file = root / path
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), "Nonregular manifest")
        contents = file.read_bytes()
        digest = hashlib.sha1(b"blob " + str(len(contents)).encode() + b"\0" + contents).hexdigest()
        check(index.get(path) == (digest, "100644") and not file.stat().st_mode & 0o111,
              "Unreviewed manifest index/mode")
    for path, (sha, mode) in expected.items():
        file = root / path
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), f"Nonregular or missing source: {path}")
        blob = file.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        check(actual == sha, f"Unreviewed source mutation: {path}")
        check(index.get(path) == (sha, mode), f"Unreviewed tracked source mode/blob: {path}")
        worktree_mode = "100755" if file.stat().st_mode & 0o111 else "100644"
        check(worktree_mode == mode, f"Unreviewed worktree source mode: {path}")
    migrations = {p: s[0] for p, s in expected.items() if p.startswith("supabase/migrations/") and p.endswith(".sql")}
    check(len(migrations) == 50 and migrations == manifest.get("integrated_migrations"),
          "Integrated50 migration identity changed")
    check(all(migrations.get(p) == s for p, s in original.items()), "Original41 migration identity changed")
    baseline_sql = {}
    for entry in git(root, "ls-tree", "-r", "-z", B_BASE_SHA, "--", "supabase/migrations").split(b"\0"):
        if not entry:
            continue
        metadata, path = entry.split(b"\t", 1)
        mode, kind, sha = metadata.decode().split()
        name = path.decode()
        if name.endswith(".sql"):
            check(kind == "blob" and mode in {"100644", "100755"}, "Invalid applied migration mode")
            baseline_sql[name] = (sha, mode)
    check(len(baseline_sql) == 50 and baseline_sql == {p: expected[p] for p in migrations},
          "Applied B50 migration identity/mode changed from fixed base")
    return {"scope": "reviewed_integrated_B_source", "base_source": base,
            "head_sha": git(root, "rev-parse", "HEAD").decode().strip(),
            "protected_blob_count": len(expected), "all_integrated_blobs_match": True,
            "migration_count": len(migrations), "original54_migrations_unchanged": True,
            "legacy383_unchanged_claim": False}

