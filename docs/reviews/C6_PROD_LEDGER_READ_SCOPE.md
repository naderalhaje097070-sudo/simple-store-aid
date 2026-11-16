# نطاق مقترح: قراءة سجل ترحيلات الإنتاج (C6/C7، البند 2ب.1)، للموافقة فقط

- **التاريخ:** 2026-11-16
- **الحالة:** مقترح. لن يُنفَّذ أي استعلام قبل أن يوافق المالك بكلماته على هذا النطاق تحديدًا. كلمة «موافق» العامة على بدء C6/C7 لا تكفي، لأن خطة C6/C7 تشترط موافقة لكل بند على حدة.

## الغرض
قبل أي تطبيق على الإنتاج، نحتاج أن نعرف بالضبط:
- أي ترحيلات الإنتاج مطبّقة فعلًا (52 صفًا حسب سجل RECOVERY-02)؛
- أيها يطابق ملفات المرشح، اسمًا ومحتوى؛
- هل في الإنتاج ترحيل ليس له ملف في المستودع؛
- صلاحيات `email_queue_dispatch()`، ولا يوجد ملف في المستودع ينشئها.

## ما سيُنفَّذ بالضبط
- كل الاستعلامات `SELECT` فقط، داخل معاملة للقراءة فقط: `SET TRANSACTION READ ONLY`.
- لا كتابة، ولا DDL، ولا قراءة لأي بيانات عملاء أو بيانات مالية.

1. **سجل الترحيلات:**
   ```sql
   select version, name, md5(array_to_string(statements, E'\n')) as stmt_md5
   from supabase_migrations.schema_migrations order by version;
   ```
2. **وجود دالة البريد وصلاحياتها:**
   ```sql
   select p.oid::regprocedure, p.prosecdef, p.proowner::regrole,
          has_function_privilege('anon', p.oid, 'EXECUTE') as anon_exec,
          has_function_privilege('authenticated', p.oid, 'EXECUTE') as auth_exec,
          has_function_privilege('service_role', p.oid, 'EXECUTE') as service_exec
   from pg_proc p join pg_namespace n on n.oid = p.pronamespace
   where p.proname in ('email_queue_dispatch','enqueue_email','read_email_batch','delete_email','move_to_dlq')
     and n.nspname not in ('pg_catalog','information_schema');
   ```

## الأداة والمكان
- **الأداة:** Supabase MCP `execute_sql`، على مشروع الإنتاج فقط. معرّف المشروع يُقرأ من `get_project`، ولا يُخمَّن.
- **ما لن يُستعمل:** أي مفاتيح أو أسرار، والـ`apply_migration`، وأي أداة كتابة.

## ما يُحفظ في المستودع
- الإصدارات والأسماء وبصمات md5 كما هي.
- نتيجة المقارنة مع ملفات المرشح: مطابق، مختلف، أو غير موجود.
- لا يُحفظ نص الترحيلات من الإنتاج.

## ما يأتي بعده، ولا يشمله هذا النطاق
كل بند مما يلي يحتاج موافقة منفصلة على نطاقه:
- التطبيق على الإنتاج؛
- النسخة الاحتياطية؛
- المحاكاة؛
- النشر (Publish).
