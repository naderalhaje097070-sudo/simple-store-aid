"""Real-browser transport regression using disposable loopback recorders only.

Never import/execute harness bodies, application handlers, credentials or SQL.
Load their pure policy and original route handler through AST for before/after
evidence. The recorders hold dummy traffic in memory and do not write records.
"""

from __future__ import annotations

import __future__
import ast
import asyncio
import json
import os
import re
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "tests/e2e"))
APP = "http://localhost:8080"
SB = "http://127.0.0.1:54321"
PROFILES = {
    "sale": "tests/e2e/sale-dashboard-close.py",
    "rapid": "tests/e2e/rapid-click-sale.py",
    "auth": "tests/e2e/isolated-auth-smoke.py",
    "visual": "tests/visual/mobile-rtl-smoke.py",
}


def load_functions(path, namespace):
    tree = ast.parse((ROOT / path).read_text())
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    exec(compile(ast.Module(body=functions, type_ignores=[]), path, "exec",
                 flags=__future__.annotations.compiler_flag), namespace)
    return tree


def policy_and_legacy_handler(profile):
    namespace = {
        "urlparse": urlparse, "re": re, "sys": sys, "Path": Path,
        "os": os, "SB_URL": SB,
        "BASE": APP, "WRITE_APP_BASE_URL": APP,
        "APP_ORIGIN": ("http", "localhost", 8080),
        "BASE_ORIGIN": ("http", "localhost", 8080),
        "LOOPBACK_HOSTS": {"localhost", "127.0.0.1"},
        "PRODUCTION_APP_HOST": "simple-store-aid.lovable.app",
        "FORBIDDEN_PRODUCTION_HOSTS": {
            "simple-store-aid.lovable.app", "dahzkekdirrngnkcxinv.supabase.co",
        },
        "browser_isolation_violations": [], "isolation_violations": [],
    }
    if profile == "sale":
        load_functions("tests/e2e/write_harness_guard.py", namespace)
    if profile == "rapid":
        from write_harness_guard import browser_request_is_isolated
        namespace["isolated_browser_request"] = browser_request_is_isolated
    tree = load_functions(PROFILES[profile], namespace)
    handler = next((node for node in ast.walk(tree) if isinstance(node, ast.AsyncFunctionDef)
                    and node.name in {"enforce_browser_isolation", "enforce_visual_isolation"}), None)
    if handler:
        exec(compile(ast.Module(body=[handler], type_ignores=[]), PROFILES[profile], "exec"), namespace)
        return namespace.get("browser_request_is_isolated"), namespace[handler.name], tree
    return namespace["browser_request_is_isolated"], None, tree


class Recorder(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, port, role):
        self.role = role
        self.hits = []
        self.destination = None
        super().__init__(("127.0.0.1", port), Handler)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def handle_request(self):
        length = int(self.headers.get("content-length", "0"))
        body = self.rfile.read(length)
        self.server.hits.append((self.command, self.path, body, self.headers.get("Upgrade")))
        if self.server.role == "sink":
            self.send_response(400 if self.headers.get("Upgrade") else 200)
            self.end_headers()
            self.wfile.write(b"DUMMY_RECORDER")
        elif self.path.startswith("/redirect/"):
            self.send_response(int(self.path.split("/")[-1]))
            self.send_header("Location", self.server.destination + "/dummy")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", "0")
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b"<html><body>DUMMY_FIXTURE</body></html>")

    do_GET = handle_request
    do_POST = handle_request
    do_OPTIONS = handle_request


async def main():
    from playwright.async_api import async_playwright
    servers = []
    failures = []
    count = 0
    try:
        for port, role in [(8080, "app"), (54321, "api"), (0, "sink")]:
            server = Recorder(port, role)
            servers.append(server)
            threading.Thread(target=server.serve_forever, daemon=True).start()
        app, api, sink = servers
        sink_origin = f"http://127.0.0.1:{sink.server_port}"
        app.destination = api.destination = sink_origin
        async with async_playwright() as pw:
            options = {"headless": True}
            executable = os.environ.get("MONGEZZ_BROWSER_TEST_EXECUTABLE")
            if executable:
                options.update(executable_path=executable,
                               args=json.loads(os.environ.get("MONGEZZ_BROWSER_TEST_ARGS", "[]")))
            browser = await pw.chromium.launch(**options)
            print("Browser version:", browser.version)
            for profile in PROFILES:
                policy, legacy, tree = policy_and_legacy_handler(profile)
                context = await browser.new_context(service_workers="block")
                violations = []
                if legacy:
                    await context.route("**/*", legacy)
                else:
                    from browser_network_guard import install_browser_network_guard
                    # Assert actual harness wiring reaches this same helper.
                    assert any(isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                               and node.func.id == "install_browser_network_guard" for node in ast.walk(tree))
                    await install_browser_network_guard(context, policy, violations.append)
                page = await context.new_page()
                await page.goto(APP)
                for status in [301, 302, 303, 307, 308]:
                    attempt = await context.new_page()
                    await attempt.goto(APP)
                    before = len(sink.hits)
                    before_violations = len(violations)
                    try:
                        await attempt.goto(f"{APP}/redirect/{status}", timeout=5000)
                    except Exception:
                        pass  # Rejection is expected; recorder count proves the boundary.
                    count += 1
                    if len(sink.hits) != before:
                        failures.append(f"{profile}: navigation redirect{status} reached forbidden recorder")
                    if not legacy:
                        assert "HTTP_REDIRECT_BLOCKED" in violations[before_violations:]
                    # An aborted navigation can finish on chrome-error:// later.
                    # Close its disposable page instead of racing the next case.
                    await attempt.close()
                for status in [307, 308]:
                    before = len(sink.hits)
                    await page.evaluate("""async url => {
                        try { await fetch(url, {method:'POST', body:'DUMMY_ONLY'}); } catch {}
                    }""", f"{APP}/redirect/{status}")
                    count += 1
                    if len(sink.hits) != before:
                        failures.append(f"{profile}: POST redirect{status} reached forbidden recorder")
                before = len(sink.hits)
                await page.evaluate("""async url => {
                    try { await fetch(url, {method:'POST', body:'DUMMY_ONLY'}); } catch {}
                }""", sink_origin + "/dummy")
                count += 1
                if len(sink.hits) != before:
                    failures.append(f"{profile}: alternate-origin POST reached forbidden recorder")
                before = len(sink.hits)
                await page.evaluate("""url => new Promise(resolve => {
                    const ws = new WebSocket(url); ws.onerror = resolve; ws.onclose = resolve;
                    ws.onopen = () => { ws.send('DUMMY_ONLY'); ws.close(); resolve(); };
                    setTimeout(resolve, 1500);
                })""", sink_origin.replace("http:", "ws:") + "/dummy")
                count += 1
                if len(sink.hits) != before:
                    failures.append(f"{profile}: WebSocket reached forbidden recorder")
                before = len(sink.hits)
                async with context.expect_page() as popup_info:
                    await page.evaluate("url => window.open(url)", sink_origin + "/dummy")
                popup = await popup_info.value
                try:
                    await popup.wait_for_load_state(timeout=1500)
                except Exception:
                    pass
                count += 1
                if len(sink.hits) != before:
                    failures.append(f"{profile}: popup navigation reached forbidden recorder")
                await popup.close()
                # Positive application reads and isolated API POST still work.
                await page.goto(APP)
                assert "DUMMY_FIXTURE" in await page.content()
                count += 1
                before = len(app.hits)
                async with context.expect_page() as allowed_popup_info:
                    await page.evaluate("url => window.open(url)", APP + "/dummy")
                allowed_popup = await allowed_popup_info.value
                await allowed_popup.wait_for_load_state()
                assert "DUMMY_FIXTURE" in await allowed_popup.content()
                assert len(app.hits) > before
                count += 1
                await allowed_popup.close()
                if not legacy:
                    from browser_network_guard import OFFLINE_FONT_STYLESHEET
                    # Pin the stub to the application's actual dependency.
                    assert OFFLINE_FONT_STYLESHEET in (ROOT / "src/routes/__root.tsx").read_text()
                    before = len(violations)
                    await page.evaluate("""url => new Promise((resolve, reject) => {
                        const link = document.createElement('link'); link.rel = 'stylesheet';
                        link.href = url; link.onload = resolve; link.onerror = reject;
                        document.head.appendChild(link);
                    })""", OFFLINE_FONT_STYLESHEET)
                    assert len(violations) == before
                    count += 1
                    for method in ["POST", "GET"]:
                        before = len(violations)
                        await page.evaluate("""async args => {
                            try { await fetch(args.url, {method:args.method}); } catch {}
                        }""", {"url": OFFLINE_FONT_STYLESHEET, "method": method})
                        assert "HTTP_FONT_REQUEST_BLOCKED" in violations[before:]
                        count += 1
                    attempt = await context.new_page()
                    before = len(violations)
                    try:
                        await attempt.goto(OFFLINE_FONT_STYLESHEET, timeout=5000)
                    except Exception:
                        pass
                    assert "HTTP_FONT_REQUEST_BLOCKED" in violations[before:]
                    count += 1
                    await attempt.close()
                if profile != "visual":
                    before = len(api.hits)
                    await page.evaluate("""async url => {
                        await fetch(url, {method:'POST', body:'DUMMY_ONLY'});
                    }""", SB + "/dummy")
                    assert len(api.hits) > before
                    count += 1
                await context.close()
            await browser.close()
        for failure in failures:
            print("FAIL:", failure)
        print(f"BROWSER_TRANSPORT_REGRESSION: {count} scenarios; {len(failures)} failures; dummy loopback fixtures only")
        return 1 if failures else 0
    finally:
        for server in servers:
            server.shutdown()
            server.server_close()


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
