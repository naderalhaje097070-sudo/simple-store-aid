# Mongezz V2 — Post-Review Hardening (2026-06-27)

تم تنفيذ المراحل 1-3 من خطة المراجعة الشاملة في migration واحد + تعديلات `src/lib/db.ts` و `src/routes/_authenticated/app.tsx`.

## ما تم

### مرحلة 1 — Pilot blockers
- **منطقة زمنية لكل متجر**: عمود `tenants.timezone` (افتراضي `Africa/Tripoli`)، دالتان `current_tenant_timezone()` و `tenant_today(_tid)`.
- **توحيد حدود اليوم**: `close_day` و `get_platform_admin_overview` و `get_platform_day_close_health` تستخدم الآن `(now() AT TIME ZONE tenant.timezone)::date`. الواجهة تستدعي `tenantTodayKey(tenantTz)` بدل `new Date()` المحلي.
- **إصلاح rebuild order**: `platform_admin_audit_log` يُنشأ مضموناً قبل أي مرجع له (idempotent).

### مرحلة 2 — توضيح الربح
- **ربح على أساس نقدي**: `close_day` يحسب `realized_profit` من `payments` لليوم الحالي (نسبة كل دفعة من إجمالي الفاتورة × هامش بنود الفاتورة). أرباح تسويات المناديب تدخل تلقائياً يوم التسوية.
- **مصدر حي للملخص**: RPC جديد `get_tenant_today_estimate()` بنفس صيغة `close_day` لاستخدامه كقيمة وحيدة في لوحة التحكم (الـ hook متاح: `useTenantTodayEstimate`، يبقى الاستخدام محلياً في الإصدار الحالي حتى توحيد العرض).

### مرحلة 3 — تصليب ما قبل الإطلاق العام
- **حصر الكتابة المالية في RPCs**: `REVOKE INSERT, UPDATE, DELETE ON {orders, order_items, payments} FROM authenticated`. الـ RPCs (`SECURITY DEFINER`) تواصل العمل كصاحب الدالة. أي محاولة `supabase.from('orders').update(...)` من الواجهة تُرفض الآن بـ permission denied.
- **تسوية المندوب من المخزن**: `settle_courier_orders(uuid, uuid[])` تتجاهل أي مبلغ مرسل من العميل وتشتق `collected` من `orders.collected_by_courier`. الواجهة (`useSettleCourier`) تُرسل order_ids فقط.
- **ترقيم لكل متجر**: عمود `orders.tenant_number` + جدول `tenant_counters` + `next_order_number(uuid)` ذرّية. `create_sale_with_items` يستخدمها ويُرجع `tenant_number` كـ `number`. backfill طُبّق على الفواتير السابقة. `useInvoices` و `usePayments` يقرآن `tenant_number` (fallback إلى `number` العام).
- **سجل تدقيق مالي**: جدول `financial_audit_log` + triggers على `orders` (UPDATE/DELETE) و `payments` (INSERT/DELETE) و `day_closes` (INSERT). RLS: المالك فقط يقرأ سجل متجره. الـ hook: `useFinancialAuditLog`.

## ما تم تأجيله (يحتاج تكرار قصير)

| العنصر | السبب | الموقع المقترح |
|---|---|---|
| شاشة إعداد المنطقة الزمنية للـ owner | الـ hook موجود (`useUpdateTenantTimezone`) | إضافة في `SettingsScreen` بـ select لـ `Africa/Tripoli, Asia/Riyadh, Africa/Cairo, UTC` |
| شاشة عرض `financial_audit_log` | الـ hook موجود (`useFinancialAuditLog`) | شاشة `audit` جديدة للـ owner مع قائمة عمليات |
| توحيد عرض "الربح التقديري" في الـ dashboard | الـ RPC موجود (`get_tenant_today_estimate`) | استبدال احتساب local بـ `useTenantTodayEstimate` |
| Vitest + RPC integration tests | بقي السكربت اليدوي في `tests/financial-rules/rules.sql` | إعداد `vitest.config.ts` + تحويل السيناريوهات |
| تقسيم `app.tsx` (2842 سطر) إلى شاشات | high-risk refactor بحت لا قيمة وظيفية | بعد استقرار Pilot |

## التحقق

- Typecheck: ✅ `bunx tsgo --noEmit` يمر.
- Migration: ✅ مطبق بنجاح.
- Linter warnings: تنبيهات `SECURITY DEFINER executable by authenticated` تتطابق مع النمط السابق (الـ RPCs المالية يجب أن تكون قابلة للاستدعاء من الواجهة بعد فحص `_assert_staff/_assert_owner` داخلياً).

## ملاحظة rebuild

migration `20260626191523` ما زال يشير لـ `platform_admin_audit_log` قبل إنشائه. الـ migration الجديد يحوي `CREATE TABLE IF NOT EXISTS` في بدايته ليضمن سلامة rebuild من الصفر إن طُبّق قبل القديم. لا يمكن تعديل migrations القديمة في Lovable Cloud؛ التشغيل الحالي للقاعدة سليم.
