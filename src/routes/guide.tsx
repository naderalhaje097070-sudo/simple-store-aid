import { createFileRoute, Link } from "@tanstack/react-router";

export const Route = createFileRoute("/guide")({
  head: () => ({
    meta: [
      { title: "دليل منجز — نسخة المرجع النهائي" },
      {
        name: "description",
        content:
          "دليل صفحة واحدة لنسخة منجز المرجعية: الرحلات الأساسية، الحدود المالية، وكلمات الواجهة.",
      },
    ],
  }),
  component: GuidePage,
});

function Section({
  id,
  title,
  children,
}: {
  id: string;
  title: string;
  children: React.ReactNode;
}) {
  return (
    <section id={id} className="scroll-mt-20 border-t border-border pt-8 mt-8 first:border-0 first:pt-0 first:mt-0">
      <h2 className="text-xl font-bold text-foreground mb-4">{title}</h2>
      <div className="space-y-4 text-sm leading-7 text-foreground/90">{children}</div>
    </section>
  );
}

function Row({ k, v, note }: { k: string; v: string; note?: string }) {
  return (
    <div className="grid grid-cols-[1fr_1fr] gap-3 py-2 border-b border-border/50 last:border-0">
      <div className="font-medium text-foreground">{k}</div>
      <div className="text-muted-foreground">
        {v}
        {note ? <div className="text-xs mt-1 opacity-70">{note}</div> : null}
      </div>
    </div>
  );
}

function GuidePage() {
  return (
    <div className="min-h-screen bg-background" dir="rtl">
      {/* Header */}
      <header className="sticky top-0 z-10 bg-background/95 backdrop-blur border-b border-border">
        <div className="max-w-3xl mx-auto px-4 py-3 flex items-center justify-between">
          <div>
            <div className="text-xs text-muted-foreground">منجز · دليل المرجع</div>
            <h1 className="text-base font-bold text-foreground">نسخة المرجع النهائي</h1>
          </div>
          <Link
            to="/"
            className="text-xs font-medium text-primary hover:underline"
          >
            ← العودة للتطبيق
          </Link>
        </div>
      </header>

      <main className="max-w-3xl mx-auto px-4 py-6">
        {/* TOC */}
        <nav aria-label="فهرس" className="rounded-lg bg-muted/50 p-4 mb-6 text-sm">
          <div className="font-semibold mb-2">المحتويات</div>
          <ul className="grid grid-cols-2 gap-y-1 gap-x-3 text-primary">
            <li><a href="#purpose" className="hover:underline">الغرض</a></li>
            <li><a href="#journeys" className="hover:underline">الرحلات الأساسية</a></li>
            <li><a href="#boundaries" className="hover:underline">الحدود المالية</a></li>
            <li><a href="#words" className="hover:underline">كلمات الواجهة</a></li>
            <li><a href="#alerts" className="hover:underline">التنبيهات</a></li>
            <li><a href="#constraints" className="hover:underline">قيود لا تُكسر</a></li>
          </ul>
        </nav>

        <Section id="purpose" title="الغرض">
          <p>
            هذه النسخة هي <strong>المرجع البصري والسلوكي</strong> لتطبيق منجز —
            ليست منتجًا تشغيليًا. الهدف: صاحب محل صغير يفتح التطبيق فيرى
            <strong> ٣ أرقام فقط</strong>، ويُصدر فاتورة بيع في
            <strong> أقل من ١٠ ثوانٍ</strong>، ولا يرى أي رقم يخلط بين
            <em> ما بِيع</em> و<em> ما حُصِّل</em>.
          </p>
        </Section>

        <Section id="journeys" title="الرحلات الأساسية">
          <div className="space-y-5">
            <div>
              <h3 className="font-semibold mb-1">١) البيع السريع (&lt; ١٠ ثوانٍ)</h3>
              <ol className="list-decimal pr-5 space-y-1 text-muted-foreground">
                <li>ضغط FAB «بيع» من الهوم.</li>
                <li>تركيز تلقائي على البحث، أو اختيار من شبكة ٣ أعمدة.</li>
                <li>ضغط مطوّل = +٥ للكمية.</li>
                <li>شريط سفلي ثابت: الإجمالي + «إصدار فاتورة».</li>
                <li>اختيار: نقدًا / آجل / تحويل → تأكيد.</li>
              </ol>
            </div>

            <div>
              <h3 className="font-semibold mb-1">٢) التحصيل من عميل</h3>
              <p className="text-muted-foreground">
                من الهوم → «العملاء المتأخرون» → فتح العميل → «استلام دفعة» →
                المبلغ ينقص من <em>دين العميل</em> ويُضاف إلى <em>المحصّل اليوم</em>.
                لا يُغيّر رقم «بِعت اليوم».
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-1">٣) تسوية مع المندوب</h3>
              <p className="text-muted-foreground">
                «المندوبون» → فتح مندوب → «تسوية» → إدخال المسلَّم. ينقص من
                <em> عهدة المندوب</em>، ولا يُحتسب تحصيلًا من العملاء.
              </p>
            </div>

            <div>
              <h3 className="font-semibold mb-1">٤) إقفال اليوم (UX فقط)</h3>
              <p className="text-muted-foreground">
                ملخّص اليوم: بِعت / محصّل / مصاريف / صافي الكاش. لا قفل
                محاسبي — يمكن تعديل أي حركة بعد الإقفال.
              </p>
            </div>
          </div>
        </Section>

        <Section id="boundaries" title="الحدود المالية (لا يجوز خلطها)">
          <div className="rounded-lg border border-border overflow-hidden">
            <Row k="بِعت اليوم" v="مجموع الفواتير الصادرة (نقدًا + آجل)" />
            <Row k="محصّل اليوم" v="كاش دخل الدرج فعلًا (بيع نقدي + دفعات ديون)" />
            <Row k="دين العميل" v="ما على العميل من فواتير آجلة لم تُحصَّل" />
            <Row k="عهدة المندوب" v="بضاعة/نقد مع المندوب لم تُسوَّ بعد" note="لا تُخصم من دين العملاء" />
            <Row k="ربح تقديري" v="بِعت − تكلفة البضاعة (دفتري)" note="ليس كاش متاح" />
            <Row k="ربح من المحصّل" v="حصة الربح من المبالغ التي دخلت فعلًا" note="هذا ما يمكن سحبه" />
          </div>
          <p className="text-xs text-muted-foreground">
            القاعدة: كل رقم على الواجهة يجب أن يُجيب على سؤال واحد فقط.
            إن لزم الجمع، اعرض الرقمين بجانب بعض، لا تجمعهما في رقم ثالث.
          </p>
        </Section>

        <Section id="words" title="كلمات الواجهة الأساسية">
          <div className="rounded-lg border border-border overflow-hidden">
            <Row k="بِعت" v="إجمالي قيمة البيع — لا يعني وصول الكاش" />
            <Row k="محصّل" v="كاش وصل فعلًا اليوم" />
            <Row k="مبالغ لم تدخل بعد" v="بديل عن «مديونية» — أوضح للمستخدم" />
            <Row k="إيقاف العرض مؤقتًا" v="بديل عن «إلغاء» — لا يحذف البيانات" />
            <Row k="استلام دفعة" v="تحصيل من عميل على دين قائم" />
            <Row k="تسوية" v="مع مندوب فقط — ليست تحصيلًا" />
            <Row k="إصدار فاتورة" v="ينتهي به البيع — ليس «حفظ» ولا «تأكيد»" />
            <Row k="إقفال اليوم" v="ملخّص بصري — ليس قفلًا محاسبيًا" />
          </div>
        </Section>

        <Section id="alerts" title="التنبيهات الذكية (الهوم)">
          <ul className="list-disc pr-5 space-y-1 text-muted-foreground">
            <li>عملاء تأخّر دينهم عن المعتاد.</li>
            <li>مندوب عليه عهدة كبيرة دون تسوية.</li>
            <li>منتجات قاربت على النفاد بناءً على سرعة البيع.</li>
          </ul>
          <p className="text-xs text-muted-foreground">
            كل تنبيه قابل للضغط ويفتح الإجراء المناسب مباشرة — لا شاشة وسيطة.
          </p>
        </Section>

        <Section id="constraints" title="قيود لا تُكسر">
          <ul className="list-disc pr-5 space-y-1 text-muted-foreground">
            <li>لا ERP. لا حسابات معقّدة. لا فروع.</li>
            <li>لا أكثر من ٣ أرقام على الشاشة الأولى.</li>
            <li>لا خلط بين «بِعت» و«محصّل» في أي مكان.</li>
            <li>لا قفل مالي حقيقي في «إقفال اليوم».</li>
            <li>RTL كامل، موبايل أولًا، خط Tajawal، مسافات لمس ≥ 44px.</li>
          </ul>
        </Section>

        <footer className="mt-10 pt-6 border-t border-border text-xs text-muted-foreground">
          هذه الصفحة هي المرجع الوحيد المعتمد لنقل النسخة إلى منجز الحقيقي
          عبر PRs صغيرة ومستقلة.
        </footer>
      </main>
    </div>
  );
}
