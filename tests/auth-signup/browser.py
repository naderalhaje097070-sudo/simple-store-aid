"""Sign-up with an email that already has an account must never read as success.

Runs the actual src/routes/auth.tsx screen and the real supabase-js client in
Chromium; the GoTrue /signup reply is answered in the browser. Reply shapes:
  existing_422   verbatim from GoTrue v2.188.1 (local, 2026-11-10), confirmed email, as
                 supabase-js receives it (it sends X-Supabase-Api-Version: 2024-01-01)
  existing_422_legacy  the same refusal without the API-version header (verbatim)
  existing_fake  success-shaped reply with no identities and no session
                 (GoTrue email-enumeration protection)
  new_unconfirmed  verbatim shape of a new user awaiting confirmation (1 identity)
  network_down / server_500  transport and server failures
No network beyond the local fixture server.
"""
import functools, http.server, json, sys, threading
from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path(sys.argv[1]).resolve()
evidence = Path(sys.argv[2]) if len(sys.argv) > 2 else None


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_): pass


server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), functools.partial(Quiet, directory=str(out)))
threading.Thread(target=server.serve_forever, daemon=True).start()
origin = 'http://127.0.0.1:' + str(server.server_port)

EXISTING = 'هذا البريد مسجّل مسبقًا'
CREATED = 'تم إنشاء حسابك'
MAYBE_CREATED = 'فقد تم إنشاء حسابك'
FAILED = 'تعذّر إنشاء الحساب الآن'
USER = {'id': '00000000-0000-4000-8000-0000000c0d01', 'aud': 'authenticated', 'role': 'authenticated',
        'email': 'owner@example.test', 'created_at': '2026-11-10T12:00:00Z', 'updated_at': '2026-11-10T12:00:00Z',
        'app_metadata': {'provider': 'email', 'providers': ['email']}, 'user_metadata': {}, 'is_anonymous': False}
REPLIES = {
    'existing_422': (422, {'code': 'user_already_exists', 'message': 'User already registered'},
                     {'X-Supabase-Api-Version': '2024-01-01'}),
    'existing_422_legacy': (422, {'code': 422, 'error_code': 'user_already_exists', 'msg': 'User already registered'}),
    'existing_fake': (200, {**USER, 'identities': [], 'confirmation_sent_at': '2026-11-10T12:00:00Z'}),
    'new_unconfirmed': (200, {**USER, 'identities': [{'identity_id': 'x', 'id': USER['id'], 'user_id': USER['id'],
                                                      'provider': 'email', 'identity_data': {}}],
                              'confirmation_sent_at': '2026-11-10T12:00:00Z'}),
    'network_down': None,
    'server_500': (500, {'code': 500, 'error_code': 'unexpected_failure', 'msg': 'Unexpected failure'}),
}
controls = []


def control(name, ok, **detail):
    controls.append({'name': name, 'passed': bool(ok), **detail})


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for label, width in (('desktop', 1280), ('mobile', 390)):
        for case, reply in REPLIES.items():
            ctx = browser.new_context(viewport={'width': width, 'height': 900})
            page = ctx.new_page(); errors = []; external = []; signups = []
            page.on('pageerror', lambda e: errors.append(str(e)))

            def make_route(reply):
              def route(r):
                url = r.request.url
                if url.startswith(origin + '/'): return r.continue_()
                if url.startswith('http://127.0.0.1:54321/auth/v1/signup'):
                    signups.append(url)
                    if reply is None: return r.abort('connectionrefused')
                    return r.fulfill(status=reply[0], content_type='application/json', body=json.dumps(reply[1]),
                                     headers={'Access-Control-Allow-Origin': '*',
                                              'Access-Control-Expose-Headers': 'X-Supabase-Api-Version',
                                              **(reply[2] if len(reply) > 2 else {})})
                if url.startswith('http://127.0.0.1:54321/'):
                    return r.fulfill(status=200, content_type='application/json', body='{}')
                external.append(url); r.abort()
              return route
            page.route('**/*', make_route(reply))
            page.goto(origin + '/')
            page.wait_for_function('window.authReady===true')
            page.get_by_role('button', name='حساب جديد', exact=True).click()
            page.get_by_placeholder('name@example.com').fill('owner@example.test')
            page.get_by_placeholder('••••••').fill('Xk9!long-pass-2026')
            page.get_by_role('button', name='إنشاء حساب', exact=True).click()
            page.wait_for_function('document.body.innerText.includes("%s")||document.body.innerText.includes("%s")||'
                                   'document.body.innerText.includes("%s")' % (EXISTING, CREATED, FAILED), timeout=15000)
            text = page.inner_text('body')
            signin = page.get_by_role('button', name='دخول', exact=True).count() >= 2  # tab + submit
            resend = page.get_by_role('button', name='إعادة إرسال رسالة التفعيل', exact=True).count() == 1
            nav = page.evaluate('window.authNavigations')
            base = dict(viewport=label, signup_requests=len(signups))
            if case.startswith('existing'):
                control(f'{label}_{case}_says_already_registered',
                        EXISTING in text and CREATED not in text and len(signups) == 1, **base)
                control(f'{label}_{case}_switches_to_signin_with_resend', signin and resend and nav == [], **base)
            elif case == 'new_unconfirmed':
                control(f'{label}_{case}_says_created_check_email',
                        CREATED in text and EXISTING not in text and resend and nav == [], **base)
            else:
                control(f'{label}_{case}_says_failed_not_created',
                        FAILED in text and CREATED not in text and MAYBE_CREATED not in text and nav == [], **base)
            control(f'{label}_{case}_no_script_or_external_error', not errors and not external, errors=errors[:2])
            ctx.close()
    browser.close()
server.shutdown()

result = {'probe': 'c-signup-01', 'controls': controls}
print('AUTH_SIGNUP_RESULT ' + json.dumps(result, ensure_ascii=False))
if evidence:
    evidence.mkdir(parents=True, exist_ok=True)
    (evidence / 'auth-signup.json').write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n')
failed = [c['name'] for c in controls if not c['passed']]
if failed:
    raise SystemExit('AUTH_SIGNUP_FAILED ' + ','.join(failed))
