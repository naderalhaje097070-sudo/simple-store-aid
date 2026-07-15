"""Authenticated owner and employee UI smoke for the isolated CI environment."""

import asyncio
import os
from pathlib import Path

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080")
OWNER_EMAIL = os.environ["PILOT_QA_EMAIL"]
OWNER_PASSWORD = os.environ["PILOT_QA_PASSWORD"]
EMPLOYEE_EMAIL = os.environ["EMPLOYEE_QA_EMAIL"]
EMPLOYEE_PASSWORD = os.environ["EMPLOYEE_QA_PASSWORD"]
EVIDENCE = Path("/tmp/mongezz-auth-smoke")
EVIDENCE.mkdir(parents=True, exist_ok=True)


def critical(errors: list[str]) -> list[str]:
    markers = ("react error #418", "hydration failed", "hydration mismatch")
    return [item for item in errors if any(marker in item.lower() for marker in markers)]


async def login(page, email: str, password: str, label: str, errors: list[str]) -> None:
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

    await page.locator("#auth-email").fill(email)
    await page.locator("#auth-password").fill(password)
    await page.locator('button[type="submit"]').click()


async def assert_layout(page, errors: list[str], label: str) -> None:
    layout = await page.evaluate(
        "() => ({ width: window.innerWidth, scroll: document.documentElement.scrollWidth, dir: document.documentElement.dir, lang: document.documentElement.lang })"
    )
    if layout["scroll"] > layout["width"] + 1:
        raise AssertionError(f"Horizontal overflow ({label}): {layout}")
    if layout["dir"] != "rtl" or layout["lang"] != "ar":
        raise AssertionError(f"Incorrect locale attributes ({label}): {layout}")
    if critical(errors):
        raise AssertionError(f"Hydration error ({label}): {critical(errors)}")


async def owner_smoke(browser, width: int, height: int, label: str) -> None:
    context = await browser.new_context(
        viewport={"width": width, "height": height},
        locale="ar-LY",
    )
    page = await context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: errors.append(message.text) if message.type == "error" else None,
    )

    await login(page, OWNER_EMAIL, OWNER_PASSWORD, f"owner-{label}", errors)
    try:
        await page.wait_for_url("**/app", timeout=20000)
    except PlaywrightTimeoutError:
        await page.screenshot(
            path=str(EVIDENCE / f"owner-{label}-login-failure.png"),
            full_page=True,
        )
        print(f"OWNER LOGIN FAILURE URL ({label}): {page.url}")
        print(f"OWNER LOGIN FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}")
        print(f"OWNER LOGIN FAILURE ERRORS ({label}): {errors}")
        raise

    await page.wait_for_load_state("networkidle", timeout=20000)
    await page.get_by_text("فاتورة جديدة", exact=True).first.wait_for(timeout=10000)
    await assert_layout(page, errors, f"owner-{label}")
    await page.screenshot(path=str(EVIDENCE / f"owner-{label}.png"), full_page=True)
    await context.close()


async def employee_smoke(browser, width: int, height: int, label: str) -> None:
    context = await browser.new_context(
        viewport={"width": width, "height": height},
        locale="ar-LY",
    )
    page = await context.new_page()
    errors: list[str] = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.on(
        "console",
        lambda message: errors.append(message.text) if message.type == "error" else None,
    )

    await login(page, EMPLOYEE_EMAIL, EMPLOYEE_PASSWORD, f"employee-{label}", errors)
    try:
        await page.wait_for_url("**/employee", timeout=20000)
    except PlaywrightTimeoutError:
        await page.screenshot(
            path=str(EVIDENCE / f"employee-{label}-redirect-failure.png"),
            full_page=True,
        )
        print(f"EMPLOYEE REDIRECT FAILURE URL ({label}): {page.url}")
        print(f"EMPLOYEE REDIRECT FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}")
        print(f"EMPLOYEE REDIRECT FAILURE ERRORS ({label}): {errors}")
        raise

    await page.get_by_text("الطلبات المسندة إليّ", exact=True).wait_for(timeout=15000)
    await page.get_by_text("عميل اختبار الموظف", exact=True).wait_for(timeout=10000)
    await page.get_by_text("منتج اختبار الموظف", exact=True).wait_for(timeout=10000)

    if await page.get_by_text("فاتورة جديدة", exact=True).count() != 0:
        raise AssertionError("Employee portal exposed owner sale action")
    if await page.get_by_text("الأرباح", exact=True).count() != 0:
        raise AssertionError("Employee portal exposed owner profit data")

    await assert_layout(page, errors, f"employee-{label}")
    await page.screenshot(path=str(EVIDENCE / f"employee-{label}.png"), full_page=True)
    await context.close()


async def main() -> None:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        raise RuntimeError("This smoke test is restricted to isolated CI")

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
            await owner_smoke(browser, width, height, label)
            await employee_smoke(browser, width, height, label)
        await browser.close()

    print("PASS: isolated owner and employee authenticated UI smoke")


if __name__ == "__main__":
    asyncio.run(main())
