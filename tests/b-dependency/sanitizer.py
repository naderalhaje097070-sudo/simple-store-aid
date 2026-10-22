"""Current installed sanitizer in Chromium; all HTTP/WebSocket traffic blocked."""
import asyncio
import hashlib
import json
import os
from pathlib import Path
import sys
from playwright.async_api import async_playwright


async def main():
    violations = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(args=["--disable-background-networking"])
        context = await browser.new_context(service_workers="block")

        async def route_http(route):
            if route.request.method == "GET" and route.request.url == "http://127.0.0.1:19871/":
                await route.fulfill(status=200, content_type="text/html", body="<html><body></body></html>")
            else:
                violations.append("unexpected-http")
                await route.abort("blockedbyclient")

        async def route_ws(socket):
            violations.append("unexpected-websocket")
            await socket.close(code=1008, reason="offline fixture")

        await context.route("**/*", route_http)
        await context.route_web_socket("**/*", route_ws)
        page = await context.new_page()
        await page.goto("http://127.0.0.1:19871/")
        dist = Path("node_modules/dompurify/dist/purify.js")
        await page.add_script_tag(path=str(dist))
        original = await page.evaluate(Path("tests/g0-dompurify/browser-cases.js").read_text())
        assert original["version"] == "3.4.17"
        assert len(original["results"]) == 10 and all(x["pass"] for x in original["results"]), original
        current = await page.evaluate(Path("tests/b-dependency/sanitizer-cases.js").read_text())
        assert len(current) == 4 and all(x["pass"] for x in current), current
        assert not violations, violations
        receipt = {"source": os.environ["GITHUB_SHA"], "version": original["version"],
                   "dist_sha256": hashlib.sha256(dist.read_bytes()).hexdigest(),
                   "browser": browser.version, "original": original["results"], "current": current,
                   "network_violations": violations, "service_workers": "blocked",
                   "old_vulnerable_replay": False, "database_or_provider_calls": 0}
        Path(sys.argv[1]).write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n")
        print(json.dumps({"sanitizer_controls": 10 + len(current), "passed": True}))
        await context.close()
        await browser.close()


asyncio.run(main())
