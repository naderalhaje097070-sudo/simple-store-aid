-- Release restore check (C6/C7 plan 2.2): the application triggers that live on tables OUTSIDE the application
-- schemas (e.g. auth.users -> public.handle_new_user, created by migration 20260626142422). The Supabase CLI schema
-- dump does not include them, so a restore without them silently loses sign-up provisioning. Read only; prints one
-- CREATE TRIGGER statement per trigger, to be applied after the schema in the same restore transaction.
begin transaction read only;
set local search_path to pg_catalog;
select pg_get_triggerdef(t.oid) || ';'
from pg_trigger t join pg_class c on c.oid = t.tgrelid join pg_proc f on f.oid = t.tgfoid
where not t.tgisinternal
  and c.relnamespace not in (select oid from pg_namespace where nspname in ('public', 'monjez_private'))
  and f.pronamespace in (select oid from pg_namespace where nspname in ('public', 'monjez_private'))
order by c.relnamespace::regnamespace::text, c.relname, t.tgname;
rollback;
