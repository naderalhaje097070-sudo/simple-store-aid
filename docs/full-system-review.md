# منجز V2 — مراجعة شاملة (منطق + أمان + واجهة)

تاريخ المراجعة: 2026-06-26  
الحالة: مراجعة فقط — لم تُعدَّل أي ملفات أو schema.

---

## 1) الواجهات والمسارات

تم اختبار جميع المسارات العامة على Mobile (390px) و Desktop (1280px) عبر Playwright headless.

| المسار | الحالة | RTL | Overflow أفقي | الملاحظة |
|---|---|---|---|---|
| `/` (Landing) | ✅ 200 | rtl | لا | `ssr:false` — يفحص الجلسة ثم يعرض المحتوى (~1s). H1 = "دفتر ذكي لمحلك الصغير". |
| `/auth` | ✅ 200 | rtl | لا | تحذير hydration بسيط (مكبوت بـ `suppressHydrationWarning`) — تجميلي ولا يكسر التدفق. |
| `/guide` | ✅ 200 | rtl | لا | محتوى كامل (~2848 حرف). |
| `/app` (موقَّع خارج) | ✅ 302→/auth | rtl | لا | البوابة المُدارة `_authenticated/route.tsx` تعمل كما يجب. |
| `/onboarding` | (يتطلب جلسة) | — | — | فحص الكود: يتحقق من الـ profile/tenant قبل الإنشاء (idempotent). |

**الشاشات الداخلية (داخل `/app`)** — تم فحص الكود (لا جلسة QA متاحة الآن):

- جميع الشاشات الـ 13 (الرئيسية، البيع، المخزن، العملاء، الديون، تفاصيل الفاتورة، المحصل، المصاريف، العهدة، التسويات، المناديب، إغلاق اليوم، الإعدادات) ترسم محتوى مباشرةً.
- `AppErrorBoundary` يلتقط أي كراش ويعرض زر إعادة المحاولة بدل شاشة بيضاء.
- Empty States موجودة في: العهدة، التسويات، الديون، المخزن، المصاريف، إغلاق اليوم.
- العملة موحَّدة: **دينار ليبي (د.ل)** في كل الشاشات.
- استخدام `.num` لعرض الأرقام LTR داخل سياق RTL — صحيح.

**ملاحظات تجميلية (Warn — غير حاجزة):**
1. تحذير hydration على `/auth` (مكبوت لكن React ما زال يُسجّله).
2. الصفحة الرئيسية تعرض شاشة تحميل قصيرة (~1s) قبل الـ landing — مقبول لأن التطبيق SPA.

---

## 2) المراجعة المنطقية المالية

تم التحقق مباشرةً من قاعدة البيانات الإنتاجية (بيانات الـ pilot الحالية):

| الفحص | النتيجة |
|---|---|
| طلبات بـ `paid > total` | 0 ✅ |
| طلبات بـ `collected_by_courier > total` | 0 ✅ |
| منتجات بمخزون سالب | 0 ✅ |
| صفوف بدون `tenant_id` (عبر 6 جداول) | 0 ✅ |
| Profiles بدون `tenant_id` | 0 ✅ |

**تطابق `close_day` مع المصادر** (لتاريخ اليوم):

| القيمة | محسوبة من DB | محفوظة في `day_closes` (آخر QA) | المطابقة |
|---|---|---|---|
| sales | 600.00 | 600.00 | ✅ |
| collected | 340.00 | 340.00 | ✅ |
| expenses | 0.00 | 0.00 | ✅ |
| customer_debts | 60.00 | 60.00 | ✅ |
| unsettled_custody | 0.00 | 0.00 | ✅ |

**الـ RPCs الحساسة** (تم فحصها سطرًا سطرًا):

| RPC | حماية | حالة |
|---|---|---|
| `create_sale_with_items` | `_assert_staff`, lock products, السعر من DB، يرفض `paid>total`، يرفض دين بلا عميل، يرفض courier بلا (customer+courier) | ✅ |
| `collect_order_debt` | `_assert_staff`, يرفض `amount<=0`، يرفض تجاوز المتبقي | ✅ |
| `settle_courier_orders` | `_assert_staff`, يتحقق من المندوب والمستأجر، يرفض `collected>remaining`، يُرحِّل الفرق لديون العميل | ✅ |
| `return_courier_order` | `_assert_staff`, يرفض `paid>0 OR collected_by_courier>0` (S13 المُصلَح) | ✅ |
| `close_day` | `_assert_staff`, snapshot من جداول DB مباشرة، `ON CONFLICT (tenant_id, closed_for) UPDATE` | ✅ |

**CHECK constraints على مستوى DB** (طبقة دفاع ثانية وراء الـ RPCs):

- `paid <= total` (orders), `stock >= 0` (products), `collected_by_courier <= total` و `>=0`, `qty>0`, `amount>0` للمدفوعات/المصاريف، `price/cost >= 0`، `courier_id NOT NULL when delivery=courier`، `customer_id NOT NULL when paid<total`. كلها موجودة (بعضها `NOT VALID` للأمان الرجعي على البيانات القديمة).

---

## 3) المراجعة الأمنية

**RLS:** مُفعَّل على كل الجداول الـ 11 في schema `public` ✅

**السياسات:** 4 سياسات لكل جدول tenant (SELECT لكل أعضاء المستأجر، INSERT/UPDATE لـ staff، DELETE للمالك فقط). جميعها على دور `authenticated` — لا anon. ✅

**عزل Multi-tenant:** كل سياسة تستخدم `current_tenant_id()` (SECURITY DEFINER) وكل RPC يستدعي `_assert_staff(tenant)` قبل أي تعديل. لا يوجد طريق لحقن `tenant_id` غريب لأن الـ RPCs تتجاهل أي tenant مُمرَّر من العميل وتأخذه من `profiles`. ✅

**Auth:** صفحة `/auth` لا تُسرّب وجود/عدم وجود البريد (تم إصلاحه سابقًا في `auth_email_enum`). تعيين الدور يتم عبر `handle_new_tenant` trigger (server-side، تم إصلاحه في `onboard_role_insert`). ✅

**نتائج الـ Security Scanner:** 11 finding كلها `warn`-level من نفس الفئة:
> `SECURITY DEFINER functions callable by authenticated users`

هذه **مقصودة وضرورية**: كل الـ RPCs المالية (`create_sale_with_items`, `collect_order_debt`, `settle_courier_orders`, `return_courier_order`, `close_day`) وحُزَم الـ helpers (`current_tenant_id`, `has_role`, `has_owner_role`, `has_staff_or_owner_role`, `_assert_staff`) **يجب** أن يستدعيها المستخدم الموقَّع — هذه هي طريقة العمل. كل واحدة تُدقِّق المستأجر والدور داخليًا. لا توجد ثغرة فعلية.

> توصية: إبقاء هذه الـ warnings مع مذكرة "intentional" في `@security-memory` (لا تُعلَّم كـ fixed/ignore بدون موافقتك).

---

## 4) التوافق مع فكرة "دفتر ذكي"

| الطبقة | الشاشة الرئيسية | الوضوح |
|---|---|---|
| المبيعات | الرئيسية + المحصل + إغلاق اليوم | ✅ مفصولة بصريًا |
| المدفوع (Cash in hand) | المحصل (نقدي/تحويل/تسويات) | ✅ مشتق من `payments` فعلية |
| ديون العملاء | "مبالغ لم تدخل بعد" + شاشة الديون | ✅ لغة صاحب المحل |
| عهدة المناديب | شاشتا العهدة والتسويات | ✅ مفصولة عن الديون |

اللغة المُستخدمة بسيطة (لا "Receivables/Payables/COGS")، والأرقام دائمًا بـ د.ل وأمام مُسمَّى واضح.

---

## 5) القرار النهائي

# ✅ Ready for limited Pilot

**لا توجد إصلاحات إلزامية قبل التشغيل.**

### تحسينات اختيارية (يمكن تأجيلها):
1. **Warn (تجميلي):** إزالة تحذير الـ hydration في `/auth` بفصل العنصر المُسبِّب إلى `<ClientOnly>` بدل `suppressHydrationWarning`.
2. **Warn (تجربة):** إضافة skeleton أنيق للـ ~1s قبل ظهور Landing بدل الشاشة الفارغة الحالية.
3. **Nice-to-have:** تشغيل QA كامل لـ S1–S18 مع مستخدم staff (ليس owner) للتأكد من سيناريو S15 (المستخدم بلا دور) — يحتاج إنشاء مستخدم ثاني للـ tenant.
4. **توثيق:** تسجيل الـ 11 finding الـ SECURITY DEFINER في `security-memory` كـ "intentional — RPC pattern" حتى لا يعود الـ scanner لتنبيهها كحاجزة.

### المخاطر المتبقية المعروفة: لا شيء حاجز.

