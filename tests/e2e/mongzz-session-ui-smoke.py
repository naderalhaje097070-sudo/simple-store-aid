import asyncio
import json
import os
import re
import subprocess
import time
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlparse

import requests
from playwright.async_api import async_playwright

BASE = os.environ.get("APP_BASE_URL", "http://127.0.0.1:8080").rstrip("/")
API_URL = os.environ["API_URL"].rstrip("/")
ANON_KEY = os.environ["ANON_KEY"]
SESSION_FILE = Path(os.environ.get("SESSION_FILE", "/tmp/password-token.json"))
TEST_EMAIL = os.environ.get("TEST_EMAIL", "pilot.qa@mongzz.test")
OUT = Path(os.environ.get("SMOKE_OUT", "/tmp/mongzz-session-smoke"))
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


def rpc(token: str, name: str, body: dict) -> None:
    response = requests.post(
        f"{API_URL}/rest/v1/rpc/{name}",
        headers={
            "apikey": ANON_KEY,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json=body,
        timeout=30,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"RPC {name} failed {response.status_code}: {response.text}")


async def open_sale(page) -> None:
    for label in ("بيع جديد", "بيع سريع"):
        try:
            await page.get_by_role("button", name=label).first.click(timeout=3000)
            return
        except Exception:
            pass
    await page.get_by_text("بيع سريع", exact=False).first.click(timeout=5000)


async def run() -> None:
    session = json.loads(SESSION_FILE.read_text(encoding="utf-8"))
    if not session.get("access_token") or not session.get("refresh_token"):
        raise RuntimeError("Password token file does not contain a valid session")
    session.setdefault("expires_at", int(time.time()) + int(session.get("expires_in", 3600)))

    escaped_email = TEST_EMAIL.replace("'", "''")
    tenant_id = psql_one(f"""
        SELECT t.id::text FROM public.tenants t
        JOIN auth.users u ON u.id=t.owner_user_id
        WHERE lower(u.email)=lower('{escaped_email}') LIMIT 1
    """)
    if not tenant_id:
        raise RuntimeError("Test tenant not found")

    product_id = psql_one(f"""
        INSERT INTO public.products
          (tenant_id,name,price,cost,stock,is_active,is_discount)
        VALUES ('{tenant_id}','{TAG} منتج',{PRICE},{COST},{STOCK},true,false)
        RETURNING id::text
    """)

    timezone_expr = f"COALESCE((SELECT timezone FROM public.tenants WHERE id='{tenant_id}'),'UTC')"
    today_expr = f"public.tenant_today('{tenant_id}')"

    def sales_total() -> Decimal:
        return Decimal(psql_one(f"""
          SELECT COALESCE(SUM(total),0)::text FROM public.orders
          WHERE tenant_id='{tenant_id}'
          AND (created_at AT TIME ZONE {timezone_expr})::date={today_expr}
        """))

    def cash_total() -> Decimal:
        return Decimal(psql_one(f"""
          SELECT COALESCE(SUM(amount),0)::text FROM public.payments
          WHERE tenant_id='{tenant_id}' AND method='cash'
          AND (created_at AT TIME ZONE {timezone_expr})::date={today_expr}
        """))

    base_sales, base_cash = sales_total(), cash_total()
    report = {"tag": TAG, "tenantId": tenant_id, "checks": []}
    errors = []
    failed_responses = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={"width": 1280, "height": 900}, locale="ar-LY", accept_downloads=True
        )
        page = await context.new_page()
        page.on("pageerror", lambda exc: errors.append(str(exc)))
        page.on("console", lambda msg: msg.type == "error" and errors.append(msg.text))
        page.on(
            "response",
            lambda response: response.status >= 400
            and failed_responses.append({"status": response.status, "url": response.url}),
        )

        await page.goto(f"{BASE}/auth", wait_until="domcontentloaded", timeout=30000)
        project_ref = (urlparse(API_URL).hostname or "127").split(".")[0]
        storage_value = json.dumps(session, ensure_ascii=False)
        keys = [f"sb-{project_ref}-auth-token", "sb-127-auth-token", "sb-localhost-auth-token"]
        await page.evaluate(
            "([keys,value]) => keys.forEach(key => localStorage.setItem(key,value))",
            [keys, storage_value],
        )
        await page.goto(f"{BASE}/app", wait_until="domcontentloaded", timeout=30000)
        try:
            await page.wait_for_url(re.compile(r".*/app(?:[/?#].*)?$"), timeout=15000)
            await page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            await page.screenshot(path=str(OUT / "00_session_failure.png"), full_page=True)
            state = {
                "url": page.url,
                "body": (await page.locator("body").inner_text())[:2000],
                "storageKeys": await page.evaluate("Object.keys(localStorage)"),
                "failedResponses": failed_responses[-20:],
                "errors": errors[-10:],
            }
            (OUT / "session-failure.json").write_text(
                json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8"
            )
            raise

        await page.screenshot(path=str(OUT / "01_dashboard.png"), full_page=True)
        report["checks"].append("authenticated_session")
        if await page.evaluate("document.documentElement.dir") != "rtl":
            raise AssertionError("Authenticated app is not RTL")

        await page.set_viewport_size({"width": 390, "height": 844})
        await page.wait_for_timeout(500)
        if await page.evaluate("document.documentElement.scrollWidth > document.documentElement.clientWidth + 1"):
            raise AssertionError("Mobile dashboard has horizontal overflow")
        await page.screenshot(path=str(OUT / "02_mobile_dashboard.png"), full_page=True)
        report["checks"].append("mobile_390_no_overflow")
        await page.set_viewport_size({"width": 1280, "height": 900})

        await open_sale(page)
        await page.wait_for_timeout(700)
        await page.screenshot(path=str(OUT / "03_sale_open.png"), full_page=True)
        await page.get_by_text(f"{TAG} منتج", exact=False).first.click(timeout=10000)
        await page.wait_for_timeout(300)
        await page.screenshot(path=str(OUT / "04_product_added.png"), full_page=True)
        await page.get_by_text("إصدار الفاتورة", exact=False).first.click(timeout=10000)
        await page.wait_for_timeout(1800)
        await page.screenshot(path=str(OUT / "05_invoice_issued.png"), full_page=True)
        report["checks"].append("cash_sale_ui")

        order_row = psql_one(f"""
          SELECT id::text||'|'||total::text||'|'||paid::text||'|'||status||'|'||delivery
          FROM public.orders WHERE tenant_id='{tenant_id}'
          AND created_at>=now()-interval '3 minutes'
          ORDER BY created_at DESC LIMIT 1
        """)
        if not order_row:
            raise AssertionError("No order was created")
        order_id, total, paid, status, delivery = order_row.split("|")
        if Decimal(total) != PRICE or Decimal(paid) != PRICE or status != "paid" or delivery != "direct":
            raise AssertionError(f"Unexpected order: {order_row}")
        report["order"] = {"id": order_id, "total": total, "paid": paid, "status": status, "delivery": delivery}
        report["checks"].append("order_db")

        payment_row = psql_one(f"""
          SELECT kind||'|'||method||'|'||amount::text FROM public.payments
          WHERE order_id='{order_id}' ORDER BY created_at DESC LIMIT 1
        """)
        kind, method, amount = payment_row.split("|")
        if kind != "sale" or method != "cash" or Decimal(amount) != PRICE:
            raise AssertionError(f"Unexpected payment: {payment_row}")
        if Decimal(psql_one(f"SELECT stock::text FROM public.products WHERE id='{product_id}'")) != STOCK - 1:
            raise AssertionError("Stock did not decrement")
        report["checks"].extend(["payment_db", "stock_decrement"])

        await page.goto(f"{BASE}/app", wait_until="domcontentloaded")
        await page.wait_for_load_state("networkidle", timeout=20000)
        await page.wait_for_timeout(800)
        await page.screenshot(path=str(OUT / "06_dashboard_after.png"), full_page=True)
        if sales_total() - base_sales != PRICE or cash_total() - base_cash != PRICE:
            raise AssertionError("Dashboard aggregate delta is incorrect")
        if "د.ل" not in await page.locator("body").inner_text():
            raise AssertionError("Currency token missing")
        report["checks"].append("dashboard_aggregates")

        rpc(session["access_token"], "close_day", {"p_note": TAG})
        close_row = psql_one(f"""
          SELECT sales::text||'|'||collected::text||'|'||realized_profit::text||'|'||
                 customer_debts::text||'|'||unsettled_custody::text
          FROM public.day_closes WHERE tenant_id='{tenant_id}' AND note='{TAG}'
          ORDER BY created_at DESC LIMIT 1
        """)
        if not close_row:
            raise AssertionError("Day close snapshot missing")
        sales, collected, profit, debts, custody = [Decimal(x) for x in close_row.split("|")]
        if sales < PRICE or collected < PRICE or profit < PRICE - COST:
            raise AssertionError(f"Unexpected day close: {close_row}")
        report["dayClose"] = {
            "sales": str(sales), "collected": str(collected), "realizedProfit": str(profit),
            "customerDebts": str(debts), "unsettledCustody": str(custody),
        }
        report["checks"].append("day_close")

        if errors:
            report["browserErrors"] = errors[:10]
        report["failedResponses"] = failed_responses[-20:]
        await context.close()
        await browser.close()

    (OUT / "results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("\nMONGZZ SESSION BUSINESS FLOW SMOKE PASSED")


if __name__ == "__main__":
    asyncio.run(run())
