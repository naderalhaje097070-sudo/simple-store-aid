## نطاق محدود — 3 RPCs/migrations + تغيير تسمية واحد في الواجهة

### 1) H3 — Migration: `platform_admin_audit_log` (idempotent)

ملف migration واحد:

```sql
CREATE TABLE IF NOT EXISTS public.platform_admin_audit_log (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES auth.users(id) ON DELETE SET NULL,
  action text NOT NULL,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);

GRANT SELECT ON public.platform_admin_audit_log TO authenticated;
GRANT ALL ON public.platform_admin_audit_log TO service_role;
REVOKE ALL ON public.platform_admin_audit_log FROM anon, PUBLIC;

ALTER TABLE public.platform_admin_audit_log ENABLE ROW LEVEL SECURITY;

-- DROP IF EXISTS ثم CREATE حتى يكون idempotent
DROP POLICY IF EXISTS "platform_admins_read_audit" ON public.platform_admin_audit_log;
CREATE POLICY "platform_admins_read_audit"
  ON public.platform_admin_audit_log FOR SELECT
  TO authenticated
  USING (public.is_platform_admin());

CREATE INDEX IF NOT EXISTS idx_pa_audit_created_at
  ON public.platform_admin_audit_log (created_at DESC);
CREATE INDEX IF NOT EXISTS idx_pa_audit_user_id
  ON public.platform_admin_audit_log (user_id);
```

ملاحظة: `_log_platform_admin_action` يُدرج عبر SECURITY DEFINER فلا يحتاج INSERT policy.

### 2) H2 — تحديث `close_day` لتعريف موحّد للديون

نفس توقيع الدالة، نغيّر فقط حساب `v_customer_debts`:

```sql
SELECT COALESCE(SUM(
  CASE
    WHEN delivery = 'direct' OR courier_id IS NULL
      THEN GREATEST(total - paid, 0)
    WHEN delivery = 'courier' AND courier_state = 'delivered_none'
      THEN total
    WHEN delivery = 'courier' AND courier_state = 'delivered_partial'
      THEN GREATEST(total - collected_by_courier, 0)
    ELSE 0  -- pending / delivered_full / returned: لا يُحتسب هنا
  END
), 0) INTO v_customer_debts
FROM public.orders
WHERE tenant_id = v_tenant
  AND status IN ('partial','debt');
```

`unsettled_custody` و `collected` يبقيان كما هما. لا double count لأن المبلغ في يد المندوب يُحسب في custody فقط، والمبلغ على العميل يُحسب في debts فقط.

### 3) H4 — حارس في `collect_order_debt` لطلبات المندوب

داخل نفس الدالة، بعد `SELECT ... INTO v_order` و قبل التحقق من remaining:

```sql
IF v_order.delivery = 'courier' AND v_order.courier_id IS NOT NULL THEN
  IF COALESCE(v_order.collected_by_courier, 0) > 0
     OR v_order.courier_state IN ('pending','delivered_partial','delivered_full') THEN
    RAISE EXCEPTION 'settle_courier_first';
  END IF;
  -- مسموح فقط: delivered_none بدون عهدة (نادر لكن منطقي)
END IF;
```

في `src/lib/db.ts` داخل `rpcMessage`، أضف:
```ts
settle_courier_first: 'سوِّ عهدة المندوب أولًا قبل تحصيل هذه الفاتورة',
```

### 4) H1 — التسمية فقط (الخيار الآمن)

في `src/routes/_authenticated/app.tsx` شاشة الأرباح / إغلاق اليوم: تغيير عرض `realized_profit` من "الربح المحقق" إلى **"ربح تقديري"** مع تلميح صغير: "حساب نهائي يتم بعد توحيد منطق الأرباح". لا تغيير في DB أو الحساب.

### QA يدوي بعد الـ migrations

سأشغّل عبر `supabase--read_query` للتحقق:
- `SELECT * FROM platform_admin_audit_log LIMIT 1` — لا خطأ.
- إنشاء طلب courier تجريبي ثم محاولة `collect_order_debt` → يجب أن يرفع `settle_courier_first`.
- تشغيل `close_day` على tenant Pilot ومقارنة `customer_debts` مع تعريف الواجهة.
- Regression: بيع مباشر كامل/جزئي/دين، تحصيل دين direct، تسوية مندوب، إرجاع قبل/بعد تحصيل.

### Files changed

1. `supabase/migrations/<ts>_pilot_hardening.sql` — جديد (يحوي H3 + H2 + H4 معًا).
2. `src/lib/db.ts` — سطر واحد في `rpcMessage`.
3. `src/routes/_authenticated/app.tsx` — تغيير نص تسمية `realized_profit` فقط.

### المخرجات النهائية

تقرير مختصر: الملفات، اسم الـ migration، ملخص SQL، نتائج QA، والقرار النهائي.
