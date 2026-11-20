"""Candidate63-only, evidence-only outlines for the B5 harness (item 3.4, post-merge run 44798187106).

Nothing here is a predicate. The historical shared modules (mcp_probe.py, owner_closure_probe.py,
egress_trace.py) stay byte-identical to the frozen A41/B50 snapshots; these helpers are used only by the
candidate adapters in tests/b5-lifecycle. Outputs are fixed class names, allowlisted syscall names and
counts: never response text, a hash of text, arguments, addresses, identifiers or row content.
"""
import re

RESPONSE_CLASSES = ('tool_error_account_inactive', 'tool_error_other', 'tool_success', 'protocol_error',
                    'unexpected_shape', 'non_200')
# The same network calls egress_trace.sanitize_syscalls attributes (egress_trace.CALLS); copied, not imported,
# so this file cannot change the historical module's behavior.
TRACED_CALLS = ('connect', 'getsockopt', 'sendmmsg', 'sendmsg', 'sendto')


def tool_response_outline(status, body, name):
    """Class of an MCP tool response and, for a successful list tool, its item count."""
    from mcp_probe import TOOLS  # lazy: ssr_runtime imports this module without tests/account-lifecycle on its path
    if status != 200:
        return {'class': 'non_200', 'items': None}
    if not isinstance(body, dict):
        return {'class': 'unexpected_shape', 'items': None}
    if body.get('error') is not None:
        return {'class': 'protocol_error', 'items': None}
    result = body.get('result')
    if not isinstance(result, dict):
        return {'class': 'unexpected_shape', 'items': None}
    if result.get('isError') is True:
        named = result.get('content') == [{'type': 'text', 'text': 'account_inactive'}]
        return {'class': 'tool_error_account_inactive' if named else 'tool_error_other', 'items': None}
    structured = result.get('structuredContent')
    value = structured.get(TOOLS.get(name)) if isinstance(structured, dict) else None
    return {'class': 'tool_success', 'items': len(value) if isinstance(value, list) else None}


LINE = re.compile(r'^(\d+)(?:<[^>]+>)?\s+\d+\.\d+\s+(.+)$')


def unfinished_outline(strace_text):
    """For each thread whose last traced call never resumed: the call's allowlisted name (else 'other'),
    and how many of those threads later show an exit or kill marker. Mirrors egress_trace's line grammar."""
    pending, exited = {}, set()
    for line in strace_text.splitlines():
        m = LINE.match(line)
        if not m:
            continue
        pid, body = int(m[1]), m[2]
        if body.startswith(('+++ exited with ', '+++ killed by ')):
            exited.add(pid)
            continue
        if body.startswith(('--- ', '+++ ')):
            continue
        if '<unfinished ...>' in body:
            c = re.match(r'(\w+)\(', body)
            pending[pid] = c[1] if c and c[1] in TRACED_CALLS else 'other'
            continue
        if re.match(r'<\.\.\. \w+ resumed>', body):
            pending.pop(pid, None)
    names = {}
    for name in pending.values():
        names[name] = names.get(name, 0) + 1
    return {'unfinished_calls': len(pending), 'unfinished_call_names': dict(sorted(names.items())),
            'unfinished_calls_then_thread_exited': sum(1 for pid in pending if pid in exited)}
