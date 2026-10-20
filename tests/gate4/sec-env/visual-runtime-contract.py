"""Read-only semantic proof of the visual harness and its shared guard wiring."""
import __future__
import ast
import asyncio
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[3]


class ContractFailure(AssertionError):
    pass


def require(condition, name):
    if not condition:
        raise ContractFailure(name)


def chain(node):
    return ast.unparse(node)


def verify(visual, helper):
    tree = ast.parse(visual)
    shared = ast.parse(helper)
    ns = {'urlparse': urlparse, 'BASE_ORIGIN': ('http', 'localhost', 8080)}
    constant_names = {'PRODUCTION_APP_HOST', 'PRODUCTION_SUPABASE_HOST',
                      'FORBIDDEN_PRODUCTION_HOSTS', 'BLOCK_SENTINEL'}
    definitions = {'block', 'normalize_hostname', 'hostname_from_url',
                   'network_origin', 'browser_request_is_isolated'}
    nodes = [n for n in tree.body if
             isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id in constant_names for t in n.targets)
             or isinstance(n, ast.FunctionDef) and n.name in definitions]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), '<visual-pure-policy>', 'exec',
                 flags=__future__.annotations.compiler_flag), ns)
    policy = ns['browser_request_is_isolated']
    cases = [
        ('own_navigation', 'GET', 'http://localhost:8080/app', True, True),
        ('own_head', 'HEAD', 'http://localhost:8080/app', False, True),
        ('own_options', 'OPTIONS', 'http://localhost:8080/app', False, True),
        ('foreign_navigation', 'GET', 'https://assets.example/app', True, False),
        ('alternate_port', 'GET', 'http://localhost:8000/app', True, False),
        ('alternate_scheme', 'GET', 'https://localhost:8080/app', True, False),
        ('production_app', 'GET', 'https://simple-store-aid.lovable.app', False, False),
        ('production_api', 'GET', 'https://dahzkekdirrngnkcxinv.supabase.co', False, False),
        ('invalid_protocol', 'GET', 'file:///etc/passwd', False, False),
    ] + [('write_'+m, m, 'http://localhost:8080/app', False, False)
         for m in ['POST', 'PUT', 'PATCH', 'DELETE']]
    for name, method, url, nav, expected in cases:
        require(policy(method, url, nav) is expected, 'policy_'+name)

    imports = [n for n in tree.body if isinstance(n, ast.ImportFrom)
               and n.module == 'browser_network_guard'
               and any(a.name == 'install_browser_network_guard' and a.asname is None for a in n.names)]
    require(len(imports) == 1, 'shared_helper_import')
    require(not any(isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == 'install_browser_network_guard'
                    or isinstance(n, ast.Name) and n.id == 'install_browser_network_guard' and isinstance(n.ctx, ast.Store)
                    for n in ast.walk(tree)), 'no_shadowed_helper')
    calls = [n for n in ast.walk(tree) if isinstance(n, ast.Call)
             and chain(n.func) == 'install_browser_network_guard']
    pages = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and chain(n.func) == 'ctx.new_page']
    require(len(calls) == 1 and len(pages) == 1, 'context_guard_and_page')
    require([chain(a) for a in calls[0].args] ==
            ['ctx', 'browser_request_is_isolated', 'reject_browser_request'], 'actual_policy_wiring')
    require(calls[0].lineno < pages[0].lineno, 'guard_before_page')
    require(any(isinstance(n, ast.Await) and n.value is calls[0] for n in ast.walk(tree)), 'guard_awaited')
    guard_statement = next(n for n in ast.walk(tree) if isinstance(n, ast.Expr)
                           and isinstance(n.value, ast.Await) and n.value.value is calls[0])
    page_statement = next(n for n in ast.walk(tree) if isinstance(n, ast.Assign)
                          and isinstance(n.value, ast.Await) and n.value.value is pages[0])
    sequences = [value for node in ast.walk(tree) for _, value in ast.iter_fields(node)
                 if isinstance(value, list) and guard_statement in value and page_statement in value]
    require(len(sequences) == 1 and sequences[0].index(guard_statement) < sequences[0].index(page_statement),
            'guard_and_page_direct_control_sequence')
    require(any(isinstance(n, ast.Call) and chain(n.func) == 'isolation_violations.append'
                for n in ast.walk(tree)), 'violation_callback')

    gotos = [n for n in ast.walk(tree) if isinstance(n, ast.Try)
             and any(isinstance(c, ast.Call) and chain(c.func) == 'page.goto'
                     for statement in n.body for c in ast.walk(statement))]
    require(bool(gotos), 'navigation_try')
    for node in gotos:
        require(bool(node.handlers) and all(any(isinstance(s, ast.Raise) for s in h.body)
                                           for h in node.handlers), 'navigation_failure_fatal')
    shots = [n for n in ast.walk(tree) if isinstance(n, ast.Call) and chain(n.func) == 'page.screenshot']
    require(len(shots) == 1, 'screenshot_exists')
    origins = [n for n in ast.walk(tree) if isinstance(n, ast.If)
               and chain(n.test) == 'network_origin(page.url) != BASE_ORIGIN'
               and any(isinstance(s, ast.Raise) for s in n.body)]
    violations = [n for n in ast.walk(tree) if isinstance(n, ast.If)
                  and chain(n.test) == 'isolation_violations'
                  and any(isinstance(s, ast.Raise) for s in n.body)]
    for group, name in [(origins, 'final_origin_fatal'), (violations, 'violations_fatal')]:
        require(any(n.lineno < shots[0].lineno for n in group)
                and any(n.lineno > shots[0].lineno for n in group), name)
    require('visual navigation failed for' in visual and
            'visual smoke reached unapproved application origin' in visual and
            'visual smoke blocked forbidden/off-origin request(s)' in visual, 'original_failure_messages')

    # Invoke the actual extracted transport helper with in-memory routes only.
    helper_ns = {}
    functions = [n for n in shared.body if isinstance(n, ast.AsyncFunctionDef)
                 and n.name == 'install_browser_network_guard']
    require(len(functions) == 1, 'actual_shared_helper')
    constant = next(n for n in shared.body if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == 'OFFLINE_FONT_STYLESHEET' for t in n.targets))
    exec(compile(ast.Module(body=[constant, functions[0]], type_ignores=[]), '<shared-helper>', 'exec',
                 flags=__future__.annotations.compiler_flag), helper_ns)

    async def forwarding():
        class Context:
            async def route_web_socket(self, pattern, callback):
                self.websocket = callback
            async def route(self, pattern, callback):
                self.http = callback
        class Request:
            method = 'GET'
            url = 'http://localhost:8080/app'
            resource_type = 'document'
            def is_navigation_request(self):
                return True
        class Route:
            request = Request()
            aborted = False
            async def abort(self, reason):
                self.aborted = True
            async def fetch(self, **kwargs):
                raise ContractFailure('denied_navigation_reached_fetch')
        observed, rejected = [], []
        def denied(method, url, nav):
            observed.append((method, url, nav))
            return False
        context = Context()
        await helper_ns['install_browser_network_guard'](context, denied, rejected.append)
        route = Route()
        await context.http(route)
        require(observed == [('GET', Request.url, True)], 'real_navigation_flag_forwarded')
        require(route.aborted and rejected == ['HTTP_ORIGIN_BLOCKED'], 'denied_navigation_aborted')
    asyncio.run(forwarding())
    return {'policy_cases': len(cases), 'shared_navigation_forwarding': True,
            'context_wiring': True, 'fatal_navigation': True, 'before_after_origin_and_violations': True}


def main():
    result = verify((ROOT/'tests/visual/mobile-rtl-smoke.py').read_text(),
                    (ROOT/'tests/e2e/browser_network_guard.py').read_text())
    print('SEC_ENV_VISUAL_RUNTIME_ORIGIN_GUARD_CONFIRMED')
    print(json.dumps(result, sort_keys=True))


if __name__ == '__main__':
    main()
