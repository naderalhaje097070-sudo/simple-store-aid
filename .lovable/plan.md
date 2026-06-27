## المشكلة
زر "تأكيد التسوية" يفشل بـ `collected_exceeds_remaining`. سبب فعلي مثبت من قاعدة البيانات: فاتورتان عند المندوب لهما `paid = total = 100, status='paid'` لكن `courier_state='delivered_full'` و `collected_by_courier=100`. التحقق `collected > total - paid` = `100 > 0` يفجّر الـ RPC.

## الإصلاح (Migration واحدة فقط — لا تعديل واجهة)

### 1) تنظيف بيانات يتيمة (مرة واحدة)
```sql
UPDATE public.orders
   SET delivery='direct', courier_id=NULL, courier_state=NULL, collected_by_courier=0
 WHERE delivery='courier'
   AND status='paid'
   AND paid >= total
   AND courier_state IS NOT NULL;
```
لا يلمس مبالغ، فقط يُخرج فواتير مدفوعة بالكامل من حالة العهدة.

### 2) تصليب `settle_courier_orders` (clamp بدل throw)
داخل الحلقة، استبدال:
```sql
IF v_collected > v_order.total - v_order.paid THEN
  RAISE EXCEPTION 'collected_exceeds_remaining';
END IF;
```
بـ:
```sql
v_collected := LEAST(v_collected, GREATEST(v_order.total - v_order.paid, 0));
```
- لو `remaining = 0`: `v_collected = 0` → الحارس `IF v_collected > 0` يمنع إنشاء سجل دفع مكرر، وتُمسح حقول العهدة فقط.
- لو `collected ≤ remaining`: السلوك مطابق تمامًا للحالي.
- لا تغيير في إجمالي المحصّل أو الأرباح المحققة لأي فاتورة سليمة.

## ما يبقى كما هو
- `src/routes/_authenticated/app.tsx` (شاشة `SettlementsScreen`) — بدون تعديل.
- `src/lib/db.ts` (`useSettleCourier`) — بدون تعديل.
- باقي RPCs المالية (`create_sale_with_items`, `collect_order_debt`, `close_day`, `return_courier_order`) — بدون تعديل.
- صلاحيات `GRANT/REVOKE` على الـ RPC تُعاد كما هي.

## التحقق بعد التنفيذ
1. شاشة "تسوية" مع المندوب الحالي → الزر يعمل، رسالة النجاح تظهر، الفواتير تختفي من شاشة العهدة.
2. المحصّل اليومي لا يتضاعف (لأن paid كان أصلاً = total، والـ clamp يُضيف 0).
3. تجربة بيع courier جديد بسير كامل: pending → delivered_full → تسوية → يدخل المبلغ مرة واحدة فقط في المحصّل (سلوك معتاد).
