#!/usr/bin/env python3
"""C6: emit the apply block for one migration file (same mechanism as RECOVERY-02 make_stage.py).
Differences from RECOVERY-02: files without their own BEGIN/COMMIT are executed as-is; created_by='claude-c6'.
usage: make_stage_c6.py STAGE_NAME [--inject] file.sql"""
import sys, hashlib
args = sys.argv[1:]; stage = args.pop(0); inject = False
if args and args[0] == '--inject': inject = True; args.pop(0)
out = [f"-- stage {stage}", "DO $stage$", "DECLARE src text; body text;", "BEGIN",
       "  IF current_user <> 'postgres' THEN RAISE EXCEPTION 'APPLY_REQUIRES_POSTGRES'; END IF;",
       "  PERFORM set_config('lock_timeout','5s', true);"]
for path in args:
    raw = open(path, 'rb').read(); text = raw.decode('utf-8'); md5 = hashlib.md5(raw).hexdigest()
    name = path.split('/')[-1][:-4]; version = name[:14]
    tag = 'src' + hashlib.sha1(raw).hexdigest()[:8]
    assert f'${tag}$' not in text
    wrapped = text.count('\nBEGIN;\n') + text.startswith('BEGIN;\n')
    assert wrapped in (0, 1), path
    if wrapped: assert text.rstrip('\n').endswith('COMMIT;'), path
    out += [f"  src := ${tag}${text}${tag}$;",
            f"  IF md5(src) <> '{md5}' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH {name}'; END IF;",
            "  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '%s') THEN RAISE EXCEPTION 'ALREADY_APPLIED %s'; END IF;" % (version, version)]
    if wrapped:
        out.append("  body := regexp_replace(regexp_replace(src, E'(^|\\n)BEGIN;\\n', E'\\\\1'), E'\\nCOMMIT;\\n*$', E'\\n');")
    else:
        out.append("  body := src;")
    out += ["  EXECUTE body;",
            f"  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('{version}', '{name[15:]}', ARRAY[src], 'claude-c6');"]
if inject: out.append("  RAISE EXCEPTION 'INJECTED_FAILURE_AT_END_OF_STAGE %', '" + stage + "';")
out += ["END", "$stage$;"]
sys.stdout.write('\n'.join(out) + '\n')
