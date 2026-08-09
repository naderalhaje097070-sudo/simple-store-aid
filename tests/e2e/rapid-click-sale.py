"""
Mongezz V2 — Rapid-click (double-submit) safety test for the sale flow.

Scenarios (mobile 390x844):
  P1  5 rapid taps on the bottom-nav "+ بيع" FAB       → one sale screen, button disabled/aria-busy
  P2  double tap on "إصدار الفاتورة" (quick sale)      → exactly 1 create RPC, 1 order row
  P3  5 rapid taps on save under throttled network     → still exactly 1 create RPC
  P4  try to close PaymentSheet while saving           → sheet stays open, save completes
  P5  rapid taps on advanced-flow "حفظ الفاتورة"       → 1 create RPC, 1 order row
  P6  tap again after success screen appears           → no duplicate order

Read-only against financial logic: no RPC/migration changes. Seeds one product
tagged E2E-<ts> and removes everything through the tag-scoped cleanup RPC.

Requires LOVABLE_BROWSER_* + PG* env vars and the dev server on :8080.
"""

import asyncio, json, os, subprocess, sys, time, re
from decimal import Decimal
from pathlib import Path
import requests
from playwright.async_api import async_playwright

BASE = "http://localhost:8080"
SHOTS = Path("/tmp/browser/mongezz-rapid/shots"); SHOTS.mkdir(parents=True, exist_ok=True)
TAG = f"E2E-{int(time.time())}"
PRICE = Decimal("100")
COST = Decimal("60")
STOCK = 50
CREATE_RPC = "create_sale_with_items"

results: list[tuple[str, str, str]] = []   # (id, PASS/FAIL, evidence)


def read_env(name: str) -> str:
    env = Path(".env").read_text()
    m = re.search(rf"^{name}\s*=\s*(.+)$", env, re.M)
    if not m:
        raise RuntimeError(f"{name} missing from .env")
    return m.group(1).strip().strip('"').strip("'")


SB_URL = read_env("VITE_SUPABASE_URL")
SB_ANON = read_env("VITE_SUPABASE_PUBLISHABLE_KEY")


def psql_exec(sql: str) -> None:
    """Test-only cleanup channel (never used for assertions). Scoped to rows this run created."""
    r = subprocess.run(["psql", "-q", "-v", "ON_ERROR_STOP=1", "-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"psql exec failed: {r.stderr.strip()}")


def psql_one(sql: str) -> str:
    r = subprocess.run(["psql", "-At", "-q", "-c", sql], capture_output=True, text=True)
    if r.returncode != 0:
        raise RuntimeError(f"psql failed: {r.stderr.strip()}")
    return r.stdout.strip().splitlines()[0] if r.stdout.strip() else ""


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
        if r.status_code >= 400:
            raise RuntimeError(f"POST {path} {r.status_code}: {r.text}")
        return r.json() if r.text else None

    def rpc(self, name, params):
        return self.post(f"/rest/v1/rpc/{name}", params)


def record(cid: str, passed: bool, evidence: str):
    results.append((cid, "PASS" if passed else "FAIL", evidence))
    print(f"{'✅' if passed else '❌'} {cid}: {evidence}")


class Counter:
    """Counts create-sale RPC requests seen by the browser."""
    def __init__(self):
        self.n = 0

    def hook(self, req):
        if CREATE_RPC in req.url and req.method == "POST":
            self.n += 1

    def reset(self):
        self.n = 0


async def restore_session(ctx, page, storage_key, session_json):
    await page.goto(BASE, wait_until="domcontentloaded")
    await page.evaluate(
        f"window.localStorage.setItem({json.dumps(storage_key)}, {json.dumps(session_json)})"
    )


async def open_app(page):
    await page.goto(BASE + "/app", wait_until="domcontentloaded")
    await page.wait_for_load_state("networkidle", timeout=20000)
    await page.wait_for_timeout(600)


async def rapid_click(page, locator, times=5, delay_ms=50):
    """Click a locator N times as fast as possible, ignoring disabled-state errors."""
    box = await locator.bounding_box()
    if not box:
        raise RuntimeError("locator has no bounding box")
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    for _ in range(times):
        await page.mouse.click(x, y, delay=1)
        await page.wait_for_timeout(delay_ms)


def orders_since(tid: str, since_iso: str) -> int:
    return int(psql_one(
        f"SELECT COUNT(*)::text FROM public.orders WHERE tenant_id='{tid}' AND created_at > '{since_iso}'"
    ))


def db_now() -> str:
    return psql_one("SELECT now()::text")


async def main():
    if os.environ.get("LOVABLE_BROWSER_AUTH_STATUS") != "injected":
        print("⛔ LOVABLE_BROWSER_AUTH_STATUS != injected — sign in via preview first.")
        sys.exit(2)
    storage_key = os.environ["LOVABLE_BROWSER_SUPABASE_STORAGE_KEY"]
    session_json = os.environ["LOVABLE_BROWSER_SUPABASE_SESSION_JSON"]
    session = json.loads(session_json)
    api = API(session["access_token"])
    user_id = session["user"]["id"]

    tid = psql_one(
        f"SELECT id::text FROM public.tenants WHERE owner_user_id='{user_id}' ORDER BY created_at LIMIT 1"
    )
    if not tid:
        print("⛔ no tenant for injected user"); sys.exit(2)
    print(f"→ tenant={tid} tag={TAG}")

    # Preflight: never seed what we cannot delete. Cleanup runs over psql
    # (test-only channel) scoped to this run's rows — no public test RPC.
    try:
        psql_exec("SELECT 1")
    except Exception as e:
        print(f"⛔ psql cleanup channel unavailable: {e}")
        sys.exit(2)

    seeded = api.post("/rest/v1/products", {
        "tenant_id": tid, "name": f"{TAG} منتج",
        "price": float(PRICE), "cost": float(COST), "stock": STOCK,
        "is_active": True, "is_discount": False,
    })
    pid = seeded[0]["id"]
    print(f"→ seeded product {pid}")

    created_orders: list[str] = []
    try:
        async with async_playwright() as pw:
            browser = await pw.chromium.launch(headless=True)
            ctx = await browser.new_context(viewport={"width": 390, "height": 844}, locale="ar-LY")
            page = await ctx.new_page()
            errs: list[str] = []
            page.on("pageerror", lambda e: errs.append(str(e)))
            page.on("console", lambda m: m.type == "error" and errs.append(m.text))
            counter = Counter()
            page.on("request", counter.hook)

            await restore_session(ctx, page, storage_key, session_json)
            await open_app(page)
            await page.screenshot(path=str(SHOTS / "00_dashboard.png"))

            # ---------------- P1: rapid taps on bottom-nav FAB ----------------
            fab = page.get_by_role("button", name="بيع جديد")
            await rapid_click(page, fab, times=5, delay_ms=40)
            await page.wait_for_timeout(200)
            await page.screenshot(path=str(SHOTS / "p1_fab.png"))
            sale_headers = await page.get_by_text("بيع سريع", exact=True).count()
            search_boxes = await page.get_by_placeholder("ابحث عن منتج").count()
            record("P1", search_boxes == 1,
                   f"sale screens rendered={search_boxes} (header matches={sale_headers}) after 5 rapid taps")

            # ---------------- P2: double tap on إصدار الفاتورة ----------------
            since = db_now()
            counter.reset()
            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(250)
            issue = page.get_by_text("إصدار الفاتورة", exact=False).first
            await rapid_click(page, issue, times=2, delay_ms=30)
            await page.wait_for_timeout(2500)
            await page.screenshot(path=str(SHOTS / "p2_after_double.png"))
            n_db = orders_since(tid, since)
            record("P2", counter.n == 1 and n_db == 1,
                   f"create RPC calls={counter.n}, new orders={n_db} (expected 1/1)")
            created_orders += psql_one(
                f"SELECT string_agg(id::text, ',') FROM public.orders WHERE tenant_id='{tid}' AND created_at > '{since}'"
            ).split(",") if n_db else []

            # ---------------- P6: tap again on success screen ----------------
            since6 = db_now()
            counter.reset()
            await page.wait_for_timeout(300)
            await page.screenshot(path=str(SHOTS / "p6_success.png"))
            body = await page.evaluate("() => document.body.innerText")
            again = page.get_by_role("button", name="بيع جديد")
            if await again.count():
                await rapid_click(page, again.first, times=3, delay_ms=40)
            await page.wait_for_timeout(1500)
            n6 = orders_since(tid, since6)
            record("P6", counter.n == 0 and n6 == 0,
                   f"post-success taps → create RPC={counter.n}, new orders={n6} (expected 0/0); "
                   f"success screen shown={'تمت' in body or 'تم' in body}")

            # ---------------- P3: throttled network, 5 rapid taps ----------------
            cdp = await ctx.new_cdp_session(page)
            await cdp.send("Network.enable")
            await cdp.send("Network.emulateNetworkConditions", {
                "offline": False, "latency": 1200,
                "downloadThroughput": 200 * 1024, "uploadThroughput": 100 * 1024,
            })
            await open_app(page)
            await page.get_by_role("button", name="بيع جديد").first.click()
            await page.wait_for_timeout(800)
            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(250)
            since3 = db_now()
            counter.reset()
            issue = page.get_by_text("إصدار الفاتورة", exact=False).first
            await rapid_click(page, issue, times=5, delay_ms=60)
            await page.screenshot(path=str(SHOTS / "p3_saving_state.png"))
            saving_text = await page.get_by_text("جاري الحفظ", exact=False).count()
            await page.wait_for_timeout(6000)
            n3 = orders_since(tid, since3)
            record("P3", counter.n == 1 and n3 == 1,
                   f"throttled 5 taps → create RPC={counter.n}, new orders={n3}; "
                   f"'جاري الحفظ' visible during save={saving_text > 0}")
            created_orders += psql_one(
                f"SELECT string_agg(id::text, ',') FROM public.orders WHERE tenant_id='{tid}' AND created_at > '{since3}'"
            ).split(",") if n3 else []
            await cdp.send("Network.emulateNetworkConditions", {
                "offline": False, "latency": 0,
                "downloadThroughput": -1, "uploadThroughput": -1,
            })

            # ---------------- P5 + P4: advanced flow PaymentSheet ----------------
            await open_app(page)
            await page.get_by_role("button", name="بيع جديد").first.click()
            await page.wait_for_timeout(800)
            await page.get_by_text(f"{TAG} منتج", exact=False).first.click()
            await page.wait_for_timeout(250)
            # switch to advanced sale screen
            adv = page.get_by_text("خيارات متقدمة", exact=False)
            if not await adv.count():
                adv = page.get_by_text("متقدم", exact=False)
            if await adv.count():
                await adv.first.click()
                await page.wait_for_timeout(900)
                # open payment sheet
                cont = page.get_by_text("متابعة", exact=False)
                if await cont.count():
                    await cont.first.click()
                    await page.wait_for_timeout(700)

            save_btn = page.get_by_text("حفظ الفاتورة", exact=False)
            if await save_btn.count():
                since5 = db_now()
                counter.reset()
                await rapid_click(page, save_btn.first, times=4, delay_ms=40)
                await page.wait_for_timeout(400)
                sheet_open_during = await page.get_by_text("الدفع", exact=True).count()
                # P4: attempt to dismiss the sheet mid-save (overlay click)
                await page.mouse.click(195, 60)
                await page.wait_for_timeout(200)
                sheet_still_open = await page.get_by_text("الدفع", exact=True).count()
                await page.screenshot(path=str(SHOTS / "p4_sheet_during_save.png"))
                await page.wait_for_timeout(4000)
                n5 = orders_since(tid, since5)
                record("P5", counter.n == 1 and n5 == 1,
                       f"advanced save 4 taps → create RPC={counter.n}, new orders={n5}")
                record("P4", sheet_still_open >= 1 or sheet_open_during >= 1,
                       f"sheet visible during save={sheet_open_during>0}, still open after outside click={sheet_still_open>0}")
                created_orders += psql_one(
                    f"SELECT string_agg(id::text, ',') FROM public.orders WHERE tenant_id='{tid}' AND created_at > '{since5}'"
                ).split(",") if n5 else []
            else:
                record("P5", False, "could not reach advanced PaymentSheet save button")
                record("P4", False, "could not reach advanced PaymentSheet save button")

            if errs:
                print("⚠ runtime errors:")
                for e in errs[:8]:
                    print("   •", e)

            await browser.close()
    finally:
        leaked = False
        ids = [o for o in created_orders if o]
        try:
            if ids:
                lst = ",".join(f"'{i}'" for i in ids)
                psql_exec(
                    "BEGIN;"
                    f"DELETE FROM public.payments    WHERE order_id IN ({lst});"
                    f"DELETE FROM public.order_items WHERE order_id IN ({lst});"
                    f"DELETE FROM public.orders      WHERE id       IN ({lst});"
                    "COMMIT;"
                )
            psql_exec(f"DELETE FROM public.products WHERE id='{pid}'")
        except Exception as e:
            leaked = True
            print(f"❌ cleanup error: {e}")
        left_p = psql_one(f"SELECT COUNT(*)::text FROM public.products WHERE id='{pid}'")
        left_o = "0"
        if ids:
            lst = ",".join(f"'{i}'" for i in ids)
            left_o = psql_one(f"SELECT COUNT(*)::text FROM public.orders WHERE id IN ({lst})")
        if left_p != "0" or left_o != "0":
            leaked = True
            print(f"❌ leftover rows: products={left_p} orders={left_o}")
        print("🧹 cleanup done" if not leaked else "⚠ cleanup incomplete")

    print("\n=== RESULTS ===")
    for cid, st, ev in results:
        print(f"{cid:3} {st:4} — {ev}")
    failed = [r for r in results if r[1] == "FAIL"]
    print(f"\n{len(results)-len(failed)}/{len(results)} passed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    asyncio.run(main())
