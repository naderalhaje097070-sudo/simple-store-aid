"""Synthetic React UI regression; every browser HTTP/WebSocket request is blocked.

Run from repository root after build.ts. No backend, credentials, auth session or SQL.
The original baseline receipt is retained separately; this runner asserts fixed behavior.
"""
import asyncio
import json
import os
from pathlib import Path
import sys
from playwright.async_api import async_playwright

UNAVAILABLE = "بيانات العميل غير متاحة"
LOADING = "جارٍ تحميل بيانات العميل…"


async def main():
    out = Path(sys.argv[1])
    results, violations, errors = [], [], []
    async with async_playwright() as pw:
        options = {"args": ["--disable-background-networking"]}
        if os.environ.get("DEBT_TEST_CHROMIUM"):
            options["executable_path"] = os.environ["DEBT_TEST_CHROMIUM"]
        browser = await pw.chromium.launch(**options)
        context = await browser.new_context(service_workers="block")

        async def reject_http(route):
            violations.append({"kind": "http", "url": route.request.url})
            await route.abort("blockedbyclient")

        async def reject_ws(socket):
            violations.append({"kind": "websocket", "url": socket.url})
            await socket.close()

        await context.route("**/*", reject_http)
        await context.route_web_socket("**/*", reject_ws)
        page = await context.new_page()
        page.on("pageerror", lambda error: errors.append(str(error)))
        await page.set_content('<html lang="ar"><meta charset="utf-8"><div id="root"></div></html>')
        await page.add_script_tag(path=str(out / "bundle.js"))

        async def reset(expression="{}"):
            await page.evaluate(f"window.fixture.reset({expression})")

        async def expect_no_effects():
            assert await page.evaluate("window.effects") == []

        async def expect_sixty(count):
            assert await page.get_by_text("60", exact=True).count() == count
            assert await page.get_by_text("0", exact=True).count() == 0

        async def click_disabled(button):
            assert await button.is_disabled()
            # Native DOM click on a disabled control must not run its callback.
            await button.evaluate("element => element.click()")
            await expect_no_effects()

        async def case(name, check):
            try:
                await check()
                results.append({"name": name, "passed": True})
            except Exception as error:
                results.append({"name": name, "passed": False, "error": str(error)})

        async def unavailable_row():
            await reset()
            row = page.get_by_role("button", name=UNAVAILABLE)
            await expect_sixty(2)  # Independent expected debt: 100 - 40 = 60.
            assert await row.count() == 1
            await click_disabled(row)
            assert await page.get_by_role("heading", name="الديون", exact=True).count() == 1

        async def loading_then_appears():
            await reset("{customersLoading:true}")
            row = page.get_by_role("button", name=LOADING)
            await expect_sixty(2)
            assert await page.get_by_text(UNAVAILABLE, exact=True).count() == 0
            await click_disabled(row)
            await page.evaluate("window.fixture.update({customersLoading:false,customers:[window.fixture.customer]})")
            row = page.get_by_role("button", name="عميل تجريبي")
            assert await row.is_enabled()
            await row.click()
            assert await page.evaluate("window.effects") == [["customer", "customer-fixture"], ["go", "debt_customer"]]
            await expect_sixty(2)
            assert await page.get_by_role("button", name="تحصيل دفعة").is_enabled()

        async def persistent_absence():
            await reset("{customersLoading:true}")
            await page.evaluate("window.fixture.update({customersLoading:false})")
            await expect_sixty(2)
            await click_disabled(page.get_by_role("button", name=UNAVAILABLE))
            assert await page.get_by_text(LOADING, exact=True).count() == 0

        async def present_customer():
            await reset("{customers:[window.fixture.customer]}")
            await page.get_by_role("button", name="عميل تجريبي").click()
            await expect_sixty(2)
            assert await page.get_by_role("status").count() == 0
            await page.get_by_role("button", name="تحصيل دفعة").click()
            assert await page.evaluate("window.effects") == [
                ["customer", "customer-fixture"], ["go", "debt_customer"],
                ["invoice", "invoice-fixture"], ["go", "invoice_detail"],
            ]

        async def absent_details():
            await reset("{screen:'debt_customer'}")
            await expect_sixty(2)
            assert await page.get_by_role("status").get_by_text(UNAVAILABLE, exact=True).count() == 1
            await click_disabled(page.get_by_role("button", name="تحصيل دفعة"))
            await page.get_by_role("button", name="الرجوع إلى الديون", exact=True).click()
            assert await page.evaluate("window.effects") == [["back", None]]
            assert await page.get_by_role("heading", name="الديون", exact=True).count() == 1
            await expect_sixty(2)

        async def disappears_in_details():
            await reset("{customers:[window.fixture.customer]}")
            await page.get_by_role("button", name="عميل تجريبي").click()
            await page.evaluate("window.effects=[];window.fixture.update({customers:[]})")
            await expect_sixty(2)
            assert await page.get_by_role("status").get_by_text(UNAVAILABLE, exact=True).count() == 1
            await click_disabled(page.get_by_role("button", name="تحصيل دفعة"))
            # Contact controls also become unavailable; no valid actions disappear silently.
            assert await page.locator('button[disabled]').count() == 3
            await page.get_by_role("button", name="رجوع", exact=True).click()
            assert await page.evaluate("window.effects") == [["back", None]]
            await expect_sixty(2)

        async def details_recover():
            await reset("{screen:'debt_customer',customersLoading:true}")
            await expect_sixty(2)
            assert await page.get_by_role("status").get_by_text(LOADING, exact=True).count() == 1
            await click_disabled(page.get_by_role("button", name="تحصيل دفعة"))
            await page.evaluate("window.fixture.update({customersLoading:false,customers:[window.fixture.customer]})")
            assert await page.get_by_role("status").count() == 0
            assert await page.get_by_role("heading", name="عميل تجريبي", exact=True).count() == 1
            await expect_sixty(2)
            assert await page.get_by_role("button", name="تحصيل دفعة").is_enabled()
            await expect_no_effects()

        async def missing_selection():
            await reset("{screen:'debt_customer',openCustomerId:null}")
            assert await page.get_by_text("0", exact=True).count() == 0
            assert await page.get_by_text("إجمالي المستحق", exact=True).count() == 0
            assert await page.get_by_role("button", name="تحصيل دفعة").count() == 0
            assert await page.get_by_text(UNAVAILABLE, exact=True).count() == 1
            await expect_no_effects()

        async def isolated_invoices():
            await reset("{screen:'debt_customer'}")
            await page.evaluate("window.fixture.update({invoices:[...window.fixture.unrelatedInvoices,{id:'invoice-fixture',number:'001',customerId:'customer-fixture',items:[],total:100,paid:40,delivery:'direct'}]})")
            await expect_sixty(2)
            assert await page.get_by_text("#001", exact=True).count() == 1
            for number in ("#002", "#003", "#004", "#005"):
                assert await page.get_by_text(number, exact=True).count() == 0
            await expect_no_effects()

        for name, check in [
            ("missing-row-keeps-sixty-and-blocks-click", unavailable_row),
            ("loading-then-customer-appears", loading_then_appears),
            ("loading-ends-with-persistent-absence", persistent_absence),
            ("present-customer-keeps-original-navigation", present_customer),
            ("missing-details-keep-sixty-and-back", absent_details),
            ("customer-disappears-during-details", disappears_in_details),
            ("details-loading-then-recovers", details_recover),
            ("no-selection-does-not-invent-zero-or-customer", missing_selection),
            ("selected-id-excludes-other-unassigned-returned-pending", isolated_invoices),
        ]:
            await case(name, check)
        await page.wait_for_timeout(50)
        report = {"results": results, "page_errors": errors, "network_violations": violations,
                  "browser_version": browser.version,
                  "scope": "Actual extracted React screens; synthetic data; no backend or authenticated full-app journey"}
        (out / "browser-results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        print(json.dumps(report, ensure_ascii=False))
        await browser.close()
        assert len(results) == 9 and all(result["passed"] for result in results), report
        assert not errors and not violations, report


asyncio.run(main())
