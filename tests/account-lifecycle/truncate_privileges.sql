SELECT jsonb_build_object(
 'identity',jsonb_build_object('current_user',current_user,'session_user',session_user),
 'table_acl',(SELECT jsonb_agg(x ORDER BY x.relation,x.grantee,x.privilege,x.grantor) FROM (
   SELECT n.nspname||'.'||c.relname relation,
     CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END grantee,
     pg_get_userbyid(a.grantor) grantor,a.privilege_type privilege,a.is_grantable grantable
   FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace
   CROSS JOIN LATERAL aclexplode(coalesce(c.relacl,acldefault('r',c.relowner))) a
   WHERE n.nspname IN ('public','auth','storage','monjez_private') AND c.relkind IN ('r','p')
 ) x),
 'table_matrix',(SELECT jsonb_agg(x ORDER BY x.relation,x.role) FROM (
   SELECT n.nspname||'.'||c.relname relation,r.rolname role,
     jsonb_build_object('SELECT',has_table_privilege(r.oid,c.oid,'SELECT'),
       'INSERT',has_table_privilege(r.oid,c.oid,'INSERT'),
       'UPDATE',has_table_privilege(r.oid,c.oid,'UPDATE'),
       'DELETE',has_table_privilege(r.oid,c.oid,'DELETE'),
       'TRUNCATE',has_table_privilege(r.oid,c.oid,'TRUNCATE'),
       'REFERENCES',has_table_privilege(r.oid,c.oid,'REFERENCES'),
       'TRIGGER',has_table_privilege(r.oid,c.oid,'TRIGGER'),
       'MAINTAIN',has_table_privilege(r.oid,c.oid,'MAINTAIN')) rights
   FROM pg_class c JOIN pg_namespace n ON n.oid=c.relnamespace CROSS JOIN pg_roles r
   WHERE n.nspname IN ('public','auth','storage','monjez_private') AND c.relkind IN ('r','p')
 ) x),
 'default_acl',(SELECT jsonb_agg(x ORDER BY x.creator,x.schema,x.object_type,x.grantee,x.privilege) FROM (
   SELECT pg_get_userbyid(d.defaclrole) creator,
     CASE WHEN d.defaclnamespace=0 THEN '<global>' ELSE n.nspname END schema,
     d.defaclobjtype::text object_type,
     CASE WHEN a.grantee=0 THEN 'PUBLIC' ELSE pg_get_userbyid(a.grantee) END grantee,
     pg_get_userbyid(a.grantor) grantor,a.privilege_type privilege,a.is_grantable grantable
   FROM pg_default_acl d LEFT JOIN pg_namespace n ON n.oid=d.defaclnamespace
   CROSS JOIN LATERAL aclexplode(d.defaclacl) a
 ) x)
);
