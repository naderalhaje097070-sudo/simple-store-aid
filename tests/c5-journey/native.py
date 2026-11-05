"""Only uncovered actual UI financial journeys; reuse immutable lower-layer proof."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('frozen_collection_probe',ROOT/'tests/c5-collection/native.py')
prior=importlib.util.module_from_spec(spec);spec.loader.exec_module(prior)
sys.path.insert(0,str(Path(__file__).parent))
from journey_identity import verify


def safe_diagnostic(raw):
    fields={'quantity_inputs','quick_checkout_buttons','advanced_checkout_buttons',
            'sale_recovery_buttons','sale_rpc_calls','sale_rpc_completed',
            'sale_rpc_http200','page_errors','blocked_external'}
    if not isinstance(raw,dict):return {}
    return {key:value for key,value in raw.items()
            if key in fields and type(value) is int and 0<=value<=10000}


def main():
    parser=argparse.ArgumentParser()
    for name in ('status-file','evidence-dir','private-state'):parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--expected-source',required=True);args=parser.parse_args()
    verify(ROOT)
    p=prior.FinanceProbe(args.status_file,args.evidence_dir,args.expected_source);p.stage='setup'
    try:
        p.control('exact_reused_PostgreSQL_17_6',p.query("select current_setting('server_version_num')::integer;")==170006)
        if os.environ.get('COLLECTION_PHASE')=='seed54':
            result=p.seed_upgrade(args.private_state)
            (args.evidence_dir/'upgrade-seed.json').write_text(json.dumps(result,indent=2)+'\n')
            return 0
        versions,_=prior.verify_source(ROOT)
        prior.verify_history(versions,p.query('select jsonb_agg(version order by version) from supabase_migrations.schema_migrations;'))
        state=json.loads(args.private_state.read_text()) if args.private_state.exists() else {'actors':{}}
        if 'upgrade_snapshot' in state:p.control('populated54_to55_all_relations_preserved',p.snapshot()==state['upgrade_snapshot'])
        foreign=p.fixture('Journey_foreign');state['actors']['journey_foreign']=foreign;p.save(args.private_state,state)
        foreign_pid=p.seed_product(foreign)
        p.sql(f"update public.products set name='Journey foreign canary' where id='{foreign_pid}';")
        foreign_order=p.order(foreign,foreign_pid,.25,25)
        foreign_before=p.effect(foreign_order)
        from browser import run
        receipts=run(p,state,args.private_state)
        p.control('populated_foreign_financial_rows_unchanged',p.effect(foreign_order)==foreign_before and p.stock(foreign_pid)==9.75)
        result={'source_sha':p.source,'mode':os.environ['CONTRACT_MODE'],'controls':p.controls,'viewports':receipts,
                'journey_acceptance':True,'full_C5_acceptance':False,'integration_accepted':False,
                'scope':'actual app component and navigation with real Query/SDK/Auth/API/DB; router/auth entry, PDF, SW and restored HTTP/Auth excluded'}
        (args.evidence_dir/'journey-result.json').write_text(json.dumps(result,indent=2)+'\n')
        print('C5_JOURNEY_RESULT '+json.dumps({'source':p.source,'mode':os.environ['CONTRACT_MODE'],'controls':len(p.controls),'viewports':receipts,'journey_acceptance':True,'full_C5_acceptance':False}))
        return 0
    except Exception as error:
        result={'source_sha':p.source,'mode':os.environ['CONTRACT_MODE'],'stage':p.stage,
                'failure_type':type(error).__name__,'controls':p.controls,'journey_acceptance':False,'full_C5_acceptance':False,
                'diagnostic':safe_diagnostic(getattr(p,'journey_diagnostic',{}))}
        (args.evidence_dir/'journey-failure.json').write_text(json.dumps(result,indent=2)+'\n')
        print('C5_JOURNEY_FAILED '+json.dumps({'source':p.source,'stage':p.stage,'failure_type':type(error).__name__,'controls_completed':len(p.controls),'diagnostic':result['diagnostic']}))
        return 2


if __name__=='__main__':raise SystemExit(main())
