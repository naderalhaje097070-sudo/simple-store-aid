# Financial Rules Regression Suite

اختبارات SQL تتحقق من قواعد الأرباح/الديون/العهدة في Mongezz V2 عبر استدعاء الـ RPCs الفعلية ثم التراجع `ROLLBACK` بحيث لا تترك أي بيانات.

## التشغيل

```bash
bash tests/financial-rules/run.sh
```

يتطلب وجود متغيرات `PG*` (متاحة داخل sandbox Lovable). الاسكربت يختار أول tenant ويستخدم مالكه كـ `auth.uid()` عبر `request.jwt.claims`.

## ماذا يُختبر (13 سيناريو)

| # | السيناريو | القاعدة |
|---|-----------|---------|
| T1 | بيع مباشر مدفوع كامل | `status=paid`, سجل دفع، خصم مخزون |
| T2 | بيع مباشر جزئي مع عميل | `status=partial`, دين = total - paid |
| T3 | بيع مباشر بدون عميل وبه دين | يُرفض (`customer_required_for_debt`) |
| T4 | المدفوع > الإجمالي | يُرفض (`paid_exceeds_total`) |
| T5 | مندوب بدون مال (pending) | لا سجل دفع، عهدة = 0 |
| T6 | مندوب مع مال عند الإنشاء | المال **عهدة** وليس صندوق (orders.paid=0) |
| T7 | تحصيل دين والعهدة على المندوب | يُرفض (`settle_courier_first`) |
| T8 | تسوية عهدة المندوب | المال يدخل الصندوق، تنتهي العهدة، `courier_id=NULL` |
| T9 | مرتجع مندوب قبل أي تحصيل | المخزون يعود، تنتهي العهدة |
| T10 | مرتجع مندوب بعد تحصيل جزئي | يُرفض (`cannot_return_partially_paid_order`) |
| T11 | حذف فاتورة مباشرة غير مدفوعة | المخزون يعود، الفاتورة تُحذف |
| T12 | حذف فاتورة مدفوعة | يُرفض (`cannot_delete_paid_order`) |
| T13 | بيع بكمية تفوق المخزون | يُرفض (`insufficient_stock`) |

## كيف يضمن عدم التلوث؟

كل شيء داخل `BEGIN ... ROLLBACK`. حتى المنتجات/العميل/المندوب التجريبيين يختفون بعد التنفيذ. أي تعديل لاحق على RPC مالية سيكسر اختباراً واحداً على الأقل من هذه السيناريوهات.

## متى تُشغّل؟

- بعد كل تعديل على RPCs مالية (`create_sale_with_items`, `collect_order_debt`, `settle_courier_orders`, `return_courier_order`, `delete_order_with_restore_stock`, `update_courier_order_state`).
- قبل أي migration يلمس جداول `orders` / `payments` / `products`.
- قبل النشر للـ Pilot.
