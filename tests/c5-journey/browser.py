"""Actual application component, real Query/SDK/Auth/RPC and independent DB oracles."""
import functools
import http.server
import json
from pathlib import Path
import re
import threading
import uuid
from playwright.sync_api import sync_playwright

SALE = 'create_sale_with_items_idempotent'
COLLECT = 'collect_order_debt_idempotent'


def run(p, state, private):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',4173),functools.partial(Quiet,directory='/tmp/monjez-c5sale/browser'))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:4173'
    receipts=[]
    try:
        with sync_playwright() as pw:
            browser=pw.chromium.launch(headless=True)
            for label,width in [('desktop',1280),('mobile',390)]:
                p.stage=label+'_setup'
                actor=p.fixture('Journey_'+label)
                state['actors'][label]=actor;p.save(private,state)
                pid=p.seed_product(actor)
                customer,courier=p.customer_courier(actor)
                p.sql(f"update public.customers set name='Journey customer' where id='{customer}'; update public.couriers set name='Journey courier' where id='{courier}';")
                context=browser.new_context(viewport={'width':width,'height':900})
                context.add_init_script('window.journeyFixture='+json.dumps({'url':p.base,'anon':p.anon,'token':actor['token'],'refresh':actor['refresh']}))
                page=context.new_page();errors=[];external=[]
                page.set_default_timeout(20000)
                page.on('pageerror',lambda e:errors.append(type(e).__name__))
                def route(r):
                    if r.request.url.startswith((origin+'/',p.base+'/')):r.continue_()
                    else:external.append('rejected');r.abort()
                page.route('**/*',route)
                page.goto(origin);page.wait_for_function('window.journeyReady===true')

                def control(name,ok,**details):p.control(label+'_'+name,ok,**details)
                def checkpoint(step):
                    p.stage=label+'_'+step;p.journey_diagnostic={}
                    sale_calls=page.evaluate('(rpc)=>(window.journeyCalls||[]).filter(c=>c.rpc===rpc).map(c=>({status:c.status,complete:c.result!==undefined}))',SALE)
                    p.journey_diagnostic={
                        'quantity_inputs':page.get_by_role('textbox',name='الكمية',exact=True).count(),
                        'quick_checkout_buttons':page.get_by_role('button',name=re.compile('إصدار الفاتورة')).count(),
                        'advanced_checkout_buttons':page.get_by_role('button',name='إتمام البيع',exact=True).count(),
                        'sale_recovery_buttons':page.get_by_role('button',name='استعادة البيع المحفوظ',exact=True).count(),
                        'sale_rpc_calls':len(sale_calls),'sale_rpc_completed':sum(c['complete'] for c in sale_calls),
                        'sale_rpc_http200':sum(c['status']==200 for c in sale_calls),
                        'page_errors':len(errors),'blocked_external':len(external)}
                def click(name,exact=True):
                    matches=page.get_by_role('button',name=name,exact=exact)
                    for i in range(matches.count()):
                        item=matches.nth(i)
                        if item.is_visible():item.click();return
                    # Wait for pending Query rendering, then retry the same locator.
                    matches.first.wait_for(state='visible');matches.first.click()
                def home():
                    if page.get_by_role('button',name='عودة للرئيسية',exact=True).count():click('عودة للرئيسية')
                    else:click('الرئيسية')
                    page.get_by_text('إجراءات سريعة',exact=True).wait_for()
                def calls(rpc):return page.evaluate('(rpc)=>window.journeyCalls.filter(c=>c.rpc===rpc)',rpc)
                def completed(rpc,before):
                    page.wait_for_function('([rpc,n])=>window.journeyCalls.filter(c=>c.rpc===rpc&&c.status!==null&&c.result!==undefined).length>n',arg=[rpc,before])
                    values=calls(rpc);control(rpc+'_success',values[-1]['status']==200)
                    return values[-1]
                def invoice(oid):
                    home();click('الفواتير')
                    number=p.query(f"select to_jsonb(coalesce(tenant_number::text,number::text)) from public.orders where id='{oid}';")
                    page.get_by_role('button').filter(has=page.get_by_text('#'+number,exact=True)).last.click()
                    page.get_by_role('heading',name='فاتورة #'+number,exact=True).wait_for()
                def collect(oid,amount,drop=False):
                    p.stage=label+'_collect'
                    invoice(oid)
                    if drop:page.evaluate('(rpc)=>window.journeyDrop[rpc]=1',COLLECT)
                    click('تحصيل دفعة');page.get_by_placeholder('المبلغ',exact=True).fill(str(amount))
                    before=len(calls(COLLECT));click('تأكيد التحصيل');return completed(COLLECT,before)
                def start_sale(qty,advanced=False,courier_sale=False):
                    checkpoint('sale_home')
                    if page.get_by_role('button',name='عودة للرئيسية',exact=True).count():home()
                    elif not page.get_by_text('إجراءات سريعة',exact=True).count():home()
                    checkpoint('sale_open');click(re.compile('فاتورة جديدة'))
                    checkpoint('sale_product_wait')
                    page.get_by_text('C2 dummy',exact=True).first.wait_for()
                    control('foreign_nonempty_product_hidden',page.get_by_text('Journey foreign canary',exact=True).count()==0)
                    checkpoint('sale_product_add');page.get_by_text('C2 dummy',exact=True).first.click()
                    if advanced:
                        checkpoint('sale_advanced_open');click('بيع متقدم');page.get_by_text('C2 dummy',exact=True).first.click()
                    field=page.get_by_role('textbox',name='الكمية',exact=True)
                    checkpoint('sale_quantity_fill');field.fill(str(qty))
                    checkpoint('sale_quantity_commit');field.press('Tab')
                    if advanced:
                        checkpoint('sale_advanced_checkout')
                        click('إتمام البيع');click('دين')
                        if courier_sale:click('عبر مندوب')
                        click('اختر عميلًا — لا يمكن تسجيل متبقٍّ دون عميل')
                        click('Journey customer')
                        if courier_sale:click('Journey courier')
                        before=len(calls(SALE));click('حفظ الفاتورة')
                    else:
                        checkpoint('sale_quick_checkout')
                        before=len(calls(SALE));click(re.compile('إصدار الفاتورة'))
                    checkpoint('sale_rpc_wait')
                    call=completed(SALE,before)
                    oid=str(uuid.UUID(call['result']['order_id']))
                    if advanced:
                        checkpoint('sale_success_wait');page.get_by_text('تم حفظ الفاتورة',exact=True).wait_for()
                    return oid,call
                def custody():
                    home()
                    nav=page.get_by_role('button',name='عهدة المندوب',exact=True)
                    if any(nav.nth(i).is_visible() for i in range(nav.count())):click('عهدة المندوب')
                    else:click(re.compile('طلبات توصيل غير مكتملة'))
                    page.get_by_role('heading',name='عهدة المندوب',exact=True).wait_for()
                def ui_row(label_text,expected):
                    row=page.get_by_text(label_text,exact=True).locator('..').locator('..')
                    row.locator('.num').filter(has_text=re.compile('^'+str(expected)+'$')).first.wait_for()
                    nums=row.locator('.num').all_text_contents()
                    control('display_'+label_text.replace(' ','_'),str(expected) in [v.replace(',','').strip() for v in nums],expected=expected)
                def day(collected,debt,custody_value,close=False):
                    p.stage=label+'_day_close'
                    home();click(re.compile('إقفال اليوم'))
                    page.get_by_role('heading',name='إقفال اليوم',exact=True).wait_for()
                    ui_row('دخل فعلًا اليوم',collected);ui_row('ديون لم تُحصّل',debt);ui_row('عند المندوب (لم تُسوَّ)',custody_value)
                    if close:
                        ui_row('مصروفات اليوم',5);ui_row('صافي الكاش اليوم',220)
                        before=len(calls('close_day'));click('تثبيت إقفال اليوم');completed('close_day',before)

                page.get_by_text('إجراءات سريعة',exact=True).wait_for()
                page.evaluate('(rpc)=>window.journeyDrop[rpc]=1',SALE)
                quick,first=start_sale(.25)
                control('quarter_first_committed_cash_stock',p.effect(quick)=={'total':25,'paid':25,'payment_count':1,'payment_sum':25,'debt_payment_count':0,'debt_payment_sum':0} and p.stock(pid)==9.75)
                checkpoint('sale_recovery_wait');page.get_by_role('button',name='استعادة البيع المحفوظ',exact=True).wait_for()
                page.reload();page.wait_for_function('window.journeyReady===true')
                page.get_by_role('button',name='استعادة البيع المحفوظ',exact=True).wait_for()
                n=len(calls(SALE));click('استعادة البيع المحفوظ');replay=completed(SALE,n)
                control('quarter_reload_same_key_payload_actor_one_effect',replay['payload']==first['payload'] and p.stock(pid)==9.75 and p.query(f"select count(*) from public.financial_idempotency where operation='sale.create.v2' and idempotency_key='{first['payload']['p_idempotency_key']}' and created_by='{actor['uid']}';")==1 and p.effect(quick)['payment_count']==1)
                debt,_=start_sale(1,advanced=True)
                lost=collect(debt,20,True)
                control('partial_collection_first_committed',p.effect(debt)['paid']==20 and p.effect(debt)['payment_count']==1)
                page.get_by_role('button',name='استعادة التحصيل المحفوظ',exact=True).wait_for()
                page.reload();page.wait_for_function('window.journeyReady===true')
                page.get_by_role('button',name='استعادة التحصيل المحفوظ',exact=True).wait_for()
                n=len(calls(COLLECT));click('استعادة التحصيل المحفوظ');again=completed(COLLECT,n)
                control('partial_reload_same_key_payload_one_effect',again['payload']==lost['payload'] and p.effect(debt)['paid']==20 and p.effect(debt)['payment_count']==1)
                collect(debt,80)
                control('full_collection_after_partial',p.effect(debt)=={'total':100,'paid':100,'payment_count':2,'payment_sum':100,'debt_payment_count':2,'debt_payment_sum':100})
                carried,_=start_sale(1,advanced=True,courier_sale=True)
                custody();click('تحديث حالة التسليم ←');click('سُلِّمت جزئيًا');page.get_by_placeholder('0',exact=True).fill('40')
                n=len(calls('update_courier_order_state'));click('تأكيد');completed('update_courier_order_state',n)
                control('delivery_not_cash',p.courier_effect(carried)=={'total':100,'paid':0,'status':'debt','delivery':'courier','state':'delivered_partial','custody':40,'unassigned':False,'payments':0,'cash':0})
                day(125,60,40)
                home();click('تسوية مندوب');page.get_by_role('button',name='تأكيد التسوية',exact=True).wait_for()
                n=len(calls('settle_courier_orders'));click('تأكيد التسوية');completed('settle_courier_orders',n)
                control('settlement_cash_once',p.courier_effect(carried)=={'total':100,'paid':40,'status':'partial','delivery':'direct','state':None,'custody':0,'unassigned':True,'payments':1,'cash':40})
                day(165,60,0)
                collect(carried,60);control('courier_remaining_full',p.effect(carried)['paid']==100 and p.effect(carried)['payment_count']==2)
                returned,_=start_sale(.5,advanced=True,courier_sale=True)
                control('half_stock_reserved',p.stock(pid)==7.25)
                custody();click('تحديث حالة التسليم ←');click('أُرجعت')
                n=len(calls('update_courier_order_state'));click('تأكيد');returned_call=completed('update_courier_order_state',n)
                control('return_UI_uses_existing_courier_adapter',returned_call['payload']['p_state']=='returned')
                control('return_exact_stock_no_cash_debt_custody',p.stock(pid)==7.75 and p.courier_effect(returned)=={'total':50,'paid':0,'status':'debt','delivery':'direct','state':'returned','custody':0,'unassigned':True,'payments':0,'cash':0})
                p.stage=label+'_expense'
                home();click('إضافة مصروف')
                page.get_by_placeholder('0',exact=True).fill('5')
                page.get_by_placeholder('مثال: نقل',exact=True).fill('Journey expense')
                click('حفظ المصروف');page.get_by_text('تم تسجيل المصروف',exact=True).wait_for()
                control('real_UI_expense_stored',p.query(f"select coalesce(sum(amount),0) from public.expenses where tenant_id='{actor['tenant']}';")==5)
                click('عرض حركة اليوم المالية (الكاش، الديون، العهدة)')
                ui_row('بعت (قيمة الفواتير)',275);ui_row('المحصّل فعلًا',225);ui_row('المصروفات',5);ui_row('صافي الكاش',220)
                click('الربح في شاشة مستقلة ←')
                profit=page.get_by_text('ربح تقديري',exact=True).locator('..').locator('.num').first
                profit.filter(has_text=re.compile('^130$')).wait_for()
                control('actual_profit_display_after_expense',profit.inner_text().strip()=='130')
                day(225,0,0,True)
                observed=p.query(f"select jsonb_build_object('sales',sales,'collected',collected,'expenses',expenses,'realized_profit',realized_profit,'customer_debts',customer_debts,'unsettled_custody',unsettled_custody) from public.day_closes where tenant_id='{actor['tenant']}';")
                expected={'sales':275,'collected':225,'expenses':5,'realized_profit':130,'customer_debts':0,'unsettled_custody':0}
                control('final_day_close_independent_oracle',observed==expected,observed=observed,expected=expected)
                control('browser_no_external_or_script_error',not errors and not external)
                receipts.append({'viewport':label,'actual_application_component':True,'real_Query_SDK_Auth_RPC_DB':True,'stored_final':observed,'stock':7.75,'external_requests':0,'script_errors':0})
                context.close()
            browser.close()
    finally:
        server.shutdown();server.server_close()
    return receipts
