"""Reproduce the sole static-default clone patch in the official Rollup tar.

Never patch application code, resolver behavior, general merge semantics or versions.
Input is a verified official @rollup/plugin-node-resolve@16.0.3 tarball.
"""
import difflib
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tarfile

source, output, evidence = map(Path, sys.argv[1:])
evidence.mkdir(parents=True, exist_ok=True)
files = {}
with tarfile.open(source, "r:gz") as archive:
    for entry in archive.getmembers():
        name = PurePosixPath(entry.name)
        assert not name.is_absolute() and ".." not in name.parts
        assert entry.isfile() or entry.isdir(), "Unexpected archive link/device"
        if entry.isfile():
            files[entry.name] = archive.extractfile(entry).read()
original = dict(files)
package = json.loads(files["package/package.json"])
assert package["name"] == "@rollup/plugin-node-resolve"
assert package["version"] == "16.0.3"
assert package["dependencies"].pop("deepmerge") == "^4.2.2"
files["package/package.json"] = (json.dumps(package, indent=2) + "\n").encode()
for name in ["package/dist/cjs/index.js", "package/dist/es/index.js"]:
    text = files[name].decode()
    if "/cjs/" in name:
        text, imports = re.subn(r"^(?:var|const) deepMerge = require\(['\"]deepmerge['\"]\);\n", "", text, flags=re.M)
        text, interop = re.subn(r"^(?:var|const) deepMerge__default = (?:/\*#__PURE__\*/)?\s*_interopDefault(?:Legacy)?\(deepMerge\);\n", "", text, flags=re.M)
        assert imports == interop == 1, "Unrecognized official CommonJS import shape"
    else:
        text, imports = re.subn(r"^import deepMerge from ['\"]deepmerge['\"];\n", "", text, flags=re.M)
        assert imports == 1, "Unrecognized official ESM import shape"
    text, calls = re.subn(r"deepMerge(?:__default)?(?:\[['\"]default['\"]\]|\.default)?\(\{\}, defaults\)", "JSON.parse(JSON.stringify(defaults))", text)
    assert calls == 1, "Static DEFAULTS clone must be the sole merge call"
    assert not re.search(r"\bdeepMerge(?:__default)?\b|['\"]deepmerge['\"]", text)
    assert "deepFreeze(JSON.parse(JSON.stringify(defaults)))" in text
    files[name] = text.encode()
changed = [name for name in files if files[name] != original[name]]
assert sorted(changed) == ["package/dist/cjs/index.js", "package/dist/es/index.js", "package/package.json"]
patch = "".join("".join(difflib.unified_diff(original[name].decode().splitlines(True), files[name].decode().splitlines(True), fromfile="official/" + name, tofile="patched/" + name)) for name in changed)
(evidence / "rollup-local.patch").write_text(patch)
receipt = {
    "package": "@rollup/plugin-node-resolve", "version": "16.0.3",
    "official_archive_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
    "changed_paths": changed,
    "files": {name: {"official_sha256": hashlib.sha256(original[name]).hexdigest(), "patched_sha256": hashlib.sha256(content).hexdigest()} for name, content in files.items()},
    "scope": "Transparent local patch: static DEFAULTS clone only; unused deepmerge dependency/import removed. No upstream fixed-release claim.",
}
output.parent.mkdir(parents=True, exist_ok=True)
# Stable metadata/order/gzip timestamp make the local archive reproducible.
import gzip
with output.open("wb") as target:
    with gzip.GzipFile(filename="", mode="wb", fileobj=target, mtime=0) as zipped:
        with tarfile.open(fileobj=zipped, mode="w") as archive:
            for name in sorted(files):
                entry = tarfile.TarInfo(name)
                entry.size = len(files[name])
                entry.mode = 0o644
                archive.addfile(entry, io.BytesIO(files[name]))
receipt["local_archive_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
(evidence / "rollup-provenance.json").write_text(json.dumps(receipt, indent=2) + "\n")
