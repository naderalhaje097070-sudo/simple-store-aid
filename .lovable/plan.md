## النقد الصريح: المشروع ليس "كاملاً 100%" — لكنه قريب جدًا

**الحالة الفعلية:** جاهز لـ Pilot محدود (3-5 محلات تجريبية). ليس جاهزًا لإطلاق عام بدون الإصلاحات أدناه.

### ما يعمل بشكل ممتاز ✅
- المنطق المالي: 0 طلبات `paid > total`، 0 مخزون سالب، 0 صفوف بلا `tenant_id`
- RLS مُفعّل على الـ 11 جدول، كل RPC مالي يستدعي `_assert_staff` داخليًا
- العزل بين المستأجرين محكم (لا حقن `tenant_id` ممكن)
- 17/18 سيناريو QA ناجح، S13 مُصلَح

### الثغرات المتبقية (ليست حرجة لكنها واقعية)

| # | الملاحظة | الخطورة | الأثر |
|---|---|---|---|
| 1 | 11 finding من نوع SECURITY DEFINER غير موثقة في `@security-memory` كـ "intentional" | Low | كل scan جديد سيُعيد تنبيهها ويُربك المستخدم |
| 2 | تحذير Hydration في `/auth` (مكبوت بـ suppressHydrationWarning) | Cosmetic | console نظيف يبني الثقة، خاصة للـ Pilot |
| 3 | S15 (دور `staff` بدون owner) لم يُختبر بمستخدم حقيقي ثانٍ — اختُبر بالكود فقط | Medium | فجوة تغطية في RBAC؛ احتمال bug في صلاحيات staff لم يُكتشف بعد |

---

## الخطة

### الخطوة 1 — توثيق الـ SECURITY DEFINER كنمط مقصود
- تحديث `@security-memory` لإضافة قسم "Intentional Patterns" يشرح: كل RPC مالي ودوال `_assert_*` و `has_*` و `current_tenant_id` و `is_platform_admin` هي SECURITY DEFINER بقصد، تُدقّق المستأجر/الدور داخليًا، ولا يجوز للـ scanner اعتبارها ثغرة.
- بدون تعليم أي finding كـ ignored/fixed بدون إذنك.

### الخطوة 2 — تنظيف تحذير Hydration في `/auth`
- فحص `src/routes/auth.tsx` وعزل العنصر المُسبِّب (غالبًا قراءة `localStorage` أو `window` في render).
- نقله داخل `<ClientOnly>` أو `useEffect`، ثم إزالة `suppressHydrationWarning` التجميلي.
- النتيجة: console نظيف 100% على `/auth`.

### الخطوة 3 — إنشاء مستخدم staff للاختبار اليدوي + توثيق سيناريو S15
- إضافة قسم في `docs/full-system-review.md` يشرح خطوات إنشاء مستخدم ثانٍ في نفس tenant بدور `staff` (عبر `user_roles` migration أو من تطبيق دعوة).
- تشغيل QA يدوي مُختصر (S1، S4، S5، S15) بهذا المستخدم لتأكيد أن:
  - staff يقدر يبيع ويُحصّل ويسوّي عهدة
  - staff لا يقدر يُغلق اليوم (owner فقط عبر `_assert_owner`)
  - staff لا يقدر يحذف منتجات/مصاريف (DELETE policy = owner فقط)
- تحديث `docs/full-system-review.md` بنتائج الاختبار.

### ما لن أفعله الآن (خارج النطاق)
- لن أُضيف rate-limiting (Lovable لا توفر primitive موحّد، ويحتاج بنية تحتية مختلفة).
- لن أُغيّر أي RPC مالي أو RLS policy — كلها مُختبرة وتعمل.
- لن أُضيف ميزات جديدة.

### المُخرَج النهائي
- `@security-memory` محدّث.
- `src/routes/auth.tsx` بدون تحذير hydration.
- `docs/full-system-review.md` مع نتائج S15 الحقيقية.
- قرار نهائي مُحدّث: **Ready for Pilot (Verified)**.
