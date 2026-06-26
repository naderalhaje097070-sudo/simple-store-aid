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
│   ├── hooks/               ← React hooks مخصصة
│   ├── lib/                 ← المنطق المشترك (DB helpers، types)
│   ├── routes/              ← ملفات التوجيه (TanStack File-Based)
│   │   ├── _authenticated/  ← المنطقة المحمية (التطبيق)
│   │   ├── api/             ← نقاط نهاية API العامة
│   │   ├── auth.tsx         ← صفحة تسجيل الدخول
│   │   ├── index.tsx        ← صفحة الهبوط (Landing)
│   │   └── guide.tsx        ← دليل تجربة المستخدم
│   ├── styles.css           ← تصميم Tailwind v4 (tokens + theme)
│   └── integrations/        ← Supabase client، auth middleware
├── supabase/
│   └── migrations/          ← ترحيلات قاعدة البيانات (RLS، Policies)
├── .env                     ← متغيرات البيئة (SUPABASE_URL، ...)
├── package.json
└── vite.config.ts
```

---

## كيفية التشغيل داخل Lovable

> **المتطلبات:** لا شيء — Lovable يدير البيئة بالكامل.

### 1. معاينة حية (Preview)

عند فتح المشروع في Lovable، يُشغّل خادم التطوير تلقائيًا:
- **الواجهة الأمامية:** يعمل على `localhost:8080`
- **إعادة التحميل السريعة:** أي تعديل على الملفات يظهر مباشرة في المعاينة

### 2. بناء الإنتاج (Build)

```bash
bun run build
```

- يُنشئ مجلد `dist/` جاهزًا للنشر.
- يدعم SSR بشكل افتراضي.

### 3. بناء وضع التطوير

```bash
bun run build:dev
```

- مفيد للفحص قبل الرفع إلى البيئة الإنتاجية.

### 4. فحص الأنواع (TypeScript)

```bash
npx tsc --noEmit
```

- المشروع يستخدم `strict: true` — كل الاستيرادات يجب أن تكون صحيحة.

### 5. تنسيق الكود

```bash
bun run format
```

### 6. التشغيل المحلي خارج Lovable

إذا نسخت المستودع إلى جهازك:

```bash
# 1. تثبيت التبعيات
bun install

# 2. نسخ متغيرات البيئة
# أنشئ ملف .env بناءً على المتغيرات التي يوفرها Lovable Cloud
# (VITE_SUPABASE_URL، VITE_SUPABASE_PUBLISHABLE_KEY)

# 3. تشغيل التطوير
bun run dev
```

---

## الربط مع Lovable Cloud (Backend)

- **قاعدة البيانات:** PostgreSQL مُدار عبر Lovable Cloud (Supabase)
- **الجداول الرئيسية:** `tenants`، `profiles`، `products`، `customers`، `orders`، `payments`، `expenses`، `couriers`، `day_closes`
- **الأمان:** RLS (Row Level Security) + Tenant Isolation
- **الأدوار:** `owner`، `manager`، `cashier`، `viewer`

> لا تحتاج لتشغيل Supabase محليًا — كل شيء مُدار في السحابة.

---

## ملاحظات التطوير

- **لا تُنشئ `src/pages/`** — التوجيع يعتمد على `src/routes/` (TanStack Start).
- **لا تُعدّل `src/routeTree.gen.ts`** — يُولّد تلقائيًا.
- **الملفات المنتهية بـ `.server.ts`** — لا يمكن استيرادها من المكونات (server-only).
- **الملفات المنتهية بـ `.functions.ts`** — server functions يمكن استدعاؤها من المكونات.
- **متغيرات البيئة:**
  - `VITE_*` — متاحة في المتصفح والخادم
  - `process.env.*` — خادم فقط (داخل `createServerFn`)

---

## المساهمة

هذا المشروع نموذج UX/POC تم تحويله إلى تطبيق SaaS حقيقي. إذا كنت تُطوره، راجع دليل UX في مسار `/guide` لفهم القيود والتعريفات المالية قبل أي تعديل.
