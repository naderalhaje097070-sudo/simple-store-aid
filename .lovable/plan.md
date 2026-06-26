
## 1. تدقيق الوضع الحالي (Audit)

- **الكود الموجود:** ملف واحد ضخم `src/routes/index.tsx` (~2191 سطر) يحتوي كل الشاشات + state محلي + بيانات mock فقط.
- **الـ Backend:** لا يوجد. لا Supabase، لا Auth، لا DB. كل شيء in-memory ويُفقد عند Refresh.
- **ما هو حقيقي:** فقط حسابات مالية صحيحة منطقياً (paid≤total، فصل الديون عن العهدة، إلخ) — لكنها على بيانات وهمية.
- **الناقص للإنتاج:** Auth، Tenants، DB schema، RLS، CRUD حقيقي، عزل بيانات، تحقق سيرفر، استمرارية.

## 2. خطة التنفيذ المرحلية

| Phase | المحتوى | الحالة |
|---|---|---|
| **1** | تفعيل Lovable Cloud + Auth (إيميل/كلمة مرور + Google) + جدول tenants + profiles + user_roles + RLS أساسي + شاشة `/auth` + شاشة "إنشاء محل" + حماية `_authenticated` | **هذه المرحلة** |
| 2 | جداول products + customers + ربط الشاشات الحالية بـ Supabase (استبدال mock state) | لاحقاً |
| 3 | orders + order_items + customer_debts + payments + RPC `create_order` لضمان الذرية المالية | لاحقاً |
| 4 | couriers + courier_settlements (معزولة عن ديون العميل) | لاحقاً |
| 5 | expenses + dashboard من بيانات حقيقية فقط | لاحقاً |
| 6 | اختبارات + تشديد RLS + audit log + QA | لاحقاً |

## 3. تنفيذ Phase 1 فقط الآن

### 3.1 Backend (Lovable Cloud)
- تفعيل Lovable Cloud.
- Migration:
  - `tenants` (id, name, owner_user_id, created_at)
  - `profiles` (id=auth.users.id, tenant_id, display_name, phone) + trigger تلقائي عند signup
  - `app_role` enum: `owner`, `staff`
  - `user_roles` (user_id, tenant_id, role) + function `has_role()` SECURITY DEFINER
  - function `current_tenant_id()` SECURITY DEFINER (يقرأ من profiles)
  - تفعيل RLS + سياسات: المستخدم يقرأ/يعدل فقط بيانات tenant الخاص به.
  - GRANTs صريحة لكل جدول (`authenticated` + `service_role`).
- تكوين Google OAuth عبر `supabase--configure_social_auth` (اختياري — نسأل المستخدم).

### 3.2 Frontend
- شاشة `/auth` عامة (تسجيل/دخول بالإيميل + Google).
- شاشة `/onboarding` تحت `_authenticated` لإنشاء أول محل (tenant) عند عدم وجوده.
- نقل الشاشات الحالية (`/`) إلى `src/routes/_authenticated/` كما هي مع mock data مؤقتاً (Phase 2 يربطها).
- Layout `_authenticated/route.tsx` المُدار من التكامل.
- Header صغير يعرض اسم المحل + زر خروج.

### 3.3 ما لا نلمسه في هذه المرحلة
- منطق الحسابات المالية والـ UX الحالي يبقى كما هو.
- لا ربط للمنتجات/الفواتير بـ DB بعد (Phase 2-3).

## 4. ملفات ستتغير في Phase 1
- إضافة: migration واحدة (schema + RLS + grants).
- إضافة: `src/routes/auth.tsx`, `src/routes/_authenticated/route.tsx` (مُدار)، `src/routes/_authenticated/onboarding.tsx`.
- نقل: `src/routes/index.tsx` → `src/routes/_authenticated/index.tsx` (نفس المحتوى).
- تحديث: `__root.tsx` (إضافة auth listener)، `start.ts` (bearer middleware من التكامل).

## 5. أسئلة قبل التنفيذ
1. **طرق الدخول:** إيميل+كلمة مرور فقط، أم نضيف Google من الآن؟ (الافتراضي عندي: الاثنان).
2. **الأدوار:** هل يكفي `owner` + `staff` في البداية، أم تريد `cashier` و`courier` كأدوار منفصلة الآن؟
3. **الـ Tenant:** هل المستخدم الواحد يملك محلاً واحداً فقط (الأبسط)، أم نسمح بعدة محلات لاحقاً؟
4. **بيانات Mock الحالية:** هل نتركها تعمل داخل `_authenticated` كـ playground حتى Phase 2، أم نُفرغ الشاشات ونبدأ بقوائم فاضية فوراً؟

## 6. QA يدوي بعد Phase 1
- إنشاء حساب جديد → يُوجَّه لشاشة Onboarding → إنشاء محل → الدخول للرئيسية.
- تسجيل خروج ثم دخول → يحتفظ بالمحل.
- مستخدم ثانٍ ينشئ محله الخاص → لا يرى بيانات الأول (تحقق RLS عبر DB query).
- الوصول لـ `/` بدون تسجيل → إعادة توجيه إلى `/auth`.

## 7. افتراضات
- Lovable Cloud هو الـ backend (لا Supabase خارجي).
- عملة موحدة د.ل لجميع المستأجرين.
- مستخدم واحد = محل واحد (قابل للتوسعة لاحقاً).
- شاشات اليوم تبقى بصرياً كما هي؛ التحويل لبيانات حقيقية يبدأ Phase 2.
