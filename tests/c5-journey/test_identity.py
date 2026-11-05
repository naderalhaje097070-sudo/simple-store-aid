import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import journey_identity as identity
from integrated_identity import IdentityError


class FinanceIdentity(unittest.TestCase):
    def setUp(self):
        self.root=Path(tempfile.mkdtemp(prefix='c5-journey-identity-'))
        self.g('init','-q');self.g('remote','add','origin','https://github.com/'+identity.REPOSITORY)
        self.write('.gitignore','__pycache__/\n')
        for p in ['src/finance.ts','package.json','bun.lock','patches/minimatch@11.0.1.patch',*identity.CHANGES]:
            self.write(p,'old\n')
        for n in range(55):self.write(f'supabase/migrations/{n:03}.sql','select 1;\n')
        frozen={}
        for p in identity.FROZEN:
            self.write(p,'{}\n');frozen[p]=identity.blob((self.root/p).read_bytes())
        self.commit();base=self.g('rev-parse','HEAD').decode().strip()
        self.patches=[patch.object(identity,'BASE',base),patch.dict(os.environ,{'EXPECTED_SOURCE':''})]
        for p in self.patches:p.start()
        changes={}
        for p in identity.CHANGES:
            before=identity.blob((self.root/p).read_bytes())
            self.write(p,'new admission\n')
            changes[p]={'before':before,'after':identity.blob((self.root/p).read_bytes())}
        for p in identity.ADDITIONS:self.write(p,'fixture\n')
        self.m={'schema_version':1,'scope':'C5-FULL-JOURNEY-01','repository':identity.REPOSITORY,'base_source':base,
                'changes':changes, 'additions':{p:identity.blob((self.root/p).read_bytes()) for p in identity.ADDITIONS}}
        self.save();self.commit()

    def tearDown(self):
        for p in reversed(self.patches):p.stop()
        shutil.rmtree(self.root)

    def g(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL)
    def write(self,p,data):
        file=self.root/p;file.parent.mkdir(parents=True,exist_ok=True);file.write_text(data)
    def commit(self):
        self.g('add','.');self.g('-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-qm','fixture')
    def save(self):self.write(identity.MANIFEST,json.dumps(self.m,indent=2)+'\n')
    def deny(self):
        with self.assertRaises(IdentityError):identity.verify(self.root)
    def test_explicit_delta(self):
        self.assertEqual(identity.verify(self.root)['migration_count'],55)
        self.assertFalse(identity.verify(self.root)['financial_acceptance'])
    def test_financial_source_drift(self):self.write('src/finance.ts','changed\n');self.deny()
    def test_committed_financial_drift_masked_by_staged_restoration(self):
        self.write('src/finance.ts','unreviewed committed finance\n');self.commit()
        self.write('src/finance.ts','old\n');self.g('add','src/finance.ts')
        self.deny()
    def test_inventory_diagnostics_withhold_unknown_names(self):
        result=identity.inventory_delta({'src/finance.ts'},{'private_secret_token_name'})
        self.assertEqual(result['missing'],['src/finance.ts'])
        self.assertEqual(result['extra_count'],1)
        self.assertNotIn('private_secret_token_name',json.dumps(result))
    def test_sql_drift(self):self.write('supabase/migrations/053.sql','select 2;\n');self.deny()
    def test_package_lock_patch_drift(self):
        for p in ['package.json','bun.lock','patches/minimatch@11.0.1.patch']:
            self.write(p,'changed\n');self.deny();self.write(p,'old\n')
    def test_frozen_manifest_drift(self):
        for p in identity.FROZEN:
            self.write(p,'changed\n');self.deny();self.write(p,'{}\n')
    def test_self_adopted_financial_source(self):
        self.write('src/finance.ts','changed\n');self.m['additions']['src/finance.ts']=identity.blob(b'changed\n');self.save();self.commit();self.deny()
    def test_untracked_executable(self):self.write('tests/injection.py','bad\n');self.deny()
    def test_missing_addition(self):(self.root/'tests/c5-journey/browser.py').unlink();self.deny()
    def test_omitted_declared_addition(self):del self.m['additions']['tests/c5-journey/browser.py'];self.save();self.commit();self.deny()
    def test_wrong_change_before(self):self.m['changes']['tests/g01-acceptance/capture.py']['before']='0'*40;self.save();self.commit();self.deny()
    def test_wrong_change_scope(self):self.m['changes']['src/finance.ts']=self.m['changes'].pop('tests/g01-acceptance/capture.py');self.save();self.commit();self.deny()
    def test_wrong_authority(self):self.m['base_source']='0'*40;self.save();self.commit();self.deny()
    def test_uncommitted_manifest(self):self.m['scope']='forged';self.save();self.deny()
    def test_wrong_head(self):
        with patch.dict(os.environ,{'EXPECTED_SOURCE':'0'*40}):self.deny()
    def test_wrong_remote(self):self.g('remote','set-url','origin','https://github.com/other/repo');self.deny()
    def test_source_symlink(self):
        p=self.root/'src/finance.ts';p.unlink();p.symlink_to(self.root/'package.json');self.deny()
    def test_source_mode(self):(self.root/'src/finance.ts').chmod(0o755);self.deny()
    def test_manifest_mode(self):(self.root/identity.MANIFEST).chmod(0o755);self.deny()
    def test_readonly_docs(self):self.write('changes/c5-finance/receipt.md','evidence\n');self.assertTrue(identity.verify(self.root)['all_integrated_blobs_match'])


if __name__=='__main__':unittest.main()

