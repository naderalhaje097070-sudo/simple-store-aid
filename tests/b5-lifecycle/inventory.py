"""Strict B50 inventory: preserves the historical A41 rather than weakening it."""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "tests/g01-acceptance"))
from integrated_identity import verify


def versions(paths):
    return [Path(p).name.split("_")[0] for p in sorted(paths)]


def applied(expected, actual):
    if type(actual) is not list or actual != expected:
        raise RuntimeError("exact_ordered_migration_identity")
    return True


def inventory(root=ROOT):
    # Verifies actual index/worktree, immutable B base50 and frozen A41 first.
    identity = verify(root)
    m = json.loads((Path(root) / "tests/g01-acceptance/integrated-b-source.json").read_text())
    all_paths = sorted(m["integrated_migrations"])
    original = sorted(m["original54_migrations"])
    if len(all_paths) != 50 or len(original) != 41 or all_paths[:41] != original:
        raise RuntimeError("B50_original41_inventory")
    return {"identity": identity, "all_paths": all_paths, "original_paths": original,
            "full_versions": versions(all_paths), "original_versions": versions(original)}


if __name__ == "__main__":
    print(json.dumps(inventory(), indent=2))
