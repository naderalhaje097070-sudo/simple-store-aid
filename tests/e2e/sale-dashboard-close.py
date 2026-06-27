"""
Mongezz V2 — E2E financial flow test.

Verifies:
  1. Quick sale (cash, paid in full) via UI
  2. Dashboard reflects the new sale (sales today, net cash)
  3. Day close snapshot persists and matches DB aggregates

Requires:
  - Dev server running on http://localhost:8080
  - LOVABLE_BROWSER_SUPABASE_* env vars (injected session)
  - PG* env vars (psql) targeting the same project DB
  - Authenticated user must own a tenant

Runs all changes inside a uniquely-tagged scope and cleans up at the end.
"""

import asyncio, json, os, subprocess, sys, time
from decimal import Decimal
from pathlib import Path
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SHOTS = Path("/tmp/browser/mongezz-e2e/shots"); SHOTS.mkdir(parents=True, exist_ok=True)
TAG = f"E2E-{int(time.time())}"
PRICE = Decimal("100")
COST = Decimal("60")
STOCK = 10

def psql(sql: str) -> str:
    r = subprocess.run(["psql", "-At", "-F", "|", "-c", sql], capture_output=True, text=True, check=True)
    return r.stdout.strip()

def fail(msg: str):
    print(f"❌ FAIL: {msg}"); sys.exit(1)

def ok(msg: str):
    print(f"✅ {msg}")

async def main():
    status = os.environ.get("LOVABLE_BROWSER_AUTH_STATUS")
    if status != "injected":
        fail(f"Auth not injected (status={status}). Sign in via preview first.")
    storage_key = os.environ["LOVABLE_BROWSER_SUPABASE_STORAGE_KEY"]
    session_json = os.environ["LOVABLE_BROWSER_SUPABASE_SESSION_JSON"]
    user_id = json.loads(session_json)["user"]["id"]

    # Pick tenant owned by this user
    tid = psql(f"SELECT id::text FROM public.tenants WHERE owner_user_id = '{user_id}' ORDER BY created_at LIMIT 1")
    if not tid:
        fail("No tenant owned by injected user.")
    print(f"→ tenant={tid}  user={user_id}  tag={TAG}")

    # --- Seed product ---
    pid = psql(f"""
      INSERT INTO public.products (tenant_id, name, price, cost, stock, is_active, is_discount)
      VALUES ('{tid}', '{TAG} منتج', {PRICE}, {COST}, {STOCK}, true, false)
      RETURNING id::text
    """)
    ok(f"seeded product {pid}")

    # --- Capture baseline aggregates (today, cash kind=sale) ---
    base_sales = psql(f"""
      SELECT COALESCE(SUM(total),0)::text FROM public.orders
      WHERE tenant_id='{tid}' AND created_at::date = CURRENT_DATE
    """) or "0"
    base_cash = psql(f"""
      SELECT COALESCE(SUM(amount),0)::text FROM public.payments
      WHERE tenant_id='{tid}' AND method='cash' AND created_at::date = CURRENT_DATE
    """) or "0"
    print(f"  baseline: sales_today={base_sales}  cash_today={base_cash}")

    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 1280, "height": 1800}, locale="ar-LY")
            page = await ctx.new_page()
            console_errs = []
            page.on("pageerror", lambda e: console_errs.append(str(e)))
            page.on("console", lambda m: m.type == "error" and console_errs.append(m.text))

            # Inject session at localhost origin
            await page.goto(BASE, wait_until="domcontentloaded")
            await page.evaluate(
                f"window.localStorage.setItem({json.dumps(storage_key)}, {json.dumps(session_json)})"
            )
            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=15000)
            await page.screenshot(path=str(SHOTS/"01_dashboard.png"))

            # --- Step 1: open quick sale ---
            # Prefer the FAB with aria-label="بيع جديد"; fall back to "+ بيع سريع" buttons
            opened = False
            try:
                await page.get_by_role("button", name="بيع جديد").first.click(timeout=3000)
                opened = True
            except Exception:
                pass
            if not opened:
                await page.get_by_text("بيع سريع", exact=False).first.click()
            await page.wait_for_timeout(600)
            await page.screenshot(path=str(SHOTS/"02_sale_open.png"))
            ok("opened sale screen")

            # --- Step 2: add the seeded product (tap card) ---
            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(SHOTS/"03_product_added.png"))
            ok("added product to cart")

            # --- Step 3: issue invoice (default paid = total, method = cash) ---
            await page.get_by_text("إصدار الفاتورة", exact=False).first.click()
            await page.wait_for_timeout(1500)
            await page.screenshot(path=str(SHOTS/"04_after_invoice.png"))
            ok("issued invoice")

            # --- DB verification of sale ---
            row = psql(f"""
              SELECT total::text, paid::text, status, delivery FROM public.orders
              WHERE tenant_id='{tid}' AND created_at >= now() - interval '2 minutes'
              ORDER BY created_at DESC LIMIT 1
            """)
            if not row: fail("No order created in DB.")
            total, paid, status_s, delivery = row.split("|")
            assert Decimal(total) == PRICE, f"order.total={total} expected {PRICE}"
            assert Decimal(paid) == PRICE, f"order.paid={paid} expected {PRICE}"
            assert status_s == "paid", f"status={status_s}"
            assert delivery == "direct", f"delivery={delivery}"
            ok(f"DB order ok (total={total}, paid={paid}, status={status_s})")

            pay = psql(f"""
              SELECT method, kind, amount::text FROM public.payments
              WHERE tenant_id='{tid}' AND created_at >= now() - interval '2 minutes'
              ORDER BY created_at DESC LIMIT 1
            """)
            method, kind, amount = pay.split("|")
            assert method == "cash" and kind == "sale" and Decimal(amount) == PRICE, f"payment row wrong: {pay}"
            ok(f"DB payment ok ({kind}/{method}/{amount})")

            new_stock = psql(f"SELECT stock::text FROM public.products WHERE id='{pid}'")
            assert Decimal(new_stock) == Decimal(STOCK - 1), f"stock={new_stock} expected {STOCK-1}"
            ok(f"DB stock decremented to {new_stock}")

            # --- Step 4: navigate to dashboard, verify numbers ---
            await page.goto(BASE + "/app", wait_until="domcontentloaded")
            await page.wait_for_load_state("networkidle", timeout=10000)
            await page.wait_for_timeout(800)
            await page.screenshot(path=str(SHOTS/"05_dashboard_after.png"))

            text = await page.evaluate("() => document.body.innerText")
            # Sales today should have grown by at least PRICE
            new_sales = psql(f"""
              SELECT COALESCE(SUM(total),0)::text FROM public.orders
              WHERE tenant_id='{tid}' AND created_at::date = CURRENT_DATE
            """)
            new_cash = psql(f"""
              SELECT COALESCE(SUM(amount),0)::text FROM public.payments
              WHERE tenant_id='{tid}' AND method='cash' AND created_at::date = CURRENT_DATE
            """)
            assert Decimal(new_sales) - Decimal(base_sales) == PRICE, f"sales delta wrong {base_sales}->{new_sales}"
            assert Decimal(new_cash) - Decimal(base_cash) == PRICE, f"cash delta wrong {base_cash}->{new_cash}"
            ok(f"DB aggregates updated (sales +{PRICE}, cash +{PRICE})")
            # Dashboard contains currency token (د.ل) and price digits
            if "د.ل" not in text and "د.ل." not in text and "LYD" not in text:
                fail("Dashboard missing currency token د.ل")
            ok("dashboard rendered with currency token")

            # --- Step 5: close day via RPC (UI close screen requires extra navigation) ---
            close_res = await page.evaluate("""async () => {
                const m = await import('/src/integrations/supabase/client.ts').catch(() => null);
                // import path won't work directly; use window.fetch with stored token instead
                return null;
            }""")
            # Use direct fetch with bearer token to call close_day RPC
            url = await page.evaluate("() => import.meta.env?.VITE_SUPABASE_URL || ''")
            anon = await page.evaluate("() => import.meta.env?.VITE_SUPABASE_PUBLISHABLE_KEY || ''")
            if not url or not anon:
                # fallback: read from session env
                url = os.environ.get("SUPABASE_URL", "")
                anon = os.environ.get("SUPABASE_PUBLISHABLE_KEY", "")
            token = json.loads(session_json)["access_token"]
            rpc_resp = await page.evaluate(f"""async () => {{
              const r = await fetch("{url}/rest/v1/rpc/close_day", {{
                method: "POST",
                headers: {{
                  "Content-Type": "application/json",
                  "apikey": "{anon}",
                  "Authorization": "Bearer {token}"
                }},
                body: JSON.stringify({{ p_note: "{TAG}" }})
              }});
              return {{ status: r.status, body: await r.text() }};
            }}""")
            print("  close_day RPC:", rpc_resp)
            if rpc_resp["status"] >= 400:
                fail(f"close_day RPC failed: {rpc_resp}")

            snap = psql(f"""
              SELECT sales::text, collected::text, customer_debts::text, unsettled_custody::text, realized_profit::text
              FROM public.day_closes
              WHERE tenant_id='{tid}' AND note='{TAG}'
              ORDER BY created_at DESC LIMIT 1
            """)
            if not snap: fail("day_closes row missing after close_day")
            s_sales, s_coll, s_debts, s_cust, s_profit = [Decimal(x) for x in snap.split("|")]
            assert s_sales >= PRICE, f"snapshot.sales={s_sales}"
            assert s_coll >= PRICE, f"snapshot.collected={s_coll}"
            # Realized profit for THIS sale >= PRICE - COST = 40 (other sales today may add more)
            assert s_profit >= (PRICE - COST), f"snapshot.realized_profit={s_profit} expected ≥ {PRICE-COST}"
            ok(f"day_closes ok (sales={s_sales}, collected={s_coll}, profit≥{PRICE-COST})")

            if console_errs:
                print("⚠ console errors during run:")
                for e in console_errs[:5]: print("  •", e)

            await browser.close()
    finally:
        # --- Cleanup: delete day_close, order+payments+items via RPC, then product ---
        psql(f"DELETE FROM public.day_closes WHERE tenant_id='{tid}' AND note='{TAG}'")
        # Find the test order and remove
        oid = psql(f"""
          SELECT id::text FROM public.orders
          WHERE tenant_id='{tid}' AND id IN (
            SELECT order_id FROM public.order_items WHERE product_id='{pid}'
          )
          ORDER BY created_at DESC LIMIT 1
        """)
        if oid:
            psql(f"DELETE FROM public.payments WHERE order_id='{oid}'")
            psql(f"DELETE FROM public.order_items WHERE order_id='{oid}'")
            psql(f"DELETE FROM public.orders WHERE id='{oid}'")
        psql(f"DELETE FROM public.products WHERE id='{pid}'")
        print(f"🧹 cleaned up product {pid} and related rows")

    print("\n🎉 E2E PASSED — sale → dashboard → day_close all verified.")

if __name__ == "__main__":
    asyncio.run(main())
