import functools
import http.server
import json
from pathlib import Path
import re
import sys
import threading
from playwright.sync_api import expect, sync_playwright

out = Path(sys.argv[1]).resolve()
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet,directory=str(out)))
threading.Thread(target=server.serve_forever,daemon=True).start()
origin = 'http://127.0.0.1:' + str(server.server_port)
results = []
TRACE = """() => {
  if (window.__qtraceInstalled) return; window.__qtraceInstalled = true; window.__qtrace = [];
  const t0 = performance.now(); const log = (kind, extra) => window.__qtrace.push(
    {t: Math.round(performance.now() - t0), kind, ...extra});
  const desc = Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value');
  Object.defineProperty(HTMLInputElement.prototype, 'value', {configurable: true,
    get() { return desc.get.call(this); },
    set(v) { if (this.getAttribute('aria-label') === 'الكمية') log('set', {v: String(v),
      stack: (new Error().stack || '').split('\\n').slice(2, 7).map(s => s.trim())});
      return desc.set.call(this, v); }});
  for (const type of ['focusin', 'focusout', 'input', 'change', 'keydown', 'pointerdown', 'pointerup', 'click'])
    document.addEventListener(type, (e) => log(type, {target: (e.target.getAttribute && e.target.getAttribute('aria-label')) || e.target.tagName,
      value: e.target.value, key: e.key}), true);
  new MutationObserver((ms) => ms.forEach((m) => { for (const n of [...m.addedNodes, ...m.removedNodes])
    if (n.querySelector && n.querySelector('input[aria-label="الكمية"]')) log(m.addedNodes.length ? 'mount' : 'unmount', {}); }))
    .observe(document.body, {childList: true, subtree: true});
}"""
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for label,width in [('desktop',1280),('mobile',390)]:
        for screen in ['sale_quick','sale']:
            context = browser.new_context(viewport={'width':width,'height':900})
            page = context.new_page(); external=[]; errors=[]
            page.on('pageerror',lambda error:errors.append(str(error)))
            page.route('**/*',lambda route:route.continue_() if route.request.url.startswith(origin+'/') else (external.append(route.request.url),route.abort()))
            page.goto(origin+'/#'+screen)
            page.evaluate(TRACE)
            page.get_by_text('صنف تجريبي',exact=True).first.click()
            quantity=page.get_by_role('textbox',name='الكمية',exact=True)
            # Precondition a person sees before typing: the added line shows its
            # initial quantity. Then confirm the typed value was kept before
            # checkout. The wire assertions below are unchanged.
            expect(quantity).to_have_value('1')
            quantity.fill('0.25');quantity.press('Tab')
            try:
                expect(quantity).to_have_value('0.25')
            except AssertionError:
                print('C4_QUANTITY_TRACE '+json.dumps({'label':label,'screen':screen,'trace':page.evaluate('window.__qtrace')},ensure_ascii=False))
                raise
            if screen=='sale':
                page.get_by_role('button',name='إتمام البيع',exact=True).click()
                page.get_by_role('button',name='حفظ الفاتورة',exact=True).click()
                page.get_by_role('alert').filter(has_text='لم تتأكد نتيجة الحفظ').wait_for()
            else:
                page.get_by_role('button',name=re.compile('إصدار الفاتورة')).click()
            recovery=page.get_by_role('button',name='استعادة البيع المحفوظ',exact=True)
            recovery.wait_for()
            # Recovery is rendered by the durable-save event before the async RPC
            # is dispatched. Observe the transport, not that earlier UI event.
            page.wait_for_function('JSON.parse(localStorage.getItem("fixtureCalls") || "[]").length >= 1')
            first=page.evaluate('JSON.parse(localStorage.getItem("fixtureCalls"))')
            assert len(first)==1 and first[0]['p_items'][0]['qty']==0.25 and first[0]['p_paid']==3.13, {'viewport':label,'screen':screen,'actual_first_calls':first}
            key=first[0]['p_idempotency_key']
            page.reload();recovery.wait_for()
            # Sign-in transition hides another actor's record without deleting it.
            page.evaluate('window.fixtureSwitch("44444444-4444-4444-8444-444444444444")')
            recovery.wait_for(state='hidden')
            page.evaluate('window.fixtureSwitch("11111111-1111-4111-8111-111111111111")')
            recovery.wait_for()
            page.evaluate('sessionStorage.setItem("fixtureMode","success")')
            recovery.click()
            page.wait_for_function('document.querySelector("#opened").textContent.length>0')
            calls=page.evaluate('JSON.parse(localStorage.getItem("fixtureCalls"))')
            assert len(calls)==2 and calls[1]==first[0] and calls[1]['p_idempotency_key']==key
            assert page.evaluate('Object.keys(JSON.parse(localStorage.getItem("fixtureEffects"))).length')==1
            assert errors==[] and external==[]
            page.screenshot(path=str(out/(label+'-'+screen+'.png')),full_page=True)
            results.append({'viewport':label,'screen':screen,'fraction_and_cents_wire':True,'actual_hook_and_recovery_components':True,'reload_retains_UUID':True,'actor_switch_hides_and_preserves_record':True,'retry_exact_request':True,'modeled_effects':1,'external_requests':0})
            context.close()
    browser.close()
server.shutdown()
(out/'browser.json').write_text(json.dumps({'cases':results,'transport':'recording synthetic RPC; native stored test separate','database_calls':0},indent=2)+'\n')
print('C4_BROWSER_CASES='+str(len(results)))
