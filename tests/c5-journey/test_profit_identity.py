"""Negative controls for the new layer; historical guards remain unchanged."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import profit_identity as identity
from integrated_identity import IdentityError

class Admission(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.env=patch.dict(os.environ);self.env.start();os.environ.pop('EXPECTED_SOURCE',None)
        self.g('init','-q');self.g('remote','add','origin','https://github.com/'+identity.REPOSITORY+'.git')
        for path in identity.CHANGES|identity.FROZEN|{'src/untouched.ts','tests/c5-journey/source.json','tests/c5-journey/journey_identity.py','tests/c5-collection/source.json','tests/c5-collection/collection_identity.py','package.json','bun.lock'}:
            self.write(path,'old\n')
        for n in range(55):self.write(f'supabase/migrations/20260101{n:06d}_prior.sql','select 1;\n')
        self.commit();base=self.g('rev-parse','HEAD').decode().strip()
        self.base=patch.object(identity,'BASE',base);self.base.start()
        changes={p:{'before':identity.blob((self.root/p).read_bytes())} for p in identity.CHANGES}
        for p in identity.CHANGES:self.write(p,'approved\n');changes[p]['after']=identity.blob((self.root/p).read_bytes())
        for p in identity.ADDITIONS:self.write(p,'approved addition\n')
        self.m={'schema_version':1,'repository':identity.REPOSITORY,'scope':'C5-PROFIT-CONTRACT-IMPLEMENT-01','base_source':base,'changes':changes,
                'additions':{p:identity.blob((self.root/p).read_bytes()) for p in identity.ADDITIONS}}
        self.save();self.commit()
    def tearDown(self):self.base.stop();self.env.stop();self.tmp.cleanup()
    def g(self,*args):return subprocess.check_output(['git','-C',str(self.root),*args],stderr=subprocess.DEVNULL)
    def write(self,p,s):f=self.root/p;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s)
    def commit(self):self.g('add','.');self.g('-c','user.name=Fixture','-c','user.email=fixture@example.test','commit','-qm','fixture')
    def save(self):self.write(identity.MANIFEST,json.dumps(self.m,indent=2)+'\n')
    def deny(self):
        with self.assertRaises(IdentityError):identity.verify(self.root)
    def test_exact_adopted_delta(self):
        result=identity.verify(self.root)
        self.assertEqual(result['migration_count'],56);self.assertTrue(result['original55_unchanged']);self.assertFalse(result['financial_acceptance'])
    def test_old_sql_tamper(self):self.write('supabase/migrations/20260101000000_prior.sql','select 2;\n');self.deny()
    def test_old_sql_missing(self):(self.root/'supabase/migrations/20260101000000_prior.sql').unlink();self.deny()
    def test_new_sql_tamper(self):self.write(identity.MIGRATION,'select 2;\n');self.deny()
    def test_extra_sql_duplicate_version(self):self.write(identity.MIGRATION.replace('_c5_day','_unreviewed_day'),'select 1;\n');self.deny()
    def test_unrelated_app_drift(self):self.write('src/untouched.ts','new\n');self.deny()
    def test_untracked_executable(self):self.write('src/untracked.ts','new\n');self.deny()
    def test_unknown_cache(self):self.write('supabase/.temp/cli-latest','new\n');self.deny()
    def test_frozen_prior_journey_manifest(self):self.write('tests/c5-journey/source.json','{}\n');self.deny()
    def test_frozen_prior_collection_guard(self):self.write('tests/c5-collection/collection_identity.py','changed\n');self.deny()
    def test_frozen_integrated_manifest(self):self.write(next(iter(identity.FROZEN)),'changed\n');self.deny()
    def test_manifest_only_widening(self):
        self.write('src/untouched.ts','changed\n');self.m['changes']['src/untouched.ts']={'before':identity.blob(b'old\n'),'after':identity.blob(b'changed\n')};self.save();self.commit();self.deny()
    def test_false_before_sha(self):
        self.m['changes'][next(iter(identity.CHANGES))]['before']='0'*40;self.save();self.commit();self.deny()
    def test_symlink(self):
        p=self.root/'src/untouched.ts';p.unlink();p.symlink_to(self.root/'package.json');self.deny()
    def test_mode(self):(self.root/'src/untouched.ts').chmod(0o755);self.deny()
    def test_reviewed_head_not_staged_restoration(self):
        self.write('src/untouched.ts','unreviewed\n');self.commit();self.write('src/untouched.ts','old\n');self.g('add','src/untouched.ts');self.deny()
    def test_expected_source(self):os.environ['EXPECTED_SOURCE']='0'*40;self.deny()
    def test_remote(self):self.g('remote','set-url','origin','https://github.com/other/repo.git');self.deny()
    def test_installed_history_exact55_and56(self):
        versions=identity.verify_migrations(self.root)
        identity.verify_history(versions,versions);identity.verify_history(versions,versions[:-1],seed55=True)
        for observed in [versions[:-1],versions+['99999999999999'],list(reversed(versions))]:
            with self.assertRaises(IdentityError):identity.verify_history(versions,observed)
        with self.assertRaises(IdentityError):identity.verify_history(versions,versions,seed55=True)

if __name__=='__main__':unittest.main()
