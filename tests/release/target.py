"""Runtime migration target for financial suites, taken from the release gate.

Older suites pinned a stage-specific target (54 or 55 migrations). Under the
release workflow they use this instead: the commit and checkout are verified by
the gate, and the database history must equal the gate-verified migration set.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gate import GateFailure, check, verify, verify_migrations  # noqa: E402


def verify_source(root):
    receipt = verify(root)
    versions = verify_migrations(root)
    return versions, receipt


def verify_history(versions, observed):
    check(isinstance(observed, list) and all(type(v) is str for v in observed), 'Invalid database history')
    check(observed == versions, 'Database history differs from release migrations')


__all__ = ['GateFailure', 'verify_source', 'verify_history']
