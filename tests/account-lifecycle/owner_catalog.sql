SELECT jsonb_build_object(
 'settings',jsonb_build_object('server_version',current_setting('server_version'),
   'transaction_read_only',current_setting('transaction_read_only'),
   'session_replication_role',current_setting('session_replication_role')),
 'schemas',(SELECT jsonb_agg(nspname ORDER BY nspname) FROM pg_namespace
   WHERE nspname IN ('auth','public','storage','monjez_private')),
 'fks',(SELECT coalesce(jsonb_agg(x ORDER BY x.child,x.name),'[]') FROM (
   SELECT c.conname name,n.nspname||'.'||t.relname child,
     rn.nspname||'.'||rt.relname parent,
     ARRAY(SELECT a.attname FROM unnest(c.conkey) WITH ORDINALITY k(id,pos)
       JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=k.id ORDER BY k.pos) child_columns,
     ARRAY(SELECT a.attname FROM unnest(c.confkey) WITH ORDINALITY k(id,pos)
       JOIN pg_attribute a ON a.attrelid=c.confrelid AND a.attnum=k.id ORDER BY k.pos) parent_columns,
     CASE c.confdeltype WHEN 'a' THEN 'NO ACTION' WHEN 'r' THEN 'RESTRICT'
       WHEN 'c' THEN 'CASCADE' WHEN 'n' THEN 'SET NULL' WHEN 'd' THEN 'SET DEFAULT' END on_delete,
     c.confupdtype::text on_update_code,c.confmatchtype::text match_code,
     c.condeferrable AS "deferrable",c.condeferred AS "deferred",c.convalidated validated,
     c.confdelsetcols delete_set_columns,pg_get_constraintdef(c.oid,true) definition
   FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
   JOIN pg_namespace n ON n.oid=t.relnamespace JOIN pg_class rt ON rt.oid=c.confrelid
   JOIN pg_namespace rn ON rn.oid=rt.relnamespace
   WHERE c.contype='f' AND (n.nspname IN ('auth','public','storage','monjez_private')
      OR rn.nspname IN ('auth','public','storage','monjez_private'))
 ) x),
 'constraints',(SELECT coalesce(jsonb_agg(x ORDER BY x.relation,x.name),'[]') FROM (
   SELECT n.nspname||'.'||t.relname relation,c.conname name,c.contype::text type,
     c.convalidated validated,c.condeferrable AS "deferrable",c.condeferred AS "deferred",
     pg_get_constraintdef(c.oid,true) definition
   FROM pg_constraint c JOIN pg_class t ON t.oid=c.conrelid
   JOIN pg_namespace n ON n.oid=t.relnamespace
   WHERE n.nspname IN ('auth','public','storage','monjez_private')
 ) x),
 'columns',(SELECT coalesce(jsonb_agg(x ORDER BY x.relation,x.position),'[]') FROM (
   SELECT n.nspname||'.'||c.relname relation,a.attname name,a.attnum AS "position",
     format_type(a.atttypid,a.atttypmod) type,a.attnotnull not_null,
     pg_get_expr(d.adbin,d.adrelid) default_expression
   FROM pg_attribute a JOIN pg_class c ON c.oid=a.attrelid
   JOIN pg_namespace n ON n.oid=c.relnamespace LEFT JOIN pg_attrdef d
     ON d.adrelid=a.attrelid AND d.adnum=a.attnum
   WHERE n.nspname IN ('auth','public','storage','monjez_private')
     AND c.relkind IN ('r','p') AND a.attnum>0 AND NOT a.attisdropped
 ) x),
 'triggers',(SELECT coalesce(jsonb_agg(x ORDER BY x.relation,x.name),'[]') FROM (
   SELECT n.nspname||'.'||c.relname relation,t.tgname name,t.tgenabled::text enabled,
     t.tgisinternal internal,t.tgdeferrable AS "deferrable",t.tginitdeferred AS "deferred",
     pn.nspname||'.'||p.proname AS "function",t.tgtype::integer type_bits,
     pg_get_triggerdef(t.oid,true) definition,co.conname constraint_name
   FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
   JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_proc p ON p.oid=t.tgfoid
   JOIN pg_namespace pn ON pn.oid=p.pronamespace LEFT JOIN pg_constraint co ON co.oid=t.tgconstraint
   WHERE n.nspname IN ('auth','public','storage','monjez_private')
 ) x),
 'functions',(SELECT coalesce(jsonb_agg(x ORDER BY x.name,x.arguments),'[]') FROM (
   SELECT n.nspname||'.'||p.proname name,pg_get_function_identity_arguments(p.oid) arguments,
     p.prosecdef definer,p.provolatile::text volatility,p.proconfig config,
     p.proacl::text acl,r.rolname owner,r.rolbypassrls owner_bypass_rls,
     p.prosrc body,pg_get_functiondef(p.oid) definition,
     jsonb_build_object('anon',has_function_privilege('anon',p.oid,'EXECUTE'),
       'authenticated',has_function_privilege('authenticated',p.oid,'EXECUTE'),
       'service_role',has_function_privilege('service_role',p.oid,'EXECUTE')) execute
   FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
   JOIN pg_roles r ON r.oid=p.proowner WHERE p.prokind='f' AND
   (n.nspname IN ('public','monjez_private') OR p.oid IN (
     SELECT tgfoid FROM pg_trigger t JOIN pg_class c ON c.oid=t.tgrelid
     JOIN pg_namespace ns ON ns.oid=c.relnamespace WHERE ns.nspname IN ('auth','storage')))
 ) x),
 'relations',(SELECT coalesce(jsonb_agg(x ORDER BY x.relation),'[]') FROM (
   SELECT n.nspname||'.'||c.relname relation,c.relkind::text kind,
     c.relrowsecurity rls,c.relforcerowsecurity force_rls,c.relacl::text acl,r.rolname owner,
     (SELECT jsonb_object_agg(role,rights ORDER BY role) FROM (
       SELECT role,jsonb_build_object('SELECT',has_table_privilege(role,c.oid,'SELECT'),
         'INSERT',has_table_privilege(role,c.oid,'INSERT'),'UPDATE',has_table_privilege(role,c.oid,'UPDATE'),
         'DELETE',has_table_privilege(role,c.oid,'DELETE'),'TRUNCATE',has_table_privilege(role,c.oid,'TRUNCATE'),
         'REFERENCES',has_table_privilege(role,c.oid,'REFERENCES'),'TRIGGER',has_table_privilege(role,c.oid,'TRIGGER')) rights
       FROM unnest(ARRAY['anon','authenticated','service_role']) role) g) privileges
   FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace JOIN pg_roles r ON r.oid=c.relowner
   WHERE n.nspname IN ('auth','public','storage','monjez_private') AND c.relkind IN ('r','p','v','m')
 ) x),
 'policies',(SELECT coalesce(jsonb_agg(to_jsonb(p) ORDER BY schemaname,tablename,policyname),'[]')
   FROM pg_policies p WHERE schemaname IN ('auth','public','storage','monjez_private')),
 'roles',(SELECT jsonb_agg(jsonb_build_object('name',rolname,'superuser',rolsuper,
   'inherit',rolinherit,'bypass_rls',rolbypassrls,'login',rolcanlogin) ORDER BY rolname)
   FROM pg_roles),
 'memberships',(SELECT coalesce(jsonb_agg(jsonb_build_object('role',r.rolname,'member',m.rolname,
   'admin_option',am.admin_option,'inherit_option',am.inherit_option,'set_option',am.set_option)
   ORDER BY r.rolname,m.rolname),'[]') FROM pg_auth_members am
   JOIN pg_roles r ON r.oid=am.roleid JOIN pg_roles m ON m.oid=am.member),
 'schema_privileges',(SELECT jsonb_agg(jsonb_build_object('schema',n.nspname,'role',role,
   'usage',has_schema_privilege(role,n.oid,'USAGE'),'create',has_schema_privilege(role,n.oid,'CREATE'))
   ORDER BY n.nspname,role) FROM pg_namespace n CROSS JOIN unnest(ARRAY['anon','authenticated','service_role']) role
   WHERE n.nspname IN ('auth','public','storage','monjez_private')),
 'default_acls',(SELECT coalesce(jsonb_agg(jsonb_build_object('role',r.rolname,
   'schema',n.nspname,'object_type',d.defaclobjtype::text,'acl',d.defaclacl::text)
   ORDER BY r.rolname,n.nspname,d.defaclobjtype),'[]') FROM pg_default_acl d
   JOIN pg_roles r ON r.oid=d.defaclrole LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace),
 'migration_versions',(SELECT jsonb_agg(version ORDER BY version) FROM supabase_migrations.schema_migrations)
);
