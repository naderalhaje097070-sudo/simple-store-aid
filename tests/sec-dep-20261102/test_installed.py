"""Real installed-byte copy: negative tests must reject modified code and patch."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import installed


class Installed(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='monjez-engine-identity-'))
        shutil.copytree(installed.ROOT/'node_modules/minimatch',self.root/'node_modules/minimatch')
        for name in [installed.PATCH,'tests/sec-dep-20261102/engine.json']:
            p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True)
            shutil.copyfile(installed.ROOT/name,p)
    def tearDown(self): shutil.rmtree(self.root)
    def deny(self):
        with self.assertRaises(AssertionError): installed.verify(self.root)
    def test_exact_current_installed_engine(self): self.assertTrue(installed.verify(self.root)['exact_installed_file_hashes'])
    def test_engine_code_mutation(self):
        p=self.root/'node_modules/minimatch/dist/commonjs/index.js';p.write_bytes(p.read_bytes()+b'\n/* mutation */');self.deny()
    def test_missing_esm_export(self):
        p=self.root/'node_modules/minimatch/dist/esm/index.js';p.write_text(p.read_text().replace('export default minimatch;',''));self.deny()
    def test_patch_mutation(self):
        p=self.root/installed.PATCH;p.write_bytes(p.read_bytes()+b'\n');self.deny()
    def test_extra_engine_code(self):
        (self.root/'node_modules/minimatch/extra.cjs').write_text('module.exports = {};\n');self.deny()
    def test_nested_dependency_injection(self):
        p=self.root/'node_modules/minimatch/node_modules/injected/index.js';p.parent.mkdir(parents=True);p.write_text('module.exports = {};\n');self.deny()


if __name__ == '__main__': unittest.main()
