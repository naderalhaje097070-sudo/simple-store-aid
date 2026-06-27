
# خطة شاملة: تصليب Mongezz V2 قبل التوسّع

تنفيذ كل توصيات تقرير المراجعة في 4 مراحل متسلسلة على نفس الـ branch. لا تغييرات في تجربة المستخدم الأساسية للبيع — التغييرات في طبقة البيانات/المنطق + توضيحات صغيرة في الواجهة.

## المرحلة 1 — إصلاحات Pilot Blockers (الأهم)

### 1.1 منطقة زمنية لكل مستأجر (Risk #1)

migration واحد:
- إضافة عمود `tenants.timezone TEXT NOT NULL DEFAULT 'Africa/Tripoli'` (IANA).
- دالة `current_tenant_timezone()` security definer ترجع timezone المستأجر الحالي.
- دالة `tenant_today(_tid uuid)` ترجع `(now() AT TIME ZONE current_tenant_timezone())::date`.
- تحديث `close_day` و `get_platform_admin_overview` و `get_platform_day_close_health` لاستخدام `tenant_today` بدلاً من `(now() AT TIME ZONE 'UTC')::date`.
- استبدال كل فحوصات `created_at::date = v_today` بـ `(created_at AT TIME ZONE current_tenant_timezone())::date = v_today` داخل `close_day`.

في الواجهة (`src/routes/_authenticated/app.tsx`):
- جلب `timezone` من `tenants` مرة واحدة عند تحميل التطبيق وحفظها في `p` context.
- استبدال كل `new Date().toLocaleDateString` و `today()` بدالة موحّدة `todayInTenantTZ(tz)` باستخدام `Intl.DateTimeFormat('en-CA', { timeZone: tz })`.
- شاشة إعدادات المستأجر (owner فقط): قائمة منسدلة بأشهر المناطق الزمنية العربية + IANA.

### 1.2 إصلاح ترتيب migration الخاص بـ `platform_admin_audit_log` (Risk #3)

migration جديد فقط (لا يلمس القديم) يضمن:
- وجود الجدول قبل أي SELECT/POLICY/INDEX يشير له.
- إعادة إنشاء `CREATE TABLE IF NOT EXISTS` + الـ GRANTs + RLS + POLICY في نفس الملف.
- اختبار rebuild محلي عبر `supabase db reset` (يدوي بعد التطبيق).

## المرحلة 2 — توضيح الربح (Risk #2, #10)

### 2.1 إعادة تعريف `realized_profit` على أساس نقدي

تعديل `close_day`:
- حساب الربح من `payments` لليوم الحالي (basis = مبلغ التحصيل / إجمالي الفاتورة × ربح البنود)، لا من تاريخ إنشاء الفاتورة.
- يحل تلقائيًا Risk #10 (طلب مندوب يُسوّى لاحقًا = ربحه يدخل يوم التسوية).
- توحيد ما إذا كانت المصاريف تُطرح: القرار = **لا تُطرح** من `realized_profit` (تبقى مفصولة في عمود `expenses`)، وتُسمّى في كل مكان "ربح تقديري قبل المصاريف".

### 2.2 توحيد العرض في الواجهة

- إزالة الاحتساب المحلي للربح من `app.tsx` (الأسطر ~191, 2459).
- قراءة الرقم من `close_day` فقط أو RPC قراءة جديدة `get_tenant_today_estimate()` تستخدم نفس صيغة `close_day`.
- إزالة الازدواج البصري في app.tsx:2611-2617 (عرض رقم واحد بتسمية "ربح تقديري قبل المصاريف" + tooltip شرح).

## المرحلة 3 — تصليب مالي قبل الإطلاق العام

### 3.1 حصر الكتابة المالية في الـ RPCs فقط (Risk #4)

migration:
- سحب `INSERT, UPDATE` المباشر عن `authenticated` على: `orders`, `payments`, `order_items`.
- إبقاء `SELECT` فقط للقراءة عبر RLS.
- `DELETE` يبقى محصورًا (الموجود حاليًا).
- التأكد أن جميع مسارات الواجهة في `db.ts` تمر عبر RPCs (مراجعة + إضافة RPCs ناقصة إن وُجدت لعمليات edit بسيطة).

### 3.2 اشتقاق مبلغ التسوية من المخزّن (Risk #5)

تعديل `settle_courier_orders`:
- تجاهل `collected` القادم من العميل تمامًا.
- استخدام `v_order.collected_by_courier` كمصدر الحقيقة الوحيد.
- تغيير شكل `p_orders` إلى مصفوفة `uuid[]` فقط (order_ids).
- تحديث الواجهة (`SettlementsScreen`) لإرسال order_ids بدون مبالغ.

### 3.3 ترقيم فواتير لكل مستأجر (Risk #6)

migration:
- إضافة عمود `orders.tenant_number INT`.
- جدول `tenant_counters(tenant_id, last_order_number)` + دالة `next_order_number(_tid)` ذرّية (`UPDATE ... RETURNING`).
- backfill: ترقيم تنازلي حسب `created_at` لكل مستأجر.
- تعديل `create_sale_with_items` لاستخدام `next_order_number`.
- الواجهة: عرض `tenant_number` بدل `number` العام في كل الفواتير والـ PDF.
- إبقاء `number` العام للأغراض الداخلية (لا يُعرض).

### 3.4 Audit log للعمليات المالية (Risk #9)

migration:
- جدول `financial_audit_log(id, tenant_id, user_id, action, entity_type, entity_id, before, after, created_at)`.
- triggers على `orders` (UPDATE/DELETE) و `payments` (INSERT/DELETE) و `day_closes` (INSERT) تكتب snapshot.
- RLS: قراءة فقط للـ owner لمتجره.
- شاشة "سجل العمليات" بسيطة في إعدادات owner (جدول صفحات).

## المرحلة 4 — جودة الكود والاختبارات

### 4.1 اختبارات آلية + CI

- إضافة `vitest` + `tests/financial.spec.ts`:
  - اختبارات وحدة للثوابت (helpers مالية).
  - اختبارات RPC integration عبر psql ضد قاعدة test schema (الـ 12 سيناريو الموجود فعلًا في `tests/financial-rules/rules.sql` تُحوّل إلى vitest).
- إضافة script في `package.json`: `"test": "vitest run"`.
- ملاحظة: لا CI داخل Lovable — تترك .github/workflows للمستخدم لاحقًا.

### 4.2 تقسيم `app.tsx` (refactor خفيف، آمن)

- استخراج كل شاشة إلى `src/components/screens/<Name>.tsx`.
- استخراج types إلى `src/lib/types.ts`.
- إبقاء `p: any` كما هو الآن (تأجيل typing كامل لما بعد).
- لا تغيير منطق — نقل ملفات فقط.

## ملاحظات تقنية

- ترتيب التطبيق: migrations المرحلة 1 → 2 → 3.1 → 3.2 → 3.3 → 3.4، ثم تعديلات `app.tsx` و `db.ts` بعد كل migration.
- كل migration يحوي GRANTs الصحيحة (`authenticated` فقط للجداول، `service_role` ALL).
- الـ RPCs الجديدة/المعدّلة: `EXECUTE TO authenticated` فقط، `REVOKE FROM PUBLIC, anon`.
- `tenants.timezone` يحتاج RLS update policy للـ owner فقط.
- تغييرات `settle_courier_orders` و `tenant_number` breaking changes للواجهة — تُنفّذ في نفس الـ commit مع تحديث `db.ts`.
- PWA الحالي لا يتأثر؛ كل التغييرات server-side أو في صفحات محمية online-only.

## التحقق بعد كل مرحلة

- المرحلة 1: تشغيل بيع في 1:30 صباحًا (تعديل وقت الجهاز) → التأكد أنه يُحسب لليوم الصحيح في `close_day` وفي Dashboard.
- المرحلة 2: إقفال يوم فيه تحصيل دين قديم → الربح يظهر في يوم التحصيل لا يوم الفاتورة.
- المرحلة 3.1: محاولة `supabase.from('orders').update(...)` من الواجهة → ترفض بـ permission denied.
- المرحلة 3.2: استدعاء settle بمبلغ مزوّر في الـ payload → يُتجاهل ويُستخدم المخزّن.
- المرحلة 3.3: متجران مختلفان → أرقام فواتير متتابعة 1,2,3 في كل واحد بشكل مستقل.
- المرحلة 3.4: حذف/تعديل فاتورة → سطر في `financial_audit_log`.
- المرحلة 4: `bun test` يمر، نقل ملفات لا يكسر شيئًا.

## ما لن يتغير

- تجربة البيع السريع (نفس الـ flow، نفس الـ UI).
- لغة الواجهة (المصطلحات العربية البسيطة كما هي).
- PWA / Service Worker (آمن online-only).
- RLS عزل المستأجرين (يُشدَّد فقط، لا يُضعَّف).
- شاشات platform-admin (تتلقى تحديث `tenant_today` فقط).

