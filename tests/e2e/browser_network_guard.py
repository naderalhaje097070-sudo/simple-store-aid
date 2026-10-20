"""Shared HTTP/WebSocket containment for isolated browser harnesses.

Standard library only. All redirects and WebSockets are deliberately blocked.
A 3xx must never reach the browser: its next hop bypasses HTTP routing.
"""

from __future__ import annotations

from collections.abc import Callable

OFFLINE_FONT_STYLESHEET = (
    "https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap"
)


async def install_browser_network_guard(
    context,
    allowed: Callable[[str, str, bool], bool],
    reject: Callable[[str], None],
) -> None:
    if not callable(getattr(context, "route_web_socket", None)):
        raise RuntimeError("SEC_ENV_BROWSER_BLOCKED: Playwright WebSocket routing is required")

    async def enforce_http(route):
        request = route.request
        if request.url == OFFLINE_FONT_STYLESHEET:
            # Existing app dependency: replace its exact stylesheet offline.
            # Empty CSS keeps fallback fonts; never contact the font provider.
            if (request.method == "GET" and request.resource_type == "stylesheet"
                    and not request.is_navigation_request()):
                await route.fulfill(status=200, content_type="text/css",
                                    body="/* isolated smoke: fallback fonts */")
                return
            reject("HTTP_FONT_REQUEST_BLOCKED")
            await route.abort("blockedbyclient")
            return
        if not allowed(request.method, request.url, request.is_navigation_request()):
            reject("HTTP_ORIGIN_BLOCKED")
            await route.abort("blockedbyclient")
            return

        response = None
        try:
            response = await route.fetch(max_redirects=0, max_retries=0, timeout=20000)
            if 300 <= response.status < 400:
                reject("HTTP_REDIRECT_BLOCKED")
                await route.abort("blockedbyclient")
                return
            await route.fulfill(response=response)
        except Exception:
            # A failed fetch is a guard violation, never a successful smoke.
            # Exceptions/URLs may contain tokens or user data; log codes only.
            reject("HTTP_FETCH_BLOCKED")
            await route.abort("blockedbyclient")
        finally:
            if response is not None:
                await response.dispose()

    async def enforce_websocket(socket):
        reject("WEBSOCKET_BLOCKED")
        # Never connect_to_server: the default routed socket is mocked, so no
        # server handshake happens before this close.
        await socket.close(code=1008, reason="isolated test blocks WebSockets")

    # Context-wide and before pages, including each popup's first request.
    await context.route_web_socket("**/*", enforce_websocket)
    await context.route("**/*", enforce_http)
