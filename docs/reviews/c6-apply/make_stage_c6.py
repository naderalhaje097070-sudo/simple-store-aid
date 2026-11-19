#!/usr/bin/env python3
"""C6: emit apply blocks for migration files (same mechanism as RECOVERY-02 make_stage.py).

Differences from RECOVERY-02: files without their own BEGIN/COMMIT are executed as-is; created_by='claude-c6'.

Review fix 2026-11-19 (ledger precondition): with --base-ledger, every block first checks that the ledger
holds EXACTLY the expected version set (production's ledger plus the stages before it, in order). This binds
each stage to database identity, stage order and resume state, instead of relying on the operator.

usage: make_stage_c6.py STAGE_NAME [--inject] [--base-ledger FILE --prior V1,V2,...] file.sql [file.sql ...]
  --base-ledger FILE  first column = the production ledger versions before C6 (prod_ledger_2026-11-16.txt)
  --prior LIST        comma-separated versions applied by earlier C6 stages (may be empty)
Each file becomes one DO block; several files are emitted in order, each with its own precondition."""
import hashlib
import sys

args = sys.argv[1:]
stage = args.pop(0)
inject, base, prior = False, None, []
while args and args[0].startswith('--'):
    opt = args.pop(0)
    if opt == '--inject':
        inject = True
    elif opt == '--base-ledger':
        base = [l.split()[0] for l in open(args.pop(0)) if l.strip()]
    elif opt == '--prior':
        prior = [v for v in args.pop(0).split(',') if v]
    else:
        raise SystemExit('unknown option ' + opt)

out = []
applied = list(prior)
for i, path in enumerate(args):
    raw = open(path, 'rb').read()
    text = raw.decode('utf-8')
    md5 = hashlib.md5(raw).hexdigest()
    name = path.split('/')[-1][:-4]
    version = name[:14]
    tag = 'src' + hashlib.sha1(raw).hexdigest()[:8]
    assert f'${tag}$' not in text
    wrapped = text.count('\nBEGIN;\n') + text.startswith('BEGIN;\n')
    assert wrapped in (0, 1), path
    if wrapped:
        assert text.rstrip('\n').endswith('COMMIT;'), path
    label = stage if len(args) == 1 else f'{stage}.{i + 1}'
    out += [f"-- stage {label}", "DO $stage$", "DECLARE src text; body text;", "BEGIN",
            "  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;",
            "  PERFORM set_config('lock_timeout','5s', true);"]
    if base is not None:
        expected = sorted(set(base) | set(applied))
        assert len(expected) == len(base) + len(applied), 'duplicate version'
        emd5 = hashlib.md5(','.join(expected).encode()).hexdigest()
        out += ["  IF (SELECT md5(coalesce(string_agg(version, ',' ORDER BY version), '')) FROM supabase_migrations.schema_migrations)"
                f" <> '{emd5}' THEN RAISE EXCEPTION 'LEDGER_STATE_MISMATCH before {version}: expected exactly {len(expected)} known versions'; END IF;"]
    out += [f"  src := ${tag}${text}${tag}$;",
            f"  IF md5(src) <> '{md5}' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH {name}'; END IF;",
            "  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '%s') THEN RAISE EXCEPTION 'ALREADY_APPLIED %s'; END IF;" % (version, version)]
    if wrapped:
        out.append("  body := regexp_replace(regexp_replace(src, E'(^|\\n)BEGIN;\\n', E'\\\\1'), E'\\nCOMMIT;\\n*$', E'\\n');")
    else:
        out.append("  body := src;")
    out += ["  EXECUTE body;",
            f"  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('{version}', '{name[15:]}', ARRAY[src], 'claude-c6');"]
    if inject and i == len(args) - 1:
        out.append("  RAISE EXCEPTION 'INJECTED_FAILURE_AT_END_OF_STAGE %', '" + label + "';")
    out += ["END", "$stage$;"]
    applied.append(version)
sys.stdout.write('\n'.join(out) + '\n')
