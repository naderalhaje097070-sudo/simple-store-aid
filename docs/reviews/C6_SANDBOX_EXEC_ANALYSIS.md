# تحليل أمني: الدور `sandbox_exec` في قاعدة الإنتاج

- **التاريخ:** 2026-11-18
- **المصدر:** قراءات الكتالوج السابقة للقراءة فقط (2026-11-16 و2026-11-18).
- **ما لم يُفعل لإعداد هذا التحليل:** لم يُقرأ الإنتاج من جديد، ولم يُعدَّل الدور، ولم تُجرَّب أي محاولة دخول به.

## 1. ما ثبت من الكتالوج
| البند | القيمة |
|---|---|
| السمات | `LOGIN`، `BYPASSRLS`، `INHERIT`، ليس superuser. هذا من بصمة السمات `login\|super\|bypassrls\|inherit = true\|false\|true\|true` |
| المخطط `public` | `USAGE` |
| جداول `public` الموجودة (الـ22 كلها) | `SELECT` و`INSERT`، ومنها `orders` و`payments` و`order_items` و`products` و`tenants` و`subscriptions` و`financial_audit_log` و`user_roles` و`profiles` |
| تسلسلات `public` | `SELECT` و`USAGE` |
| الصلاحيات الافتراضية (مالكها postgres) | `SELECT`/`INSERT` على الجداول، و`SELECT`/`USAGE` على التسلسلات، **لأي كائن جديد** في `public` و`auth` و`extensions` و`storage` |
| تنفيذ الدوال | لا توجد صلاحية افتراضية له على الدوال في `public` |

## 2. الأثر المحتمل (تحليل، دون اختبار عليه)
1. **تجاوز عزل المتاجر:**
   - مع `BYPASSRLS` لا تنطبق سياسات RLS عليه، ومنها `monjez_live_actor` و«tenant members read …».
   - من يملك جلسة بهذا الدور يقرأ بيانات **كل** المتاجر.
2. **تجاوز القيود المالية:**
   - `INSERT` المباشر على `payments` و`orders` و`order_items` يتجاوز دوال الخادم (RPC) التي تفرض قواعد المال، مثل منع الدفع الزائد والتحقق من الدين ومنع idempotency المكرر.
   - **ما يبقى:** قيود الجداول نفسها (CHECK وFK) تنطبق.
3. **التدقيق:** مشغّلات التدقيق (`trg_audit_*`) تعمل على INSERT في المدفوعات، فالإدخال المباشر سيُسجَّل. هذا ما لم يكن الدور معفى منها، وهو غير مُتحقق.
4. **الجداول الجديدة:** `financial_idempotency` و`day_close_profit_report` سيحصلان عليه تلقائيًا، كما ثبت في المحاكاة.
   - **الأخطر:** صلاحيات `auth` الافتراضية، إذا أنشأ postgres جداول هناك.
5. **ما لا يستطيعه:**
   - لا `UPDATE` ولا `DELETE` ولا `TRUNCATE` على الجداول الحالية.
   - لا تنفيذ لدوال `public` عبر صلاحية افتراضية.

## 3. ما لم يُتحقق منه (يحتاج وصولًا جديدًا أو إجابة Lovable)
| السؤال | كيف يُعرف | الحالة |
|---|---|---|
| هل له كلمة مرور، وما صلاحيتها (`rolvaliduntil`)؟ | `pg_authid` يحتاج صلاحية superuser، أو إجابة Lovable | غير معروف |
| عضويات الأدوار (`pg_auth_members`): من عضو فيه، وما هو عضو فيه؟ | قراءة كتالوج للإنتاج | **لم يُقرأ**: يحتاج موافقة على نطاق جديد |
| حد الاتصالات `rolconnlimit` | قراءة كتالوج | لم يُقرأ |
| هل يتصل فعلًا؟ ومن أين؟ (`pg_stat_activity`) | قراءة الإنتاج | لم يُقرأ |
| صلاحياته على جداول `auth` و`storage` **الموجودة** | قراءة كتالوج | لم يُقرأ؛ البصمة شملت `public` و`monjez_private` فقط |
| من ينشئه ويديره؟ | Lovable | وكيل Lovable: «غير موثّق»، ويرجّح أنه داخلي لأدوات الوكيل |
| هل يُعاد منحه تلقائيًا إن قُيِّد؟ | Lovable | غير معروف |

## 4. التقييم
- **الخطر الكامن:** مرتفع، إن كان الدور قابلًا للدخول من خارج بنية Lovable. ففيه تجاوز للعزل بين المتاجر وإدخال مالي مباشر.
- **الاحتمال:** غير معروف، ويرجّح أن الدور داخلي. **لا دليل على استغلال.**
- **التوصية:**
  1. **لا يُحذف الدور ولا تُسحب صلاحياته الآن**، لأن ذلك قد يعطّل أدوات Lovable.
  2. **يُطلب من فريق Lovable تأكيد مكتوب** لأسئلة §3. أقترح النص في الملحق.
  3. **إن وافق المالك،** قراءة كتالوج جديدة محصورة: `pg_auth_members` و`rolconnlimit` وصلاحياته على `auth` و`storage` وعدد جلساته الحالية دون محتواها. **تحتاج موافقة منفصلة.**
  4. **قرار تقييد الصلاحيات الافتراضية** على الجداول المالية الجديدة يُتخذ بعد إجابة Lovable، ولا يُضمَّن في C6.

## ملحق: نص مقترح لفريق Lovable (لم يُرسل)
> In our Lovable Cloud project (id 1c38f21a-…), the database role `sandbox_exec` has LOGIN and BYPASSRLS, plus SELECT/INSERT on all public tables. It also has default privileges on new tables in public, auth, extensions and storage. Please confirm:
> (1) what uses this role;
> (2) whether it has a password or any network path reachable outside Lovable's infrastructure;
> (3) whether we may safely restrict its privileges on our financial tables, and whether Lovable re-grants them;
> (4) whether its sessions are audited.
