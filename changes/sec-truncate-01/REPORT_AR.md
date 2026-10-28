# نتيجة SEC-TRUNCATE-01 — مرشح تقوية صلاحيات معزول

التكليف: #55/6139631421؛ مطالبة التنفيذ6144887293. البداية Draft PR66 عند
`9d30064d0d42667bf4b1de6469c319e625b9f33d`. لم نجد تنفيذًا أو فرعًا سابقًا
للمهمة، ولا تصحيحًا مكررًا في مسودات PR49/50. main بقي
`43d6edbccb66fb06ce0fcb93734ad59532d1aeae`؛ لا دمج أو نشر.

المصدر الذي اختُبر: `c233f156220b4551e82edccec3eaff9161c20ba3` على الفرع
`fix/sec-truncate-01-2026-10-13`. هذه نتيجة مرشح غير مدمج، وليست إصلاحًا منشورًا
على main أو إثباتًا لسلامة إغلاق الحساب.

## سبب المنح والتغيير المحدود

catalog السابق أظهر منح TRUNCATE مباشرة لـauthenticated على21جدول تطبيق؛
tenant_counters كان الاستثناء. PUBLIC وanon لم يكن لديهما المنح. المنح الافتراضية
لدور إنشاء الجداول postgres داخل public تمنح authenticated هذه الصلاحية أيضًا؛
اختبار إنشاء الجدول الفارغ قبل الإصلاح أثبتها دون أي GRANT خاص بالاختبار.
المنح العامة global أو عضوية الأدوار ليست سببًا مرصودًا لهذه الصلاحية في البيئة.

راجعت119ملف تطبيق/خادم مثبتًا و43ترحيلًا؛ تطابقات كلمةtruncate في التطبيق كانت
CSS فقط، ولا استدعاءSQL أو مطلب صيانة عادي لهذه الصلاحية ظهر. لم يثبت مسار
استغلال عبرREST أو حادث إنتاج. مصادر الملفات في APPLICATION_SOURCE_MANIFEST.json.

التغيير ترحيل أمامي جديد واحد: `20261013120223_sec_truncate_01.sql`، ولّده فعليًا
CLI2.101.0 بأمرmigrationnew. يسحب TRUNCATE فقط منanon/authenticated/PUBLIC
على قائمة22جدول تطبيق محددة، ومن defaultACL لجداول postgres المستقبلية فيpublic.
الفحص التمهيدي يوقف الترحيل عند منشئ مختلف أو منح TRUNCATE افتراضية عامة لجداول postgres، مباشرة أو عبر PUBLIC/التوريث، خارج نطاق public؛
أما بقاء منح موروثة فعلية على الجداول فيرفضه فحص القبول بعد الترحيل؛
لا يغير defaultACL العامة أوauth/storage أوأدوار المزود أوmembership.

لا REVOKE ALL أوCASCADE أوGRANT تعويضي، ولا تغيير تطبيق/اعتماديات/ملكية/صيغة مالية
أوRLS/RPC/FK/trigger. الترحيلات43 السابقة لم تُعدّل. حمايةdefaults تخص
**postgres-created public tables فقط**؛ لا تشمل إنشاءpublicبـsupabase_admin أو أي
GRANT صريح واسع يضاف لاحقًا. هذه حدود التصميم، لا قبول تلقائي لمنح مستقبلية.

## أدلة مرتبطة بالمصدر والإصدارات

CLI2.101.0، PostgreSQL17.6/image17.6.1.106، Auth2.188.1، PostgREST14.10، Storage1.54.1.
SQL SHA256: `e2f2fa5d102a0667ec6035040a96307d08fb3b32f5201117d1f750d4ab520429`.

| التشغيل | النتيجة الفعلية |
| --- | --- |
| [run38394692253](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/38394692253)، fresh job115286889156 | SUCCESS، قاعدة جديدة بكامل44ترحيلًا |
| التشغيل نفسه، upgrade job115286889201 | SUCCESS، baseline43 ثم migrationup المحلي إلى44 |
| التشغيل نفسه، Quality job115286889333 | SUCCESS، نفس13خطوة Quality القائمة مع BASE_SHA الخاص بـpush؛66unit/159assertions و8wrapper/67browser containment scenarios |
| generator38394370225 عند4cf2ce4c | SUCCESS دون بدء DB؛ ملف الترحيل المولّد وhash طابقاSQL المحفوظ |
| generator الأول38394158093 عندd6f75dca | FAIL بسببhere-doc فيshell قبلDB؛ صُحح، محفوظ تاريخيًا ولا يعد دليل إصلاح |

التحقق المحلي والأدوات:16اختبار oracle مركّز نجحت محليًا وفي كلا مساري العقد.
خطأdelimiter فيvalidator صُحح قبل النشر الحي. لا نعد هذه الاختبارات16اختبارTRUNCATE
تنفيذيًا؛ هي فحوص الأداة نفسها. Bashsyntax لجميع21run blocks تحقق قبل المحاولة المصححة.

أدلةZIP نزلت وطابقت SHA256، والنسخ المنقحة الدائمة تحت evidence/native-c233:

- fresh artifact11811830668: `e41c684c5470ba1fba2aecc787b2960b78be9118d8e88c9d1da717c115ad1a37`.
- upgrade artifact11812050024: `73ffbf475cfabe54be92f057ebc19d963de8cc71ab6bbcecb9bb945a26dae49f`.
- generator artifact11810928623: `c80725ee9eab55bcc1db87aeec13d801bae6b06e93720a09d2457e1519d8a27a`.

## مصفوفة الصلاحيات والبيانات

الجدول الكامل PERMISSION_MATRIX.csv، والتفاصيل PERMISSION_SUMMARY.json والملفات الخام
before/after. فُحص31دورًا و1705صف table/role، مع8حقوق منها MAINTAIN فيPG17.

| البند | قبل43 | بعد44 / fresh44 |
| --- | --- | --- |
| authenticatedTRUNCATE على جداول التطبيق |trueعلى21، falseعلىtenant_counters |falseعلى22/22 |
| anonTRUNCATE وPUBLIC المباشر |غير ممنوحة على22 |غير ممنوحة على22 |
| خدمةservice_role والمالكpostgres وصيانةsupabase_admin |حقوق موجودة كما في baseline |محفوظة، بلا تغيير |
| سائرSELECT/INSERT/UPDATE/DELETE/REFERENCES/TRIGGER/MAINTAIN |مصفوفة baseline لكل الأدوار |مطابقة؛ بما فيهاDELETE البريد الذي بقي مسألة منفصلة |
| جداول المزود وdefaultACL خارجpostgres/public/client/TRUNCATE |baseline الفعلي |دون تغيير |
| جدول مستقبل فارغ أنشأهpostgres فيpublic |authenticatedTRUNCATE=true |false؛ حقوقه الأخرى وحقوق الخدمة/المالك محفوظة |

التغيير الفعلي الوحيد في مصفوفة الجداول الحالية21خلية authenticated/TRUNCATE:
true→false. غيابPUBLIC المباشر مع has_table_privilege الفعلي ومقارنةroles/memberships
يكشف صلاحيات التوريث؛ لا اختبار عضوية مصطنعة أوSET ROLE. المنشئ/current_user/session_user
ظلpostgres. كائن __sec_truncate_default_probe فارغ داخلBEGIN/ROLLBACK، وتأكد عدم
وجوده بعدها. لاTRUNCATE/DELETE/INSERT/DROP أو تغيير هوية مستخدم نفّذته أداة الاختبار.

بصمات22جدولًا عامًا ثابتة قبل/بعد القراءات والـupgrade؛ المالية السبعة الأصلية
orders/order_items/products/customers/payments/expenses/day_closes خالية. Authusers
وtenants صفر، ولاfixtures. email_send_state seed الأصلي بقي ثابتًا؛ لا فحص مالي
غير فارغ. تطابقت بياناتRPC/RLS/FK/trigger/roles/schema privileges غير المستهدفة.
fresh قارَنACL/defaultACL الخام معbaseline بعد استثناءTRUNCATE المقصود فقط؛
upgrade قارَنexpandedACL وكل الأدوار وdefaultACL وschema/data داخل نفس البيئة.

## العزل والمراجعة وحدود CI

أعيد استخدام حاجز البيئة والـUID/loopback وreadonlycatalog وsnapshot والحجر والتنظيف
دون تعديل sharedharness. الملف الجديد يستخدم psql داخلUID نفسه؛ الاستثناء الكتابي
الوحيد للأداة هوDDL الجدول الفارغ المتراجع. migrationup المحلي يطبق ترحيلACL المصرح.
no unexpected UID egress، evidence_no_credentials=true، cleanup3/3true في المسارين
معstop--no-backup وإزالةkeys/processes/containers. لا ندعي تدقيق خروج كل خدمات المزود.

المراجع المستقل /root/sec_truncate_review قرأ المصدر والسجلات الأصلية، طابقZIPs
والملفات التسعة، وأعاد16اختبارًا محليًا وحساب مقارناتcatalog/ACL/defaults/data.
قبل النطاق دون ملاحظة مانعة. **لم يعد التشغيل الحي أوQuality/DB/lifecycle.**
التفصيل في INDEPENDENT_REVIEW.md؛ الحفظ النهائي يحتاج مقارنةdocs-only بلا تغييرSQL/tools.

بسببmigrationglob فيWorkflows القديمة، اختُبر فرعpush قبل فتحDraft. Workflowجديد
مخصص شغّل fresh/upgrade ونسخة13خطوةQuality مطابقة، باستثناءBASE_SHA لـpush فقط.
لم تشغّل workflowQuality الأصلية لهذاpush ولم تعد lifecycle/financial/history suites.
الحفظ النهائي وإصدارDraft يكونان على[skip ci] لمنع أحداثPR خارج النطاق؛ هذا ليس
GREEN للرأس التوثيقي أو إعفاء بوابة دمج. نتائج c233 محفوظة مع إثبات بقاء runnable
blobs/SQL دون تغيير. أداة الدفعة مربوطة بحدود43→44، وليست gate عامة لكل ترحيل مستقبل.

غير مثبت: تنفيذ رفضTRUNCATE/DELETE فعليًا (ممنوع هنا)، وصولREST/SQL لمستخدم عادي،
سلوك إنتاج/ترقيةقاعدةغيرفارغة/قفل تحت حمل/تزامن، كلdefaultcreator/schema، حماية ضد
GRANTواسع صريح لاحق، سلامة إغلاق حساب أو حفظ تاريخ مالي غير فارغ. تبقى
closure_verified=false وintegration_accepted=false؛ لا فتح بوابات مالية أو إطلاق.

## الرجوع والخطوة الواحدة التالية

لا إعادة منحTRUNCATE تلقائيًا كـrollback. أبقِ المرشح غير مدمج؛ إذا أعقب نشرًا
مصرحًا لاحقًا عائق حقيقي، يقترح ترحيل تعويضي أمامي يحفظ منع العميل ويُراجع مستقلاً.
لا edit لمهاجرة مطبقة أوforcepush/restore إنتاج. البيئتان المؤقتتان نُظفتا.

ONE NEXT للتخطيط: مراجعة مرشح SEC-TRUNCATE-01 ثم تحديد تصميم إغلاق المالك وحدود
account/store/idempotence وfixture isolation في دفعة مستقلة باستخدام PR66. سياسة
OWNER-RETENTION-01 محفوظة، ومدة الاحتفاظ/ضوابط المحو قرار مستقل. توقف التنفيذ هنا؛
لا تنفيذ إغلاق أو دمج أو نشر من هذه الدفعة.
