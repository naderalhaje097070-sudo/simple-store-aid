"""Strict candidate63 inventory: preserves the historical A41 and the frozen B50 rather than weakening them."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/g01-acceptance"))
from candidate_identity import CANDIDATE_MANIFEST, verify


def versions(paths):
    return [Path(p).name.split("_")[0] for p in sorted(paths)]


def applied(expected, actual):
    if type(actual) is not list or actual != expected:
        raise RuntimeError("exact_ordered_migration_identity")
    return True


def inventory(root=ROOT):
    # Verifies actual index/worktree, the fixed candidate63 ledger, the frozen B50 and A41 first.
    identity = verify(root)
    m = json.loads((Path(root) / CANDIDATE_MANIFEST).read_text())
    b = json.loads((Path(root) / "tests/g01-acceptance/integrated-b-source.json").read_text())
    all_paths = [x["path"] for x in m["migration_ledger"]]
    b50 = sorted(b["integrated_migrations"])
    original = sorted(b["original54_migrations"])
    if (len(all_paths) != 63 or all_paths != sorted(all_paths) or len(b50) != 50 or len(original) != 41
            or [p for p in all_paths if p in set(b50)] != b50 or all_paths[:41] != original):
        raise RuntimeError("candidate63_B50_original41_inventory")
    return {"identity": identity, "all_paths": all_paths, "b50_paths": b50, "original_paths": original,
            "full_versions": versions(all_paths), "b50_versions": versions(b50),
            "original_versions": versions(original), "count": len(all_paths)}


if __name__ == "__main__":
    print(json.dumps(inventory(), indent=2))
