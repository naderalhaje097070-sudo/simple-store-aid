# A5 / A8 — ثمانية طلبات، ولا إغلاق قبل الدمج المأذون

المصدر التنفيذي421774f4bb2f6e541be8ca03faf3714e7c81bab8. الرؤوس الأصلية والدليل التفصيلي فيcoverage-proof.json؛ main43d6edb. عداد المشروع28مفتوحًا، close now0. لا نحذف الفروع أو نعيد كتابة التاريخ.

| PR | ما حُفظ أو حُل محله | التصرف بعد إذن المالك ووصول البديل إلىmain |
|---|---|---|
|32|14Markdown أصلية byte-identical تحتchanges/sec-ci-001؛ تصميم عزل/CLI/reporting/policy تاريخي، والتحقق المالي الكامل باقٍC5|إغلاق كتصميم متجاوز بالخطة الحالية، لا كاعتماد لكل البوابات المالية المقترحة|
|33|14Markdown أصلية byte-identical تحتchanges/sec-env-001؛ حواجز resolver/SSR/CI مثبتة ضمن48/54 والأساس الحالي|إغلاق المتجاوز مع رابط البديل والأدلة|
|48|18مسارًا:7exact و11مصالحة موضحة أدناه؛ لا محتوى مطلوب يُطرح لمجرد تقليل العدد|إغلاق superseded بعد فحص حماية البديل علىmain|
|51|وثائق المصدر والخطة الأصلية محفوظة في ancestor والتحديثات التراكمية للحالة؛ current plan هو70/6263266625|إغلاق مع بيان أن التوثيق التاريخي محفوظ وتجاوزته الحالة الجديدة|
|52|ancestor؛ ترقياتTanStack/serializer واختبارات security محفوظة، مع تحديثات آمنة لاحقة|إغلاق بعد إثبات وصول graph/guards المقبولة إلىmain|
|53|ancestor؛ معالجة الاعتماديات/lock/evidence محفوظة؛ audit الحالي كامل ناجح دون تجاهل|إغلاق مع ربط التقرير النهائي؛ لا توريث أرقامaudit قديمة|
|54|ancestor؛ عزل البيئات والـREST/proxy/browser حُفظ وشُدد؛ nativeG1 على421|إغلاق مع ربط قبول الأساس الحالي|
|72|الطلب القائم الممثل للحزمة، من6da4dad إلى المرشح الجديد fast-forward بلا ضياع؛ base سيصبحmain|الدمج المحمي بعد موافقة المالك؛ GitHub يغلقه كمدمج، ثم يُثبت SHAعلىmain|

الإغلاق مشروط بمقارنة ما وصل إلىmain بالمصدر/التغطية المقبولين، وتسجيل البديل. أي فرق مطلوب غير محفوظ يبقى مهمة داخلA؛ العدد وحده ليس معيار إنجاز. متطلبات B/C لا تُحذف بإغلاق تصميم تاريخي؛ تبقى في الخطة الحالية وسجل findings.

## مصالحة18مسارًا من48

القيم exact/changed وSHAs لكل مسار فيcoverage-proof.json محدثة على421، لا على رأس توثيق سابق. المسارات7المتطابقة: `.env.example`، isolated-auth-smoke workflow، sec-ci-gate4 workflow، `src/server.ts`، financial-rules/run.sh، supabase-build-config unit، vite.config.ts.

المسارات11المحدثة:

| المسار | سبب المصالحة ودليل حفظ الغرض |
|---|---|
|quality.yml|حفظ البناء المعزول/حواجز البيئة؛ إضافةchanged lint للامتدادات6 والفشل الصريح والاختبارات/ثبات التوليد ونتائج المتصفح؛ لا تخفيف قواعد|
|sec-env-gate4-probe.yml|عزل54 والحراس اللاحقة محفوظة؛ nativeenvironment probes تقرأ المسارات الفعلية|
|config/supabase-build-config.ts|resolver صريح fail-closed وتوافق الأنواع/التنسيق؛ unit/SSR target agreement/counter controls|
|tests/e2e/README.md|توثيق الحدود والإعدادات المحدثة، لا كود بديل أو تصريح إنتاج|
|isolated-auth-smoke.py|نقل/متصفح مثبت المصدر إلى origins المعتمدة، service workers محظورة|
|rapid-click-sale.py|حارسtarget/REST وعدم وراثةproxy وعدم اتباعredirects؛ ضوابطstatic/runtime الحالية|
|tests/e2e/run.sh|إعداد صريح للبيئة المحلية وعدم انتقاء إنتاج تلقائي|
|sale-dashboard-close.py|نفس حدود الكتابة المصادق عليها، وguards للنقل/المتصفح؛ لم يُستبدل بfixtureاليوم|
|write_harness_guard.py|رفضproxy/targetغيرالمأذون قبلالكتابة؛ G1environment يعيدchallengeالفعلي|
|tests/gate4/sec-env/probe.ts|مصدرمصالحة54/اختباراتtarget محفوظ؛ لاproductionfallback|
|mobile-rtl-smoke.py|canonicalorigins ورفضruntime mismatch وخطأالعزل صريح؛ لاجاهزيةvisualعامةمستنتجة|

هذا حفظ تعاقدي للحماية، وليس ادعاء تطابق حرفي للمسارات11. المرجع: مراجعة الأساس المستقلة19أكتوبر، source-delta/CHANGE_FILES، الضوابط الحالية والفرق النهائي؛ حساباتالمبيعات/المخزونالأوسعحزمةC.
