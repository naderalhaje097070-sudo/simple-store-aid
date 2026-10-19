"""Actual React app with synthetic query/mutation transport; no backend or provider."""
import asyncio
import json
from pathlib import Path
import sys
from playwright.async_api import async_playwright, expect


async def main():
    out = Path(sys.argv[1])
    results, requests, errors = [], [], []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--disable-background-networking"])
        context = await browser.new_context(service_workers="block")

        async def reject_http(route):
            requests.append(route.request.url)
            await route.abort("blockedbyclient")

        async def reject_ws(socket):
            requests.append(socket.url)
            await socket.close()

        await context.route("**/*", reject_http)
        await context.route_web_socket("**/*", reject_ws)
        page = await context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        await page.set_content('<html lang="ar"><meta charset="utf-8"><div id="root"></div></html>')
        await page.add_script_tag(path=str(out / "bundle.js"))

        async def reset(spec=None):
            await page.evaluate("spec => window.fixture.reset(spec)", spec or {})

        async def update(spec):
            await page.evaluate("spec => window.fixture.update(spec)", spec)

        async def check(name, run):
            try:
                await run()
                results.append({"name": name, "passed": True})
            except Exception as error:
                results.append({"name": name, "passed": False, "error": str(error)})

        async def initial():
            await reset({"reads": {k: "missing" for k in ["invoices", "payments", "expenses"]}})
            await expect(page.get_by_text("الملخص المالي غير مكتمل", exact=True)).to_be_visible()
            await expect(page.get_by_text("وضعك اليوم: جيد", exact=True)).to_have_count(0)

        async def cached_debt():
            await reset({"screen": "debts"})
            await update({"reads": {"invoices": "cached-error"}})
            await expect(page.get_by_text("تعذّر تحميل البيانات المالية", exact=True)).to_be_visible()
            assert await page.get_by_text("60", exact=True).count() > 0

        async def empty():
            await reset({"screen": "debts", "empty": True})
            await expect(page.get_by_text("لا ديون مستحقة — ممتاز 👍", exact=True)).to_be_visible()
            await update({"reads": {"invoices": "cached-error"}})
            await expect(page.get_by_text("لا ديون مستحقة — ممتاز 👍", exact=True)).to_have_count(0)

        async def modal():
            await reset()
            await page.get_by_role("button", name="عرض حركة اليوم المالية", exact=False).click()
            await update({"reads": {"payments": "cached-error"}})
            sheet = page.locator("div.fixed.inset-0.z-50")
            await expect(sheet.get_by_text("تعذّر تحميل البيانات المالية", exact=True)).to_be_visible()
            await update({"reads": {"payments": "error"}})
            await expect(sheet.get_by_text("المحصّل فعلًا", exact=True)).to_have_count(0)
            await sheet.get_by_role("button", name="الرجوع", exact=True).click()
            await expect(sheet).to_have_count(0)

        async def export_guards():
            await reset()
            await page.evaluate("window.fixture.openInvoice()")
            await update({"reads": {"payments": "error"}})
            for label in ["تحميل PDF", "طباعة"]:
                button = page.get_by_role("button", name=label, exact=True)
                await expect(button).to_be_disabled()
                await button.evaluate("element => element.click()")
            assert await page.evaluate("window.fixture.effects()") == []
            await update({"reads": {"payments": "ready"}})
            await page.get_by_role("button", name="تحميل PDF", exact=True).click()
            await page.get_by_role("button", name="طباعة", exact=True).click()
            assert await page.evaluate("window.fixture.effects().map(x => x[0])") == ["pdf", "print"]

        async def collect_sheet():
            await reset()
            await page.evaluate("window.fixture.openInvoice()")
            await page.get_by_role("button", name="تحصيل دفعة", exact=True).click()
            await page.get_by_placeholder("المبلغ", exact=True).fill("1")
            await update({"reads": {"invoices": "cached-error"}})
            sheet = page.locator("div.fixed.inset-0.z-50")
            await expect(sheet.get_by_text("تعذّر تحميل البيانات المالية", exact=True)).to_be_visible()
            button = sheet.get_by_role("button", name="تأكيد التحصيل", exact=True)
            await expect(button).to_be_disabled()
            await button.evaluate("element => element.click()")
            assert await page.evaluate("window.fixture.effects()") == []
            await update({"reads": {"invoices": "ready"}})
            await button.click()
            assert await page.evaluate("window.fixture.effects()[0][0]") == "useCollectDebt"

        async def directory():
            await reset({"screen": "customers", "reads": {"invoices": "error"}})
            await expect(page.get_by_text("عميل تجريبي", exact=True)).to_be_visible()
            await expect(page.get_by_role("button", name="لا دين", exact=True)).to_be_disabled()
            await expect(page.get_by_text("الرصيد غير مؤكد", exact=True)).to_be_visible()

        for name, run in [("initial unavailable", initial), ("cache survives refetch failure", cached_debt),
                          ("empty success versus failed cache", empty), ("warning inside closable financial sheet", modal),
                          ("export rejected then recovers", export_guards), ("collection sheet rejects stale balance then recovers", collect_sheet),
                          ("directory survives unavailable balance", directory)]:
            await check(name, run)
        results.append({"name": "no browser errors or network requests", "passed": not errors and not requests,
                        "errors": errors, "requests": requests})
        await browser.close()
    (out / "browser.json").write_text(json.dumps({"results": results,
        "passed": sum(r["passed"] for r in results), "total": len(results),
        "scope": "Real React/Chromium UI; synthetic hooks/PDF/mutations, no server finance or provider"}, ensure_ascii=False, indent=2))
    if not all(r["passed"] for r in results):
        raise SystemExit(1)


asyncio.run(main())
