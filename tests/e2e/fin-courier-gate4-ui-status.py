"""FIN-COURIER-001 Gate 4 — courier wording and operational-status probe.

Seeds isolated courier-order shapes directly through the local Postgres test DB,
then verifies the application wording. No production access and no app financial
write is performed.
"""

import asyncio
import os
import re
import subprocess
from pathlib import Path

from playwright.async_api import async_playwright

BASE_URL = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080")
EMAIL = os.environ["PILOT_QA_EMAIL"]
PASSWORD = os.environ["PILOT_QA_PASSWORD"]
DB_URL = os.environ["DB_URL"]
EVIDENCE = Path("/tmp/fin-courier-gate4-ui-status")
EVIDENCE.mkdir(parents=True, exist_ok=True)

EXPECTED_OPERATIONAL_STATUSES = (
    "قيد التوصيل",
    "عهدة كاملة",
    "عهدة جزئية ودين",
    "دين كامل",
    "تمت التسوية",
    "مرتجع",
)


def seed_status_fixtures() -> None:
    sql = r"""
    insert into public.customers(id, tenant_id, name)
    values ('eeee5555-1100-4000-8000-000000000001',
            '11111111-1111-4111-8111-111111111111',
            'GATE4-STATUS-CUSTOMER')
    on conflict (id) do nothing;

    insert into public.orders(
      id, tenant_id, total, paid, status, delivery, courier_id,
      courier_state, collected_by_courier, customer_id, created_at
    ) values
      ('aa110001-1100-4000-8000-000000000001','11111111-1111-4111-8111-111111111111',100,0,'debt','courier','ffff6666-1000-0000-0000-000000000001','pending',0,'eeee5555-1100-4000-8000-000000000001',now()),
      ('aa110002-1100-4000-8000-000000000002','11111111-1111-4111-8111-111111111111',100,0,'debt','courier','ffff6666-1000-0000-0000-000000000001','delivered_full',100,'eeee5555-1100-4000-8000-000000000001',now()),
      ('aa110003-1100-4000-8000-000000000003','11111111-1111-4111-8111-111111111111',100,0,'debt','courier','ffff6666-1000-0000-0000-000000000001','delivered_partial',40,'eeee5555-1100-4000-8000-000000000001',now()),
      ('aa110004-1100-4000-8000-000000000004','11111111-1111-4111-8111-111111111111',100,0,'debt','courier','ffff6666-1000-0000-0000-000000000001','delivered_none',0,'eeee5555-1100-4000-8000-000000000001',now()),
      ('aa110005-1100-4000-8000-000000000005','11111111-1111-4111-8111-111111111111',100,0,'debt','direct',null,'returned',0,'eeee5555-1100-4000-8000-000000000001',now()),
      ('aa110006-1100-4000-8000-000000000006','11111111-1111-4111-8111-111111111111',100,100,'paid','direct',null,null,0,'eeee5555-1100-4000-8000-000000000001',now())
    on conflict (id) do nothing;

    insert into public.payments(
      id, tenant_id, kind, method, amount, order_id, customer_id, courier_id, created_at
    ) values (
      'bb110006-1100-4000-8000-000000000006',
      '11111111-1111-4111-8111-111111111111',
      'courier_settlement','cash',100,
      'aa110006-1100-4000-8000-000000000006',
      'eeee5555-1100-4000-8000-000000000001',
      'ffff6666-1000-0000-0000-000000000001',now()
    ) on conflict (id) do nothing;
    """
    subprocess.run(
        ["psql", DB_URL, "-v", "ON_ERROR_STOP=1", "-c", sql],
        check=True,
        text=True,
        capture_output=True,
    )


async def login(page) -> None:
    await page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
    await page.locator("#auth-email").wait_for(state="visible", timeout=20_000)
    await page.locator("#auth-email").fill(EMAIL)
    await page.locator("#auth-password").fill(PASSWORD)
    await page.locator('button[type="submit"]').click()
    await page.wait_for_url("**/app", timeout=20_000)
    await page.wait_for_load_state("networkidle", timeout=20_000)


async def open_courier_custody(page, label: str) -> None:
    if label == "desktop":
        await page.get_by_text("عهدة المندوب", exact=True).first.click()
    else:
        alert = page.get_by_text(re.compile(r"طلبات توصيل غير مكتملة"))
        await alert.first.wait_for(state="visible", timeout=15_000)
        await alert.first.click()
    await page.wait_for_timeout(400)


async def assert_wording(page, label: str) -> None:
    await open_courier_custody(page, label)
    await page.get_by_text("تحديث حالة التسليم ←", exact=True).first.click()
    await page.wait_for_timeout(200)
    body = await page.locator("body").inner_text()

    if "لم تُسلَّم (دين)" in body:
        await page.screenshot(path=str(EVIDENCE / f"{label}-i3-old-wording.png"), full_page=True)
        raise AssertionError(
            "GATE4_UI_STATUS_EXPECTED_RED:I3 old 'لم تُسلَّم (دين)' wording is still present"
        )
    if "تم التسليم دون تحصيل" not in body:
        raise AssertionError(
            "GATE4_UI_STATUS_EXPECTED_RED:I3 missing 'تم التسليم دون تحصيل' outcome"
        )
    if "لم يتم التسليم / مرتجع" not in body and "لم يتم التسليم" not in body:
        raise AssertionError(
            "GATE4_UI_STATUS_EXPECTED_RED:I3 missing separate not-delivered/returned path"
        )


async def go_home(page) -> None:
    home = page.get_by_text("الرئيسية", exact=True)
    if await home.count() > 0:
        await home.first.click()
    else:
        await page.goto(f"{BASE_URL}/app", wait_until="networkidle")
    await page.wait_for_timeout(300)


async def assert_invoice_statuses(page, label: str) -> None:
    await go_home(page)
    await page.get_by_text("الفواتير", exact=True).first.click()
    await page.wait_for_timeout(500)
    body = await page.locator("body").inner_text()
    missing = [status for status in EXPECTED_OPERATIONAL_STATUSES if status not in body]
    if missing:
        await page.screenshot(path=str(EVIDENCE / f"{label}-j2-statuses.png"), full_page=True)
        raise AssertionError(
            "GATE4_UI_STATUS_EXPECTED_RED:J2 missing operational statuses: " + ", ".join(missing)
        )


async def main() -> None:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        raise RuntimeError("Gate 4 UI status probe is restricted to isolated CI")

    seed_status_fixtures()

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)
        try:
            for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
                context = await browser.new_context(
                    viewport={"width": width, "height": height}, locale="ar-LY"
                )
                page = await context.new_page()
                await login(page)
                await assert_wording(page, label)
                await assert_invoice_statuses(page, label)
                await context.close()
        finally:
            await browser.close()

    print("GATE4_UI_STATUS_GREEN: I3/J2 wording and operational statuses passed")


if __name__ == "__main__":
    asyncio.run(main())
