-- Release restore check (C6/C7 plan item 2.2): catalog fingerprint of the application schemas, one line per object.
-- Read only. ACLs are normalized with acldefault(), so a NULL ACL and an explicit owner-only ACL compare equal
-- (they grant the same thing); every other grant difference shows. Output is sorted for a plain text diff.
begin transaction read only;
with ns as (select oid, nspname from pg_namespace where nspname in ('public', 'monjez_private')),
rel as (
  select 'rel|' || n.nspname || '.' || c.relname || '|' || md5(
           c.relkind::text || '|' || c.relrowsecurity || '|' || c.relforcerowsecurity || '|' || c.relowner::regrole::text || '|'
           || coalesce(c.relacl, acldefault(case when c.relkind = 'S' then 's'::"char" else 'r'::"char" end, c.relowner))::text || '|'
           || coalesce((select string_agg(a.attname || ':' || format_type(a.atttypid, a.atttypmod) || ':' || a.attnotnull || ':'
                                          || coalesce(pg_get_expr(d.adbin, d.adrelid), '') || ':' || coalesce(a.attacl::text, ''),
                                          ',' order by a.attnum)
                        from pg_attribute a left join pg_attrdef d on d.adrelid = a.attrelid and d.adnum = a.attnum
                        where a.attrelid = c.oid and a.attnum > 0 and not a.attisdropped), '') || '|'
           -- review fix (#98, Graphify P2): a view or materialized view's defining query is part of the relation, so a
           -- changed query with the same columns changes the line
           || case when c.relkind in ('v', 'm') then coalesce(pg_get_viewdef(c.oid), '') else '' end) as line
  from pg_class c join ns n on n.oid = c.relnamespace
  where c.relkind in ('r', 'p', 'v', 'm', 'S', 'f')),
fn as (
  select 'fn|' || p.oid::regprocedure::text || '|' || md5(
           p.prokind::text || '|' || p.proowner::regrole::text || '|' || p.prosecdef || '|' || coalesce(p.proconfig::text, '') || '|'
           || coalesce(p.proacl, acldefault('f'::"char", p.proowner))::text || '|'
           || case when p.prokind in ('f', 'p', 'w') then pg_get_functiondef(p.oid) else '' end) as line
  from pg_proc p join ns n on n.oid = p.pronamespace),
pol as (
  select 'policy|' || p.polrelid::regclass::text || '.' || p.polname || '|' || md5(
           p.polpermissive || '|' || p.polcmd::text || '|' || array_to_string(p.polroles::regrole[]::text[], ',') || '|'
           || coalesce(pg_get_expr(p.polqual, p.polrelid), '') || '|' || coalesce(pg_get_expr(p.polwithcheck, p.polrelid), '')) as line
  from pg_policy p join pg_class c on c.oid = p.polrelid join ns n on n.oid = c.relnamespace),
con as (
  select 'constraint|' || c.conrelid::regclass::text || '.' || c.conname || '|' || md5(pg_get_constraintdef(c.oid)) as line
  from pg_constraint c join ns n on n.oid = c.connamespace where c.conrelid <> 0),
idx as (
  select 'index|' || n.nspname || '.' || i.relname || '|' || md5(pg_get_indexdef(i.oid)) as line
  from pg_index x join pg_class i on i.oid = x.indexrelid join ns n on n.oid = i.relnamespace),
trg as (
  select 'trigger|' || t.tgrelid::regclass::text || '.' || t.tgname || '|' || md5(pg_get_triggerdef(t.oid)) as line
  -- any table: an application trigger may sit on a platform table (auth.users -> handle_new_user)
  from pg_trigger t join pg_class c on c.oid = t.tgrelid join pg_proc f on f.oid = t.tgfoid
  where not t.tgisinternal and (c.relnamespace in (select oid from ns) or f.pronamespace in (select oid from ns))),
typ as (
  select 'type|' || n.nspname || '.' || t.typname || '|' || md5(t.typtype::text || '|'
           || coalesce((select string_agg(e.enumlabel, ',' order by e.enumsortorder) from pg_enum e where e.enumtypid = t.oid), '')) as line
  from pg_type t join ns n on n.oid = t.typnamespace where t.typtype in ('e', 'd') or (t.typtype = 'c' and exists (select 1 from pg_class rc where rc.oid = t.typrelid and rc.relkind = 'c'))),
dacl as (
  select 'default_acl|' || d.defaclrole::regrole::text || '.' || n.nspname || '.' || d.defaclobjtype::text || '|' || md5(d.defaclacl::text) as line
  from pg_default_acl d join ns n on n.oid = d.defaclnamespace),
sch as (
  select 'schema|' || n.nspname || '|' || md5(coalesce(n.nspacl::text, '')) as line from pg_namespace n join ns s on s.oid = n.oid)
select line from (select line from rel union all select line from fn union all select line from pol union all select line from con
                  union all select line from idx union all select line from trg union all select line from typ
                  union all select line from dacl union all select line from sch) all_lines
order by line;
rollback;
