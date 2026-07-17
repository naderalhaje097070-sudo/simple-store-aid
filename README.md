# منجز (Mongezz) — Simple Store Aid

> دفتر ذكي لصاحب المحل الصغير. لا يُشبه البرامج المحاسبية الثقيلة — سريع، واضح، ويعمل على الجوال والكمبيوتر.

---

## ما هو المشروع؟

**منجز** هو نظام نقاط بيع (POS) مُصمم خصيصًا لأصحاب المتاجر الصغيرة في العالم العربي. بدلاً من واجهات ERP المعقّدة، يقدّم "دفترًا ذكيًا" يُغطي أربع طبقات مالية أساسية:

1. **المبيعات** — تسجيل فواتير سريعة (< 10 ثوانٍ)
2. **المحصّل** — نقدي + تحويل + تسويات
3. **ديون العملاء** — فواتير مفتوحة + تسديدات جزئية
4. **عهدة المندوب** — تسليم بضاعة + تسوية بعد الجولة

---

## التقنيات المستخدمة

| التقنية | الدور |
|---|---|
| **TanStack Start** | إطار عمل Full-Stack React 19 مع SSR/SSG |
| **TanStack Router** | التوجيه (File-Based Routing) |
| **TanStack Query** | إدارة البيانات والتخزين المؤقت |
| **Tailwind CSS v4** | التنسيق (Native CSS @theme) |
| **shadcn/ui** | مكونات واجهة المستخدم (Radix UI) |
| **Supabase (Lovable Cloud)** | قاعدة البيانات PostgreSQL + Auth + RLS |
| **Zod** | التحقق من صحة المدخلات |
| **Recharts** | الرسوم البيانية والتقارير |
| **date-fns** | معالجة التواريخ |

---

## البنية العامة للمجلدات

```
.
├── src/
│   ├── components/        ← مكونات UI المُعاد استخدامها
│   ├── hooks/             ← React hooks مخصصة
│   ├── lib/               ← المنطق المشترك (DB helpers، types)
│   ├── routes/            ← ملفات التوجيه (TanStack File-Based)
│   │   ├── _authenticated/← المنطقة المحمية (التطبيق)
│   │   ├── api/           ← نقاط نهاية API العامة
│   │   ├── auth.tsx       ← صفحة تسجيل الدخول
│   │   ├── index.tsx      ← صفحة الهبوط (Landing)
│   │   └── guide.tsx      ← دليل تجربة المستخدم
│   ├── styles.css         ← تصميم Tailwind v4 (tokens + theme)
│   └── integrations/      ← Supabase client، auth middleware
├── supabase/
│   └── migrations/        ← ترحيلات قاعدة البيانات (RLS، Policies)
├── package.json
└── vite.config.ts
```

---

## التشغيل والتحقق

### داخل Lovable

عند فتح المشروع في Lovable، تُدار بيئة المعاينة تلقائيًا. لا تُستخدم بيئة المعاينة كدليل على صحة العمليات المالية أو كبديل عن فحوص GitHub المعزولة.

### الأوامر الأساسية

```bash
bun install --frozen-lockfile
bun run dev
bun run typecheck
bun run lint
bun run test:unit
bun run build
```

فحوص قاعدة البيانات والقواعد المالية والواجهة المسجلة تعمل من GitHub Actions على Supabase معزول. لا يجوز استخدام Production للاختبارات المدمرة أو بيانات QA.

### متغيرات البيئة

استخدم متغيرات البيئة التي توفرها البيئة المستهدفة. لا يجوز اعتبار غياب المتغيرات سببًا للاتصال تلقائيًا بقاعدة Production في بيئة Local أو CI أو Preview. فصل البيئات الكامل مسجل كعمل P0 في `TASKS.md` تحت `SEC-ENV-001`.

---

## Lovable Cloud وSupabase

- **قاعدة البيانات:** PostgreSQL مُدار عبر Lovable Cloud (Supabase).
- **الجداول الرئيسية:** `tenants`، `profiles`، `products`، `customers`، `orders`، `payments`، `expenses`، `couriers`، `day_closes`.
- **الأمان:** RLS + Tenant Isolation، مع وجوب التحقق من صلاحيات كل Actor على الخادم وقاعدة البيانات.
- **الأدوار الحالية في Schema:** `owner`، `staff`.
- قيمة `staff` تصف الـenum الحالي فقط، وليست تصميمًا نهائيًا لحساب موظف محدود الصلاحيات. نموذج الموظفين المؤسسي مؤجل إلى Change Gates مستقلة.

---

## قواعد مالية لا تتغير

- `Delivered` لا يعني `Settled`.
- الطلب المرتجع لا ينشئ دين عميل أو عهدة مندوب.
- أموال المندوب لا تدخل `paid` أو `payments` قبل التسوية المعتمدة.
- الكتابات المالية تمر عبر حدود Transactional معتمدة على الخادم أو قاعدة البيانات.
- الواجهة ليست حد صلاحية.

---

## ملاحظات التطوير

- اقرأ `AGENTS.md` و`PROJECT_STATE.md` و`DECISIONS.md` و`TASKS.md` قبل أي عمل جوهري.
- لا تُنشئ `src/pages/`؛ التوجيه يعتمد على `src/routes/`.
- لا تعدل `src/routeTree.gen.ts` يدويًا؛ يُولد تلقائيًا.
- الملفات المنتهية بـ `.server.ts` خادمية فقط.
- Migrations المطبقة غير قابلة للتعديل؛ استخدم Migration جديدة Forward-only.
- لا تُعد كتابة Git history المرتبط بـLovable.
- لا تدمج أو تنشر تلقائيًا.

---

## حالة المنتج

Mongezz حاليًا Functional MVP في مرحلة تثبيت النواة المالية والاستعداد لـPilot محدود للمالك فقط. الـPilot الحقيقي محجوب حتى إغلاق مخاطر فصل البيئات، تقارير CI، وIdempotency المالية. راجع `PROJECT_STATE.md` و`TASKS.md` للحالة الدقيقة.
