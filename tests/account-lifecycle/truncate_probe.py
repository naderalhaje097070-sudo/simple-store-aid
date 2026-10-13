"""SEC-TRUNCATE-01: catalog proof only; no TRUNCATE/DELETE/financial operation."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from owner_catalog_probe import CatalogProbe, SQL, validated_inventory
from live_probe import FINANCE_TABLES, HarnessFailure
from tanstack_route_probe import publish_result

ROOT=Path(__file__).resolve().parents[2]
PRIVILEGES=Path(__file__).with_name('truncate_privileges.sql')
TEMPLATE=ROOT/'changes/sec-truncate-01/REVOKE_TRUNCATE.sql'
BASE_CATALOG=ROOT/'changes/owner-retention-verify/evidence/native-9a5a/catalog.json'
CLIENTS={'anon','authenticated','PUBLIC'}
TABLES=tuple(sorted(r['relation'] for r in json.loads(BASE_CATALOG.read_text())['relations']
                    if r['relation'].startswith('public.') and r['kind'] in ('r','p')))


def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def validate_sql(sql):
    # A narrow static contract supplements (does not replace) live ACL observations.
    if 'REVOKE TRUNCATE ON TABLE\n' not in sql:
        raise HarnessFailure('explicit TRUNCATE-only revoke missing')
    expected_tables=re.findall(r'public\.([a-z_]+)',sql.split('REVOKE TRUNCATE ON TABLE',1)[1].split('FROM anon',1)[0])
    if ['public.'+n for n in expected_tables]!=list(TABLES):
        raise HarnessFailure('migration table allowlist changed')
    if re.search(r'^\s*(TRUNCATE|DELETE|INSERT|UPDATE|DROP|GRANT|CREATE|ALTER TABLE|ALTER ROLE)\b',sql,re.I|re.M):
        raise HarnessFailure('migration contains unapproved operation')
    if len(re.findall(r'ALTER DEFAULT PRIVILEGES',sql,re.I))!=1 or 'FOR ROLE postgres IN SCHEMA public' not in sql:
        raise HarnessFailure('default privilege scope changed')
    if 'REVOKE ALL' in sql.upper() or 'CASCADE' in sql.upper() or 'auth.' in sql or 'storage.' in sql:
        raise HarnessFailure('migration scope broadened')
    if 'SEC_TRUNCATE_UNSCOPED_GLOBAL_DEFAULT_GRANT' not in sql or not sql.strip().endswith('COMMIT;'):
        raise HarnessFailure('atomic global-default preflight missing')
    return True


def structural(catalog):
    value=copy.deepcopy(catalog)
    value.pop('migration_versions')
    value.pop('default_acls')
    for r in value['relations']:
        if r['relation'] in TABLES:
            r.pop('acl')
            for role,rights in r['privileges'].items():
                if role in ('anon','authenticated'):
                    rights.pop('TRUNCATE')
    return value


def eligible_acl(row):
    return row['relation'] in TABLES and row['grantee'] in CLIENTS and row['privilege']=='TRUNCATE'


def eligible_default(row):
    return row['creator']=='postgres' and row['schema']=='public' and row['object_type']=='r' and row['grantee'] in CLIENTS and row['privilege']=='TRUNCATE'


def validate_privilege_delta(before,after):
    required={'identity','table_acl','table_matrix','default_acl'}
    if set(before)!=required or set(after)!=required or before['identity']!=after['identity'] or before['identity']!={'current_user':'postgres','session_user':'postgres'}:
        raise HarnessFailure('migration creator/session identity changed')
    if not before['table_matrix'] or not after['table_matrix']:
        raise HarnessFailure('empty privilege matrix')
    if [r for r in before['table_acl'] if not eligible_acl(r)]!=after['table_acl']:
        raise HarnessFailure('non-target table ACL changed or client TRUNCATE remains')
    if [r for r in before['default_acl'] if not eligible_default(r)]!=after['default_acl']:
        raise HarnessFailure('default ACL changed outside postgres/public/client/TRUNCATE')
    expected=copy.deepcopy(before['table_matrix'])
    for r in expected:
        if r['relation'] in TABLES and r['role'] in ('anon','authenticated'):
            r['rights']['TRUNCATE']=False
    if expected!=after['table_matrix']:
        raise HarnessFailure('non-target role/right changed or inherited TRUNCATE remains')
    expected_pairs={(t,role) for t in TABLES for role in ('anon','authenticated')}
    actual={(r['relation'],r['role']) for r in after['table_matrix'] if r['relation'] in TABLES and r['role'] in ('anon','authenticated')}
    if expected_pairs!=actual:
        raise HarnessFailure('target privilege matrix incomplete')
    return True


def compare_baseline(catalog,phase):
    prior=json.loads(BASE_CATALOG.read_text())
    rights={r['relation']:r['privileges'] for r in catalog['relations'] if r['relation'] in TABLES}
    expected={r['relation']:r['privileges'] for r in prior['relations'] if r['relation'] in TABLES}
    if phase=='after':
        for value in expected.values():
            for role in ('anon','authenticated'):value[role]['TRUNCATE']=False
    if rights!=expected:
        raise HarnessFailure('historical baseline rights mismatch')
    return True


class TruncateProbe(CatalogProbe):
    def transactional_probe(self,sql):
        # The sole write-capable test is a fixed empty object CREATE in a rolled-back
        # transaction under the existing postgres identity; never SET ROLE or data DML.
        from write_harness_guard import _psql_command
        command=['sudo','-u','mcp-route','env','-i','PATH=/usr/bin:/bin','PGPASSWORD=postgres',
                 'PGOPTIONS=-c statement_timeout=30000']+_psql_command(self.config,'-Atq','-v','ON_ERROR_STOP=1')
        r=subprocess.run(command,input=sql,capture_output=True,text=True,timeout=60)
        if r.returncode:raise HarnessFailure('rolled-back defaults probe failed')
        try:return json.loads(r.stdout.strip())
        except ValueError as exc:raise HarnessFailure('defaults probe result incomplete') from exc

    def default_probe(self):
        if self.query("SELECT to_jsonb(to_regclass('public.__sec_truncate_default_probe') IS NULL);") is not True:
            raise HarnessFailure('default test object already exists')
        query="""BEGIN;
CREATE TABLE public.__sec_truncate_default_probe (probe_value integer);
SELECT jsonb_build_object('creator',current_user,'session_user',session_user,
 'owner',(SELECT pg_get_userbyid(relowner) FROM pg_class WHERE oid='public.__sec_truncate_default_probe'::regclass),
 'rights',(SELECT jsonb_object_agg(r.rolname,jsonb_build_object(
   'SELECT',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','SELECT'),
   'INSERT',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','INSERT'),
   'UPDATE',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','UPDATE'),
   'DELETE',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','DELETE'),
   'TRUNCATE',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','TRUNCATE'),
   'REFERENCES',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','REFERENCES'),
   'TRIGGER',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','TRIGGER'),
   'MAINTAIN',has_table_privilege(r.oid,'public.__sec_truncate_default_probe','MAINTAIN')) ORDER BY r.rolname) FROM pg_roles r),
 'acl',(SELECT jsonb_agg(jsonb_build_object('grantee',CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END,
   'grantor',pg_get_userbyid(a.grantor),'privilege',a.privilege_type,'grantable',a.is_grantable)
   ORDER BY a.grantee,a.privilege_type) FROM pg_class c CROSS JOIN LATERAL aclexplode(c.relacl) a
   WHERE c.oid='public.__sec_truncate_default_probe'::regclass));
ROLLBACK;"""
        result=self.transactional_probe(query)
        result['rolled_back_object_absent']=self.query("SELECT to_jsonb(to_regclass('public.__sec_truncate_default_probe') IS NULL);")
        if result['creator']!='postgres' or result['session_user']!='postgres' or result['owner']!='postgres' or result['rolled_back_object_absent'] is not True:
            raise HarnessFailure('creator/default object rollback contract mismatch')
        return result

    def capture(self,phase):
        before=self.snapshot();counts_before=self.counts()
        if any(counts_before[t] for t in FINANCE_TABLES) or counts_before['users'] or counts_before['tenants']:
            raise HarnessFailure('fixture-free isolated stack required')
        catalog=self.query(SQL.read_text());validated_inventory(catalog)
        acl=self.query(PRIVILEGES.read_text())
        default=self.default_probe()
        after=self.snapshot();counts_after=self.counts()
        if before!=after or counts_before!=counts_after:
            raise HarnessFailure('data changed during permission-only observation')
        migrations=sorted((ROOT/'supabase/migrations').glob('*.sql'))
        original=json.loads((ROOT/'changes/account-deletion-safety-intake/SOURCE_MAP.json').read_text())
        manifest={x['path']:x['sha256'] for x in original['source_manifest']}
        for path in original['migration_order']:
            if hashlib.sha256((ROOT/path).read_bytes()).hexdigest()!=manifest[path]:raise HarnessFailure('old migration modified')
        correction=[p for p in migrations if p.name.endswith('_sec_truncate_01.sql')]
        if len(migrations)!=44 or len(correction)!=1 or correction[0].read_bytes()!=TEMPLATE.read_bytes():
            raise HarnessFailure('generated correction migration source mismatch')
        validate_sql(correction[0].read_text())
        expected_versions=[p.name.split('_')[0] for p in migrations]
        if phase=='before':expected_versions=expected_versions[:-1]
        if catalog['migration_versions']!=expected_versions:raise HarnessFailure('actual migration chain mismatch')
        compare_baseline(catalog,phase)
        if default['rights']['authenticated']['TRUNCATE']!=(phase=='before') or default['rights']['anon']['TRUNCATE']:
            raise HarnessFailure('future app table defaults mismatch')
        if any(r['grantee']=='PUBLIC' and r['privilege']=='TRUNCATE' for r in default['acl']):
            raise HarnessFailure('PUBLIC future-table TRUNCATE')
        result=dict(source_sha=self.source,phase=phase,catalog=catalog,acl=acl,default_probe=default,
          public_before=before,public_after=after,counts_before=counts_before,counts_after=counts_after,
          migration_file=correction[0].name,migration_sha256=hashlib.sha256(correction[0].read_bytes()).hexdigest(),
          all_43_migrations_unchanged=True,closure_verified=False,integration_accepted=False)
        (self.evidence_dir/(phase+'-observation.json')).write_text(json.dumps(result,separators=(',',':'))+'\n')
        return result

    def run_truncate(self,phase,mode):
        result=self.capture(phase)
        if phase=='before':
            published=publish_result(self.evidence_dir,dict(phase=phase,baseline_ready=True,integration_accepted=False),[self.anon,self.admin])
            if not published.get('evidence_no_credentials'):raise HarnessFailure('baseline credential evidence quarantined')
            return
        checks={}
        if mode=='upgrade':
            before=json.loads((self.evidence_dir/'before-observation.json').read_text())
            validate_privilege_delta(before['acl'],result['acl'])
            checks['all_non_target_role_rights_and_provider_ACLs_preserved']=True
            if structural(before['catalog'])!=structural(result['catalog']):raise HarnessFailure('non-target schema/RPC/RLS/FK/trigger changed')
            checks['non_target_structure_unchanged']=True
            if before['public_before']!=result['public_after'] or before['counts_before']!=result['counts_after']:
                raise HarnessFailure('data changed across upgrade')
            checks['public_22_before_after_upgrade_unchanged']=True
            expected=copy.deepcopy(before['default_probe'])
            expected['rights']['authenticated']['TRUNCATE']=False
            expected['acl']=[a for a in expected['acl'] if not(a['grantee'] in CLIENTS and a['privilege']=='TRUNCATE')]
            if expected!=result['default_probe']:raise HarnessFailure('non-target future-table default rights changed')
            checks['future_table_non_target_rights_preserved']=True
        else:
            # Reuse the prior full catalog baseline; compare targeted change only.
            prior=json.loads(BASE_CATALOG.read_text())
            left=structural(prior);right=structural(result['catalog'])
            # Internal RI trigger names include installation-local OIDs.
            for value in (left,right):
                for t in value['triggers']:
                    if t['internal']:
                        t['name']='<internal RI>'
                        t['definition']=re.sub(r'RI_ConstraintTrigger_[a-z]_\d+','<internal RI>',t['definition'])
                value['triggers']=sorted(value['triggers'],key=lambda x:json.dumps(x,sort_keys=True))
            if left!=right:raise HarnessFailure('fresh structure drift from reviewed baseline')
            checks['fresh_structure_matches_prior_baseline_except_target_ACLs']=True
        for r in result['acl']['table_matrix']:
            if r['relation'] in TABLES and r['role'] in ('anon','authenticated') and r['rights']['TRUNCATE']:
                raise HarnessFailure('client inherited TRUNCATE remains')
        if any(eligible_acl(a) for a in result['acl']['table_acl']):raise HarnessFailure('PUBLIC/direct client TRUNCATE remains')
        checks.update(client_TRUNCATE_denied_all_22=True,explicit_PUBLIC_and_inheritance_checked=True,
                      original_financial_7_empty=True,future_postgres_public_table_client_TRUNCATE_denied=True,
                      default_probe_object_rolled_back=True,all_43_migrations_unchanged=True,
                      no_TRUNCATE_DELETE_or_lifecycle_executed=True)
        receipt=dict(source_sha=self.source,mode=mode,migration_file=result['migration_file'],
          migration_sha256=result['migration_sha256'],checks=checks,candidate_accepted=all(checks.values()),
          postgres_version=result['catalog']['settings']['server_version'],
          cli_version=subprocess.run(['supabase','--version'],capture_output=True,text=True,check=True).stdout.strip(),
          runtime_images=subprocess.run(['docker','ps','--format','{{.Image}}'],capture_output=True,text=True,check=True).stdout.splitlines(),
          closure_verified=False,integration_accepted=False)
        published=publish_result(self.evidence_dir,receipt,[self.anon,self.admin])
        if not published.get('evidence_no_credentials'):raise HarnessFailure('credential evidence quarantined')
        (self.evidence_dir/'truncate-result.json').write_text(json.dumps(published,indent=2)+'\n')
        (self.evidence_dir/'route-result.json').unlink()
        print(json.dumps(published))


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--status-file',type=Path,required=True);p.add_argument('--evidence-dir',type=Path,required=True)
    p.add_argument('--expected-source',required=True);p.add_argument('--phase',choices=['before','after'],required=True)
    p.add_argument('--mode',choices=['fresh','upgrade'],required=True)
    a=p.parse_args()
    try:TruncateProbe(a.status_file,a.evidence_dir,a.expected_source).run_truncate(a.phase,a.mode)
    except (HarnessFailure,OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as e:
        a.evidence_dir.mkdir(parents=True,exist_ok=True)
        reason=str(e) if isinstance(e,HarnessFailure) else type(e).__name__
        (a.evidence_dir/'truncate-failure.json').write_text(json.dumps(dict(source_sha=a.expected_source,mode=a.mode,
            reason=reason,candidate_accepted=False,integration_accepted=False))+'\n')
        print('SEC_TRUNCATE_HARNESS_FAILED: '+reason);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
