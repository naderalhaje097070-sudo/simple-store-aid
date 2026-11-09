#!/usr/bin/env python3
"""Emit the production apply block for one stage (identical mechanism for rehearsal and production).
usage: make_stage.py STAGE_NAME [--inject] file1.sql [file2.sql ...]"""
import sys, hashlib, re
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
    assert text.count('\nBEGIN;\n') + text.startswith('BEGIN;\n') == 1 and text.endswith('\nCOMMIT;\n'), path
    out += [f"  src := ${tag}${text}${tag}$;",
            f"  IF md5(src) <> '{md5}' THEN RAISE EXCEPTION 'SOURCE_MD5_MISMATCH {name}'; END IF;",
            "  IF EXISTS (SELECT 1 FROM supabase_migrations.schema_migrations WHERE version = '%s') THEN RAISE EXCEPTION 'ALREADY_APPLIED %s'; END IF;" % (version, version),
            "  body := regexp_replace(regexp_replace(src, E'(^|\\n)BEGIN;\\n', E'\\\\1'), E'\\nCOMMIT;\\n$', E'\\n');",
            "  EXECUTE body;",
            f"  INSERT INTO supabase_migrations.schema_migrations(version, name, statements, created_by) VALUES ('{version}', '{name[15:]}', ARRAY[src], 'claude-recovery-02');"]
if inject: out.append("  RAISE EXCEPTION 'INJECTED_FAILURE_AT_END_OF_STAGE %', '" + stage + "';")
out += ["END", "$stage$;"]
sys.stdout.write('\n'.join(out) + '\n')
