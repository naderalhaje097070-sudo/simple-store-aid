"""Actual collection UI -> SDK/Auth/RPC -> stored rows; no credential artifacts."""
import functools
import http.server
import json
from pathlib import Path
import threading
from playwright.sync_api import sync_playwright

def run(probe, a, customer):
    out=Path('/tmp/monjez-c5sale/browser')
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self,*_): pass
    server=http.server.ThreadingHTTPServer(('127.0.0.1',54323),functools.partial(Quiet,directory=str(out)))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    origin='http://127.0.0.1:54323'
    receipts=[]
    try:
        with sync_playwright() as playwright:
            browser=playwright.chromium.launch(headless=True)
            for label,width in [('desktop',1280),('mobile',390)]:
                oid=probe.order(a,probe.seed_product(a),1,0,customer)
                context=browser.new_context(viewport={'width':width,'height':900})
                config={'url':probe.base,'anon':probe.anon,'tenant':a['tenant'],'order':oid,'token':a['token'],'refresh':a['refresh']}
                context.add_init_script('window.collectionFixture='+json.dumps(config))
                page=context.new_page();external=[];errors=[]
                page.on('pageerror',lambda error:errors.append(type(error).__name__))
                def route(r):
                    if r.request.url.startswith((origin+'/',probe.base+'/')):r.continue_()
                    else: external.append('rejected');r.abort()
                page.route('**/*',route)
                page.goto(origin)
                page.get_by_role('button',name='تحصيل دفعة',exact=True).click()
                page.get_by_placeholder('المبلغ',exact=True).fill('20')
                page.get_by_role('button',name='تأكيد التحصيل',exact=True).click()
                page.wait_for_function('window.collectionReplies.length>0')
                first=page.evaluate('window.collectionCalls')
                probe.control(label+'_real_UI_hidden_success',len(first)==1 and first[0]['p_amount']==20 and probe.effect(oid)['paid']==20 and probe.effect(oid)['payment_count']==1)
                page.reload()
                recovery=page.get_by_role('button',name='استعادة التحصيل المحفوظ',exact=True)
                recovery.wait_for()
                page.evaluate('window.collectionDrop=false')
                recovery.click()
                page.wait_for_function('window.collectionReplies.length>0')
                recovery.wait_for(state='hidden')
                retry=page.evaluate('window.collectionCalls')
                probe.control(label+'_reload_exact_same_key_single_stored_effect',retry==first and probe.effect(oid)['paid']==20 and probe.effect(oid)['payment_count']==1)
                page.wait_for_function('document.querySelector("#paid").textContent==="20"')
                page.get_by_role('button',name='تحصيل دفعة',exact=True).click()
                page.get_by_placeholder('المبلغ',exact=True).fill('20')
                page.get_by_role('button',name='تأكيد التحصيل',exact=True).click()
                page.wait_for_function('document.querySelector("#paid").textContent==="40"')
                calls=page.evaluate('window.collectionCalls')
                probe.control(label+'_intentional_equal_second_payment_new_key',len(calls)==2 and calls[1]['p_idempotency_key']!=first[0]['p_idempotency_key'] and probe.effect(oid)['paid']==40 and probe.effect(oid)['payment_count']==2)
                probe.control(label+'_browser_no_external_or_script_error',external==[] and errors==[])
                receipts.append({'viewport':label,'actual_collection_components_SDK_Auth_RPC_DB':True,'hidden_reply_reload_one_effect':True,'second_genuine_payment':True,'external_requests':0})
                context.close()
            browser.close()
    finally:server.shutdown();server.server_close()
    return receipts
