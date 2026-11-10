"""Sign-up and resend screens must not reveal whether an email has an account.

Runs the actual src/routes/auth.tsx screen and the real supabase-js client in
Chromium; GoTrue replies are answered in the browser. Shapes observed on a local
GoTrue v2.188.1 with email confirmations on (2026-11-10), headers as supabase-js
receives them (it sends X-Supabase-Api-Version: 2024-01-01):
  new / existing_unconfirmed  200, user with 1 identity, no session (same shape)
  existing_confirmed_422      422 {"code":"user_already_exists",...}
  existing_422_legacy         the same refusal without the API-version header
  existing_fake               documented enumeration-protection reply: user, no identities
  resend_*                    200 {} for confirmed, unknown and pending emails alike
Controls: every account-state case leaves the screen in exactly the same visible
state (same text, same mode, same buttons, password cleared, no navigation), and
never says the email is registered or that an account was created. Transport and
server failures say the attempt failed. No network beyond the local fixture server.
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

NEUTRAL = 'إذا كان هذا البريد غير مسجّل، فقد طلبنا إرسال رابط التفعيل إليه'
RESEND_NEUTRAL = 'إذا كان لهذا البريد حساب لم يُفعَّل بعد'
FAILED = 'تعذّر إنشاء الحساب الآن'
LEAKS = ('مسجّل مسبقًا', 'تم إنشاء حسابك', 'فقد تم إنشاء حسابك', 'أرسلنا رسالة التفعيل',
         'تم إرسال الرابط مؤخراً', 'تم الإرسال مؤخراً')
V2024 = {'X-Supabase-Api-Version': '2024-01-01'}
USER = {'id': '00000000-0000-4000-8000-0000000c0d01', 'aud': 'authenticated', 'role': 'authenticated',
        'email': 'owner@example.test', 'created_at': '2026-11-10T12:00:00Z', 'updated_at': '2026-11-10T12:00:00Z',
        'confirmation_sent_at': '2026-11-10T12:00:00Z', 'app_metadata': {'provider': 'email', 'providers': ['email']},
        'user_metadata': {}, 'is_anonymous': False}
ONE_IDENTITY = [{'identity_id': 'x', 'id': USER['id'], 'user_id': USER['id'], 'provider': 'email', 'identity_data': {}}]
ACCOUNT_STATES = {
    'new': (200, {**USER, 'identities': ONE_IDENTITY}, V2024),
    'existing_unconfirmed': (200, {**USER, 'identities': ONE_IDENTITY}, V2024),
    'existing_confirmed_422': (422, {'code': 'user_already_exists', 'message': 'User already registered'}, V2024),
    'existing_422_legacy': (422, {'code': 422, 'error_code': 'user_already_exists', 'msg': 'User already registered'}, {}),
    'existing_fake': (200, {**USER, 'identities': []}, V2024),
    # Measured with the default 60s send interval: sign-up again within 60s for an existing
    # unconfirmed email (a new email gets 200). Verbatim body.
    'existing_pending_429': (429, {'code': 'over_email_send_rate_limit',
                                   'message': 'For security purposes, you can only request this after 59 seconds.'}, V2024),
}
FAILURES = {
    'network_down': None,
    'server_500': (500, {'code': 'unexpected_failure', 'message': 'Unexpected failure'}, V2024),
}
RESENDS = {
    'resend_any_email': ((200, {}, V2024), RESEND_NEUTRAL),
    # Measured: resend within 60s for a pending account gets 429 (unknown/confirmed: 200).
    'resend_rate_limited': ((429, {'code': 'over_email_send_rate_limit',
                                   'message': 'For security purposes, you can only request this after 59 seconds.'}, V2024),
                            RESEND_NEUTRAL),
}
controls = []


def control(name, ok, **detail):
    controls.append({'name': name, 'passed': bool(ok), **detail})


def make_route(signup_reply, resend_reply, calls, external):
    def answer(r, reply):
        if reply is None: return r.abort('connectionrefused')
        return r.fulfill(status=reply[0], content_type='application/json', body=json.dumps(reply[1]),
                         headers={'Access-Control-Allow-Origin': '*',
                                  'Access-Control-Expose-Headers': 'X-Supabase-Api-Version', **reply[2]})

    def route(r):
        url = r.request.url
        if url.startswith(origin + '/'): return r.continue_()
        if url.startswith('http://127.0.0.1:54321/auth/v1/signup'):
            calls.append('signup'); return answer(r, signup_reply)
        if url.startswith('http://127.0.0.1:54321/auth/v1/resend'):
            calls.append('resend'); return answer(r, resend_reply)
        if url.startswith('http://127.0.0.1:54321/'):
            return r.fulfill(status=200, content_type='application/json', body='{}')
        external.append(url); r.abort()
    return route


def screen_state(page):
    card = page.locator('form').first
    return {
        'text': card.inner_text(),
        'signin_submit': page.get_by_role('button', name='دخول', exact=True).count() >= 2,
        'resend_button': page.get_by_role('button', name='إعادة إرسال رسالة التفعيل', exact=True).count(),
        'password_empty': page.get_by_placeholder('••••••').input_value() == '',
        'email_kept': page.get_by_placeholder('name@example.com').input_value() == 'owner@example.test',
        'navigations': page.evaluate('window.authNavigations'),
    }


def sign_up(browser, width, signup_reply, resend_reply=None):
    ctx = browser.new_context(viewport={'width': width, 'height': 900})
    page = ctx.new_page(); errors = []; external = []; calls = []
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.route('**/*', make_route(signup_reply, resend_reply, calls, external))
    page.goto(origin + '/')
    page.wait_for_function('window.authReady===true')
    page.get_by_role('button', name='حساب جديد', exact=True).click()
    page.get_by_placeholder('name@example.com').fill('owner@example.test')
    page.get_by_placeholder('••••••').fill('Xk9!long-pass-2026')
    page.get_by_role('button', name='إنشاء حساب', exact=True).click()
    page.wait_for_function('%s.some(t=>document.body.innerText.includes(t))'
                           % json.dumps([NEUTRAL, FAILED, *LEAKS], ensure_ascii=False), timeout=15000)
    return ctx, page, errors, external, calls


with sync_playwright() as pw:
    browser = pw.chromium.launch(headless=True)
    for label, width in (('desktop', 1280), ('mobile', 390)):
        states = {}
        for case, reply in ACCOUNT_STATES.items():
            ctx, page, errors, external, calls = sign_up(browser, width, reply)
            st = screen_state(page); states[case] = st
            control(f'{label}_{case}_neutral_message_no_account_claim',
                    NEUTRAL in st['text'] and not any(x in st['text'] for x in LEAKS) and calls == ['signup'])
            control(f'{label}_{case}_signin_mode_resend_password_cleared',
                    st['signin_submit'] and st['resend_button'] == 1 and st['password_empty'] and st['email_kept']
                    and st['navigations'] == [])
            control(f'{label}_{case}_no_script_or_external_error', not errors and not external, errors=errors[:2])
            ctx.close()
        reference = states['new']
        control(f'{label}_all_account_states_render_identically',
                all(st == reference for st in states.values()),
                differing=sorted(k for k, st in states.items() if st != reference))

        for case, reply in FAILURES.items():
            ctx, page, errors, external, calls = sign_up(browser, width, reply)
            st = screen_state(page)
            control(f'{label}_{case}_says_failed_not_created',
                    FAILED in page.inner_text('body') and NEUTRAL not in page.inner_text('body')
                    and not any(x in page.inner_text('body') for x in LEAKS) and st['navigations'] == [])
            control(f'{label}_{case}_no_script_or_external_error', not errors and not external, errors=errors[:2])
            ctx.close()

        resend_states = {}
        for case, (reply, expected) in RESENDS.items():
            ctx, page, errors, external, calls = sign_up(browser, width, ACCOUNT_STATES['new'], reply)
            page.get_by_role('button', name='إعادة إرسال رسالة التفعيل', exact=True).click()
            page.wait_for_function('%s.some(t=>document.body.innerText.includes(t))'
                                   % json.dumps([expected, *LEAKS], ensure_ascii=False), timeout=15000)
            body = page.inner_text('body')
            resend_states[case] = screen_state(page)
            control(f'{label}_{case}_message', expected in body and not any(x in body for x in LEAKS)
                    and calls == ['signup', 'resend'])
            control(f'{label}_{case}_no_script_or_external_error', not errors and not external, errors=errors[:2])
            ctx.close()
        control(f'{label}_resend_states_render_identically',
                resend_states['resend_any_email'] == resend_states['resend_rate_limited'])
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
