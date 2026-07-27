"""FIN-COURIER-001 Gate 4 UI contract probe.

Read-only with respect to financial writes: it logs into an isolated tenant, opens
sale UI, and verifies the approved primary-flow / courier-outcome contract without
saving an invoice.

On the pre-implementation Gate-4 baseline this test is expected to fail with a
GATE4_UI_EXPECTED_RED marker. After PR-C it must pass without changing the test.
"""

import asyncio
import os
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ["PILOT_QA_EMAIL"]
PASSWORD = os.environ["PILOT_QA_PASSWORD"]
EVIDENCE = Path("/tmp/fin-courier-gate4-ui")
EVIDENCE.mkdir(parents=True, exist_ok=True)

EXPECTED_OUTCOMES = (
    "قيد التوصيل",
    "تم التحصيل بالكامل",
    "تم التحصيل جزئياً",
    "تم التسليم دون تحصيل",
)


async def login(page) -> None:
    await page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
    await page.locator("#auth-email").wait_for(state="visible", timeout=20_000)
    await page.locator("#auth-email").fill(EMAIL)
    await page.locator("#auth-password").fill(PASSWORD)
    await page.locator('button[type="submit"]').click()
    await page.wait_for_url("**/app", timeout=20_000)
    await page.wait_for_load_state("networkidle", timeout=20_000)


async def assert_contract(page, label: str) -> None:
    # I1 / J1: the primary "فاتورة جديدة" CTA must open advanced sale, not quick sale.
    await page.get_by_text("فاتورة جديدة", exact=True).first.click()
    await page.wait_for_timeout(500)
    body = await page.locator("body").inner_text()
    if "بيع سريع" in body:
        await page.screenshot(path=str(EVIDENCE / f"{label}-i1-quick-sale.png"), full_page=True)
        raise AssertionError(
            "GATE4_UI_EXPECTED_RED:I1/J1 primary new-sale CTA still opens quick sale"
        )
    if "إتمام البيع" not in body:
        raise AssertionError("GATE4_UI_EXPECTED_RED:I1/J1 advanced sale did not open")

    # Open the payment sheet without saving any financial write.
    await page.get_by_text("GATE4-PRODUCT", exact=True).click()
    await page.get_by_text("إتمام البيع", exact=True).click()
    await page.get_by_text("عبر مندوب", exact=True).click()
    await page.wait_for_timeout(300)
    body = await page.locator("body").inner_text()

    # I2 / J3: courier mode must expose operational outcomes, not generic payment states.
    missing = [text for text in EXPECTED_OUTCOMES if text not in body]
    if missing:
        await page.screenshot(path=str(EVIDENCE / f"{label}-i2-outcomes.png"), full_page=True)
        raise AssertionError(
            "GATE4_UI_EXPECTED_RED:I2/J3 missing courier outcomes: " + ", ".join(missing)
        )

    generic = ("مدفوع", "جزئياً", "دين")
    if all(text in body for text in generic):
        raise AssertionError(
            "GATE4_UI_EXPECTED_RED:I2/J3 generic payment-state trio still drives courier outcome"
        )

    await page.screenshot(path=str(EVIDENCE / f"{label}-green.png"), full_page=True)


async def main() -> None:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        raise RuntimeError("FIN-COURIER Gate 4 UI probe is restricted to isolated CI")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
                context = await browser.new_context(
                    viewport={"width": width, "height": height},
                    locale="ar-LY",
                )
                page = await context.new_page()
                await login(page)
                await assert_contract(page, label)
                await context.close()
        finally:
            await browser.close()

    print("GATE4_UI_GREEN: primary advanced-sale and courier-outcome contract passed")


if __name__ == "__main__":
    asyncio.run(main())
