import asyncio
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright

BASE = os.environ.get("SMOKE_BASE_URL", "https://mongzz.lovable.app").rstrip("/")
OUT = Path(os.environ.get("SMOKE_OUT", "/tmp/mongzz-public-smoke"))
OUT.mkdir(parents=True, exist_ok=True)

TARGETS = [
    ("landing", "/"),
    ("auth", "/auth"),
    ("guide", "/guide"),
    ("app_redirect", "/app"),
]
VIEWPORTS = [
    ("desktop_1440", 1440, 900),
    ("mobile_390", 390, 844),
    ("mobile_360", 360, 780),
]

async def run() -> None:
    results = []
    failures = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        for viewport_name, width, height in VIEWPORTS:
            context = await browser.new_context(
                viewport={"width": width, "height": height}, locale="ar-LY"
            )
            page = await context.new_page()
            browser_errors = []
            page.on("pageerror", lambda exc: browser_errors.append(("pageerror", str(exc))))
            page.on("console", lambda msg: msg.type == "error" and browser_errors.append(("console", msg.text)))

            for page_name, path in TARGETS:
                browser_errors.clear()
                response = None
                navigation_error = None
                requested_url = BASE + path
                try:
                    response = await page.goto(
                        requested_url, wait_until="domcontentloaded", timeout=30000
                    )
                    await page.wait_for_timeout(1500)
                except Exception as exc:
                    navigation_error = str(exc)

                shot = OUT / f"{viewport_name}_{page_name}.png"
                await page.screenshot(path=str(shot), full_page=True)
                info = await page.evaluate("""() => {
                    const html = document.documentElement;
                    const body = document.body;
                    const text = (body?.innerText || '').trim();
                    const badRequests = performance.getEntriesByType('resource')
                      .filter(r => r.name && r.duration === 0)
                      .map(r => r.name).slice(0, 10);
                    return {
                      dir: html.dir,
                      lang: html.lang,
                      finalUrl: location.href,
                      title: document.title,
                      textLen: text.length,
                      firstText: text.slice(0, 220),
                      hasScrollX: html.scrollWidth > html.clientWidth + 1,
                      tooSmallTaps: Array.from(document.querySelectorAll('button,a,[role=button]'))
                        .filter(el => {
                          const r = el.getBoundingClientRect();
                          return r.width > 0 && r.height > 0 && (r.width < 40 || r.height < 40);
                        }).length,
                      nodes: body?.children.length || 0,
                      badRequests,
                    };
                }""")
                status = response.status if response else None
                entry = {
                    "viewport": viewport_name,
                    "page": page_name,
                    "requestedUrl": requested_url,
                    "status": status,
                    "navigationError": navigation_error,
                    **info,
                    "errors": browser_errors[-10:],
                    "screenshot": str(shot),
                }
                results.append(entry)

                prefix = f"{viewport_name}/{page_name}"
                if navigation_error:
                    failures.append(f"{prefix}: navigation failed: {navigation_error}")
                if status is not None and status >= 400:
                    failures.append(f"{prefix}: HTTP {status}")
                if info["textLen"] < 20:
                    failures.append(f"{prefix}: nearly empty page")
                if info["dir"] != "rtl":
                    failures.append(f"{prefix}: html dir={info['dir']!r}, expected rtl")
                if info["hasScrollX"]:
                    failures.append(f"{prefix}: horizontal overflow")
                if browser_errors:
                    failures.append(f"{prefix}: browser errors: {browser_errors[-3:]}")
                if path == "/app" and not any(token in info["finalUrl"] for token in ("/auth", "/login")):
                    failures.append(f"{prefix}: unauthenticated /app did not redirect to auth")

            await context.close()
        await browser.close()

    (OUT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))
    if failures:
        print("\nPUBLIC SMOKE FAILURES:")
        for failure in failures:
            print("-", failure)
        raise SystemExit(1)
    print("\nMONGZZ PUBLIC LIVE SMOKE PASSED")

if __name__ == "__main__":
    asyncio.run(run())
