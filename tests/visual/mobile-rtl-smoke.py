"""Read-only mobile/RTL visual smoke for explicit non-production targets only."""

import asyncio
import json
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

PRODUCTION_HOST = "simple-store-aid.lovable.app"
LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
ALLOWED_TARGETS = {"local", "ci", "preview", "staging"}
BLOCK_SENTINEL = "SEC_ENV_VISUAL_SMOKE_BLOCKED"
OK_SENTINEL = "SEC_ENV_VISUAL_SMOKE_PREFLIGHT_OK"


def block(reason: str) -> None:
    print(f"{BLOCK_SENTINEL}: {reason}")
    raise SystemExit(2)


def normalize_hostname(value: str) -> str:
    host = value.strip().rstrip(".")
    try:
        # Python's IDNA codec maps browser-equivalent DNS separators such as
        # U+3002/U+FF0E/U+FF61 to '.', matching Chromium's hostname semantics.
        return host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        block("visual smoke hostname is not valid IDNA")


def hostname_from_url(url_value: str) -> str:
    try:
        parsed = urlparse(url_value)
        return normalize_hostname(parsed.hostname or "")
    except (ValueError, SystemExit):
        return ""


def validate_target() -> str:
    target = os.environ.get("MONGEZZ_DEPLOY_TARGET", "").strip()
    base_url = os.environ.get("MONGEZZ_VISUAL_TEST_BASE_URL", "").strip().rstrip("/")

    if target not in ALLOWED_TARGETS:
        block("MONGEZZ_DEPLOY_TARGET must be local, ci, preview, or staging")
    if not base_url:
        block("MONGEZZ_VISUAL_TEST_BASE_URL must be explicit")

    try:
        parsed = urlparse(base_url)
        host = normalize_hostname(parsed.hostname or "")
    except ValueError:
        block("MONGEZZ_VISUAL_TEST_BASE_URL is invalid")

    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        block("visual smoke base URL cannot contain credentials/query/fragment")
    if parsed.path not in {"", "/"}:
        block("visual smoke base URL must be an origin, not a routed path")
    if host == PRODUCTION_HOST:
        block("visual smoke is not authorized against the production host")

    if target in {"local", "ci"}:
        if parsed.scheme != "http" or host not in LOOPBACK_HOSTS:
            block("local/ci visual smoke must use an HTTP loopback origin")
    else:
        if parsed.scheme != "https" or not host or host in LOOPBACK_HOSTS:
            block("preview/staging visual smoke must use an explicit non-production HTTPS origin")

    return base_url


BASE = validate_target()

if "--preflight-only" in sys.argv:
    print(f"{OK_SENTINEL}: explicit non-production visual target verified")
    raise SystemExit(0)

# Browser dependency and local artifact creation happen only after target validation.
from playwright.async_api import async_playwright

OUT = Path("/tmp/browser/mongezz/shots")
OUT.mkdir(parents=True, exist_ok=True)

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
        for vname, width, height in VIEWPORTS:
            ctx = await browser.new_context(
                viewport={"width": width, "height": height}, locale="ar-EG"
            )
            page = await ctx.new_page()

            async def block_production_requests(route):
                if hostname_from_url(route.request.url) == PRODUCTION_HOST:
                    print(
                        f"SEC_ENV_VISUAL_SMOKE_BROWSER_BLOCKED: {route.request.method} {route.request.url}"
                    )
                    await route.abort("blockedbyclient")
                    return
                await route.continue_()

            await page.route("**/*", block_production_requests)

            errs = []
            page.on("pageerror", lambda error: errs.append(("pageerror", str(error))))
            page.on(
                "console",
                lambda message: errs.append(("console", message.text))
                if message.type == "error"
                else None,
            )
            for name, path in TARGETS:
                url = BASE + path
                try:
                    await page.goto(url, wait_until="domcontentloaded", timeout=25000)
                except Exception as error:
                    errs.append((f"goto:{name}", str(error)))
                await page.wait_for_timeout(800)
                shot = OUT / f"{vname}_{name}.png"
                await page.screenshot(path=str(shot))
                info = await page.evaluate(
                    """() => {
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
                }"""
                )
                results.append(
                    {"viewport": vname, "page": name, **info, "errors": errs[-5:]}
                )
            await ctx.close()
        await browser.close()
    Path("/tmp/browser/mongezz/results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2)
    )
    print(json.dumps(results, ensure_ascii=False, indent=2))


asyncio.run(run())
