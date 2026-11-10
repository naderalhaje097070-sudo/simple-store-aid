"""Quick sale's delayed search autofocus must not steal focus from a field the
person is already using (deterministic, browser clock controlled).

CI trace (run 42807331130): the 60 ms search autofocus fired after the test had
entered the quantity field, so the typed 0.25 went into the search box.
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
cases = 0
with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True)
    for width in (1280, 390):
        page = browser.new_context(viewport={'width': width, 'height': 900}).new_page()
        page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
        page.clock.install(time=1_800_000_000_000)
        page.clock.pause_at(1_800_000_000_100)    # timers advance only when the test says so
        page.goto(origin + '/#sale_quick')
        page.get_by_text('صنف تجريبي', exact=True).first.click()
        quantity = page.get_by_role('textbox', name='الكمية', exact=True)
        expect(quantity).to_have_value('1')
        quantity.focus()                          # the person is already in the quantity field
        page.clock.run_for(200)                   # now the 60 ms search autofocus timer fires
        assert page.evaluate("document.activeElement?.getAttribute('aria-label')") == 'الكمية', 'focus stolen'
        page.keyboard.press('Control+A'); page.keyboard.type('0.25'); page.keyboard.press('Tab')
        expect(quantity).to_have_value('0.25')
        page.context.close()
        cases += 1
    # With nothing focused, the search field still receives the autofocus.
    page = browser.new_context(viewport={'width': 390, 'height': 900}).new_page()
    page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
    page.clock.install(time=1_800_000_000_000); page.clock.pause_at(1_800_000_000_100)
    page.goto(origin + '/#sale_quick'); page.clock.run_for(200)
    assert page.evaluate("document.activeElement?.tagName") == 'INPUT' and page.evaluate("document.activeElement?.getAttribute('aria-label')") != 'الكمية', 'search autofocus lost'
    page.context.close(); cases += 1
    browser.close()
print(f'C4_AUTOFOCUS_RACE_CASES={cases}')
assert cases == 3
