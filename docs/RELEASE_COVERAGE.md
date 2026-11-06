# خريطة تغطية الفحوص: من سلسلة المراحل إلى فحوص الـPR على `main`

الغرض: توثيق أين ذهب كل فحص قديم، وما لم يُستبدل بعد. هذه وثيقة حقائق لا وعود. كل بند
"مغطّى" أدناه يشير إلى خطوة أو control موجود فعلًا في الـworkflow المذكور.

## الفحوص المطلوبة على كل PR إلى `main` (المرحلة B في `RELEASE_GATE_SETTINGS.md`؛ في المرحلة A البوابة وحدها)

| الفحص | المصدر | ما يثبته |
|---|---|---|
| `trusted-release-gate` | `release-gate-trusted.yml` (`pull_request_target`، يعمل من نسخة `main`) | الـMigrations القديمة كما هي بالبايت، والجديدة لاحقة زمنيًا وليست في المستقبل البعيد، وأي تغيير خارج المنتج يحتاج وسمًا من المالك مربوطًا بالـSHA |
| `suite (collection, fresh/upgrade/populated)` | `release-finance.yml` | التحصيل والتسوية والإرجاع والتزامن وفقدان الرد والصلاحيات والإيقاف |
| `suite (sale, fresh/upgrade/populated)` | `release-finance.yml` | البيع بالمفتاح، الاستدعاءات المتوازية، الكسور، المنتج الأجنبي، المندوب |
| `suite (journey, fresh/upgrade)` | `release-finance.yml` | الرحلة الفعلية في المتصفح على سطح المكتب والجوال، وعقد الربح |
| `suite (quantity, fresh)` | `release-finance.yml` | الكميات الكسرية، رفض الكميات والمخزون غير الصالح بشكل ذري، رفض الأجنبي والموقوف |
| `integrated-quality` | `integration-verification.yml` | Typecheck وlint والوحدات والبناء وعقود المتصفح، **ومعها سلسلة الهوية القديمة** (انظر "حدود") |

كل suite يفشل إذا لم تُنفَّذ وتنجح مجموعة controls مسماة له (حد أدنى في كل mode). ويفشل
أيضًا إذا فشل أي control مسجّل.

## ما انتقل وأين

| الـworkflow القديم (push على فرع التكامل فقط) | البديل على الـPR |
|---|---|
| `c4-sale.yml` composition (3 modes) | `suite (sale, *)` |
| `c4-sale.yml` browser | خطوة "Database-free browser regressions" في `suite (sale, *)` |
| `c5-collection.yml` | `suite (collection, *)` مع `test_verdict.py` و`history.test.cjs` و`contracts.test.cjs` |
| `c5-stored-finance.yml` (fresh, populated) | `suite (collection, fresh/populated)`: كل controls الـ20 موجودة فيه بالاسم نفسه، عدا pin الـ54 الذي استُبدل بسجل الـgate |
| `c5-journey.yml` | `suite (journey, *)` مع `profit-report.test.ts` وفحص الأنواع المولدة و`selector_contract` |
| `c5-journey.yml` upgrade (seed55 ثم 56) | `upgrade` من Migrations `main` (50) إلى المرشح (56). البذر بـRPCs `main` نفسها، ثم مقارنة كل صف في كل جدول على أعمدته السابقة، وسجل البداية = `main`، وسجل النهاية = المرشح |
| `c2-quantity.yml` (fresh) | `suite (quantity, fresh)`. البيع يمر عبر العقد المعتمد `create_sale_with_items_idempotent`، لأن Migration `20261029044024` تسحب الدالة القديمة من `authenticated` عمدًا (FIN-IDEM). الشروط نفسها لم تتغير |
| بصمات البايت لكل مرحلة | `trusted-release-gate` في `release-finance`، و`tests/release/target.py` |

## ما لم يُستبدل (فجوات معروفة)

| الفحص | السبب | القرار |
|---|---|---|
| `c2-quantity.yml` upgrade | يعيد إنتاج خطأ ما قبل الإصلاح على حالة 50 Migration. هذه خاصية مرحلة، لا خاصية إصدار | لا يُنقل |
| `c3-composition.yml` (30 control) | نصفه إعادة إنتاج لأخطاء ما قبل التصحيح. النصف الدائم مغطّى جزئيًا فقط: تكرار المفتاح نفسه، ACL، الإيقاف، التزامن (في collection/sale). **غير مغطّى بالاسم:** `idempotency_table_RLS_deny_by_default` و`direct_idempotency_table_denied_*` و`same_key_replay_returns_original_without_writes` | فجوة. مهمة قبل أول PR في المرحلة الثانية (TASKS) |
| `c5-restore.yml` و`c5-restore-independent.yml` | الاستعادة شرط Pilot (المرحلة 5) ببيانات اصطناعية | خارج فحوص الـPR. تبقى على فرع التكامل |
| `b2-scanner-auth`, `b3-tenant-entitlement`, `b4-webhook-persistence` | لم تكن فحوص PR أصلًا | فجوة. تبقى على فرع التكامل. تُراجع قبل المرحلة الثانية |
| ربط صورة PostgreSQL بالـdigest (`c5-journey`) | `release-finance` يثبت إصدار CLI (`2.101.0`) و`PostgreSQL 17.6` (control `exact_reused_PostgreSQL_17_6`)، لا digest الصورة | مقبول. مذكور كخطر متبقٍ |

## حدود صريحة

- `integrated-quality` ما زال يشغّل سلسلة الهوية القديمة (`capture.py identity` وما يتبعه).
  أي PR لاحق يغيّر ملفًا محميًا فيها يجب أن يحدّث manifest المرحلة، وإلا يفشل. هذا فشل مغلق
  ولا يُضعف شيئًا، لكنه عبء. إزالته قرار منفصل بعد أن يثبت `trusted-release-gate` نفسه
  على `main`، عملًا بقاعدة "لا تحذف الآليات القديمة قبل إثبات البديل".
- `release-finance` على `pull_request` يختبر commit الدمج (`github.sha`)، لا رأس الـPR.
  مع "Require branches to be up to date" يكون commit الدمج هو ما سيصل إلى `main`.
- أدوات `supabase/setup-cli@v2` و`oven-sh/setup-bun@v2` مثبتة بالوسم لا بالـSHA.
