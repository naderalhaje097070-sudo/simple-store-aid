
## ملخص الفحص

المشروع جيد عمومًا (RLS مفعّل، RPCs محمية، locks على المعاملات الحرجة)، لكن الفحص الشامل كشف **3 مشاكل Critical**، **4 High**، **8 Medium**، **7 Low**. التقرير الكامل أعلاه يحتوي كل التفاصيل مع file:line.

---

## خطة الإصلاح المُقترحة (موجة واحدة)

### المرحلة 1 — الإصلاحات الحرجة (Backend RPCs)

**migration واحدة** تحتوي:

1. **[C1] `delete_order_with_restore_stock(p_order_id uuid)`**
   - يتحقق `_assert_owner`
   - يمنع حذف طلبات courier التي لها `collected_by_courier > 0`
   - يستعيد المخزون لكل بند داخل transaction
   - يحذف payments → order_items → order

2. **[C2] `update_courier_order_state(p_order_id, p_state, p_collected)`**
   - يتحقق `_assert_staff` و `p_collected ≤ total`
   - يحدّث `courier_state`, `collected_by_courier`, `paid`, `status` ذرّيًا
   - يسجّل payment إذا زاد المحصّل

3. **[M8] تحسين `return_courier_order`** — بعد الإرجاع: `delivery='direct'`, `courier_state='returned'` لإخراج الطلب من قوائم العهدة.

4. **[M6] index مركّب**: `CREATE INDEX orders_tenant_created_idx ON orders(tenant_id, created_at DESC)`.

5. **[M3] `VALIDATE CONSTRAINT`** على القيود الموجودة كـ `NOT VALID` (يفشل بأمان إن كانت هناك بيانات مخالفة، ونعرف نُبلّغك).

> **C3 (أرقام فواتير per-tenant)** يحتاج migration أكبر (إعادة ترقيم وتعديل عمود `number`). أقترح تأجيلها لموجة ثانية لأنها قد تربك مراجعة الفواتير القديمة عند المستخدمين الحاليين.

### المرحلة 2 — إصلاحات الواجهة (`src/lib/db.ts` + `src/routes/_authenticated/app.tsx`)

6. **[C1+C2]** إعادة كتابة `useDeleteInvoice` و `useUpdateCourierState` لاستدعاء RPCs الجديدة.
7. **[H1]** إضافة Sheet لإضافة عميل في `CustomersScreen` (نسخ نمط `CouriersScreen`).
8. **[H2+M7]** قَصْر `DayCloseScreen` على بيانات "اليوم" فقط بصرف النظر عن فلتر الرئيسية، وتنظيف input غير المُستخدم في `useCloseDay`.
9. **[H3]** توحيد منطق `realizedProfit` في الواجهة مع منطق `close_day` (نسبة per-order وليس إجمالية).
10. **[H4]** استثناء طلبات `courierState = "pending"` من حسابات ديون العميل في `DebtCustomerScreen`.
11. **[M2]** إصلاح guard `PilotScreen` ليشمل `role === null` وإضافة حالة تحميل.
12. **[M4]** ترتيب `useInvoices` تنازليًا (`ascending: false`) وتقليل `slice` على الـ DB إن أمكن.
13. **[M5]** استبدال `alert()` بـ `showToast` المستخدم في الباقي.
14. **[L7]** تغيير `fmtTime` إلى `ar` locale.

### المرحلة 3 — تنظيف (سريع)

15. **[M1+L2+L3+L5]** حذف `nextOrderNumber`، الـ stubs الفارغة، و `console.error` المتسرّبة في onboarding.
16. **[L4]** إضافة تعريف `AppContext` موحّد بدل `any` (إن كان الوقت يسمح — وإلا تأجيل).

---

## ما هو خارج النطاق الآن

- C3 (per-tenant invoice numbering) — موجة ثانية مستقلة.
- L4 الكامل (إعادة كتابة كل props إلى types) — تحسين تدريجي.
- مراقبة الأخطاء عبر خدمة خارجية (Sentry) — قرار منتج.

---

## النتيجة المتوقعة

بعد هذه الموجة: لا يبقى أي finding بمستوى Critical أو High، والـ Medium يصبح ≤ 2 (C3 + L4 المُؤجَّلَين). جاهز تمامًا للـ Pilot الموسّع.

هل أبدأ بالتنفيذ بالكامل، أم تريد الاقتصار على Critical + High فقط في هذه الموجة؟
