"""
Mongezz V2 — destructive E2E financial flow test.

Verifies the most sensitive financial path against an explicitly isolated
local/CI environment only:
  1. Quick sale (cash, paid in full) via UI
  2. Dashboard re-renders and aggregates update
  3. Day close snapshot persists with correct numbers

The shared SEC-ENV write-harness guard executes before requests/Playwright,
browser session access, SQL, API calls, or screenshot creation.
"""

import asyncio
import json
import os
import sys
import time
from decimal import Decimal
from pathlib import Path

from write_harness_guard import (
    browser_request_is_isolated,
    preflight_only,
    psql_exec as guarded_psql_exec,
    psql_one as guarded_psql_one,
    require_write_harness,
)

if "--preflight-only" in sys.argv:
    preflight_only()
    raise SystemExit(0)

WRITE_CONFIG = require_write_harness()
SB_URL = WRITE_CONFIG.supabase_url
SB_ANON = WRITE_CONFIG.supabase_publishable_key

# External/browser/network dependencies are intentionally imported only after
# the destructive-test preflight succeeds.
import requests
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SHOTS = Path("/tmp/browser/mongezz-e2e/shots")
SHOTS.mkdir(parents=True, exist_ok=True)
TAG = f"E2E-{int(time.time())}"
PRICE = Decimal("100")
COST = Decimal("60")
STOCK = 10


def fail(msg):
    print(f"❌ FAIL: {msg}")
    sys.exit(1)


def ok(msg):
    print(f"✅ {msg}")


def psql_one(sql: str) -> str:
    return guarded_psql_one(WRITE_CONFIG, sql)


def psql_exec(sql: str) -> None:
    guarded_psql_exec(WRITE_CONFIG, sql)


def reject_write_redirect(response, operation: str) -> None:
    """Never forward a write body or auth header to a redirected origin."""

    if 300 <= response.status_code < 400:
        raise RuntimeError(f"{operation} redirect forbidden: HTTP {response.status_code}")


class API:
    def __init__(self, token: str):
        self.h = {
            "apikey": SB_ANON,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }

    def post(self, path, body):
        r = requests.post(
            f"{SB_URL}{path}",
            headers=self.h,
            json=body,
            timeout=20,
            allow_redirects=False,
        )
        reject_write_redirect(r, f"POST {path}")
        if r.status_code >= 400:
            raise RuntimeError(f"POST {path} {r.status_code}: {r.text}")
        return r.json() if r.text else None

    def delete(self, path):
        r = requests.delete(
            f"{SB_URL}{path}",
            headers=self.h,
            timeout=20,
            allow_redirects=False,
        )
        reject_write_redirect(r, f"DELETE {path}")
        if r.status_code >= 400 and r.status_code != 404:
            raise RuntimeError(f"DELETE {path} {r.status_code}: {r.text}")

    def rpc(self, name, params):
        return self.post(f"/rest/v1/rpc/{name}", params)


def preflight_cleanup_channel(api: "API") -> None:
    """Verify the tag-scoped cleanup RPC before seeding any row."""

    probe_tag = f"E2E-{int(time.time())}"
    r = requests.post(
        f"{SB_URL}/rest/v1/rpc/__test_force_delete_e2e_order",
        headers=api.h,
        timeout=10,
        json={"p_order_id": None, "p_product_id": None, "p_tag": probe_tag},
        allow_redirects=False,
    )
    if 300 <= r.status_code < 400:
        print(
            "⛔ Blocked: cleanup channel returned an HTTP redirect; refusing to forward test credentials or writes."
        )
        sys.exit(2)
    if r.status_code == 200:
        return
    print(
        "⛔ Blocked: cleanup channel unavailable — RPC __test_force_delete_e2e_order "
        f"returned {r.status_code}: {r.text[:200]}"
    )
    print("   Refusing to seed test rows that could not be removed.")
    sys.exit(2)


async def main():
    if os.environ.get("LOVABLE_BROWSER_AUTH_STATUS") != "injected":
        fail("LOVABLE_BROWSER_AUTH_STATUS != injected — sign in to the isolated dev app first.")
    storage_key = os.environ["LOVABLE_BROWSER_SUPABASE_STORAGE_KEY"]
    session_json = os.environ["LOVABLE_BROWSER_SUPABASE_SESSION_JSON"]
    session = json.loads(session_json)
    token = session["access_token"]
    user_id = session["user"]["id"]
    api = API(token)

    tid = psql_one(
        f"SELECT id::text FROM public.tenants WHERE owner_user_id='{user_id}' ORDER BY created_at LIMIT 1"
    )
    if not tid:
        fail("No tenant owned by injected user.")
    print(f"→ tenant={tid}  tag={TAG}")

    # Refuse to seed anything we cannot later delete.
    preflight_cleanup_channel(api)
    ok("preflight: E2E cleanup RPC reachable")

    seeded = api.post(
        "/rest/v1/products",
        {
            "tenant_id": tid,
            "name": f"{TAG} منتج",
            "price": float(PRICE),
            "cost": float(COST),
            "stock": STOCK,
            "is_active": True,
            "is_discount": False,
        },
    )
    pid = seeded[0]["id"]
    ok(f"seeded product {pid}")

    tz_expr = f"COALESCE((SELECT timezone FROM public.tenants WHERE id='{tid}'),'UTC')"
    today_expr = f"public.tenant_today('{tid}')"

    def agg_sales():
        return Decimal(
            psql_one(
                f"SELECT COALESCE(SUM(total),0)::text FROM public.orders WHERE tenant_id='{tid}' AND (created_at AT TIME ZONE {tz_expr})::date = {today_expr}"
            )
        )

    def agg_cash():
        return Decimal(
            psql_one(
                f"SELECT COALESCE(SUM(amount),0)::text FROM public.payments WHERE tenant_id='{tid}' AND method='cash' AND (created_at AT TIME ZONE {tz_expr})::date = {today_expr}"
            )
        )

    base_sales, base_cash = agg_sales(), agg_cash()
    print(f"  baseline: sales_today={base_sales}  cash_today={base_cash}")

    order_id = None
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(
                viewport={"width": 1280, "height": 1800},
                locale="ar-LY",
                service_workers="block",
            )
            page = await ctx.new_page()
            browser_isolation_violations: list[str] = []

            async def enforce_browser_isolation(route):
                request = route.request
                if not browser_request_is_isolated(
                    request.method,
                    request.url,
                    request.is_navigation_request(),
                ):
                    browser_isolation_violations.append(f"{request.method} {request.url}")
                    print(
                        f"SEC_ENV_WRITE_HARNESS_BROWSER_BLOCKED: {request.method} {request.url}"
                    )
                    await route.abort("blockedbyclient")
                    return
                await route.continue_()

            await page.route("**/*", enforce_browser_isolation)

            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on(
                "console",
                lambda m: errs.append(m.text) if m.type == "error" else None,
            )

            await page.goto(BASE, wait_until="domcontentloaded")
            await page.evaluate(
                f"window.localStorage.setItem({json.dumps(storage_key)}, {json.dumps(session_json)})"
            )
            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await page.screenshot(path=str(SHOTS / "01_dashboard.png"))

            opened = False
            for name in ["بيع جديد", "بيع سريع"]:
                try:
                    await page.get_by_role("button", name=name).first.click(timeout=2500)
                    opened = True
                    break
                except Exception:
                    pass
            if not opened:
                await page.get_by_text("بيع سريع", exact=False).first.click()
            await page.wait_for_timeout(700)
            await page.screenshot(path=str(SHOTS / "02_sale_open.png"))
            ok("opened sale screen")

            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(SHOTS / "03_added.png"))
            ok("added product")

            await page.get_by_text("إصدار الفاتورة", exact=False).first.click()
            await page.wait_for_timeout(1800)
            await page.screenshot(path=str(SHOTS / "04_after_invoice.png"))
            ok("issued invoice")

            row = psql_one(
                f"""
              SELECT id::text || '|' || total::text || '|' || paid::text || '|' || status || '|' || delivery
              FROM public.orders WHERE tenant_id='{tid}' AND created_at >= now() - interval '2 minutes'
              ORDER BY created_at DESC LIMIT 1
            """
            )
            if not row:
                fail("no order row created")
            order_id, total, paid, status_s, delivery = row.split("|")
            assert (
                Decimal(total) == PRICE
                and Decimal(paid) == PRICE
                and status_s == "paid"
                and delivery == "direct"
            ), row
            ok(
                f"DB order ok (id={order_id[:8]} total={total} paid={paid} {status_s}/{delivery})"
            )

            pay = psql_one(
                f"""
              SELECT kind || '|' || method || '|' || amount::text
              FROM public.payments WHERE order_id='{order_id}' ORDER BY created_at DESC LIMIT 1
            """
            )
            kind, method, amount = pay.split("|")
            assert kind == "sale" and method == "cash" and Decimal(amount) == PRICE, pay
            ok(f"DB payment ok ({kind}/{method}/{amount})")

            new_stock = Decimal(psql_one(f"SELECT stock::text FROM public.products WHERE id='{pid}'"))
            assert new_stock == Decimal(STOCK - 1), f"stock={new_stock} expected {STOCK - 1}"
            ok(f"stock decremented to {new_stock}")

            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=10000)
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(SHOTS / "05_dashboard_after.png"))
            body_text = await page.evaluate("() => document.body.innerText")
            assert agg_sales() - base_sales == PRICE, "sales delta wrong"
            assert agg_cash() - base_cash == PRICE, "cash delta wrong"
            assert "د.ل" in body_text, "currency token missing from dashboard"
            ok(f"dashboard updated (sales +{PRICE}, cash +{PRICE}, currency token present)")

            api.rpc("close_day", {"p_note": TAG})
            snap = psql_one(
                f"""
              SELECT sales::text || '|' || collected::text || '|' || realized_profit::text || '|' ||
                     customer_debts::text || '|' || unsettled_custody::text
              FROM public.day_closes WHERE tenant_id='{tid}' AND note='{TAG}'
              ORDER BY created_at DESC LIMIT 1
            """
            )
            if not snap:
                fail("day_closes row missing")
            s_sales, s_coll, s_profit, s_debts, s_cust = [Decimal(x) for x in snap.split("|")]
            assert s_sales >= PRICE, f"snap.sales={s_sales}"
            assert s_coll >= PRICE, f"snap.collected={s_coll}"
            assert s_profit >= (PRICE - COST), (
                f"snap.realized_profit={s_profit} < {PRICE - COST}"
            )
            ok(
                f"day_close snapshot ok (sales={s_sales}, collected={s_coll}, profit≥{PRICE - COST})"
            )

            if browser_isolation_violations:
                fail(
                    f"browser isolation blocked {len(browser_isolation_violations)} remote request(s)"
                )

            if errs:
                print("⚠ runtime errors during run:")
                for error in errs[:5]:
                    print("  •", error)

            await browser.close()
    finally:
        leaked = False
        try:
            api.rpc(
                "__test_force_delete_e2e_order",
                {
                    "p_order_id": order_id,
                    "p_product_id": pid,
                    "p_tag": TAG,
                },
            )
            left_o = psql_one(
                f"SELECT COUNT(*)::text FROM public.orders WHERE id='{order_id or '00000000-0000-0000-0000-000000000000'}'"
            )
            left_p = psql_one(f"SELECT COUNT(*)::text FROM public.products WHERE id='{pid}'")
            left_d = psql_one(
                f"SELECT COUNT(*)::text FROM public.day_closes WHERE tenant_id='{tid}' AND note='{TAG}'"
            )
            if left_o != "0" or left_p != "0" or left_d != "0":
                leaked = True
                print(
                    f"❌ cleanup leftover: orders={left_o} products={left_p} day_closes={left_d}"
                )
            else:
                print("🧹 cleanup ok (order, product, day_close removed)")
        except Exception as error:
            leaked = True
            print(f"❌ cleanup error: {error}")
        if leaked:
            sys.exit(1)

    print("\n🎉 E2E PASSED — sale → dashboard → day_close all verified.")


if __name__ == "__main__":
    asyncio.run(main())
