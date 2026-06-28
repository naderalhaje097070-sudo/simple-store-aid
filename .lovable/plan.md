# تشخيص "This page didn't load" بعد دمج PR #2

## الخطأ الفعلي (من console)
```
Error: Missing Supabase environment variable(s):
SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY.
Connect Supabase in Lovable Cloud.
   at src/integrations/supabase/client.ts (createSupabaseClient)
```
الـ Error Boundary في `__root.tsx` يلتقطه ويعرض شاشة "This page didn't load".

## نطاق العطل

| البيئة | HTTP | العنوان | الحالة |
|---|---|---|---|
| Preview `/`  (id-preview--…lovable.app) | 200 | "Internal Lovable project" (shell فارغ) | ❌ معطّل |
| Preview `/app` | 200 (يعيد توجيه عبر `_authenticated`) | "Internal Lovable project" | ❌ نفس الخطأ |
| Published `https://mongzz.lovable.app/` | 200 | "منجز — دفتر ذكي…" | ✅ يعمل |

الخلاصة: **كل الصفحات في Preview معطّلة، وليست homepage فقط**. السبب واحد لا يخص route معيّن.

## السبب الجذري

- الكراش يحدث في `src/integrations/supabase/client.ts` عند أول قراءة لـ `import.meta.env.VITE_SUPABASE_URL` / `VITE_SUPABASE_PUBLISHABLE_KEY`.
- `.env` موجود محلياً ويحتوي على المفاتيح (3 أسطر `VITE_SUPABASE_*`).
- لكن **build الـ Preview المنشور (static preview) تم بدون حقن متغيرات `VITE_*`**، لذا انضغطت `undefined` داخل bundle الـ client (`assets/index-DxQdmFzr.js`).
- لذلك Published يعمل (build جديد بمفاتيح صحيحة)، Preview لا يعمل (build قديم/ناقص).
- ليست مشكلة كود، ولا route، ولا منطق. هي مشكلة **build artifact للـ static preview** بعد merge PR #2.

## Build / Runtime

- Build: passed (bundle موجود ويُحمَّل، وProduction build يعمل من نفس الكود).
- Runtime: خطأ متغير بيئة في init الـ Supabase client → React Error Boundary.
- لا أخطاء TypeScript، لا فشل في الـ route tree، لا migrations أو RLS متعلقة بالموضوع.

## هل يحتاج Rebuild / Refresh؟

نعم. preview stale build. الحل (لاحقاً عند الموافقة، لا الآن):
1. Hard refresh أولاً (احتمال SW يخدم نسخة قديمة — PWA مفعّلة).
2. لو استمر، إعادة بناء preview (يكفي أي تعديل تافه أو إعادة تشغيل النشر/البناء) ليتم حقن `VITE_SUPABASE_*` في bundle جديد.
3. لا حاجة لأي تعديل كود، UI، business logic، migrations، أو RLS.

## ممنوع في هذا التشخيص (مُحترَم)
- لا R4d، لا إصلاح كود، لا UI، لا منطق، لا migrations/RLS/RPC/Publish.

## التالي
انتظار قرارك: هل أكتفي بطلب Hard Refresh، أم نطلب Rebuild للـ preview؟
