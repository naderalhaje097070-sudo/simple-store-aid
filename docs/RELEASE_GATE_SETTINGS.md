# إعدادات GitHub المطلوبة من المالك لحماية `main`

هذه الإعدادات لا يستطيع الوكيل تطبيقها: هي في إعدادات المستودع وتحتاج صلاحية المالك.
بدونها تبقى البوابات مجرد فحوص تظهر نتيجتها، ولا تمنع الدمج.

## متى تُطبَّق

بعد دمج الـPR الذي يُدخل `release-gate-trusted.yml` و`release-finance.yml` إلى `main`.
قبل ذلك لا يملك GitHub أسماء هذه الفحوص ليختارها.

## الخطوات

المسار: **Settings ← Rules ← Rulesets ← New ruleset ← New branch ruleset**

1. **Ruleset name:** `main-protection`
2. **Enforcement status:** `Active`
3. **Target branches:** Add target ← `Include default branch` (أي `main`)
4. فعّل القواعد التالية:
   - **Restrict deletions** — منع حذف `main`.
   - **Block force pushes** — منع إعادة كتابة تاريخ `main`. ضروري أيضًا لربط Lovable.
   - **Require a pull request before merging**
     - Required approvals: `0`. أنت الحساب الوحيد، وصاحب الـPR لا يستطيع اعتماد طلبه بنفسه،
       لذا المراجعة المستقلة تكون تقريرًا مكتوبًا في الـPR، والدمج قرارك.
     - فعّل **Dismiss stale pull request approvals when new commits are pushed**.
   - **Require status checks to pass**
     - فعّل **Require branches to be up to date before merging**.
     - أضف الفحوص التالية بأسمائها كما تظهر:
       - `gate` (من Release gate (trusted))
       - `suite (collection, fresh)`
       - `suite (collection, upgrade)`
       - `suite (collection, populated)`
       - `suite (sale, fresh)`
       - `suite (sale, upgrade)`
       - `suite (sale, populated)`
       - `suite (journey, fresh)`
       - `suite (journey, upgrade)`
       - `quality` (من Integrated G0 verification)
5. **Bypass list:** اتركها فارغة. لو أضفت نفسك، تستطيع تجاوز كل ما سبق بضغطة واحدة.
6. اضغط **Create**.

## حدود صريحة

- أنت مالك المستودع، وتستطيع دائمًا تعديل هذه القواعد أو حذفها. هي تحمي من الأخطاء
  ومن انحراف أي وكيل عن الخطة، لا من المالك نفسه.
- بوابة `gate` تعمل من نسخة `main` ولا تنفّذ كود الـPR، لذا لا يستطيع PR تعطيلها بتعديل
  ملف الـworkflow الخاص به.
- اختبارات `suite (...)` تنفّذ كود الـPR (هذا هو الغرض منها) بصلاحية قراءة فقط ودون أسرار.

## التحقق بعد التطبيق

افتح PR تجريبيًا يعدّل Migration قديمة موجودة في `main` (دون دمجه). يجب أن يفشل فحص
`gate` برسالة `Base migration changed`، وأن يكون زر الدمج معطّلًا. ثم أغلق الـPR.
