"""Fail-closed process evidence, including setup failure before user creation."""
import json
import os
from pathlib import Path
import pwd
import subprocess


def process_state(lookup=pwd.getpwnam, run=subprocess.run):
    try:
        uid = lookup('g01-app').pw_uid
    except KeyError:
        return {'state': 'user_absent', 'removed': True}
    except Exception:
        return {'state': 'user_lookup_failed', 'removed': False}
    try:
        result = run(['pgrep', '-u', str(uid)], capture_output=True, timeout=10)
    except (OSError, subprocess.TimeoutExpired):
        return {'state': 'process_read_failed', 'removed': False}
    if result.returncode == 1:
        return {'state': 'no_processes', 'removed': True}
    if result.returncode == 0:
        return {'state': 'processes_remaining', 'removed': False}
    return {'state': 'process_read_failed', 'removed': False}


def main():
    root = Path(os.environ['RUNNER_TEMP'])
    state = process_state()
    try:
        containers = subprocess.run(['docker', 'ps', '-a', '--format', '{{.Names}}'],
                                    capture_output=True, text=True, check=True, timeout=15)
        container_state = 'absent' if 'g01-stack' not in containers.stdout else 'remaining'
    except (OSError, subprocess.SubprocessError):
        container_state = 'read_failed'
    checks = {'status_removed': not (root/'g01-status.json').exists(),
              'worker_env_removed': not Path('/tmp/g01-runtime/worker.env').exists(),
              'processes_removed': state['removed'],
              'containers_removed': container_state == 'absent'}
    receipt = {**checks, 'process_state': state['state'], 'container_state': container_state,
               'source_sha': os.environ['EXPECTED_SOURCE'], 'passed': all(checks.values())}
    out = root/'g01-evidence'; out.mkdir(exist_ok=True)
    (out/'cleanup.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    return 0 if receipt['passed'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
