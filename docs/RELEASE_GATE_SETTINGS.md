# إعدادات GitHub المطلوبة من المالك لحماية `main`

هذه الإعدادات لا يستطيع الوكيل تطبيقها: هي في إعدادات المستودع وتحتاج صلاحية المالك.
بدونها تبقى البوابات مجرد فحوص تظهر نتيجتها، ولا تمنع الدمج.

## متى تُطبَّق: على مرحلتين

يطلب GitHub الفحص بالاسم. إذا طُلب فحص لا يعمل على `main`، يتعلق كل PR بانتظاره. وإذا تكرر
الاسم، يصبح الطلب غامضًا. الحقائق على `main` الآن (من فحوص PR #74):
- لا يوجد عليه `release-finance.yml`، فلا تعمل فحوص `suite (...)` إلا على PR يحمل الملف نفسه.
- يوجد فيه فحصان باسم `quality` (Quality وIntegrated G0) وفحصان باسم `audit`.
- إعادة التسمية إلى `integrated-quality` موجودة في فرع التكامل فقط.

لذلك:
- **المرحلة A:** بعد دمج PR #73 (البوابة الموثوقة فقط). لا تنتظر شيئًا آخر.
- **المرحلة B:** بعد دمج فرع التكامل في `main`. يصل حينها `release-finance.yml` واسم
  `integrated-quality`.

## الخطوات المشتركة

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
     - أضف الفحوص حسب المرحلة (أدناه). لا يعرض GitHub في القائمة إلا الفحوص التي عملت مؤخرًا.
       إن لم يظهر اسم، فشغّل PR يُنتجه أولًا.

### المرحلة A: الفحوص المطلوبة بعد دمج PR #73

- `trusted-release-gate` (من Release gate (trusted)) فقط.

لا تُضِف `quality` ولا `audit` الآن، فكلاهما مكرر على `main`. الفحوص الأخرى ستظل تعمل على كل
PR وتظهر نتائجها، لكنها لا تمنع الدمج آليًا في هذه المرحلة.

**المرحلة A مؤقتة، وليست حماية مالية.** `trusted-release-gate` يحرس الـMigrations وتغييرات الحوكمة،
لكنه لا يمنع وحده دمج كود تفشل اختباراته. شروط الانتقال من A إلى B:
1. لا يُدمج فرع التكامل إلا بعد نجاح وظائف `release-finance` التسع، وG0 وB1 وC5، على SHA واحد هو
   رأس الـPR نفسه، ومع المراجعة المستقلة وموافقتك الصريحة.
2. تُفعَّل المرحلة B فور الدمج.
3. يُختبر المنع فعليًا بالـPRين التجريبيين في قسم التحقق قبل أي تطوير جديد.

ملاحظة: PR دمج فرع التكامل يغيّر ملفات خارج المنتج، فسيفشل فيه `trusted-release-gate` حتى تضيف
الوسم `gov-ok-<SHA>` بنفسك بعد مراجعته. هذا هو المقصود.

### المرحلة B: الفحوص المطلوبة بعد دمج فرع التكامل

عدّل الـruleset نفسه وأضف إلى `trusted-release-gate`:
- `suite (collection, fresh)`
- `suite (collection, upgrade)`
- `suite (collection, populated)`
- `suite (sale, fresh)`
- `suite (sale, upgrade)`
- `suite (sale, populated)`
- `suite (journey, fresh)`
- `suite (journey, upgrade)`
- `suite (quantity, fresh)`
- `integrated-quality` (من Integrated G0 verification)

اسما `trusted-release-gate` و`integrated-quality` فريدان عمدًا: اختبار `tests/b7-ci-routing`
يفشل إن عرّف أي workflow آخر وظيفة بالاسم نفسه. هذه القائمة (11 فحصًا) هي نفسها قائمة
`docs/RELEASE_COVERAGE.md`.

5. **Bypass list:** اتركها فارغة. لو أضفت نفسك، تستطيع تجاوز كل ما سبق بضغطة واحدة.
6. اضغط **Create**.

## اعتماد تغييرات الحوكمة (لكل commit)

أي PR يغيّر ملفًا خارج المنتج نفسه يفشل فيه `trusted-release-gate` حتى تعتمده أنت.
المنتج المسموح بتغييره دون اعتماد: `src/` و`public/` و`supabase/migrations/`
(تحكمها قواعد الـMigrations) و`supabase/functions/` و`docs/` وملفات `*.md` في الجذر.
كل ما عداها يحتاج اعتمادًا، ومنه الـworkflows والاختبارات والمساعدات المشتركة
و`package.json` و`bun.lock` وإعدادات البناء وأي ملف جديد أو منقول.

1. افتح سجل الفحص الفاشل. السطر `RELEASE_GATE_FAILED` يذكر الملفات واسم الوسم المطلوب
   بالضبط: `gov-ok-<SHA الكامل لرأس الـPR>`.
2. راجع تغييرات تلك الملفات في الـPR.
3. أنشئ الوسم بهذا الاسم من **Issues ← Labels ← New label**، ثم أضفه إلى الـPR بنفسك من
   واجهة GitHub.
4. يعيد الفحص التشغيل تلقائيًا عند إضافة الوسم.

الفحص لا يقبل الوسم إلا إذا كان آخر حدث له "إضافة" قمتَ بها أنت مباشرة. يرفضه إن أضافه
تطبيق أو وكيل (ومنه Claude) أو حساب آخر. أي push جديد يغيّر الـSHA، فيلزم وسم جديد. لا
يلزم حذف الوسوم القديمة، فهي لا تعتمد إلا commitها.

## حدود صريحة

- **Lovable:** قاعدة "Require a pull request" تمنع أي push مباشر إلى `main`، ومنها
  مزامنة Lovable إن كانت تكتب في `main` مباشرة. لم أتحقق من سلوك Lovable تحت هذه القاعدة.
  إن توقفت المزامنة، فالخيار هو أن يعمل Lovable على فرع ويُدمج عبر PR. لا تضف Lovable إلى
  قائمة التجاوز إلا بقرار واعٍ منك، لأن ذلك يفتح طريقًا إلى `main` بلا فحوص.
- ربط الاعتماد بك يعتمد على الحقل `performed_via_github_app` في أحداث الوسوم. هذا
  مأخوذ من توثيق GitHub، ولم يُختبر فعليًا في هذه الجلسة. إن غاب الحقل، يفشل الفحص مغلقًا
  ("Approval event does not state whether an app made it"). خطوة التحقق أدناه تكشف ذلك.

- أنت مالك المستودع، وتستطيع دائمًا تعديل هذه القواعد أو حذفها. هي تحمي من الأخطاء
  ومن انحراف أي وكيل عن الخطة، لا من المالك نفسه.
- بوابة `trusted-release-gate` تعمل من نسخة `main` ولا تنفّذ كود الـPR، لذا لا يستطيع PR تعطيلها بتعديل
  ملف الـworkflow الخاص به.
- اختبارات `suite (...)` تنفّذ كود الـPR (هذا هو الغرض منها) بصلاحية قراءة فقط ودون أسرار.

## التحقق بعد التطبيق

1. افتح PR تجريبيًا يعدّل Migration قديمة موجودة في `main` (دون دمجه). يجب أن يفشل
   `trusted-release-gate` برسالة `Base migration changed`، وأن يكون زر الدمج معطّلًا.
2. في PR تجريبي آخر عدّل ملفًا تحت `tests/` فقط. يجب أن يفشل الفحص ويطلب `gov-ok-<sha>`.
   أضف الوسم بنفسك فينجح الفحص. ادفع commit جديدًا فيفشل مجددًا.
3. أغلق الـPRين دون دمج.
