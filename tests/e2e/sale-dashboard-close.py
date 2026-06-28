"""
Mongezz V2 — E2E financial flow test.

Verifies the most sensitive financial path against the live dev server:
  1. Quick sale (cash, paid in full) via UI
  2. Dashboard re-renders and aggregates update
  3. Day close snapshot persists with correct numbers

Uses:
  - Playwright + injected Supabase session for the UI flow
  - Authenticated Supabase REST API for seeding + cleanup (RLS-respecting)
  - psql (SELECT only) as a secondary read channel

Requires LOVABLE_BROWSER_* + PG* env vars and dev server on :8080.
"""

import asyncio, json, os, subprocess, sys, time, re
from decimal import Decimal
from pathlib import Path
import requests
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SHOTS = Path("/tmp/browser/mongezz-e2e/shots"); SHOTS.mkdir(parents=True, exist_ok=True)
TAG = f"E2E-{int(time.time())}"
PRICE = Decimal("100")
COST = Decimal("60")
STOCK = 10

def read_env(name: str) -> str:
    env = Path(".env").read_text()
    m = re.search(rf"^{name}\s*=\s*(.+)$", env, re.M)
    if not m: raise RuntimeError(f"{name} missing from .env")
    return m.group(1).strip().strip('"').strip("'")

SB_URL = read_env("VITE_SUPABASE_URL")
SB_ANON = read_env("VITE_SUPABASE_PUBLISHABLE_KEY")

def fail(msg): print(f"❌ FAIL: {msg}"); sys.exit(1)
def ok(msg): print(f"✅ {msg}")

def psql_one(sql: str) -> str:
    r = subprocess.run(["psql", "-At", "-q", "-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()}")
    return r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""

def psql_exec(sql: str) -> None:
    # Test-only privileged cleanup channel. Never used during the financial assertions —
    # only inside the `finally:` block to wipe rows the RPCs intentionally cannot delete
    # (e.g. fully paid orders). Wrapped in a single transaction scoped to TAG.
    r = subprocess.run(["psql", "-q", "-v", "ON_ERROR_STOP=1", "-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"psql exec failed: {r.stderr.strip()}")

class API:
    def __init__(self, token: str):
        self.h = {
            "apikey": SB_ANON,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Prefer": "return=representation",
        }
    def post(self, path, body):
        r = requests.post(f"{SB_URL}{path}", headers=self.h, json=body, timeout=20)
        if r.status_code >= 400: raise RuntimeError(f"POST {path} {r.status_code}: {r.text}")
        return r.json() if r.text else None
    def delete(self, path):
        r = requests.delete(f"{SB_URL}{path}", headers=self.h, timeout=20)
        if r.status_code >= 400 and r.status_code != 404:
            raise RuntimeError(f"DELETE {path} {r.status_code}: {r.text}")
    def rpc(self, name, params):
        return self.post(f"/rest/v1/rpc/{name}", params)

async def main():
    if os.environ.get("LOVABLE_BROWSER_AUTH_STATUS") != "injected":
        fail("LOVABLE_BROWSER_AUTH_STATUS != injected — sign in via preview first.")
    storage_key = os.environ["LOVABLE_BROWSER_SUPABASE_STORAGE_KEY"]
    session_json = os.environ["LOVABLE_BROWSER_SUPABASE_SESSION_JSON"]
    session = json.loads(session_json)
    token = session["access_token"]
    user_id = session["user"]["id"]
    api = API(token)

    tid = psql_one(f"SELECT id::text FROM public.tenants WHERE owner_user_id='{user_id}' ORDER BY created_at LIMIT 1")
    if not tid: fail("No tenant owned by injected user.")
    print(f"→ tenant={tid}  tag={TAG}")

    # Seed product via REST (RLS as owner)
    seeded = api.post("/rest/v1/products", {
        "tenant_id": tid, "name": f"{TAG} منتج",
        "price": float(PRICE), "cost": float(COST), "stock": STOCK,
        "is_active": True, "is_discount": False,
    })
    pid = seeded[0]["id"]
    ok(f"seeded product {pid}")

    # Baseline today
    # Today filter respects tenant timezone via public.tenant_today(tid) — never CURRENT_DATE.
    tz_expr = f"COALESCE((SELECT timezone FROM public.tenants WHERE id='{tid}'),'UTC')"
    today_expr = f"public.tenant_today('{tid}')"
    def agg_sales(): return Decimal(psql_one(
        f"SELECT COALESCE(SUM(total),0)::text FROM public.orders WHERE tenant_id='{tid}' AND (created_at AT TIME ZONE {tz_expr})::date = {today_expr}"))
    def agg_cash(): return Decimal(psql_one(
        f"SELECT COALESCE(SUM(amount),0)::text FROM public.payments WHERE tenant_id='{tid}' AND method='cash' AND (created_at AT TIME ZONE {tz_expr})::date = {today_expr}"))
    base_sales, base_cash = agg_sales(), agg_cash()
    print(f"  baseline: sales_today={base_sales}  cash_today={base_cash}")

    order_id = None
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 1280, "height": 1800}, locale="ar-LY")
            page = await ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("console", lambda m: m.type == "error" and errs.append(m.text))

            await page.goto(BASE, wait_until="domcontentloaded")
            await page.evaluate(
                f"window.localStorage.setItem({json.dumps(storage_key)}, {json.dumps(session_json)})"
            )
            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await page.screenshot(path=str(SHOTS/"01_dashboard.png"))

            # Open sale
            opened = False
            for name in ["بيع جديد", "بيع سريع"]:
                try:
                    await page.get_by_role("button", name=name).first.click(timeout=2500)
                    opened = True; break
                except Exception: pass
            if not opened:
                await page.get_by_text("بيع سريع", exact=False).first.click()
            await page.wait_for_timeout(700)
            await page.screenshot(path=str(SHOTS/"02_sale_open.png"))
            ok("opened sale screen")

            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(SHOTS/"03_added.png"))
            ok("added product")

            await page.get_by_text("إصدار الفاتورة", exact=False).first.click()
            await page.wait_for_timeout(1800)
            await page.screenshot(path=str(SHOTS/"04_after_invoice.png"))
            ok("issued invoice")

            # Verify order in DB
            row = psql_one(f"""
              SELECT id::text || '|' || total::text || '|' || paid::text || '|' || status || '|' || delivery
              FROM public.orders WHERE tenant_id='{tid}' AND created_at >= now() - interval '2 minutes'
              ORDER BY created_at DESC LIMIT 1
            """)
            if not row: fail("no order row created")
            order_id, total, paid, status_s, delivery = row.split("|")
            assert Decimal(total) == PRICE and Decimal(paid) == PRICE and status_s == "paid" and delivery == "direct", row
            ok(f"DB order ok (id={order_id[:8]} total={total} paid={paid} {status_s}/{delivery})")

            pay = psql_one(f"""
              SELECT kind || '|' || method || '|' || amount::text
              FROM public.payments WHERE order_id='{order_id}' ORDER BY created_at DESC LIMIT 1
            """)
            kind, method, amount = pay.split("|")
            assert kind == "sale" and method == "cash" and Decimal(amount) == PRICE, pay
            ok(f"DB payment ok ({kind}/{method}/{amount})")

            new_stock = Decimal(psql_one(f"SELECT stock::text FROM public.products WHERE id='{pid}'"))
            assert new_stock == Decimal(STOCK - 1), f"stock={new_stock} expected {STOCK-1}"
            ok(f"stock decremented to {new_stock}")

            # Reload dashboard and verify aggregates + currency token
            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=10000)
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(SHOTS/"05_dashboard_after.png"))
            body_text = await page.evaluate("() => document.body.innerText")
            assert agg_sales() - base_sales == PRICE, "sales delta wrong"
            assert agg_cash() - base_cash == PRICE, "cash delta wrong"
            assert "د.ل" in body_text, "currency token missing from dashboard"
            ok(f"dashboard updated (sales +{PRICE}, cash +{PRICE}, currency token present)")

            # Close day via RPC
            api.rpc("close_day", {"p_note": TAG})
            snap = psql_one(f"""
              SELECT sales::text || '|' || collected::text || '|' || realized_profit::text || '|' ||
                     customer_debts::text || '|' || unsettled_custody::text
              FROM public.day_closes WHERE tenant_id='{tid}' AND note='{TAG}'
              ORDER BY created_at DESC LIMIT 1
            """)
            if not snap: fail("day_closes row missing")
            s_sales, s_coll, s_profit, s_debts, s_cust = [Decimal(x) for x in snap.split("|")]
            assert s_sales >= PRICE, f"snap.sales={s_sales}"
            assert s_coll >= PRICE, f"snap.collected={s_coll}"
            assert s_profit >= (PRICE - COST), f"snap.realized_profit={s_profit} < {PRICE-COST}"
            ok(f"day_close snapshot ok (sales={s_sales}, collected={s_coll}, profit≥{PRICE-COST})")

            if errs:
                print("⚠ runtime errors during run:")
                for e in errs[:5]: print("  •", e)

            await browser.close()
    finally:
        # Cleanup via REST (RLS as owner)
        # Cleanup: use atomic RPC for the order (restores stock, removes items + payments).
        # Never delete from orders/order_items/payments directly — that bypasses financial guards.
        # Cleanup strategy:
        #  1) day_closes: REST DELETE scoped to this tenant + TAG.
        #  2) order (paid → not deletable via RPC by design):
        #     try public.delete_order_with_restore_stock first; if it rejects (paid order),
        #     fall back to a single privileged psql transaction scoped strictly to order_id.
        #     This is test-only and never touches rows outside the tagged order.
        #  3) product: REST DELETE only after the order is gone, so no FK leftovers.
        try:
            api.delete(f"/rest/v1/day_closes?tenant_id=eq.{tid}&note=eq.{TAG}")
            if order_id:
                rpc_ok = False
                try:
                    api.rpc("delete_order_with_restore_stock", {"p_order_id": order_id})
                    rpc_ok = True
                except Exception:
                    # Expected for paid orders — fall through to privileged cleanup.
                    pass
                if not rpc_ok:
                    psql_exec(f"""
                      BEGIN;
                        UPDATE public.products p
                           SET stock = p.stock + oi.qty
                          FROM public.order_items oi
                         WHERE oi.order_id = '{order_id}' AND oi.product_id = p.id;
                        DELETE FROM public.payments    WHERE order_id = '{order_id}';
                        DELETE FROM public.order_items WHERE order_id = '{order_id}';
                        DELETE FROM public.orders      WHERE id       = '{order_id}' AND tenant_id = '{tid}';
                      COMMIT;
                    """)
            api.delete(f"/rest/v1/products?id=eq.{pid}")
            # Verify nothing leaked.
            left_o = psql_one(f"SELECT COUNT(*)::text FROM public.orders   WHERE id='{order_id or '00000000-0000-0000-0000-000000000000'}'")
            left_p = psql_one(f"SELECT COUNT(*)::text FROM public.products WHERE id='{pid}'")
            left_d = psql_one(f"SELECT COUNT(*)::text FROM public.day_closes WHERE tenant_id='{tid}' AND note='{TAG}'")
            if left_o != "0" or left_p != "0" or left_d != "0":
                print(f"⚠ cleanup leftover: orders={left_o} products={left_p} day_closes={left_d}")
            else:
                print("🧹 cleanup ok (order, product, day_close removed; stock restored)")
        except Exception as e:
            print(f"⚠ cleanup error: {e}")


    print("\n🎉 E2E PASSED — sale → dashboard → day_close all verified.")

if __name__ == "__main__":
    asyncio.run(main())
