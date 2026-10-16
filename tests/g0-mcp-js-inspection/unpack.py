"""Extract only ordinary package files for inspection. Never execute them."""
import hashlib
import json
import sys
import tarfile
from pathlib import Path, PurePosixPath

out = Path(sys.argv[1]).resolve()
inventories = {}
for label in ("baseline", "candidate"):
    archive = out / f"{label}.tgz"
    if not archive.exists():
        continue
    inventory = {}
    files = []
    with tarfile.open(archive, "r:gz") as tar:
        members = tar.getmembers()
        if len(members) > 5000:
            raise ValueError("Too many archive entries")
        total = 0
        for member in members:
            p = PurePosixPath(member.name)
            if p.is_absolute() or ".." in p.parts or not p.parts or p.parts[0] != "package":
                raise ValueError("Unsafe archive path")
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError("Links and special files rejected")
            total += member.size
            if member.size > 32 * 1024 * 1024 or total > 128 * 1024 * 1024:
                raise ValueError("Archive size cap exceeded")
            relative = "/".join(p.parts[1:])
            if not relative or relative in inventory:
                raise ValueError("Empty or duplicate file")
            data = tar.extractfile(member).read()
            inventory[relative] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
            files.append((relative, data))
    for relative, data in files:
        dest = out / f"{label}-files" / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(data)
    manifest = json.loads((out / f"{label}-files/package.json").read_text())
    metadata = json.loads((out / f"{label}-metadata.json").read_text())
    for key in ("name", "version", "dependencies", "exports", "engines", "bin"):
        if manifest.get(key) != metadata.get(key):
            raise ValueError(f"Published archive/registry mismatch: {label}/{key}")
    (out / f"{label}-files.json").write_text(json.dumps(inventory, indent=2) + "\n")
    inventories[label] = inventory
if len(inventories) == 2:
    before, after = inventories["baseline"], inventories["candidate"]
    diff = [{"path": p, "before": before.get(p), "after": after.get(p)}
            for p in sorted(before.keys() | after.keys()) if before.get(p) != after.get(p)]
    (out / "published-file-diff.json").write_text(json.dumps(diff, indent=2) + "\n")
    print(json.dumps({"baseline_files": len(before), "candidate_files": len(after), "changed": len(diff), "execution": "none"}))
