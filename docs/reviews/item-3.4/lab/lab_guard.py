"""Target guard for the item 3.4 lab helpers, run BEFORE any request or SQL that can write.

The helpers bypass the probe constructor (it needs the CI containment preflight), so they must enforce the
same target identity live_probe.Probe.__init__ enforces, plus a synthetic-only check of the target:
  * require_write_harness(): explicit write opt-in, no proxy routing, loopback PG on 54322, local/ci target;
  * CI_ISOLATED_SUPABASE=1;
  * status API_URL == config.supabase_url == http://127.0.0.1:54321, and both disposable keys present;
  * every existing auth identity on the target is synthetic (example.test / example.invalid / mongezz.test).
Any failure raises before a single write.
"""
import json
import os
import re

from write_harness_guard import require_write_harness
from live_probe import HarnessFailure
from write_harness_guard import _psql_command, _psql_env
import subprocess

LOOPBACK_API = 'http://127.0.0.1:54321'
SYNTHETIC = re.compile(r'.+@(example\.test|example\.invalid|mongezz\.test)')


def guarded_target(status_file):
    config = require_write_harness()
    if os.environ.get('CI_ISOLATED_SUPABASE') != '1':
        raise HarnessFailure('isolated runner marker missing')
    status = json.loads(status_file.read_text())
    base = status.get('API_URL', '').rstrip('/')
    if base != config.supabase_url or base != LOOPBACK_API:
        raise HarnessFailure('CLI API target mismatch')
    for key in ('ANON_KEY', 'SERVICE_ROLE_KEY'):
        if not isinstance(status.get(key), str) or not status[key]:
            raise HarnessFailure('missing disposable stack keys')
    run = subprocess.run(_psql_command(config, '-Atq', '-v', 'ON_ERROR_STOP=1'),
                         input="select coalesce(json_agg(email),'[]') from auth.users;",
                         capture_output=True, text=True, env=_psql_env(config))
    if run.returncode:
        raise HarnessFailure('target identity read failed')
    emails = json.loads(run.stdout.strip())
    if not all(isinstance(e, str) and SYNTHETIC.fullmatch(e) for e in emails):
        raise HarnessFailure('target holds non-synthetic identities')
    return config, status, base, len(emails)
