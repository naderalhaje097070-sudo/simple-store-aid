import asyncio, json
from pathlib import Path
from playwright.async_api import async_playwright

OUT = Path("/tmp/browser/mongezz/shots"); OUT.mkdir(exist_ok=True)
BASE = "https://simple-store-aid.lovable.app"

# financially sensitive screens (public landing only — /app requires auth)
TARGETS = [
    ("landing", "/"),
    ("auth", "/auth"),
    ("guide", "/guide"),
    ("app_redirect", "/app"),
]

VIEWPORTS = [("mobile_360", 360, 780), ("mobile_390", 390, 844)]

async def run():
    results = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        for vname, w, h in VIEWPORTS:
            ctx = await browser.new_context(viewport={"width": w, "height": h}, locale="ar-EG")
            page = await ctx.new_page()
            errs = []
            page.on("pageerror", lambda e: errs.append(("pageerror", str(e))))
            page.on("console", lambda m: m.type == "error" and errs.append(("console", m.text)))
            for name, path in TARGETS:
                url = BASE + path
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                except Exception as e:
                    errs.append((f"goto:{name}", str(e)))
                await page.wait_for_timeout(800)
                shot = OUT / f"{vname}_{name}.png"
                await page.screenshot(path=str(shot))
                info = await page.evaluate("""() => {
                    const html = document.documentElement;
                    const body = document.body;
                    const bodyText = (body?.innerText || '').trim();
                    const hasScrollX = document.documentElement.scrollWidth > document.documentElement.clientWidth + 1;
                    const tooSmallTaps = Array.from(document.querySelectorAll('button,a,[role=button]')).filter(el => {
                        const r = el.getBoundingClientRect();
                        return r.width > 0 && r.height > 0 && (r.width < 40 || r.height < 40);
                    }).length;
                    return {
                        dir: html.dir, lang: html.lang,
                        url: location.href,
                        textLen: bodyText.length,
                        firstText: bodyText.slice(0, 120),
                        hasScrollX, tooSmallTaps,
                        nodes: document.body?.children.length || 0,
                    };
                }""")
                results.append({"viewport": vname, "page": name, **info, "errors": errs[-5:]})
            await ctx.close()
        await browser.close()
    Path("/tmp/browser/mongezz/results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2))
    print(json.dumps(results, ensure_ascii=False, indent=2))

asyncio.run(run())
