# Mongezz — اعتماد `simple-store-aid` كمشروع أساسي + Refactor بنيوي آمن

> **القرار:** `simple-store-aid` هو المشروع الأساسي. `mongezz` يُهجَر.
> **هدف الخطة:** إصلاح العيوب البنيوية فقط، **دون لمس أي بكسل أو رقم**.

## القاعدة الذهبية

كل PR يلتزم بـ:
- صفر تغيير بصري (ألوان/تخطيط/نصوص/RTL).
- صفر تغيير مالي (لا RPC، لا hook، لا schema، لا migrations).
- `npm run build` + `lint` + `tsc --noEmit` خضراء.
- `tests/financial-rules/rules.sql` (T1–T14) أخضر بالكامل.
- قابل للتراجع في PR واحد صغير.

**المبدأ:** structure-only refactor — نقل ميكانيكي (cut-paste حرفي) لا إعادة كتابة.

## التشخيص (من قراءة الكود الفعلية)

| # | العيب | الدليل | الخطورة |
|---|---|---|---|
| D1 | `app.tsx` = 2921 سطر يضم 31 مكوّنًا | grep ScreenName | عالية |
| D2 | غياب أنواع props — كل شاشة `p: any` | 20+ شاشة | متوسطة |
| D3 | تمرير `{...ctx}` عملاق بلا عقد | بناء ctx في MongezzApp | متوسطة |
| D4 | `@ts-ignore` ×4 في `invoice-pdf.ts` | grep | منخفضة |
| D5 | `eslint-disable react-hooks/exhaustive-deps` ×2 | سطر 222، 250 | منخفضة |
| D6 | `platform-admin.tsx` (792)، `db.ts` (619) كبيرة | wc -l | منخفضة |
| D7 | سطر ميت `setCustomers` no-op وبقايا mock | قراءة MongezzApp | منخفضة |

**لا توجد عيوب وظيفية أو مالية.** المنطق المالي مُختبَر (T1–T14) وآمن. العلاج بنيوي بحت.

## البنية المستهدفة

```text
src/routes/_authenticated/app.tsx   ← shell + توجيه فقط (~300 سطر)
src/features/
  shared/    types.ts  AppContext.ts  Screen.tsx  StatusChip.tsx
             EmptyState.tsx  Sheet.tsx  Toast.tsx
  layout/    TopBar.tsx  BottomNav.tsx  DesktopSidebar.tsx
  home/      invoices/  inventory/  shop/  profit/  collected/
  debts/     courier/   expenses/   customers/  settings/
  sale/      dayclose/  pilot/
```

كل مكوّن يُنقل **حرفيًا** من `app.tsx` إلى ملفه الجديد بدون تعديل جسمه.

## خريطة الـ PRs

### PR R0 — Baseline (Risk: 0)
تشغيل build/lint/tsc + rules.sql وتوثيق النتائج في `docs/refactor-baseline.md`. إنشاء `src/features/` فارغ. لا نقل.

### PR R1 — الأنواع والمشترك (Risk: منخفض)
نقل الأنواع (Product/Customer/Courier/Invoice/Payment/Expense/Screen/Period) إلى `features/shared/types.ts`، ونقل StatusChip/EmptyState/Sheet/Toast إلى `features/shared/`. مكوّنات نقية بلا حالة.

### PR R2 — عقد AppContext (Risk: منخفض-متوسط)
إنشاء `features/shared/AppContext.ts` يعرّف `AppCtx` صريحًا (بديل `{...ctx}`). تحويل `ctx` في MongezzApp ليُكتب `AppCtx`. لا نقل شاشات بعد — فقط تعريف العقد، يحل D2+D3 تدريجيًا.

### PR R3 — طبقة Layout (Risk: منخفض)
نقل TopBar/BottomNav/DesktopSidebar إلى `features/layout/` بـ props صريحة موجودة أصلًا.

### PR R4 — الشاشات غير المالية (Risk: متوسط)
نقل: home, invoices, inventory, customers, settings, expenses. كل شاشة تستقبل `p: AppCtx`.

### PR R5 — الشاشات المالية الحسّاسة (Risk: مرتفع)
نقل: sale (+PaymentSheet/Success/Quick), shop, profit, collected, debts, courier (custody/settlements/list), dayclose, pilot.
**Gate إضافي:** rules.sql T1–T14 أخضر قبل وبعد + سيناريوهات يدوية (بيع كامل/جزئي، منع debt بلا عميل، منع paid>total، عهدة 100/40، تسوية).

### PR R6 — تنظيف خفيف (Risk: منخفض)
حذف `setCustomers` no-op وبقايا mock. معالجة `exhaustive-deps` الموضعين (إصلاح التبعية أو توثيق سبب الاستثناء).

### PR R7 (اختياري، مؤجَّل)
تقسيم `platform-admin.tsx` و`db.ts`. معالجة `@ts-ignore` في `invoice-pdf.ts`.

## ما لا نفعله

- ❌ تغيير بصري من أي نوع
- ❌ تغيير منطق مالي/RPC/schema/migrations
- ❌ نقل كود من/إلى `mongezz`
- ❌ ميزات جديدة (لا barcode/offline/تقارير)
- ❌ PR كبير يجمع عدة طبقات
- ❌ إعادة كتابة مكوّن (نقل حرفي فقط)

## Definition of Done

- `app.tsx` ≤ ~350 سطر (shell + توجيه).
- صفر شاشة بـ `p: any` (كلها `AppCtx`).
- كل الشاشات منظّمة تحت `features/` حسب المجال.
- صفر تغيير بصري أو مالي (مثبَّت بـ rules.sql + فحص يدوي).
- جميع Gates خضراء لكل PR.

## الخطوة التالية المقترحة

ابدأ بـ **PR R0 (baseline)** ثم **PR R1**. بعد نجاحهما أحضّر أوامر R2–R6 بنفس الدقة.
