# إصلاح الصفحات الفارغة في منجز

## التشخيص

بعد فحص `src/routes/_authenticated/app.tsx`:

1. **`SettlementsScreen` (سطر 1251–1253)**: عند عدم وجود مندوبين، السطر:
   ```ts
   const courier = p.couriers.find(...) ?? p.couriers[0]
   ```
   يُرجع `undefined`، ثم `courier.id` في السطر التالي يرمي خطأ غير ملتقط ⇒ الشاشة تختفي بالكامل (بيضاء).

2. **`CourierCustodyScreen`**: تعمل بدون كراش لكنها تعرض ثلاث بطاقات فارغة بأرقام `0` دون أي توجيه — تبدو "فارغة" للمستخدم الجديد.

3. **لا يوجد `errorComponent` على route الـ `_authenticated/app`** — أي خطأ React أثناء render يُسقط الشجرة بالكامل بدون رسالة. هذا يفسّر لماذا تظهر `/app` بيضاء بدل رسالة خطأ.

4. **شاشة Toast/تنبيهات تستدعي `go("settlements")`** من تنبيهات العهدة، فإذا ضغط المستخدم زر التنبيه دون مندوبين → كراش وشاشة بيضاء.

## الإصلاحات

### 1. `SettlementsScreen` — حماية ضد غياب المندوبين
- إن لم يوجد `courier` (لا مندوبين أصلًا، أو `openCourierId` غير صالح):
  - عرض empty state: "لا يوجد مندوبون بعد" + زر "إضافة مندوب" يفتح شاشة `couriers`.
  - منع الوصول لأي `courier.id` قبل التحقق.

### 2. `CourierCustodyScreen` — empty state واضحة
- إن لم يوجد مندوبون: نفس الـ empty state أعلاه بدل البطاقات الصفرية.
- إن وُجد مندوب بدون أي طلبات: رسالة "لا يوجد طلبات لهذا المندوب بعد".

### 3. إضافة `errorComponent` على `_authenticated/app`
- بطاقة بسيطة بالعربية: "حدث خطأ غير متوقع" + زر "إعادة المحاولة" يستدعي `router.invalidate()` + `reset()`.
- `console.error(error)` للمطور.
- يضمن أن أي خطأ مستقبلي لا يُنتج شاشة بيضاء.

### 4. حماية تنبيه العهدة في `HomeScreen`
- التنبيه يظهر فقط إذا `unsettledCustody > 0` **و** هناك مندوب واحد على الأقل.

## الملفات المتأثرة
- `src/routes/_authenticated/app.tsx` — تعديلات داخل `SettlementsScreen`، `CourierCustodyScreen`، شرط `alerts`، وإضافة `errorComponent` في `createFileRoute`.

## خارج النطاق
- لا تغيير في القواعد المالية أو الـ DB.
- لا تغيير في باقي الشاشات.
- لا migrations.
