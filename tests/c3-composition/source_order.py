"""Direct CREATE ordering regression; native catalog tests remain authoritative."""
from pathlib import Path
import json
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
TRACKED = {'_create_sale_with_items_core', 'create_sale_with_items_v2', 'create_sale_with_items',
           'update_courier_outcome_v2', 'update_courier_order_state', 'create_sale_with_items_idempotent'}


def functions(path):
    text = path.read_text()
    pattern = re.compile(r'^CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+public\.(\w+)\s*\(.*?\)\s*.*?\bAS\s+(\$\w*\$)', re.M | re.S | re.I)
    for m in pattern.finditer(text):
        if m[1] in TRACKED:
            end = text.find(m[2], m.end())
            assert end >= 0
            yield m[1], text[m.end():end]


def trace(paths):
    result = {}
    for path in paths:
        result.update(functions(path))
    return result


def main():
    all_sql = sorted((ROOT / 'supabase/migrations').glob('*.sql'))
    correction = [p for p in all_sql if p.name.endswith('_c3_reconcile_financial_adapters.sql')]
    originals = [p for p in all_sql if p.name.startswith('2026081517')]
    assert len(originals) == 2
    existing = [p for p in all_sql if p not in correction + originals]
    fresh = trace(sorted(existing + originals))
    upgrade = trace(existing + originals)
    # Both pre-correction cores coerce .999 to1; legacy adapter definitions differ.
    assert 'v_qty numeric(12,2)' in fresh['_create_sale_with_items_core']
    assert fresh['create_sale_with_items'] != upgrade['create_sale_with_items']
    assert fresh['update_courier_order_state'] != upgrade['update_courier_order_state']
    if '--baseline' in sys.argv:
        print(json.dumps({'expected_red': 'C3_PRE_FORWARD_ORDER_DEPENDENCE_AND_RAW_QTY_ROUNDING', 'SQL_runtime': False}))
        return
    assert len(correction) == 1
    a, b = trace(sorted(all_sql)), trace(existing + originals + correction)
    assert a == b and set(a) == TRACKED
    for name, body in a.items():
        assert 'monjez_private.assert_active_actor()' in body, name
    assert 'public._create_sale_with_items_core(' in a['create_sale_with_items']
    assert 'public.update_courier_outcome_v2(' in a['update_courier_order_state']
    assert 'v_qty numeric;' in a['_create_sale_with_items_core']
    assert 'v_qty <> trunc(v_qty, 2)' in a['_create_sale_with_items_core']
    print('C3_SOURCE_ORDER_REGRESSION_PASS_NATIVE_CATALOG_STILL_REQUIRED')


if __name__ == '__main__':
    main()
