#!/usr/bin/env python3
"""Pinned expectations for fractional_probe.py output (review fix 2026-11-19c).

Every (path, qty) cell must match exactly; a missing cell, an unexpected refusal, an unlinked order or a
wrong decrement fails. Exit 0 = all cells match, 1 = any mismatch.

classes:
  pre    state C0 (production today) and every failed/rolled-back bundle: the idempotent and v2 paths are
         ABSENT; the legacy path is OK and rounds integer stock (documented C0 defect, pinned exactly)
  after_unblock   after BUNDLE_C1_C10_UNBLOCK: idempotent OK, legacy OK (unblocked), v2 DENIED;
                  every OK decrement equals the invoice quantity, stock numeric
  after_revert    after the revert: idempotent OK, v2 DENIED, legacy DENIED

usage: probe_expect.py PROBE_JSON CLASS
"""
import json
import sys

QTYS = (0.5, 1.5, 0.25)
ROUNDED = {0.5: 0.0, 1.5: 1.0, 0.25: 0.0}   # integer stock: decrement as PostgreSQL rounds it (C0 defect)
EXPECT = {
    'pre': {'new idempotent': 'ABSENT', 'v2': 'ABSENT', 'legacy': ('OK', 'integer', 'rounded')},
    'after_unblock': {'new idempotent': ('OK', 'numeric', 'exact'), 'v2': 'DENIED', 'legacy': ('OK', 'numeric', 'exact')},
    'after_revert': {'new idempotent': ('OK', 'numeric', 'exact'), 'v2': 'DENIED', 'legacy': 'DENIED'},
}


def check(d, cls):
    errors = []
    for path, exp in EXPECT[cls].items():
        for q in QTYS:
            key = f'{path} qty={q}'
            v = d.get(key)
            if not isinstance(v, dict):
                errors.append(f'{key}: missing'); continue
            if isinstance(exp, str):
                if v.get('outcome') != exp:
                    errors.append(f"{key}: outcome {v.get('outcome')} != {exp}")
                continue
            outcome, stock_type, rule = exp
            if v.get('outcome') != outcome:
                errors.append(f"{key}: outcome {v.get('outcome')} != {outcome} ({v.get('error', '')})"); continue
            want_dec = ROUNDED[q] if rule == 'rounded' else q
            for field, want in (('stock_type', stock_type), ('order_tenant_ok', True), ('lines_in_order', 1),
                                ('invoice_qty', q), ('stock_decrement', want_dec), ('qty_requested', q)):
                got = v.get(field)
                ok = abs(float(got) - float(want)) < 1e-9 if isinstance(want, float) and got is not None else got == want
                if not ok:
                    errors.append(f'{key}: {field} {got!r} != {want!r}')
    return errors


if __name__ == '__main__':
    d = json.load(open(sys.argv[1]))
    errs = check(d, sys.argv[2])
    for e in errs:
        print('   mismatch:', e)
    sys.exit(1 if errs else 0)
