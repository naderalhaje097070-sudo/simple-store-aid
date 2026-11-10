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
            page.get_by_text('صنف تجريبي', exact=True).first.click()
            quantity = page.get_by_role('textbox', name='الكمية', exact=True)
            plus = quantity.locator('xpath=../following-sibling::button[1]')
            expect(quantity).to_have_value('1')
            quantity.fill('0.25'); quantity.press('Tab')
            expect(quantity).to_have_value('0.25')
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
