"""Exact, reviewed integrated-source snapshot; no per-path override fallback."""
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import subprocess

REPOSITORY = "naderalhaje097070-sudo/simple-store-aid"
MANIFEST = "tests/g01-acceptance/integrated-source.json"
STATE_DOCUMENTS = {"PROJECT_STATE.md", "TASKS.md", "DECISIONS.md"}
EVIDENCE_CODE = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".sh", ".c"}


class IdentityError(RuntimeError):
    pass


def protected(path):
    if path == MANIFEST or path in STATE_DOCUMENTS or path.endswith(".md"):
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
    check(type(manifest.get("schema_version")) is int and manifest["schema_version"] == 1,
          "Unreviewed source manifest schema")
    check(manifest.get("repository") == REPOSITORY, "Unexpected source repository")
    remote = git(root, "config", "--get", "remote.origin.url").decode().strip()
    check(remote in {f"https://github.com/{REPOSITORY}", f"https://github.com/{REPOSITORY}.git"},
          "Unexpected repository remote")
    base = manifest.get("base_source", "")
    check(isinstance(base, str) and re.fullmatch(r"[0-9a-f]{40}", base), "Invalid reviewed base")
    status = subprocess.run(["git", "-C", str(root), "merge-base", "--is-ancestor", base, "HEAD"],
                            timeout=15, capture_output=True)
    check(status.returncode == 0, "Reviewed base is not an ancestor")
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
        expected[path] = sha
    observed = {p.decode() for p in git(root, "ls-files", "--cached", "--others", "--exclude-standard", "-z").split(b"\0") if p}
    check({p for p in observed if protected(p)} == set(expected), "Protected source path set changed")
    for path, sha in expected.items():
        file = root / path
        check(file.exists() and stat.S_ISREG(file.lstat().st_mode), f"Nonregular or missing source: {path}")
        blob = file.read_bytes()
        actual = hashlib.sha1(b"blob " + str(len(blob)).encode() + b"\0" + blob).hexdigest()
        check(actual == sha, f"Unreviewed source mutation: {path}")
    migrations = {p: s for p, s in expected.items() if p.startswith("supabase/migrations/") and p.endswith(".sql")}
    check(len(migrations) == 41 and migrations == manifest.get("original54_migrations"),
          "Original41 migration identity changed")
    return {"scope": "reviewed_integrated_source", "base_source": base,
            "head_sha": git(root, "rev-parse", "HEAD").decode().strip(),
            "protected_blob_count": len(expected), "all_integrated_blobs_match": True,
            "migration_count": len(migrations), "original54_migrations_unchanged": True,
            "legacy383_unchanged_claim": False}
