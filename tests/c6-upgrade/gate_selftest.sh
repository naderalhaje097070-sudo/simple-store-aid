#!/bin/bash
# Self-test of the C6 acceptance gate (review fix 2026-11-19c): proves the gate FAILS where it must.
# Needs no database: it drives gate_lib.sh and probe_expect.py with synthetic inputs and a missing container.
# Exit 0 only if every negative and positive control behaves as required.
# usage: gate_selftest.sh <repo-root> <new-scratch-dir>
set -uo pipefail
R=$1; X=$2; H=$R/tests/c6-upgrade
[ -e "$X" ] && { echo "ABORT scratch dir exists: $X"; exit 2; }; mkdir -p "$X"
N=0
ok()  { echo "SELFTEST PASS $*"; }
bad() { echo "SELFTEST FAIL $*"; N=$((N + 1)); }

# --- 1. pinned probe expectations
python3 - "$X" <<'EOF'
import json, sys, copy
x = sys.argv[1]
Q = (0.5, 1.5, 0.25)
def ok_cell(q, dec, st): return {'outcome': 'OK', 'stock_type': st, 'order_tenant_ok': True, 'lines_in_order': 1,
                                'invoice_qty': q, 'stock_decrement': dec, 'qty_requested': q, 'order_id': 'x'}
good = {'state': 'syn'}
for q in Q:
    good[f'new idempotent qty={q}'] = ok_cell(q, q, 'numeric')
    good[f'v2 qty={q}'] = {'outcome': 'DENIED', 'qty_requested': q}
    good[f'legacy qty={q}'] = ok_cell(q, q, 'numeric')
def dump(name, d): json.dump(d, open(f'{x}/{name}.json', 'w'))
dump('good_after_unblock', good)
allref = {'state': 'syn'}
for k in good:
    if k != 'state': allref[k] = {'outcome': 'REFUSED', 'error': 'synthetic', 'qty_requested': good[k]['qty_requested']}
dump('all_refused', allref)
d = copy.deepcopy(good); d['legacy qty=1.5']['stock_decrement'] = 1.0; dump('wrong_decrement', d)
d = copy.deepcopy(good); del d['v2 qty=0.25']; dump('missing_cell', d)
d = copy.deepcopy(good); d['new idempotent qty=0.5']['order_tenant_ok'] = False; dump('other_tenant_order', d)
d = copy.deepcopy(good); d['new idempotent qty=0.5']['lines_in_order'] = 2; dump('two_lines', d)
d = copy.deepcopy(good); d['legacy qty=0.5'] = {'outcome': 'NO_ORDER', 'qty_requested': 0.5}; dump('no_order', d)
d = copy.deepcopy(good); d['legacy qty=0.25']['invoice_qty'] = 1.0; dump('wrong_invoice', d)
d = copy.deepcopy(good); d['v2 qty=0.5'] = ok_cell(0.5, 0.5, 'numeric'); dump('v2_open', d)
EOF
python3 "$H/probe_expect.py" "$X/good_after_unblock.json" after_unblock >/dev/null && ok "positive control: correct results pass" || bad "correct results rejected"
for case in all_refused wrong_decrement missing_cell other_tenant_order two_lines no_order wrong_invoice v2_open; do
  python3 "$H/probe_expect.py" "$X/$case.json" after_unblock >/dev/null; rc=$?
  [ $rc -eq 1 ] && ok "negative control '$case' fails (exit 1)" || bad "negative control '$case' exit $rc"
done
for cls in pre after_revert; do
  python3 "$H/probe_expect.py" "$X/all_refused.json" $cls >/dev/null; rc=$?
  [ $rc -eq 1 ] && ok "all nine refused, class $cls: fails" || bad "all refused passed for class $cls"
done

# --- 2. the gate library on the same inputs (FAIL counted, gate exit non-zero)
out=$(bash -c '. "$1/gate_lib.sh"; O=$2; cp "$2/all_refused.json" "$2/frac_syn.json"; probe_assert syn after_unblock; echo "FAILS=$FAILS"' _ "$H" "$X" 2>&1)
grep -q "^FAIL fractional syn" <<<"$out" && grep -q "FAILS=1" <<<"$out" && ok "gate probe_assert counts the nine refusals as a FAIL" || bad "gate probe_assert: $out"

# --- 3. fingerprint capture failure must ABORT (exit 2), never compare as 'changed' or 'same'
for fn in fp_same fp_differs fp_capture; do
  out=$(bash -c '. "$1/gate_lib.sh"; C=no-such-container-c6; P=$2; '"$fn"' "label" "deadbeef ledger=1"; echo "REACHED"' _ "$H" "$R/docs/reviews/c6-apply" 2>&1); rc=$?
  if [ $rc -eq 2 ] && ! grep -qE "^PASS|REACHED" <<<"$out"; then ok "$fn with an uncapturable fingerprint aborts (exit 2)"; else bad "$fn: rc=$rc $out"; fi
done
out=$(bash -c '. "$1/gate_lib.sh"; C=no-such-container-c6; P=$2; fp_capture V; echo "REACHED"' _ "$H" "$X/no-such-dir" 2>&1); rc=$?
[ $rc -eq 2 ] && ok "missing fingerprint SQL file aborts (exit 2)" || bad "missing fingerprint file: rc=$rc"

# --- 4. expect_fail must FAIL when the expected error is absent
out=$(bash -c '. "$1/gate_lib.sh"; C=no-such-container-c6; echo "select 1;" > "$2/one.sql"; expect_fail "guard" LEDGER_STATE_MISMATCH "$2/one.sql"; echo "FAILS=$FAILS"' _ "$H" "$X" 2>&1)
grep -q "^FAIL guard" <<<"$out" && grep -q "FAILS=1" <<<"$out" && ok "expect_fail without the expected error is a FAIL" || bad "expect_fail: $out"

# --- 5. output directory: an existing one is refused and left untouched
mkdir -p "$X/existing"; echo keep > "$X/existing/marker"
out=$(bash -c '. "$1/gate_lib.sh"; new_outdir "$2/existing"; echo REACHED' _ "$H" "$X" 2>&1); rc=$?
[ $rc -eq 2 ] && [ -f "$X/existing/marker" ] && ! grep -q REACHED <<<"$out" && ok "existing output directory refused and not deleted" || bad "new_outdir: rc=$rc"

# --- 6. the whole gate refuses an existing output directory before touching anything
out=$(bash "$H/review_fixes.sh" /nonexistent "$R" /nonexistent "$X/existing" 2>&1); rc=$?
[ $rc -eq 2 ] && [ -f "$X/existing/marker" ] && ok "review_fixes.sh refuses an existing output directory (exit 2, marker kept)" || bad "gate with existing dir: rc=$rc $out"

echo "== SELFTEST RESULT: $N failure(s)"
[ "$N" = 0 ] || exit 1
