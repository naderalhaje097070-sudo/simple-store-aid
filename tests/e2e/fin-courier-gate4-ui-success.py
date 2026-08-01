"""FIN-COURIER-001 Gate 4 — type-aware courier success-screen probe.

Unlike the read-only UI probes, this test deliberately saves disposable sales in
an isolated Supabase instance. It verifies that courier money is described as
custody, while a pending courier order is described as in transit rather than
custody/store cash.
"""

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ["PILOT_QA_EMAIL"]
PASSWORD = os.environ["PILOT_QA_PASSWORD"]
EVIDENCE = Path("/tmp/fin-courier-gate4-ui-success")
EVIDENCE.mkdir(parents=True, exist_ok=True)


async def login(page) -> None:
    await page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
    await page.locator("#auth-email").wait_for(state="visible", timeout=20_000)
    await page.locator("#auth-email").fill(EMAIL)
    await page.locator("#auth-password").fill(PASSWORD)
    await page.locator('button[type="submit"]').click()
    await page.wait_for_url("**/app", timeout=20_000)
    await page.wait_for_load_state("networkidle", timeout=20_000)


async def start_advanced_sale(page) -> None:
    await page.get_by_text("فاتورة جديدة", exact=True).first.click()
    await page.wait_for_timeout(350)
    body = await page.locator("body").inner_text()
    if "بيع سريع" in body or "إتمام البيع" not in body:
        raise AssertionError(
            "GATE4_UI_SUCCESS_EXPECTED_RED:I4 advanced-sale prerequisite is not implemented"
        )
    await page.get_by_text("GATE4-PRODUCT", exact=True).click()
    await page.get_by_text("إتمام البيع", exact=True).click()
    await page.get_by_text("عبر مندوب", exact=True).click()
    await page.get_by_text("GATE4-COURIER", exact=True).click()


async def save_outcome(page, outcome: str) -> str:
    await page.get_by_text(outcome, exact=True).click()
    save = page.get_by_text("حفظ الفاتورة", exact=True)
    await save.wait_for(state="visible", timeout=10_000)
    await save.click()
    await page.get_by_text("تم حفظ الفاتورة", exact=True).wait_for(
        state="visible", timeout=20_000
    )
    await page.wait_for_timeout(300)
    return await page.locator("body").inner_text()


async def assert_delivered_full(page, label: str) -> None:
    await start_advanced_sale(page)
    try:
        body = await save_outcome(page, "تم التحصيل بالكامل")
    except Exception:
        # Preserve diagnostics, but do not convert an unknown browser/backend/runtime
        # failure into an accepted expected-RED sentinel.
        await page.screenshot(path=str(EVIDENCE / f"{label}-i4-full-runtime.png"), full_page=True)
        raise

    if "عهدة" not in body:
        await page.screenshot(path=str(EVIDENCE / f"{label}-i4-full-wording.png"), full_page=True)
        raise AssertionError(
            "GATE4_UI_SUCCESS_EXPECTED_RED:I4 delivered_full success does not identify courier custody"
        )
    if "قيد التوصيل" in body:
        raise AssertionError(
            "GATE4_UI_SUCCESS_EXPECTED_RED:I4 delivered_full success is mislabeled pending"
        )


async def return_home(page) -> None:
    home = page.get_by_text("عودة للرئيسية", exact=True)
    await home.wait_for(state="visible", timeout=10_000)
    await home.click()
    await page.wait_for_timeout(350)


async def assert_pending(page, label: str) -> None:
    await return_home(page)
    await start_advanced_sale(page)
    try:
        body = await save_outcome(page, "قيد التوصيل")
    except Exception:
        # Same rule as delivered_full: only known contract assertions may emit
        # GATE4_UI_SUCCESS_EXPECTED_RED. Runtime failures must stay failures.
        await page.screenshot(path=str(EVIDENCE / f"{label}-i4-pending-runtime.png"), full_page=True)
        raise

    if "قيد التوصيل" not in body:
        raise AssertionError(
            "GATE4_UI_SUCCESS_EXPECTED_RED:I4 pending success does not identify in-transit state"
        )
    if "دخلت العهدة" in body or "عهدة كاملة" in body:
        raise AssertionError(
            "GATE4_UI_SUCCESS_EXPECTED_RED:I4 pending order is incorrectly presented as custody"
        )

    await page.screenshot(path=str(EVIDENCE / f"{label}-i4-green.png"), full_page=True)


async def main() -> None:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        raise RuntimeError("Gate 4 success-screen probe is restricted to isolated CI")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
                context = await browser.new_context(
                    viewport={"width": width, "height": height}, locale="ar-LY"
                )
                page = await context.new_page()
                await login(page)
                await assert_delivered_full(page, label)
                await assert_pending(page, label)
                await context.close()
        finally:
            await browser.close()

    print("GATE4_UI_SUCCESS_GREEN: I4 courier success semantics passed")


if __name__ == "__main__":
    asyncio.run(main())
