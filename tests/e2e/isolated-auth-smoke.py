"""Read-only authenticated UI smoke for the isolated CI environment."""

import asyncio
import os
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ["PILOT_QA_EMAIL"]
PASSWORD = os.environ["PILOT_QA_PASSWORD"]
EVIDENCE = Path("/tmp/mongezz-auth-smoke")
EVIDENCE.mkdir(parents=True, exist_ok=True)


def critical(errors: list[str]) -> list[str]:
    markers = ("react error #418", "hydration failed", "hydration mismatch")
    return [item for item in errors if any(marker in item.lower() for marker in markers)]


async def main() -> None:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        raise RuntimeError("This smoke test is restricted to isolated CI")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                locale="ar-LY",
            )
            page = await context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "console",
                lambda message: errors.append(message.text)
                if message.type == "error"
                else None,
            )

            await page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
            try:
                await page.locator("#auth-email").wait_for(state="visible", timeout=20000)
            except PlaywrightTimeoutError:
                await page.screenshot(
                    path=str(EVIDENCE / f"{label}-protection-failure.png"),
                    full_page=True,
                )
                print(f"PROTECTION FAILURE URL ({label}): {page.url}")
                print(f"PROTECTION FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}")
                print(f"PROTECTION FAILURE ERRORS ({label}): {errors}")
                raise

            if critical(errors):
                raise AssertionError(f"Hydration error on unauthenticated /app: {critical(errors)}")
            errors.clear()

            await page.locator("#auth-email").fill(EMAIL)
            await page.locator("#auth-password").fill(PASSWORD)
            await page.locator('button[type="submit"]').click()
            try:
                await page.wait_for_url("**/app", timeout=20000)
            except PlaywrightTimeoutError:
                await page.screenshot(
                    path=str(EVIDENCE / f"{label}-login-failure.png"),
                    full_page=True,
                )
                print(f"LOGIN FAILURE URL ({label}): {page.url}")
                print(f"LOGIN FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}")
                print(f"LOGIN FAILURE ERRORS ({label}): {errors}")
                raise

            await page.wait_for_load_state("networkidle", timeout=20000)
            await page.get_by_text("فاتورة جديدة", exact=True).first.wait_for(timeout=10000)

            layout = await page.evaluate(
                "() => ({ width: window.innerWidth, scroll: document.documentElement.scrollWidth, dir: document.documentElement.dir, lang: document.documentElement.lang })"
            )
            if layout["scroll"] > layout["width"] + 1:
                raise AssertionError(f"Horizontal overflow: {layout}")
            if layout["dir"] != "rtl" or layout["lang"] != "ar":
                raise AssertionError(f"Incorrect locale attributes: {layout}")
            if critical(errors):
                raise AssertionError(f"Hydration error after login: {critical(errors)}")

            await page.screenshot(path=str(EVIDENCE / f"{label}.png"), full_page=True)
            await context.close()

        await browser.close()

    print("PASS: isolated authenticated UI smoke")


if __name__ == "__main__":
    asyncio.run(main())
