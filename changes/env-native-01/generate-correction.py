"""Render reviewed lifecycle SQL from the immutable effective baseline catalog."""
import argparse
import hashlib
import json
from pathlib import Path

CATALOG_SHA256 = 'ae003518e72ad84b6c7730def82c67a4c466b4ded6b0aba2830d9ec8f4d024b6'
GUARD = '  PERFORM monjez_private.assert_active_actor();\n'
HELPERS = '''CREATE SCHEMA monjez_private;
REVOKE ALL ON SCHEMA monjez_private FROM PUBLIC, anon, authenticated, service_role;
GRANT USAGE ON SCHEMA monjez_private TO authenticated, service_role;

CREATE FUNCTION monjez_private.actor_is_active()
RETURNS boolean LANGUAGE sql STABLE SECURITY DEFINER SET search_path = ''
AS $guard$
  SELECT EXISTS (
    SELECT 1 FROM auth.users u
    WHERE u.id = (SELECT auth.uid()) AND u.deleted_at IS NULL
      AND (u.banned_until IS NULL OR u.banned_until <= statement_timestamp())
  );
$guard$;

CREATE FUNCTION monjez_private.assert_active_actor()
RETURNS void LANGUAGE plpgsql STABLE SECURITY DEFINER SET search_path = ''
AS $guard$
BEGIN
  -- Connection role survives SECURITY DEFINER; current_user does not.
  IF current_setting('role', true) IN ('service_role', 'supabase_admin')
     OR (current_setting('role', true) = 'none'
         AND session_user IN ('postgres', 'supabase_admin')) THEN
    RETURN;
  END IF;
  IF NOT monjez_private.actor_is_active() THEN
    RAISE EXCEPTION USING ERRCODE = '42501', MESSAGE = 'account_inactive';
  END IF;
END;
$guard$;

REVOKE ALL ON ALL FUNCTIONS IN SCHEMA monjez_private FROM PUBLIC, anon;
GRANT EXECUTE ON FUNCTION monjez_private.actor_is_active(),
  monjez_private.assert_active_actor() TO authenticated, service_role;
'''


def guarded(definition):
    header, body, tail = definition.split('$function$')
    if tail.strip():
        raise ValueError('unexpected function delimiter tail')
    if 'LANGUAGE sql' in header:
        query = body.strip().removesuffix(';')
        if not query.startswith('SELECT'):
            raise ValueError('unexpected scalar SQL function')
        header = header.replace('LANGUAGE sql', 'LANGUAGE plpgsql')
        body = '\nBEGIN\n' + GUARD + '  RETURN (\n' + query + '\n  );\nEND;\n'
    else:
        if 'LANGUAGE plpgsql' not in header or '\nBEGIN\n' not in body:
            raise ValueError('unexpected PL/pgSQL function')
        body = body.replace('\nBEGIN\n', '\nBEGIN\n' + GUARD, 1)
    return header + '$function$' + body + '$function$;\n'


def render(raw):
    if hashlib.sha256(raw).hexdigest() != CATALOG_SHA256:
        raise ValueError('baseline catalog digest mismatch')
    catalog = json.loads(raw)
    exposed = [f for f in catalog['functions'] if f['definer'] and 'authenticated=X/' in f['acl']]
    internal = [f for f in catalog['functions'] if f['name'] in ('_assert_owner', '_assert_staff', '_assert_platform_admin')]
    if len(exposed) != 30 or len(internal) != 3:
        raise ValueError('unexpected guard surface')
    tables = sorted({p['tablename'] for p in catalog['policies']})
    if len(tables) != 22:
        raise ValueError('unexpected policy surface')
    policies = ''.join(f'CREATE POLICY monjez_live_actor ON public.{t}\n  AS RESTRICTIVE FOR ALL TO authenticated\n  USING ((SELECT monjez_private.actor_is_active()))\n  WITH CHECK ((SELECT monjez_private.actor_is_active()));\n\n' for t in tables)
    definitions = ''.join(guarded(f['definition']) for f in internal + exposed)
    correction = '-- ENV-NATIVE-01: additive caller lifecycle enforcement; no row mutations.\nBEGIN;\n' + HELPERS + '\n' + policies + definitions + 'COMMIT;\n'
    rollback = '-- HUMAN APPROVAL REQUIRED: compensating rollback reopens ENV-NATIVE-01.\nBEGIN;\n'
    rollback += ''.join(f['definition'] + ';\n' for f in internal + exposed)
    rollback += ''.join(f'DROP POLICY monjez_live_actor ON public.{t};\n' for t in tables)
    rollback += 'DROP FUNCTION monjez_private.assert_active_actor();\nDROP FUNCTION monjez_private.actor_is_active();\nDROP SCHEMA monjez_private;\nCOMMIT;\n'
    return correction, rollback


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--catalog', type=Path, required=True)
    p.add_argument('--migration', type=Path, required=True)
    p.add_argument('--rollback', type=Path, required=True)
    a = p.parse_args()
    sql, rollback = render(a.catalog.read_bytes())
    a.migration.write_text(sql)
    a.rollback.parent.mkdir(parents=True, exist_ok=True)
    a.rollback.write_text(rollback)
