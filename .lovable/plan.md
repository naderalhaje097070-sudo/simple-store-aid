## القاعدة المعتمدة
عند إنشاء فاتورة `delivery = courier` مع مدفوع > 0: المال **بيد المندوب كعهدة**، ليس في صندوق المحل. لا يدخل المحصّل إلا بعد التسوية.

## التغييرات

### 1. هجرة قاعدة البيانات — تعديل `create_sale_with_items`
داخل فرع `p_delivery = 'courier'`:

| الحالة | paid | status | collected_by_courier | courier_state | سجل payments |
|---|---|---|---|---|---|
| `p_paid = 0` | 0 | `debt` | 0 | `pending` | لا |
| `0 < p_paid < total` | 0 | `debt` | `p_paid` | `delivered_partial` | لا |
| `p_paid = total` | 0 | `debt` | `p_paid` | `delivered_full` | لا |

- لا يُنشأ سجل `payments` من نوع `sale` لأي فاتورة مندوب.
- شرط `customer_required_for_debt` يبقى ساري.
- شرط `p_paid <= v_total` يبقى ساري (يمنع إدخال مبلغ أكبر من الإجمالي).
- البيع المباشر `direct` بلا تغيير.

تحقق المنطق الذي يبقى سليماً تلقائياً:
- `settle_courier_orders` يحوّل `collected_by_courier → paid` ويُنشئ `payment` بنوع `courier_settlement` → المحصّل يزيد هنا فقط.
- `close_day.collected` يجمع من `payments` → لن يتأثر قبل التسوية، ويزيد بعدها.
- `close_day.unsettled_custody` يجمع `collected_by_courier` للطلبات النشطة → سيرتفع فور إنشاء فاتورة المندوب بمبلغ.
- `return_courier_order` يرفض المرتجع إذا `collected_by_courier > 0` → يحمي العهدة.

### 2. الواجهة — `src/routes/_authenticated/app.tsx`
- في شاشة "بيع جديد" عند اختيار توصيل مندوب: تغيير تسمية الحقل من "مدفوع" إلى **"قبضه المندوب الآن"** + ملاحظة صغيرة: "هذا المبلغ يُسجَّل عهدة على المندوب، ولا يدخل صندوق المحل إلا بعد التسوية".
- بعد الحفظ في عرض الفاتورة/قائمة الفواتير: لفواتير المندوب يُعرض `collected_by_courier` كـ "بيد المندوب" بدل "مدفوع". الإجمالي والباقي يُحسبان بالنسبة للعميل كالمعتاد (الباقي = total − paid، وفاتورة المندوب paid = 0 حتى التسوية).
- لا تغيير على `CourierCustodyScreen` و `SettlementsScreen` — يلتقطان الحالة الجديدة تلقائياً.

### 3. اختبار التحقق
بعد الهجرة، تشغيل استعلامات قراءة للتأكد من سيناريو الـ100:
1. إنشاء فاتورة مندوب total=100 paid=100 → فحص: `orders.paid=0`, `orders.collected_by_courier=100`, `orders.courier_state='delivered_full'`, `orders.status='debt'`, لا صف في `payments` لهذه الفاتورة.
2. تشغيل `close_day` تجريبياً (قراءة فقط عبر RPC على بيئة الاختبار إن أمكن) للتأكد أن `collected` لم يزد و `unsettled_custody` زاد بـ100.
3. تنفيذ `settle_courier_orders` بمبلغ 100 → فحص: ظهور `payments` بنوع `courier_settlement` قيمة 100، `orders.paid=100`, `collected_by_courier=0`.

بعد موافقتك أبدأ بالهجرة ثم تحديث الواجهة ثم اختبار البيانات.