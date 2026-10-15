"""Actual installed DOMPurify in Chromium; all browser networking intercepted offline."""
import asyncio
import hashlib
import json
from pathlib import Path
import re
import sys
from playwright.async_api import async_playwright

OUT = Path('evidence/g0-dompurify')
OUT.mkdir(parents=True, exist_ok=True)
EXPECTED = {'c2j3-custom-regex', 'c2j3-custom-function',
            '55q2-detach-beforeSanitizeElements', '55q2-detach-uponSanitizeElement',
            '6688-rawtext-return-reparse'}
FONT = 'https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;800&display=swap'


async def main():
    baseline = sys.argv[1] == 'baseline'
    violations, stubs = [], []
    bundle = OUT / 'pdf-bundle.js'
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=['--disable-background-networking'])
        context = await browser.new_context(service_workers='block', accept_downloads=True)
        async def route_http(route):
            req = route.request
            if req.method == 'GET' and req.url == 'http://127.0.0.1:19871/':
                await route.fulfill(status=200, content_type='text/html', body='<html lang="ar"><body></body></html>')
            elif not baseline and req.method == 'GET' and req.url == 'http://127.0.0.1:19871/invoice.js':
                await route.fulfill(status=200, content_type='text/javascript', body=bundle.read_bytes())
            elif req.method == 'GET' and req.url == FONT and req.resource_type == 'stylesheet' and not req.is_navigation_request():
                stubs.append('exact-cairo-css-offline')
                await route.fulfill(status=200, content_type='text/css', body='/* offline fallback fonts */')
            else:
                violations.append({'type': req.resource_type, 'method': req.method, 'code': 'unexpected-http'})
                await route.abort('blockedbyclient')
        async def route_ws(socket):
            violations.append({'code': 'websocket-blocked'})
            await socket.close(code=1008, reason='offline fixture')
        await context.route('**/*', route_http)
        await context.route_web_socket('**/*', route_ws)
        page = await context.new_page()
        await page.goto('http://127.0.0.1:19871/')
        dist = Path('node_modules/dompurify/dist/purify.js')
        assert dist.is_file(), 'Optional DOMPurify absent: cannot pass'
        await page.add_script_tag(path=str(dist))
        report = await page.evaluate(Path('tests/g0-dompurify/browser-cases.js').read_text())
        report.update(browser=browser.version, baseline_control=baseline,
                      dist_sha256=hashlib.sha256(dist.read_bytes()).hexdigest())
        failed = {r['name'] for r in report['results'] if not r['pass']}
        report['failed'] = sorted(failed)
        report['passed'] = len(report['results']) - len(failed)
        report['total'] = len(report['results'])
        (OUT / 'browser-contracts.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
        print(json.dumps(report, ensure_ascii=False))
        assert report['total'] == 10
        if baseline:
            assert report['version'] == '3.4.11' and failed == EXPECTED, report
        else:
            assert report['version'] == '3.4.16' and not failed, report
            await page.add_script_tag(url='http://127.0.0.1:19871/invoice.js')
            async with page.expect_download(timeout=30000) as info:
                await page.evaluate('window.runLocalInvoice()')
            download = await info.value
            assert download.suggested_filename == 'mongezz-invoice-00017.pdf'
            pdf_path = OUT / 'synthetic-invoice.pdf'
            await download.save_as(pdf_path)
            pdf = pdf_path.read_bytes()
            assert pdf.startswith(b'%PDF-') and pdf.rstrip().endswith(b'%%EOF')
            pages = len(re.findall(rb'/Type /Page\b', pdf))
            images = len(re.findall(rb'/Subtype /Image\b', pdf))
            assert pages >= 1 and images >= 1 and len(pdf) > 5000
            assert await page.locator('iframe').count() == 0
            assert stubs, 'Expected exact invoice font dependency was not intercepted'
            await page.screenshot(path=str(OUT / 'browser-after-export.png'))
            (OUT / 'pdf-summary.json').write_text(json.dumps({
                'entry': 'src/lib/invoice-pdf.ts:downloadInvoicePdf unchanged',
                'filename': download.suggested_filename, 'bytes': len(pdf), 'pages': pages,
                'images': images, 'sha256': hashlib.sha256(pdf).hexdigest(),
                'iframe_cleanup': True, 'offline_font_stubs': len(stubs),
                'financial_or_database_writes': 0, 'font_parity': 'fallback only; no external Cairo download',
            }, indent=2)+'\n')
        (OUT / 'network.json').write_text(json.dumps({'violations': violations, 'font_stubs': stubs,
            'all_http_fulfilled_or_aborted_no_fetch_continue': True, 'service_workers': 'blocked',
            'websockets': 'intercepted before page creation'}, indent=2)+'\n')
        assert not violations, violations
        await context.close()
        await browser.close()


asyncio.run(main())
