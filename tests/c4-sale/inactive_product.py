"""Sale screens must not offer an inactive product (database-free fixture).

The database rejects selling an inactive product (product_inactive); before this
check the quick and full sale screens still listed it.
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
        for screen in ('sale_quick', 'sale'):
            page = browser.new_context(viewport={'width': width, 'height': 900}).new_page()
            errors = []
            page.on('pageerror', lambda error: errors.append(str(error)))
            page.route('**/*', lambda route: route.continue_() if route.request.url.startswith(origin + '/') else route.abort())
            page.goto(origin + '/#' + screen)
            expect(page.get_by_text('صنف تجريبي', exact=True).first).to_be_visible()
            if screen == 'sale':
                # The full sale screen lists products after the search is focused.
                search = page.get_by_role('textbox').first
                search.click()
                expect(page.get_by_text('صنف تجريبي', exact=True).first).to_be_visible()
            assert page.get_by_text('صنف موقوف', exact=True).count() == 0, screen + ': inactive product offered'
            assert errors == [], errors
            page.context.close()
            cases += 1
    browser.close()
print(f'C4_INACTIVE_PRODUCT_CASES={cases}')
assert cases == 4
