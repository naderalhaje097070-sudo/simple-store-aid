"""Read-only local catalog reconciliation; never executes lifecycle or financial APIs."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess

from mcp_probe import McpProbe
from live_probe import HarnessFailure, FINANCE_TABLES
from tanstack_route_probe import publish_result

ROOT = Path(__file__).resolve().parents[2]
MAP = ROOT / 'changes/account-deletion-safety-intake/SOURCE_MAP.json'
SQL = Path(__file__).with_name('owner_catalog.sql')


def source_expectations(root=ROOT):
    source = json.loads((root / 'changes/account-deletion-safety-intake/SOURCE_MAP.json').read_text())
    paths = sorted((root / 'supabase/migrations').glob('*.sql'))
    if [str(p.relative_to(root)) for p in paths] != source['migration_order'] or len(paths) != 43:
        raise HarnessFailure('ordered immutable migration inventory mismatch')
    manifest = {x['path']: x for x in source['source_manifest']}
    hashes = {}
    for p in paths:
        name = str(p.relative_to(root))
        digest = hashlib.sha256(p.read_bytes()).hexdigest()
        if digest != manifest[name]['sha256']:
            raise HarnessFailure('migration changed from reviewed source: ' + p.name)
        hashes[p.name] = digest
    functions = []
    for name, chain in source['function_definition_chain'].items():
        if name == 'public.__test_force_delete_e2e_order':
            continue  # Explicitly dropped by migration41, not an exposed current API.
        origin = chain[-1]
        text = '\n'.join((root / origin['path']).read_text().splitlines()[origin['line'] - 1:])
        match = re.search(r'\bAS\s+(\$\w*\$)(.*?)\1', text, re.S | re.I)
        if not match:
            raise HarnessFailure('function source body extraction failed: ' + name)
        header = text[:match.start()]
        functions.append(dict(name=name, body=match[2], definer=bool(re.search(r'SECURITY\s+DEFINER',header,re.I)),
                              path=origin['path'], line=origin['line']))
    checks = []
    for p in paths:
        text = p.read_text()
        for match in re.finditer(r'ALTER\s+TABLE\s+(public\.\w+)\s+ADD\s+CONSTRAINT\s+(\w+)\s+(CHECK\s*\(.*?);', text, re.S | re.I):
            checks.append(dict(relation=match[1], name=match[2], validated='NOT VALID' not in match[3].upper(),
                               definition=match[3], path=str(p.relative_to(root))))
    # Explicit named checks in this immutable chain are not later dropped.
    if len({(x['relation'],x['name']) for x in checks}) != len(checks):
        raise HarnessFailure('named check needs ordered override reconciliation')
    return dict(source_map=source, migration_sha256=hashes, functions=functions, checks=checks)


def row(kind, identity, expected, actual, matches, source=None, effect=None):
    return dict(kind=kind, identity=identity, expected=expected, actual=actual,
                status='MATCH' if matches else 'DIFFERENCE', source=source, policy_effect=effect)


def reconcile(expected, catalog, prior):
    rows = []
    for edge in expected['source_map']['public_fk_source_edges']:
        identity = edge['child'] + '.' + edge['column']
        actual = [f for f in catalog['fks'] if f['child'] == edge['child'] and f['child_columns'] == [edge['column']]]
        matches = len(actual) == 1 and actual[0]['parent'] == edge['parent'] and actual[0]['parent_columns'] == [edge['parent_column']] and actual[0]['on_delete'] == edge['on_delete']
        rows.append(row('FK',identity,edge,actual,matches,dict(path=edge['path'],line=edge['line']),
                        'Hard-delete edge; not a closure action. CASCADE/SET NULL can conflict with retention.'))
    expected_keys = {(e['child'],(e['column'],)) for e in expected['source_map']['public_fk_source_edges']}
    for f in catalog['fks']:
        if f['child'].startswith('public.') and (f['child'],tuple(f['child_columns'])) not in expected_keys:
            rows.append(row('FK_EXTRA',f['child']+'.'+f['name'],'no additional public FK in source map',f,False))
    for t in expected['source_map']['source_trigger_declarations']:
        table = re.search(r'ON\s+(\w+\.\w+)',t['declaration']).group(1)
        actual = [a for a in catalog['triggers'] if a['relation']==table and a['name']==t['name'] and not a['internal']]
        # PostgreSQL tgtype: ROW1 BEFORE2 INSERT4 DELETE8 UPDATE16 TRUNCATE32 INSTEAD64.
        bits = 1 + (2 if t['declaration'].startswith('BEFORE') else 0)
        bits += sum(value for event,value in [('INSERT',4),('DELETE',8),('UPDATE',16)] if event in t['declaration'].split(' ON ')[0])
        matches = len(actual)==1 and actual[0]['function']==t['function'] and actual[0]['enabled']=='O' and actual[0]['type_bits']==bits
        rows.append(row('TRIGGER',table+'.'+t['name'],t,actual,matches,dict(path=t['path'],line=t['line']),
                        'Enabled row trigger; cascade/SET NULL execution and rollback remain untested.'))
    for f in expected['functions']:
        actual = [a for a in catalog['functions'] if a['name']==f['name']]
        # prosrc preserves the dollar-quoted body. Never erase whitespace inside literals.
        matches = len(actual)==1 and actual[0]['body'].strip()==f['body'].strip() and actual[0]['definer']==f['definer']
        summary = [dict(arguments=a['arguments'],body_sha256=hashlib.sha256(a['body'].encode()).hexdigest(),
                        definer=a['definer'],config=a['config'],execute=a['execute']) for a in actual]
        rows.append(row('FUNCTION',f['name'],dict(body_sha256=hashlib.sha256(f['body'].encode()).hexdigest(),definer=f['definer']),
                        summary,matches,dict(path=f['path'],line=f['line']),'Body pinned; function not invoked.'))
    for c in expected['checks']:
        actual = [a for a in catalog['constraints'] if a['relation']==c['relation'] and a['name']==c['name']]
        matches = len(actual)==1 and actual[0]['type']=='c' and actual[0]['validated']==c['validated']
        rows.append(row('CHECK_METADATA',c['relation']+'.'+c['name'],c,actual,matches,dict(path=c['path']),
                        'Name/validation matched; raw expressions side-by-side, semantics require review, no mutation tested.'))
    public_relations = [r for r in catalog['relations'] if r['relation'].startswith('public.') and r['kind'] in ('r','p')]
    old_policies = {(p['schemaname'],p['tablename'],p['policyname']):p for p in prior['policies']}
    actual_policies = {(p['schemaname'],p['tablename'],p['policyname']):p for p in catalog['policies']}
    for key,p in old_policies.items():
        actual = actual_policies.get(key)
        rows.append(row('RLS_PRIOR', '.'.join(key),p,actual,actual==p,dict(path='changes/env-native-01/evidence/clean-baseline/catalog.json'),
                        'Historical effective policy retained; restrictive live-account policy is additive.'))
    for r in public_relations:
        key=('public',r['relation'].split('.')[1],'monjez_live_actor')
        p=actual_policies.get(key)
        direct=key[1]=='profiles'
        matches = bool(p and p['permissive']=='RESTRICTIVE' and p['cmd']=='ALL' and p['roles']==['authenticated']
                       and 'monjez_private.actor_is_active()' in p['qual'] and 'monjez_private.actor_is_active()' in p['with_check']
                       and (('SELECT' not in p['qual']) if direct else ('SELECT' in p['qual'])) and r['rls'])
        rows.append(row('RLS_LIVE',r['relation'],'RLS enabled + restrictive active-actor ALL; profiles direct call',p,matches,
                        dict(path='supabase/migrations/20261010225012_profiles_lifecycle_no_recursion.sql' if direct else 'supabase/migrations/20261010223557_enforce_live_account_state.sql'),
                        'Existing inactivity guard, not a new closure state or a populated history proof.'))
    old_grants={}
    for g in prior['table_grants']:
        old_grants.setdefault((g['table_name'],g['grantee']),set()).add(g['privilege_type'])
    for r in public_relations:
        for role,actual in r['privileges'].items():
            rights=old_grants.get((r['relation'].split('.')[1],role),set())
            expectation={p:p in rights for p in actual}
            rows.append(row('PRIVILEGES',r['relation']+'/'+role,expectation,actual,expectation==actual,
                            dict(path='changes/env-native-01/evidence/clean-baseline/catalog.json'),
                            'Effective privilege including inheritance; DELETE/TRUNCATE only inspected, never executed.'))
    mapped_policies=set(old_policies)|{('public',r['relation'].split('.')[1],'monjez_live_actor') for r in public_relations}
    for key,p in actual_policies.items():
        if key[0]=='public' and key not in mapped_policies:
            rows.append(row('RLS_EXTRA','.'.join(key),'no additional public policy in reviewed chain',p,False))
    return rows


def validated_inventory(catalog):
    required=('settings','schemas','fks','constraints','columns','triggers','functions','relations','policies','roles','memberships','schema_privileges','default_acls','migration_versions')
    if set(catalog)!=set(required) or any(not isinstance(catalog[k],list) for k in required if k!='settings'):
        raise HarnessFailure('incomplete catalog inventory')
    if set(catalog['schemas']) != {'auth','public','storage','monjez_private'} or catalog['settings']['transaction_read_only']!='on':
        raise HarnessFailure('catalog schema/read-only contract mismatch')
    if catalog['settings']['session_replication_role']!='origin':
        raise HarnessFailure('triggers not in normal origin mode')
    if not catalog['fks'] or not catalog['triggers'] or not catalog['functions'] or not catalog['constraints']:
        raise HarnessFailure('empty catalog cannot prove reconciliation')
    return True


class CatalogProbe(McpProbe):
    # Reuse target/source/credential preflight and public22 snapshots only.
    def sql(self, sql):
        from write_harness_guard import _psql_command
        command=['sudo','-u','mcp-route','env','-i','PATH=/usr/bin:/bin','PGPASSWORD=postgres',
                 'PGOPTIONS=-c default_transaction_read_only=on -c statement_timeout=30000']
        command += _psql_command(self.config,'-Atq','-v','ON_ERROR_STOP=1')
        r=subprocess.run(command,input='BEGIN READ ONLY;\n'+sql+'\nROLLBACK;',capture_output=True,text=True,timeout=60)
        if r.returncode:
            raise HarnessFailure('read-only catalog SQL failure')
        return r.stdout.strip()

    def request(self,*args,**kwargs):
        raise HarnessFailure('HTTP/lifecycle I/O forbidden in catalog probe')

    def run_catalog(self):
        expected=source_expectations()
        before=self.snapshot()
        counts_before=self.counts()
        if any(counts_before[k] for k in FINANCE_TABLES) or counts_before['users'] or counts_before['tenants']:
            raise HarnessFailure('fresh fixture-free stack required')
        catalog=self.query(SQL.read_text())
        validated_inventory(catalog)
        versions=[p.split('/')[-1].split('_')[0] for p in expected['source_map']['migration_order']]
        if catalog['migration_versions']!=versions:
            raise HarnessFailure('actual full migration chain mismatch')
        prior=json.loads((ROOT/'changes/env-native-01/evidence/clean-baseline/catalog.json').read_text())
        rows=reconcile(expected,catalog,prior)
        after=self.snapshot()
        counts_after=self.counts()
        if before!=after or counts_before!=counts_after:
            raise HarnessFailure('read-only application data invariant failed')
        runtime=subprocess.run(['docker','ps','--format','{{.Image}}'],capture_output=True,text=True,check=True).stdout.splitlines()
        result=dict(source_sha=self.source,base_sha='f37885b1ff5dcc9ab113e5cbee4516b485cedadd',
                    scope='catalog_only_no_lifecycle_no_fixture',catalog_complete=True,
                    source_map_sha256=hashlib.sha256(MAP.read_bytes()).hexdigest(),
                    migration_sha256=expected['migration_sha256'],postgres_version=catalog['settings']['server_version'],
                    cli_version=subprocess.run(['supabase','--version'],capture_output=True,text=True,check=True).stdout.strip(),
                    runtime_images=runtime,public_before=before,public_after=after,
                    counts_before=counts_before,counts_after=counts_after,comparison_rows=rows,
                    matches=sum(r['status']=='MATCH' for r in rows),differences=sum(r['status']=='DIFFERENCE' for r in rows),
                    integration_accepted=False,closure_verified=False,
                    observed_not_source_mapped=['provider Auth/Storage FK/trigger/constraints, internal RI triggers',
                      'inline/PK/UNIQUE constraint expressions and NOT NULL columns: raw inventory, not semantic equivalence',
                      'role memberships/default ACL/schema rights: raw effective inventory, no prior full baseline'],
                    untested=['hard/soft delete','ban','closure','nonempty finance','runtime RLS access','trigger execution order','concurrency','production'])
        (self.evidence_dir/'catalog.json').write_text(json.dumps(catalog,indent=2)+'\n')
        result=publish_result(self.evidence_dir,result,[self.anon,self.admin])
        if not result.get('evidence_no_credentials'):
            raise HarnessFailure('credential evidence quarantined')
        (self.evidence_dir/'catalog-result.json').write_text(json.dumps(result,indent=2)+'\n')
        (self.evidence_dir/'route-result.json').unlink()
        print(json.dumps({k:result[k] for k in ('source_sha','catalog_complete','matches','differences','closure_verified','integration_accepted')}))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--status-file',type=Path,required=True)
    parser.add_argument('--evidence-dir',type=Path,required=True)
    parser.add_argument('--expected-source',required=True)
    args=parser.parse_args()
    try:
        CatalogProbe(args.status_file,args.evidence_dir,args.expected_source).run_catalog()
    except (HarnessFailure,OSError,ValueError,KeyError,TypeError,subprocess.SubprocessError) as error:
        args.evidence_dir.mkdir(parents=True,exist_ok=True)
        # No raw SQL/exception output which might contain credentials.
        (args.evidence_dir/'catalog-failure.json').write_text(json.dumps(dict(source_sha=args.expected_source,
            stage=type(error).__name__,catalog_complete=False,closure_verified=False,integration_accepted=False))+'\n')
        print('OWNER_RETENTION_CATALOG_HARNESS_FAILED')
        return 2
    return 0


if __name__=='__main__':
    raise SystemExit(main())
