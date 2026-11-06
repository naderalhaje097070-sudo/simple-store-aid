"""Actual SQL/API/history evidence for the adopted additive reporting contract."""
import json
import subprocess
from live_probe import _psql_command, _psql_env

VIEW='day_close_profit_report'
FIELDS='realized_profit,realized_margin_before_expenses,expenses,realized_net_profit'

def raw_close(p,tenant):
    return p.query(f"select to_jsonb(t) from public.day_closes t where tenant_id='{tenant}' order by closed_for desc limit 1;")

def seed55(p,private):
    state=p.actors_state(private);a=state['actors']['b']
    customer,_=p.customer_courier(a);oid=p.order(a,p.seed_product(a),1,0,customer)
    code,_=p.collect(a,oid,20)
    p.control('prior55_keyed_collection_seed',code==200 and p.effect(oid)['paid']==20)
    p.sql(f"insert into public.expenses(tenant_id,type,amount,method,created_by) values ('{a['tenant']}','profit-upgrade',5,'cash','{a['uid']}');")
    code,result=p.rpc(a,'close_day',{'p_note':'saved55-before-view'})
    p.control('prior55_saved_gross12_expense5',code==200 and result.get('realized_profit')==12 and result.get('expenses')==5)
    state['profit_upgrade_close']=raw_close(p,a['tenant'])
    state['upgrade_snapshot']=p.snapshot();state['upgrade_checks']=p.controls
    p.save(private,state)
    return {'source_sha':p.source,'phase':'seed55','controls':p.controls}

def projection(p,tenant):
    return p.query(f"select jsonb_build_object('gross',realized_profit,'alias',realized_margin_before_expenses,'expense',expenses,'net',realized_net_profit) from public.{VIEW} where tenant_id='{tenant}' order by closed_for desc limit 1;")

def role_query(p,actor,expression,role='authenticated'):
    subject=f"set local request.jwt.claim.sub='{actor['uid']}';" if actor else ''
    return p.query(f'begin; set local role {role}; {subject} {expression} rollback;')

def sql_write_denied(p,actor,statement):
    sql=f"begin; set local role authenticated; set local request.jwt.claim.sub='{actor['uid']}'; {statement}; rollback;"
    r=subprocess.run(_psql_command(p.config,'-Atq','-v','ON_ERROR_STOP=1','-v','VERBOSITY=sqlstate'),input=sql,capture_output=True,text=True,env=_psql_env(p.config))
    return r.returncode!=0 and '42501' in r.stderr

def run(p,state,private):
    p.stage='profit_contract'
    catalog=p.query(f"select jsonb_build_object('invoker',coalesce('security_invoker=true'=any(reloptions),false),'select',has_table_privilege('authenticated',oid,'SELECT'),'insert',has_table_privilege('authenticated',oid,'INSERT'),'update',has_table_privilege('authenticated',oid,'UPDATE'),'delete',has_table_privilege('authenticated',oid,'DELETE'),'anon',has_table_privilege('anon',oid,'SELECT')) from pg_class where oid='public.{VIEW}'::regclass;")
    p.control('profit_invoker_select_only_catalog',catalog=={'invoker':True,'select':True,'insert':False,'update':False,'delete':False,'anon':False})
    if 'profit_upgrade_close' in state:
        old=state['profit_upgrade_close'];tenant=old['tenant_id']
        p.control('profit_upgrade_exact_old_row_preserved',raw_close(p,tenant)==old)
        p.control('profit_upgrade_old_gross12_net7',projection(p,tenant)=={'gross':12,'alias':12,'expense':5,'net':7})
    owner=p.fixture('profit_owner');state['actors']['profit_owner']=owner;p.save(private,state)
    staff=p.fixture('profit_staff',owner['tenant'],True);state['actors']['profit_staff']=staff;p.save(private,state)
    other=p.fixture('profit_foreign');state['actors']['profit_foreign']=other;p.save(private,state)
    pid=p.seed_product(owner);p.order(owner,pid,2.25,225)
    p.sql(f"insert into public.expenses(tenant_id,type,amount,method,created_by) values ('{owner['tenant']}','profit-contract',5,'cash','{owner['uid']}');")
    code,result=p.rpc(owner,'close_day',{'p_note':'profit-v1'})
    p.control('profit_legacy_RPC_gross135_expense5',code==200 and result.get('realized_profit')==135 and result.get('expenses')==5 and 'realized_net_profit' not in result)
    p.control('profit_raw135_alias135_servernet130',projection(p,owner['tenant'])=={'gross':135,'alias':135,'expense':5,'net':130})
    before=p.snapshot()
    for label,actor in [('owner',owner),('staff',staff),('foreign',other)]:
        code,rows=p.request('GET',f'/rest/v1/{VIEW}?select={FIELDS}&tenant_id=eq.'+owner['tenant'],token=actor['token'])
        expected=[{'realized_profit':135,'realized_margin_before_expenses':135,'expenses':5,'realized_net_profit':130}] if label!='foreign' else []
        p.control('profit_API_'+label,code==200 and rows==expected)
        count=role_query(p,actor,f"select to_jsonb(count(*)) from public.{VIEW} where tenant_id='{owner['tenant']}';")
        p.control('profit_SQL_role_'+label,count==(1 if label!='foreign' else 0))
    code,body=p.request('GET',f'/rest/v1/{VIEW}?select=id')
    p.control('profit_anon_API_denied',code in (401,403) and isinstance(body,dict) and body.get('code')=='42501')
    p.control('profit_anon_SQL_no_privilege',p.query(f"select to_jsonb(has_table_privilege('anon','public.{VIEW}','SELECT'));") is False)
    for method,path,payload,statement in [
        ('POST','',{'tenant_id':owner['tenant'],'closed_for':'2000-01-01'},f"insert into public.{VIEW}(tenant_id,closed_for) values ('{owner['tenant']}','2000-01-01')"),
        ('PATCH','?tenant_id=eq.'+owner['tenant'],{'realized_profit':999},f"update public.{VIEW} set realized_profit=999 where tenant_id='{owner['tenant']}'"),
        ('DELETE','?tenant_id=eq.'+owner['tenant'],None,f"delete from public.{VIEW} where tenant_id='{owner['tenant']}'")]:
        code,body=p.request(method,f'/rest/v1/{VIEW}'+path,payload,token=owner['token'])
        p.control('profit_view_'+method+'_API_denied',code==403 and isinstance(body,dict) and body.get('code')=='42501')
        p.control('profit_view_'+method+'_SQL_denied',sql_write_denied(p,owner,statement))
    p.control('profit_denials_all_base_rows_unchanged',p.snapshot()==before)
    original=raw_close(p,owner['tenant'])
    p.sql(f"update public.payments set created_at=created_at-interval '2 days' where tenant_id='{owner['tenant']}';")
    p.control('profit_old_snapshot_not_rebuilt_from_mutable_payments',raw_close(p,owner['tenant'])==original and projection(p,owner['tenant'])['net']==130)
    # Restore only synthetic payment timestamps for a real reclose/replay check.
    p.sql(f"update public.payments set created_at=now() where tenant_id='{owner['tenant']}';")
    money=p.query(f"select jsonb_build_object('cash',(select sum(amount) from public.payments where tenant_id='{owner['tenant']}'),'stock',(select stock from public.products where id='{pid}'));")
    for n in range(2):
        code,result=p.rpc(owner,'close_day',{'p_note':'profit-v1'})
        p.control('profit_reclose_'+str(n),code==200 and result['realized_profit']==135 and projection(p,owner['tenant'])['net']==130)
    p.control('profit_reclose_cash_stock_unchanged',p.query(f"select jsonb_build_object('cash',(select sum(amount) from public.payments where tenant_id='{owner['tenant']}'),'stock',(select stock from public.products where id='{pid}'));")==money)
    for n,(gross,expense,net) in enumerate([('0','5',-5),('-10','5',-15),('14.37','2.11',12.26)]):
        day=f'2000-01-{n+1:02d}'
        p.sql(f"insert into public.day_closes(tenant_id,closed_for,realized_profit,expenses) values ('{owner['tenant']}','{day}',{gross},{expense});")
        p.control('profit_numeric_vector_'+str(n),p.query(f"select to_jsonb(realized_net_profit) from public.{VIEW} where tenant_id='{owner['tenant']}' and closed_for='{day}';")==net)
    customer,_=p.customer_courier(other)
    old_order=p.order(other,p.seed_product(other),1,50,customer)
    p.sql(f"update public.orders set created_at=created_at-interval '2 days' where id='{old_order}'; insert into public.expenses(tenant_id,type,amount,method,created_by) values ('{other['tenant']}','prior-invoice-payment',5,'cash','{other['uid']}');")
    code,result=p.rpc(other,'close_day',{'p_note':'payment-date-basis'})
    p.control('profit_previous_invoice_payment_today_basis',code==200 and result['sales']==0 and result['collected']==50 and result['realized_profit']==30 and projection(p,other['tenant'])['net']==25)
    p.sql(f"update auth.users set banned_until=now()+interval '1 day' where id='{owner['uid']}';")
    code,rows=p.request('GET',f'/rest/v1/{VIEW}?select=id',token=owner['token'])
    p.control('profit_inactive_old_token_API_no_rows',(code==200 and rows==[]) or (code in (401,403) and isinstance(rows,dict) and rows.get('code') in ('42501','PGRST301','PGRST302')))
    p.control('profit_inactive_SQL_no_rows',role_query(p,owner,f'select to_jsonb(count(*)) from public.{VIEW};')==0)
    p.control('profit_unaffected_staff_still_allowed',role_query(p,staff,f'select to_jsonb(count(*)) from public.{VIEW};')==4)
    return {'controls':'recorded in progress.json','runtime_SQL_API':True,'historical_rows_rewritten_by_migration':False}
