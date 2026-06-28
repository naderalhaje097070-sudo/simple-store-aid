# Refactor Baseline — PR R0

التُقطت قبل بدء استخراج `app.tsx` إلى `src/features/`. الهدف: تثبيت الحالة الخضراء قبل أي نقل.

## السياق

- المشروع الأساسي المعتمد: `simple-store-aid` (Mongezz V2).
- الخطة الكاملة: `.lovable/plan.md`.
- مصدر الحقيقة للسلوك المالي: `tests/financial-rules/rules.sql` (T1–T14).
- المبدأ: **structure-only refactor — لا تغيير بصري ولا مالي.**

## أحجام الملفات قبل الـ refactor

| الملف | عدد الأسطر |
|---|---|
| `src/routes/_authenticated/app.tsx` | 2955 |
| `src/routes/_authenticated/platform-admin.tsx` | 792 |
| `src/lib/db.ts` | 619 |

## العيوب البنيوية المرصودة

| رمز | العيب | الخطورة |
|---|---|---|
| D1 | `app.tsx` ملف عملاق يضم ~31 مكوّنًا | عالية |
| D2 | كل شاشة `function XScreen(p: any)` — لا أنواع props | متوسطة |
| D3 | تمرير `{...ctx}` عملاق بلا عقد صريح | متوسطة |
| D4 | `@ts-ignore` ×4 في `src/lib/invoice-pdf.ts` | منخفضة |
| D5 | `eslint-disable react-hooks/exhaustive-deps` ×2 في `app.tsx` | منخفضة |
| D6 | ملفات ثانوية كبيرة: `platform-admin.tsx` (792)، `db.ts` (619) | منخفضة |
| D7 | سطر ميت `setCustomers` no-op وبقايا أنماط mock | منخفضة |

## بوابات الجودة (Gates) المعتمدة

كل PR لاحق (R1→R6) يجب أن يجتاز:

1. `npm run build` ✅
2. `npm run lint` ✅
3. `npx tsc --noEmit` ✅ (يُستبدل بـ `tsgo` في sandbox Lovable)
4. تشغيل يدوي للشاشات المتأثرة — لا شاشة بيضاء، لا كسر بصري.
5. `tests/financial-rules/run.sh` → كل T1–T14 خضراء (إلزامي لـ PR R5 الذي يلمس الشاشات المالية).

> ملاحظة: في sandbox Lovable يقوم النظام بتشغيل build/typecheck تلقائياً بعد كل تعديل. لذلك `R0` لا يستدعي تنفيذ بناء يدوي إضافي — الحالة الخضراء الحالية هي خط الأساس.

## ما تم في PR R0

- إنشاء مجلد فارغ `src/features/` (مع `.gitkeep`) كنقطة هبوط لاستخراجات R1→R5.
- توثيق هذا الخط الأساسي.
- **لا نقل لأي مكوّن، لا تعديل لأي ملف وظيفي.**

## الخطوة التالية

PR R1: استخراج الأنواع (`features/shared/types.ts`) والمكوّنات النقية (`StatusChip`, `EmptyState`, `Sheet`, `Toast`) إلى `src/features/shared/`. cut-paste حرفي بدون تعديل أجسام المكوّنات.
