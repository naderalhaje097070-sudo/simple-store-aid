# خطة: تحويل منجز إلى PWA خفيف وآمن

نطاق صارم: تثبيت على الموبايل + Service Worker يخزّن static assets فقط. لا offline sales، لا queue، لا تخزين لأي طلب Supabase، لا تغيير في RPCs/RLS/قاعدة البيانات.

## 1) Manifest + Icons

- إنشاء `public/manifest.webmanifest`:
  - `name: "منجز — Mongezz"`, `short_name: "منجز"`
  - `display: "standalone"`, `start_url: "/app"`, `scope: "/"`
  - `dir: "rtl"`, `lang: "ar"`
  - `theme_color` و `background_color` من design tokens الحالية (أخضر/كريمي الهوية)
  - `icons`: 192, 512, و maskable 512
- توليد الأيقونات عبر `imagegen` (شعار "منجز" أخضر على خلفية فاتحة) وحفظها في `public/icons/`.

## 2) Head meta

تحديث `src/routes/__root.tsx` لإضافة (دون لمس باقي الـ meta):
- `<link rel="manifest" href="/manifest.webmanifest">`
- `<meta name="theme-color" content="<token>">`
- `<meta name="mobile-web-app-capable" content="yes">`
- `<meta name="apple-mobile-web-app-capable" content="yes">`
- `<meta name="apple-mobile-web-app-status-bar-style" content="default">`
- `<meta name="apple-mobile-web-app-title" content="منجز">`
- `<link rel="apple-touch-icon" href="/icons/apple-touch-icon.png">`

## 3) Service Worker عبر vite-plugin-pwa (generateSW)

نتبع PWA skill — لا نكتب SW يدويًا.

- `bun add -D vite-plugin-pwa`
- تعديل `vite.config.ts` لإضافة `VitePWA({ ... })` بـ:
  - `registerType: "autoUpdate"`
  - `injectRegister: null` (التسجيل من wrapper فقط)
  - `devOptions: { enabled: false }`
  - `filename: "sw.js"`
  - `workbox`:
    - `navigateFallback: "/offline.html"` مع `navigateFallbackDenylist: [/^\/api\//, /supabase\.co/]`
    - `runtimeCaching`:
      - Navigations (`request.mode === 'navigate'`): **NetworkFirst**، fallback إلى `/offline.html` عند فشل الشبكة.
      - Same-origin hashed assets (`/assets/`): **CacheFirst**.
      - Google Fonts: **CacheFirst** بـ expiration.
    - **لا قاعدة caching تطابق `*.supabase.co` أو `/rest/v1` أو `/auth/v1` أو `/storage/v1` أو `/functions/v1`** — هذه الطلبات cross-origin لـ Supabase ولن يلتقطها أي handler، فتمر مباشرة عبر الشبكة بدون cache. نضيف تعليق صريح يوثّق ذلك.
    - `globPatterns` للـ precache: JS/CSS/woff2/png/svg/ico فقط من `dist/` (لا HTML للـ app routes).

## 4) Offline page

- إنشاء `public/offline.html` ثابتة (RTL، عربية، تستخدم inline styles):
  - عنوان: "تحتاج اتصال إنترنت"
  - نص: "منجز يحتاج إنترنت لحفظ العمليات المالية. تحقق من اتصالك وأعد المحاولة."
  - زر "إعادة المحاولة" → `location.reload()`.

## 5) Registration wrapper مع حراسات Lovable

إنشاء `src/lib/pwa-register.ts` يستدعى مرة واحدة من `src/routes/__root.tsx` داخل `useEffect`:

يرفض التسجيل (ويلغي أي تسجيل قديم لـ `/sw.js`) عندما:
- `!import.meta.env.PROD`
- داخل iframe (`window !== window.top`)
- hostname يبدأ بـ `id-preview--` أو `preview--`
- hostname يساوي أو ينتهي بـ `lovableproject.com` / `lovableproject-dev.com` / `beta.lovable.dev`
- URL يحوي `?sw=off` (kill switch)

غير ذلك: يستدعي `registerSW({ immediate: true })` من `virtual:pwa-register`.

## 6) لا تغيير في تجربة البيع

- لا lifecycle hooks تعترض fetch لطلبات Supabase.
- لا local queue، لا IndexedDB للعمليات.
- في حال انقطاع الشبكة، العملية تفشل طبيعيًا عبر استجابة Supabase fetch، وتُعرض رسالة الخطأ الحالية من `rpcMessage`. لا نضيف منطق "احفظ محليًا".
- اختياريًا (UI فقط، بدون تغيير منطق): شارة صغيرة "لا يوجد إنترنت" أعلى الشاشة عند `navigator.onLine === false` داخل `/_authenticated/app.tsx`. يمكن إسقاطها إذا فضّلت عدم لمس الشاشة.

## 7) QA

- Build production محليًا.
- فحص `dist/sw.js` للتأكد أن لا قاعدة تستهدف `supabase.co`.
- اختبار Playwright على preview المنشور:
  - Lighthouse / `BeforeInstallPromptEvent` للتحقق من installability.
  - فتح `/app` ثم go offline → التنقل يعرض `offline.html`، ومحاولة إصدار فاتورة تفشل برسالة شبكة.
  - `?sw=off` يلغي التسجيل.
- توثيق screenshots تحت `/tmp/browser/pwa/`.

## التقرير النهائي

سيتضمّن: files changed، manifest path، sw path (`/sw.js` بعد البناء)، caching strategy، تأكيد denylist لـ Supabase، نتائج installability، و final decision.

## ملاحظات تقنية

- الاعتماد على `vite-plugin-pwa` المتوافق مع TanStack Start (Vite 7) بدلًا من كتابة `public/sw.js` يدويًا — يلتزم بـ PWA skill ويتجنب stale precache بعد كل deploy.
- لا تغيير في `vite.config.ts` خارج إضافة plugin واحد.
- لا تغيير في `src/integrations/supabase/*` أو `src/lib/db.ts` أو أي RPC.
- ملفات تتغير: `vite.config.ts`, `src/routes/__root.tsx`, `src/lib/pwa-register.ts` (جديد), `public/manifest.webmanifest` (جديد), `public/offline.html` (جديد), `public/icons/*` (جديد), `package.json` (+`vite-plugin-pwa` dev).
