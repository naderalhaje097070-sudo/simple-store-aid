import asyncio
import json
import os
import re
import subprocess
import time
from decimal import Decimal
from pathlib import Path

import requests
from playwright.async_api import async_playwright

BASE = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
API_URL = os.environ["API_URL"].rstrip("/")
ANON_KEY = os.environ["ANON_KEY"]
TEST_EMAIL = os.environ.get("TEST_EMAIL", "pilot.qa@mongzz.test")
TEST_PASSWORD = os.environ.get("TEST_PASSWORD", "PilotQA-Only-2026!")
OUT = Path(os.environ.get("SMOKE_OUT", "/tmp/mongzz-ephemeral-smoke"))
OUT.mkdir(parents=True, exist_ok=True)

TAG = f"Pilot-QA-{int(time.time())}"
PRICE = Decimal("100")
COST = Decimal("60")
STOCK = 10


def psql_one(sql: str) -> str:
    result = subprocess.run(
        ["psql", "-At", "-q", "-v", "ON_ERROR_STOP=1", "-c", sql],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or "psql failed")
    return result.stdout.strip().splitlines()[0] if result.stdout.strip() else ""


def api_headers(token: str) -> dict[str, str]:
    return {
        "apikey": ANON_KEY,
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def rpc(token: str, name: str, body: dict) -> object:
    response = requests.post(
        f"{API_URL}/rest/v1/rpc/{name}",
        headers=api_headers(token),
        json=body,
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"RPC {name} failed with {response.status_code}: {response.text}")
    return response.json() if response.text else None


def read_access_token(storage: dict[str, str]) -> str:
    def scan(value):
        if isinstance(value, dict):
            if value.get("access_token"):
                return value["access_token"]
            for nested in value.values():
                token = scan(nested)
                if token:
                    return token
        return None

    for raw in storage.values():
        if not isinstance(raw, str) or "access_token" not in raw:
            continue
        try:
            token = scan(json.loads(raw))
        except json.JSONDecodeError:
            token = None
        if token:
            return token
    raise RuntimeError("Supabase access token not found in localStorage")


async def open_sale(page) -> None:
    for label in ("بيع جديد", "بيع سريع"):
        try:
            await page.get_by_role("button", name=label).first.click(timeout=3000)
            return
        except Exception:
            pass
    await page.get_by_text("بيع سريع", exact=False).first.click(timeout=5000)


async def run() -> None:
    escaped_email = TEST_EMAIL.replace("'", "''")
    tenant_id = psql_one(f"""
        SELECT t.id::text
        FROM public.tenants t
        JOIN auth.users u ON u.id = t.owner_user_id
        WHERE lower(u.email) = lower('{escaped_email}')
        ORDER BY t.created_at LIMIT 1
    """)
    if not tenant_id:
        raise RuntimeError("Seeded test tenant was not found")

    product_id = psql_one(f"""
        INSERT INTO public.products
          (tenant_id, name, price, cost, stock, is_active, is_discount)
        VALUES
          ('{tenant_id}', '{TAG} منتج', {PRICE}, {COST}, {STOCK}, true, false)
        RETURNING id::text
    """)

    timezone_expr = f"COALESCE((SELECT timezone FROM public.tenants WHERE id='{tenant_id}'),'UTC')"
    today_expr = f"public.tenant_today('{tenant_id}')"

    def aggregate_sales() -> Decimal:
        return Decimal(psql_one(f"""
            SELECT COALESCE(SUM(total),0)::text FROM public.orders
            WHERE tenant_id='{tenant_id}'
              AND (created_at AT TIME ZONE {timezone_expr})::date = {today_expr}
        """))

    def aggregate_cash() -> Decimal:
        return Decimal(psql_one(f"""
            SELECT COALESCE(SUM(amount),0)::text FROM public.payments
            WHERE tenant_id='{tenant_id}' AND method='cash'
              AND (created_at AT TIME ZONE {timezone_expr})::date = {today_expr}
        """))

    baseline_sales = aggregate_sales()
    baseline_cash = aggregate_cash()
    browser_errors: list[str] = []
    report: dict[str, object] = {
        "tag": TAG,
        "tenantId": tenant_id,
        "productId": product_id,
        "checks": [],
    }

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}, locale="ar-LY", accept_downloads=True
        )
        page = await context.new_page()
        page.on("pageerror", lambda exc: browser_errors.append(str(exc)))
        page.on("console", lambda msg: msg.type == "error" and browser_errors.append(msg.text))

        response = await page.goto(f"{BASE}/auth", wait_until="domcontentloaded", timeout=30000)
        if response and response.status >= 400:
            raise RuntimeError(f"/auth returned HTTP {response.status}")
        await page.wait_for_timeout(500)
        await page.screenshot(path=str(OUT / "00_auth.png"), full_page=True)

        await page.locator('input[type="email"]').fill(TEST_EMAIL)
        await page.locator('input[type="password"]').fill(TEST_PASSWORD)
        await page.get_by_role("button", name="دخول", exact=True).last.click()
        try:
            await page.wait_for_url(re.compile(r".*/app(?:[/?#].*)?$"), timeout=20000)
        except Exception:
            await page.screenshot(path=str(OUT / "00_login_failure.png"), full_page=True)
            state = {
                "url": page.url,
                "body": (await page.locator("body").inner_text())[:2000],
                "errors": browser_errors[-10:],
            }
            (OUT / "login-failure.json").write_text(
                json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            raise

        await page.wait_for_load_state("networkidle", timeout=20000)
        await page.screenshot(path=str(OUT / "01_login_dashboard.png"), full_page=True)
        report["checks"].append("login")

        html_dir = await page.evaluate("document.documentElement.dir")
        if html_dir != "rtl":
            raise AssertionError(f"Authenticated app dir={html_dir!r}, expected rtl")

        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(400)
        has_scroll_x = await page.evaluate(
            "document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"
        )
        await page.screenshot(path=str(OUT / "01b_mobile_dashboard.png"), full_page=True)
        if has_scroll_x:
            raise AssertionError("Authenticated mobile dashboard has horizontal overflow")
        report["checks"].append("mobile_390_rtl_no_overflow")
        await page.set_viewport_size({"width": 1280, "height": 900})

        await open_sale(page)
        await page.wait_for_timeout(700)
        await page.screenshot(path=str(OUT / "02_sale_open.png"), full_page=True)
        await page.get_by_text(f"{TAG} منتج", exact=False).first.click(timeout=10000)
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "03_product_added.png"), full_page=True)
        await page.get_by_text("إصدار الفاتورة", exact=False).first.click(timeout=10000)
        await page.wait_for_timeout(1800)
        await page.screenshot(path=str(OUT / "04_invoice_issued.png"), full_page=True)
        report["checks"].append("cash_sale_ui")

        order_row = psql_one(f"""
            SELECT id::text || '|' || total::text || '|' || paid::text || '|' || status || '|' || delivery
            FROM public.orders WHERE tenant_id='{tenant_id}'
              AND created_at >= now() - interval '3 minutes'
            ORDER BY created_at DESC LIMIT 1
        """)
        if not order_row:
            raise AssertionError("No order row was created")
        order_id, total, paid, status, delivery = order_row.split("|")
        if Decimal(total) != PRICE or Decimal(paid) != PRICE or status != "paid" or delivery != "direct":
            raise AssertionError(f"Unexpected order state: {order_row}")
        report["order"] = {"id": order_id, "total": total, "paid": paid, "status": status, "delivery": delivery}
        report["checks"].append("order_db")

        payment_row = psql_one(f"""
            SELECT kind || '|' || method || '|' || amount::text
            FROM public.payments WHERE order_id='{order_id}'
            ORDER BY created_at DESC LIMIT 1
        """)
        kind, method, amount = payment_row.split("|")
        if kind != "sale" or method != "cash" or Decimal(amount) != PRICE:
            raise AssertionError(f"Unexpected payment state: {payment_row}")
        report["checks"].append("payment_db")

        new_stock = Decimal(psql_one(f"SELECT stock::text FROM public.products WHERE id='{product_id}'"))
        if new_stock != Decimal(STOCK - 1):
            raise AssertionError(f"Unexpected stock={new_stock}; expected {STOCK - 1}")
        report["checks"].append("stock_decrement")

        await page.goto(f"{BASE}/app", wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=20000)
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(OUT / "05_dashboard_after.png"), full_page=True)
        body_text = await page.locator("body").inner_text()
        if aggregate_sales() - baseline_sales != PRICE:
            raise AssertionError("Dashboard sales aggregate delta is incorrect")
        if aggregate_cash() - baseline_cash != PRICE:
            raise AssertionError("Dashboard cash aggregate delta is incorrect")
        if "د.ل" not in body_text:
            raise AssertionError("Libyan currency token is missing from dashboard")
        report["checks"].append("dashboard_aggregates")

        storage = await page.evaluate("""() => Object.fromEntries(
            Array.from({length: localStorage.length}, (_, index) => {
                const key = localStorage.key(index);
                return [key, localStorage.getItem(key)];
            })
        )""")
        access_token = read_access_token(storage)
        rpc(access_token, "close_day", {"p_note": TAG})
        close_row = psql_one(f"""
            SELECT sales::text || '|' || collected::text || '|' || realized_profit::text || '|' ||
                   customer_debts::text || '|' || unsettled_custody::text
            FROM public.day_closes
            WHERE tenant_id='{tenant_id}' AND note='{TAG}'
            ORDER BY created_at DESC LIMIT 1
        """)
        if not close_row:
            raise AssertionError("Day-close snapshot was not created")
        sales, collected, profit, debts, custody = [Decimal(value) for value in close_row.split("|")]
        if sales < PRICE or collected < PRICE or profit < PRICE - COST:
            raise AssertionError(f"Unexpected day-close snapshot: {close_row}")
        report["dayClose"] = {
            "sales": str(sales), "collected": str(collected),
            "realizedProfit": str(profit), "customerDebts": str(debts),
            "unsettledCustody": str(custody),
        }
        report["checks"].append("day_close_rpc_and_snapshot")

        if browser_errors:
            raise AssertionError("Browser runtime errors: " + " | ".join(browser_errors[:5]))
        await context.close()
        await browser.close()

    (OUT / "results.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nMONGZZ EPHEMERAL AUTHENTICATED UI SMOKE PASSED")


if __name__ == "__main__":
    asyncio.run(run())
