"""QuantityInput regressions on the real sale screens (database-free fixture).

1. Typed fractional quantity survives leaving the field (fill + Tab).
2. Typing then leaving in the same task commits the on-screen text.
3. The +/- step buttons still apply after a typed quantity was committed.
"""
import functools
import http.server
import sys
import threading
from pathlib import Path
from playwright.sync_api import expect, sync_playwright

out = Path(sys.argv[1]).resolve()
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_): pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(out)))
threading.Thread(target=server.serve_forever, daemon=True).start()
origin = 'http://127.0.0.1:' + str(server.server_port)
SAME_TASK_TYPE_AND_LEAVE = """() => {
  const i = document.querySelector('input[aria-label="الكمية"]'); i.focus();
  Object.getOwnPropertyDescriptor(HTMLInputElement.prototype, 'value').set.call(i, '0.5');
  i.dispatchEvent(new Event('input', {bubbles: true})); i.blur();
}"""
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
cases = 0
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for width in (1280, 390):
        for screen in ('sale_quick', 'sale'):
            page = browser.new_context(viewport={'width': width, 'height': 900}).new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            page.goto(origin + '/#' + screen)
            page.evaluate(TRACE)
            page.get_by_text('صنف تجريبي', exact=True).first.click()
            quantity = page.get_by_role('textbox', name='الكمية', exact=True)
            plus = quantity.locator('xpath=../following-sibling::button[1]')
            expect(quantity).to_have_value('1')
            quantity.fill('0.25'); quantity.press('Tab')
            try:
                expect(quantity).to_have_value('0.25')
            except AssertionError:
                import json
                print('C4_QUANTITY_TRACE ' + json.dumps({'width': width, 'screen': screen,
                      'trace': page.evaluate('window.__qtrace')}, ensure_ascii=False))
                raise
            plus.click(); expect(quantity).to_have_value('1.25')
            page.evaluate(SAME_TASK_TYPE_AND_LEAVE)
            expect(quantity).to_have_value('0.5')
            plus.click(); expect(quantity).to_have_value('1.5')
            assert errors == [], errors
            page.context.close()
            cases += 1
    browser.close()
print(f'C4_QUANTITY_INPUT_CASES={cases}')
assert cases == 4
