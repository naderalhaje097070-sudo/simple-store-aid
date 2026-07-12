import asyncio
import json
import os
from pathlib import Path

from playwright.async_api import async_playwright

BASE = os.environ.get("SMOKE_BASE_URL", "https://mongezz.vercel.app").rstrip("/")
OUT = Path(os.environ.get("SMOKE_OUT", "/tmp/mongezz-public-smoke"))
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
    hard_failures = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)

        for viewport_name, width, height in VIEWPORTS:
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                locale="ar-LY",
            )
            page = await context.new_page()
            current_errors = []

            page.on("pageerror", lambda exc: current_errors.append(("pageerror", str(exc))))
            page.on(
                "console",
                lambda msg: msg.type == "error"
                and current_errors.append(("console", msg.text)),
            )

            for page_name, path in TARGETS:
                current_errors.clear()
                response = None
                navigation_error = None
                url = f"{BASE}{path}"

                try:
                    response = await page.goto(
                        url,
                        wait_until="domcontentloaded",
                        timeout=30_000,
                    )
                    await page.wait_for_timeout(1_000)
                except Exception as exc:
                    navigation_error = str(exc)

                screenshot = OUT / f"{viewport_name}_{page_name}.png"
                await page.screenshot(path=str(screenshot), full_page=True)

                info = await page.evaluate(
                    """() => {
                        const html = document.documentElement;
                        const body = document.body;
                        const bodyText = (body?.innerText || '').trim();
                        const hasScrollX =
                          html.scrollWidth > html.clientWidth + 1;
                        const tooSmallTaps = Array.from(
                          document.querySelectorAll('button,a,[role=button]')
                        ).filter((el) => {
                          const r = el.getBoundingClientRect();
                          return r.width > 0 && r.height > 0 &&
                            (r.width < 40 || r.height < 40);
                        }).length;
                        return {
                          dir: html.dir,
                          lang: html.lang,
                          finalUrl: location.href,
                          title: document.title,
                          textLen: bodyText.length,
                          firstText: bodyText.slice(0, 180),
                          hasScrollX,
                          tooSmallTaps,
                          nodes: body?.children.length || 0,
                        };
                    }"""
                )

                status = response.status if response else None
                entry = {
                    "viewport": viewport_name,
                    "page": page_name,
                    "requestedUrl": url,
                    "status": status,
                    "navigationError": navigation_error,
                    **info,
                    "errors": current_errors[-10:],
                    "screenshot": str(screenshot),
                }
                results.append(entry)

                if navigation_error:
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: navigation failed: {navigation_error}"
                    )
                if status is not None and status >= 400:
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: HTTP {status}"
                    )
                if info["textLen"] < 20:
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: nearly empty page"
                    )
                if info["dir"] != "rtl":
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: html dir={info['dir']!r}, expected rtl"
                    )
                if current_errors:
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: browser errors: {current_errors[-3:]}"
                    )
                if path == "/app" and "/auth" not in info["finalUrl"]:
                    hard_failures.append(
                        f"{viewport_name}/{page_name}: unauthenticated /app did not redirect to /auth"
                    )

            await context.close()

        await browser.close()

    (OUT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))

    if hard_failures:
        print("\nPUBLIC SMOKE FAILURES:")
        for failure in hard_failures:
            print(f"- {failure}")
        raise SystemExit(1)

    print("\nPUBLIC LIVE SMOKE PASSED")


if __name__ == "__main__":
    asyncio.run(run())
