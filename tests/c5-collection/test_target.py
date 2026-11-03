import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch
import collection_target as target
from integrated_identity import IdentityError

class CollectionTarget(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp())
        self.expected={}
        for i in range(54):
            p=f'supabase/migrations/20260101{i:06}_original.sql'
            self.write(p,'select 1;\n');self.expected[p]=target.blob(b'select 1;\n')
        self.base={**self.expected}
        self.write(target.MIGRATION,'select 2;\n');self.expected[target.MIGRATION]=target.blob(b'select 2;\n')
        self.manifest={'base_source':target.BASE,'repository':target.REPOSITORY,'scope':'C5-COLLECTION-RETRY-01','additions':{target.MIGRATION:self.expected[target.MIGRATION]}}
        self.raw=json.dumps(self.manifest).encode();self.write(target.MANIFEST,self.raw.decode())
        self.mock=patch.object(target,'git',side_effect=self.git);self.mock.start()
    def tearDown(self):self.mock.stop();shutil.rmtree(self.root)
    def write(self,p,text):
        file=self.root/p;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(text)
    def git(self,root,*args):
        if args==('show','HEAD:'+target.MANIFEST):return self.raw
        assert args==('ls-tree','-r','-z',target.BASE,'--','supabase/migrations')
        return b''.join(f'100644 blob {s}\t{p}\0'.encode() for p,s in self.base.items())
    def deny(self):
        with self.assertRaises(IdentityError):target.verify_source(self.root)
    def test_exact55(self):
        versions,receipt=target.verify_source(self.root)
        self.assertEqual(len(versions),55);self.assertFalse(receipt['financial_acceptance'])
        target.verify_history(versions,versions)
    def test_old_sql_drift(self):self.write(next(iter(self.base)),'changed');self.deny()
    def test_new_sql_drift(self):self.write(target.MIGRATION,'changed');self.deny()
    def test_missing_new(self):(self.root/target.MIGRATION).unlink();self.deny()
    def test_extra_sql(self):self.write('supabase/migrations/20270101010101_extra.sql','select 3;');self.deny()
    def test_symlink(self):
        p=self.root/target.MIGRATION;p.unlink();p.symlink_to(self.root/next(iter(self.base)));self.deny()
    def test_executable(self):(self.root/target.MIGRATION).chmod(0o755);self.deny()
    def test_uncommitted_manifest(self):self.write(target.MANIFEST,'{}');self.deny()
    def test_forged_authority(self):
        self.manifest['base_source']='0'*40;self.raw=json.dumps(self.manifest).encode();self.write(target.MANIFEST,self.raw.decode());self.deny()
    def test_bad_history(self):
        versions,_=target.verify_source(self.root)
        for observed in [versions[:-1],list(reversed(versions)),versions+[versions[0]],None]:
            with self.assertRaises(IdentityError):target.verify_history(versions,observed)
    def test_nonmigration_runtime_artifact_not_a_schema_input(self):
        self.write('.g01-cli-action/package.json','{}');self.assertEqual(len(target.verify_source(self.root)[0]),55)

if __name__=='__main__':unittest.main()
