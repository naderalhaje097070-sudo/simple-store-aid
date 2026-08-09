"""Read-only mobile/RTL visual smoke for explicit non-production targets only."""

import asyncio
import ipaddress
import json
import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

PRODUCTION_APP_HOST = "simple-store-aid.lovable.app"
PRODUCTION_SUPABASE_HOST = "dahzkekdirrngnkcxinv.supabase.co"
FORBIDDEN_PRODUCTION_HOSTS = {PRODUCTION_APP_HOST, PRODUCTION_SUPABASE_HOST}
LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
ALLOWED_TARGETS = {"local", "ci", "preview", "staging"}
REMOTE_DNS_HOST = re.compile(
    r"^(?=.{1,253}$)(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$"
)
BLOCK_SENTINEL = "SEC_ENV_VISUAL_SMOKE_BLOCKED"
OK_SENTINEL = "SEC_ENV_VISUAL_SMOKE_PREFLIGHT_OK"


def block(reason: str) -> None:
    print(f"{BLOCK_SENTINEL}: {reason}")
    raise SystemExit(2)


def reject_browser_ambiguous_url(value: str) -> None:
    """Reject raw forms whose WHATWG interpretation can differ from urllib."""

    # This test harness accepts canonical ASCII origins only. Punycode remains
    # available for international domains, but raw Unicode/IDNA separators,
    # percent-encoded hostname bytes, backslashes and browser-trimmed whitespace
    # are never treated as an approval input.
    if value != value.strip():
        block("visual smoke base URL cannot contain surrounding whitespace")
    if any(ord(character) < 0x21 or ord(character) > 0x7E for character in value):
        block("visual smoke base URL must be a printable ASCII origin")
    if "\\" in value:
        block("visual smoke base URL cannot contain backslashes")
    if "%" in value:
        block("visual smoke base URL cannot contain percent-encoding")


def normalize_hostname(value: str) -> str:
    host = value.rstrip(".")
    try:
        return host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        block("visual smoke hostname is not valid IDNA")


def hostname_from_url(url_value: str) -> str:
    try:
        parsed = urlparse(url_value)
        return normalize_hostname(parsed.hostname or "")
    except (ValueError, SystemExit):
        return ""


def parse_whatwg_ipv4_number(part: str) -> int | None:
    """Parse one WHATWG IPv4-number component (decimal/octal/hex)."""

    if not part:
        return None

    digits = part
    radix = 10
    lowered = part.lower()
    if lowered.startswith("0x"):
        digits = part[2:]
        radix = 16
        if not digits or not all(character in "0123456789abcdefABCDEF" for character in digits):
            return None
    elif len(part) >= 2 and part.startswith("0"):
        digits = part[1:]
        radix = 8
        if not digits:
            return 0
        if not all(character in "01234567" for character in digits):
            return None
    elif not part.isdigit():
        return None

    try:
        return int(digits, radix)
    except ValueError:
        return None


def is_whatwg_ipv4_host(host: str) -> bool:
    """Detect host spellings Chromium can canonicalize into an IPv4 address."""

    parts = host.split(".")
    if parts and parts[-1] == "":
        parts.pop()
    if not parts or len(parts) > 4:
        return False

    numbers: list[int] = []
    for part in parts:
        number = parse_whatwg_ipv4_number(part)
        if number is None:
            return False
        numbers.append(number)

    if any(number > 255 for number in numbers[:-1]):
        return False

    last_limit = 256 ** (5 - len(numbers))
    return numbers[-1] < last_limit


def is_ip_literal_or_legacy_numeric_host(host: str) -> bool:
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        return is_whatwg_ipv4_host(host)


def canonical_origin(parsed, host: str) -> str:
    try:
        port = parsed.port
    except ValueError:
        block("MONGEZZ_VISUAL_TEST_BASE_URL has an invalid port")

    suffix = f":{port}" if port is not None else ""
    return f"{parsed.scheme}://{host}{suffix}"


def validate_target() -> str:
    target = os.environ.get("MONGEZZ_DEPLOY_TARGET", "").strip()
    raw_base_url = os.environ.get("MONGEZZ_VISUAL_TEST_BASE_URL", "")

    if target not in ALLOWED_TARGETS:
        block("MONGEZZ_DEPLOY_TARGET must be local, ci, preview, or staging")
    if not raw_base_url:
        block("MONGEZZ_VISUAL_TEST_BASE_URL must be explicit")

    reject_browser_ambiguous_url(raw_base_url)

    try:
        parsed = urlparse(raw_base_url)
        raw_host = parsed.hostname or ""
        host = normalize_hostname(raw_host)
    except ValueError:
        block("MONGEZZ_VISUAL_TEST_BASE_URL is invalid")

    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        block("visual smoke base URL cannot contain credentials/query/fragment")
    if parsed.path not in {"", "/"} or parsed.params:
        block("visual smoke base URL must be an origin, not a routed path")
    if not host:
        block("visual smoke base URL must contain a hostname")
    if raw_host != host:
        block("visual smoke hostname must already be canonical lowercase ASCII")
    if host in FORBIDDEN_PRODUCTION_HOSTS:
        block("visual smoke is not authorized against a production host")

    origin = canonical_origin(parsed, host)
    if raw_base_url not in {origin, f"{origin}/"}:
        block("visual smoke base URL must be a canonical origin")

    if target in {"local", "ci"}:
        if parsed.scheme != "http" or host not in LOOPBACK_HOSTS or parsed.port != 8080:
            block("local/ci visual smoke must use HTTP loopback port 8080")
    else:
        if parsed.scheme != "https" or parsed.port is not None or host in LOOPBACK_HOSTS:
            block("preview/staging visual smoke must use HTTPS without a custom port")
        if is_ip_literal_or_legacy_numeric_host(host):
            block("preview/staging visual smoke cannot use IP or legacy numeric host syntax")
        if not REMOTE_DNS_HOST.fullmatch(host):
            block("preview/staging visual smoke must use a canonical DNS hostname")

    return origin


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
                if hostname_from_url(route.request.url) in FORBIDDEN_PRODUCTION_HOSTS:
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
