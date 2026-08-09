"""Read-only authenticated UI smoke for the isolated CI environment only."""

import asyncio
import os
import sys
from pathlib import Path
from urllib.parse import urlparse

LOOPBACK_HOSTS = {"127.0.0.1", "localhost"}
PRODUCTION_APP_HOST = "simple-store-aid.lovable.app"
BLOCK_SENTINEL = "SEC_ENV_AUTH_SMOKE_BLOCKED"
OK_SENTINEL = "SEC_ENV_AUTH_SMOKE_PREFLIGHT_OK"


def block(reason: str) -> None:
    print(f"{BLOCK_SENTINEL}: {reason}")
    raise SystemExit(2)


def normalize_hostname(value: str) -> str:
    host = value.strip().rstrip(".")
    try:
        return host.encode("idna").decode("ascii").lower().rstrip(".")
    except UnicodeError:
        block("application hostname is not valid IDNA")


def request_origin(url_value: str) -> tuple[str, str, int] | None:
    """Return a normalized network origin for browser routing decisions."""

    try:
        parsed = urlparse(url_value)
        host = normalize_hostname(parsed.hostname or "")
        port = parsed.port
    except (ValueError, SystemExit):
        return None

    if parsed.scheme not in {"http", "https"} or not host:
        return None
    if port is None:
        port = 80 if parsed.scheme == "http" else 443
    return (parsed.scheme, host, port)


def validate_app_origin() -> str:
    if os.environ.get("CI_ISOLATED_SUPABASE") != "1":
        block("CI_ISOLATED_SUPABASE must equal 1")

    base_url = os.environ.get("APP_BASE_URL", "").strip().rstrip("/")
    if not base_url:
        block("APP_BASE_URL must be explicit")

    try:
        parsed = urlparse(base_url)
        host = normalize_hostname(parsed.hostname or "")
        port = parsed.port
    except ValueError:
        block("APP_BASE_URL is invalid")

    if parsed.scheme != "http" or host not in LOOPBACK_HOSTS or port != 8080:
        block("APP_BASE_URL must be the isolated HTTP loopback origin on port 8080")
    if parsed.username or parsed.password or parsed.query or parsed.fragment:
        block("APP_BASE_URL cannot contain credentials/query/fragment")
    if parsed.path not in {"", "/"}:
        block("APP_BASE_URL must be an origin, not a routed path")
    if host == PRODUCTION_APP_HOST:
        block("production application host is forbidden")

    return base_url


def browser_request_is_isolated(method: str, url_value: str, is_navigation: bool) -> bool:
    origin = request_origin(url_value)
    if origin is None:
        return False

    _, host, _ = origin
    if host == PRODUCTION_APP_HOST or host.endswith(".supabase.co"):
        return False
    if is_navigation and origin != APP_ORIGIN:
        return False
    if method.upper() not in {"GET", "HEAD", "OPTIONS"} and host not in LOOPBACK_HOSTS:
        return False
    return True


BASE_URL = validate_app_origin()
APP_ORIGIN = request_origin(BASE_URL)
if APP_ORIGIN is None:
    block("validated APP_BASE_URL did not produce a canonical application origin")

if "--preflight-only" in sys.argv:
    # Freeze the full-origin boundary before credentials or Playwright are loaded.
    # Same-host redirects on a different port/scheme are distinct origins and must
    # never receive the authenticated smoke's credentials.
    if browser_request_is_isolated("GET", "http://127.0.0.1:8000/auth", True):
        block("browser isolation invariant accepted an alternate loopback port")
    if browser_request_is_isolated("GET", "https://localhost/app", True):
        block("browser isolation invariant accepted an alternate loopback scheme")
    if not browser_request_is_isolated("GET", f"{BASE_URL}/app", True):
        block("browser isolation invariant rejected the validated application origin")
    print(f"{OK_SENTINEL}: isolated application origin verified")
    raise SystemExit(0)

# Browser credentials, browser dependency and artifacts are accessed only after
# the application origin has passed the fail-closed isolation preflight.
EMAIL = os.environ["PILOT_QA_EMAIL"]
PASSWORD = os.environ["PILOT_QA_PASSWORD"]

from playwright.async_api import TimeoutError as PlaywrightTimeoutError
from playwright.async_api import async_playwright

EVIDENCE = Path("/tmp/mongezz-auth-smoke")
EVIDENCE.mkdir(parents=True, exist_ok=True)


def critical(errors: list[str]) -> list[str]:
    markers = ("react error #418", "hydration failed", "hydration mismatch")
    return [item for item in errors if any(marker in item.lower() for marker in markers)]


async def main() -> None:
    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch(headless=True)

        for width, height, label in ((1440, 900, "desktop"), (390, 844, "mobile")):
            context = await browser.new_context(
                viewport={"width": width, "height": height},
                locale="ar-LY",
            )
            page = await context.new_page()
            isolation_violations: list[str] = []

            async def enforce_browser_isolation(route):
                request = route.request
                if not browser_request_is_isolated(
                    request.method,
                    request.url,
                    request.is_navigation_request(),
                ):
                    isolation_violations.append(f"{request.method} {request.url}")
                    print(
                        f"SEC_ENV_AUTH_SMOKE_BROWSER_BLOCKED: {request.method} {request.url}"
                    )
                    await route.abort("blockedbyclient")
                    return
                await route.continue_()

            await page.route("**/*", enforce_browser_isolation)

            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on(
                "console",
                lambda message: errors.append(message.text)
                if message.type == "error"
                else None,
            )

            await page.goto(f"{BASE_URL}/app", wait_until="domcontentloaded")
            try:
                await page.locator("#auth-email").wait_for(state="visible", timeout=20000)
            except PlaywrightTimeoutError:
                await page.screenshot(
                    path=str(EVIDENCE / f"{label}-protection-failure.png"),
                    full_page=True,
                )
                print(f"PROTECTION FAILURE URL ({label}): {page.url}")
                print(
                    f"PROTECTION FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}"
                )
                print(f"PROTECTION FAILURE ERRORS ({label}): {errors}")
                raise

            if critical(errors):
                raise AssertionError(
                    f"Hydration error on unauthenticated /app: {critical(errors)}"
                )
            errors.clear()

            await page.locator("#auth-email").fill(EMAIL)
            await page.locator("#auth-password").fill(PASSWORD)
            await page.locator('button[type="submit"]').click()
            try:
                await page.wait_for_url("**/app", timeout=20000)
            except PlaywrightTimeoutError:
                await page.screenshot(
                    path=str(EVIDENCE / f"{label}-login-failure.png"),
                    full_page=True,
                )
                print(f"LOGIN FAILURE URL ({label}): {page.url}")
                print(f"LOGIN FAILURE BODY ({label}):\n{await page.locator('body').inner_text()}")
                print(f"LOGIN FAILURE ERRORS ({label}): {errors}")
                raise

            await page.wait_for_load_state("networkidle", timeout=20000)
            await page.get_by_text("فاتورة جديدة", exact=True).first.wait_for(timeout=10000)

            if isolation_violations:
                raise AssertionError(
                    f"Browser isolation blocked {len(isolation_violations)} remote request(s)"
                )

            layout = await page.evaluate(
                "() => ({ width: window.innerWidth, scroll: document.documentElement.scrollWidth, dir: document.documentElement.dir, lang: document.documentElement.lang })"
            )
            if layout["scroll"] > layout["width"] + 1:
                raise AssertionError(f"Horizontal overflow: {layout}")
            if layout["dir"] != "rtl" or layout["lang"] != "ar":
                raise AssertionError(f"Incorrect locale attributes: {layout}")
            if critical(errors):
                raise AssertionError(f"Hydration error after login: {critical(errors)}")

            await page.screenshot(path=str(EVIDENCE / f"{label}.png"), full_page=True)
            await context.close()

        await browser.close()

    print("PASS: isolated authenticated UI smoke")


if __name__ == "__main__":
    asyncio.run(main())
