"""Pin every installed fixed-engine file; a frozen exit alone is insufficient."""
import hashlib
import json
from pathlib import Path
import stat

ROOT = Path(__file__).resolve().parents[2]
PATCH = 'patches/minimatch@11.0.1.patch'
PATCH_SHA = '1c2e49a5e9608bdf3b904c9f3ee62b02cc8677e46167ec9d70f117cd3dc07015'


def verify(root=ROOT):
    root=Path(root)
    patch=root/PATCH
    assert patch.exists() and stat.S_ISREG(patch.lstat().st_mode), 'Nonregular patch'
    assert hashlib.sha256(patch.read_bytes()).hexdigest()==PATCH_SHA, 'Owner-approved patch mutated'
    data=json.loads((root/'tests/sec-dep-20261102/engine.json').read_text())
    assert data['schema_version']==1 and data['version']=='11.0.1' and data['patch_sha256']==PATCH_SHA
    files=data['files'];assert len(files)==37 and sum(x['changed'] for x in files)==4
    engine=root/'node_modules/minimatch';expected=set()
    for entry in files:
        name=entry['path'];parts=Path(name).parts
        assert name and not name.startswith('/') and '..' not in parts and '\\' not in name
        assert name not in expected;expected.add(name)
        file=engine/name
        assert file.exists() and stat.S_ISREG(file.lstat().st_mode), 'Nonregular engine: '+name
        assert hashlib.sha256(file.read_bytes()).hexdigest()==entry['installed_sha256'], 'Installed engine drift: '+name
    assert engine.is_dir() and not engine.is_symlink(), 'Nonregular installed engine directory'
    paths=list(engine.rglob('*'))
    assert all(not p.is_symlink() for p in paths), 'Symlink inside installed engine'
    observed={p.relative_to(engine).as_posix() for p in paths if p.is_file()}
    extra=observed-expected
    assert all(name.startswith('.bun-tag-') and (engine/name).stat().st_size==0 for name in extra), 'Unexpected engine files'
    package=json.loads((engine/'package.json').read_text())
    assert package['name']=='minimatch' and package['version']=='11.0.1'
    return {'fixed_engine':'minimatch11.0.1','official_files':37,'interop_files':4,'unmodified_files':33,'exact_installed_file_hashes':True,'patch_sha256':PATCH_SHA}


if __name__ == '__main__': print(json.dumps(verify(),indent=2))
