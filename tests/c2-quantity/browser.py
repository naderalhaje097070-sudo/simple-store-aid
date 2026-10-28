import functools
import http.server
import json
from pathlib import Path
import sys
import threading
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1]).resolve()
class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_):
        pass
server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(out)))
threading.Thread(target=server.serve_forever, daemon=True).start()
origin = 'http://127.0.0.1:' + str(server.server_port)
observations = []
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    for label, width in [('desktop', 1280), ('mobile', 390)]:
        page = browser.new_page(viewport={'width': width, 'height': 900})
        external = []
        def route(r):
            if r.request.url.startswith(origin + '/'):
                r.continue_()
            else:
                external.append(r.request.url)
                r.abort()
        page.route('**/*', route)
        page.goto(origin)
        quantity = page.get_by_role('textbox', name='الكمية', exact=True)
        quantity.fill('0.25')
        page.get_by_role('button', name='خارج الحقل').click()
        assert page.locator('#quantity').inner_text() == '0.25'
        for bad in ['0.001', '3']:
            quantity.fill(bad)
            page.get_by_role('button', name='خارج الحقل').click()
            assert quantity.input_value() == '0.25'
            assert page.locator('#quantity').inner_text() == '0.25'
            assert quantity.get_attribute('aria-invalid') == 'true'
            assert page.get_by_role('alert').inner_text() == 'كمية غير صالحة'
        page.goto(origin + '/index.html#product')
        fields = page.locator('input:not([type=checkbox])')
        fields.nth(0).fill('منتج تجريبي')
        fields.nth(1).fill('100')
        fields.nth(2).fill('40')
        fields.nth(3).fill('1.25')
        page.get_by_role('button', name='حفظ المنتج').click()
        page.wait_for_function('document.querySelector("#saved").textContent.length > 0')
        assert json.loads(page.locator('#saved').inner_text())['stock'] == 1.25
        fields.nth(3).fill('1.001')
        page.get_by_role('button', name='حفظ المنتج').click()
        assert json.loads(page.locator('#saved').inner_text())['stock'] == 1.25
        assert page.get_by_text('أدخل كمية صالحة حتى منزلتين عشريتين', exact=True).is_visible()
        assert external == []
        observations.append({'viewport': label, 'quarter_commit': True, 'invalid_and_excess_stock_rejected': True, 'product_fractional_stock_preserved': True, 'excess_precision_not_saved': True, 'external_requests': 0})
        page.screenshot(path=str(out / (label + '.png')), full_page=True)
        page.close()
    browser.close()
server.shutdown()
(out / 'browser-result.json').write_text(json.dumps({'observations': observations, 'component_fixture_only': True, 'database_calls': 0}, indent=2) + '\n')
print('C2_BROWSER_PASS ' + str(len(observations)))
