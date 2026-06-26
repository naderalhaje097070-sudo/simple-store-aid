import { createFileRoute, Link, useNavigate } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import {
  Zap,
  Users,
  Truck,
  ClipboardCheck,
  ShieldCheck,
  Smartphone,
  ChevronDown,
  ArrowLeft,
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/")({
  ssr: false,
  head: () => ({
    meta: [
      { title: "منجز — دفتر ذكي لمحلك الصغير" },
      {
        name: "description",
        content:
          "منجز: تطبيق بسيط لإدارة محلك الصغير. بيع سريع، متابعة ديون العملاء، عهدة المندوب، وتسويات يومية — كل شي في مكان واحد.",
      },
      { property: "og:title", content: "منجز — دفتر ذكي لمحلك الصغير" },
      {
        property: "og:description",
        content:
          "بِع، حصّل، تابع الديون والعهدة — بدون تعقيد ERP. مصمم لصاحب المحل الصغير.",
      },
      { property: "og:type", content: "website" },
      { property: "og:url", content: "https://simple-store-aid.lovable.app/" },
    ],
    links: [
      { rel: "canonical", href: "https://simple-store-aid.lovable.app/" },
    ],
  }),
  component: LandingPage,
});

function LandingPage() {
  const navigate = useNavigate();
  const [checked, setChecked] = useState(false);

  useEffect(() => {
    let cancelled = false;
    supabase.auth.getSession().then(({ data }) => {
      if (cancelled) return;
      if (data.session) {
        navigate({ to: "/app" });
      } else {
        setChecked(true);
      }
    });
    return () => {
      cancelled = true;
    };
  }, [navigate]);

  if (!checked) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background">
        <div className="text-muted-foreground text-sm">جاري التحميل…</div>
      </div>
    );
  }

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground">
      <NavBar />
      <Hero />
      <Features />
      <HowItWorks />
      <FAQ />
      <Footer />
    </div>
  );
}

function NavBar() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur bg-background/80 border-b border-border">
      <div className="mx-auto max-w-5xl px-4 h-14 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="h-8 w-8 rounded-xl bg-primary/15 grid place-items-center text-primary font-bold">
            م
          </div>
          <span className="font-bold text-lg">منجز</span>
        </div>
        <nav className="flex items-center gap-2">
          <Link
            to="/auth"
            className="px-3 py-1.5 text-sm rounded-lg text-foreground/80 hover:text-foreground hover:bg-muted transition"
          >
            دخول
          </Link>
          <Link
            to="/auth"
            className="px-3 py-1.5 text-sm rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition"
          >
            ابدأ مجاناً
          </Link>
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="px-4 pt-10 pb-12 md:pt-16 md:pb-20">
      <div className="mx-auto max-w-5xl grid md:grid-cols-2 gap-10 items-center">
        <div className="text-center md:text-right">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-medium mb-4">
            <Smartphone className="h-3.5 w-3.5" />
            مصمم للجوال أولاً
          </div>
          <h1 className="text-3xl md:text-5xl font-extrabold leading-tight tracking-tight">
            دفتر ذكي
            <br />
            لمحلك الصغير
          </h1>
          <p className="mt-4 text-base md:text-lg text-muted-foreground leading-relaxed">
            بِع، حصّل، تابع ديون عملائك وعهدة المندوب — كل شي في مكان
            واحد، بدون تعقيد ERP.
          </p>
          <div className="mt-6 flex flex-wrap gap-3 justify-center md:justify-start">
            <Link
              to="/auth"
              className="px-5 py-3 rounded-xl bg-primary text-primary-foreground font-semibold hover:opacity-90 transition inline-flex items-center gap-2"
            >
              ابدأ مجاناً
              <ArrowLeft className="h-4 w-4" />
            </Link>
            <Link
              to="/auth"
              className="px-5 py-3 rounded-xl border border-border text-foreground font-semibold hover:bg-muted transition"
            >
              سجّل دخول
            </Link>
          </div>
          <p className="mt-3 text-xs text-muted-foreground">
            بدون بطاقة. جرّب الآن في أقل من دقيقة.
          </p>
        </div>
        <HeroMockup />
      </div>
    </section>
  );
}

function HeroMockup() {
  return (
    <div className="relative mx-auto w-full max-w-[280px]">
      <div className="absolute -inset-4 bg-primary/10 rounded-[2.5rem] blur-2xl" />
      <div className="relative rounded-[2rem] border border-border bg-card shadow-xl overflow-hidden">
        <div className="px-4 pt-3 pb-2 flex items-center justify-between text-[10px] text-muted-foreground">
          <span>9:41</span>
          <span>منجز</span>
        </div>
        <div className="px-4 pb-4">
          <div className="rounded-2xl bg-muted/40 p-3 mb-3">
            <div className="text-xs text-muted-foreground">صافي اليوم</div>
            <div
              className="text-2xl font-bold text-primary mt-0.5"
              style={{ direction: "ltr" }}
            >
              1,240 ر.س
            </div>
          </div>
          <div className="grid grid-cols-3 gap-2 mb-3">
            {["شاي", "قهوة", "ماء", "كيك", "تمر", "حليب"].map((p) => (
              <div
                key={p}
                className="aspect-square rounded-xl bg-muted/30 border border-border grid place-items-center text-xs text-foreground/80"
              >
                {p}
              </div>
            ))}
          </div>
          <button className="w-full py-2.5 rounded-xl bg-primary text-primary-foreground text-sm font-semibold">
            إصدار فاتورة
          </button>
        </div>
      </div>
    </div>
  );
}

const FEATURES = [
  {
    icon: Zap,
    title: "بيع سريع",
    desc: "أصدر فاتورة كاملة بأقل من 10 ثوانٍ.",
  },
  {
    icon: Users,
    title: "ديون العملاء",
    desc: "اعرف من عليه كم، وحصّل بثقة.",
  },
  {
    icon: Truck,
    title: "عهدة المندوب",
    desc: "تابع ما خرج وما رجع، بدون لخبطة.",
  },
  {
    icon: ClipboardCheck,
    title: "تسويات يومية",
    desc: "أقفل يومك بضغطة، واعرف ربحك الحقيقي.",
  },
];

function Features() {
  return (
    <section className="px-4 py-12 md:py-16 bg-muted/30">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-bold">
            كل ما يحتاجه محلك — فقط
          </h2>
          <p className="mt-2 text-muted-foreground">
            بدون شاشات معقدة، بدون مصطلحات محاسبية.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className="rounded-2xl border border-border bg-card p-5 hover:shadow-md transition"
            >
              <div className="h-10 w-10 rounded-xl bg-primary/15 text-primary grid place-items-center mb-3">
                <f.icon className="h-5 w-5" />
              </div>
              <div className="font-semibold mb-1">{f.title}</div>
              <div className="text-sm text-muted-foreground leading-relaxed">
                {f.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const STEPS = [
  { n: "1", t: "اشترك بحسابك", d: "أنشئ حساب محلك في أقل من دقيقة." },
  { n: "2", t: "أضف منتجاتك وعملاءك", d: "ابدأ بقائمة بسيطة، وزِد لاحقاً." },
  { n: "3", t: "ابدأ البيع والمتابعة", d: "من جوالك، أينما كنت." },
];

function HowItWorks() {
  return (
    <section className="px-4 py-12 md:py-16">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-10">
          <h2 className="text-2xl md:text-3xl font-bold">كيف يعمل؟</h2>
          <p className="mt-2 text-muted-foreground">ثلاث خطوات فقط.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-4">
          {STEPS.map((s) => (
            <div
              key={s.n}
              className="rounded-2xl border border-border bg-card p-6 text-center md:text-right"
            >
              <div className="h-10 w-10 rounded-full bg-primary text-primary-foreground grid place-items-center font-bold mx-auto md:mx-0 mb-3">
                {s.n}
              </div>
              <div className="font-semibold mb-1">{s.t}</div>
              <div className="text-sm text-muted-foreground leading-relaxed">
                {s.d}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const FAQS = [
  {
    q: "هل هو مجاني للتجربة؟",
    a: "نعم، تقدر تجرب منجز مجاناً وتستكشف كل المزايا قبل أي التزام.",
  },
  {
    q: "هل أحتاج خبرة محاسبة؟",
    a: "أبداً. منجز مصمم بلغة صاحب المحل: بيع، محصّل، ديون، عهدة — بدون مصطلحات معقدة.",
  },
  {
    q: "هل بياناتي آمنة؟",
    a: "نعم. كل محل بياناته معزولة تماماً، ولا أحد يصل لها إلا أنت ومن تأذن له.",
  },
  {
    q: "هل يعمل على الجوال؟",
    a: "منجز مصمم للجوال أولاً، ويعمل أيضاً على الكمبيوتر بنفس السلاسة.",
  },
];

function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section className="px-4 py-12 md:py-16 bg-muted/30">
      <div className="mx-auto max-w-3xl">
        <div className="text-center mb-8">
          <h2 className="text-2xl md:text-3xl font-bold">أسئلة شائعة</h2>
        </div>
        <div className="space-y-3">
          {FAQS.map((f, i) => {
            const isOpen = open === i;
            return (
              <div
                key={i}
                className="rounded-xl border border-border bg-card overflow-hidden"
              >
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="w-full flex items-center justify-between px-4 py-3 text-right hover:bg-muted/50 transition"
                >
                  <span className="font-medium">{f.q}</span>
                  <ChevronDown
                    className={`h-4 w-4 text-muted-foreground transition-transform ${
                      isOpen ? "rotate-180" : ""
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="px-4 pb-4 text-sm text-muted-foreground leading-relaxed">
                    {f.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
        <div className="mt-10 rounded-2xl bg-primary text-primary-foreground p-6 md:p-8 text-center">
          <ShieldCheck className="h-8 w-8 mx-auto mb-3 opacity-90" />
          <h3 className="text-xl md:text-2xl font-bold mb-2">
            جرّب منجز اليوم
          </h3>
          <p className="opacity-90 mb-5 text-sm md:text-base">
            أنشئ حساب محلك مجاناً، وابدأ خلال دقيقة.
          </p>
          <Link
            to="/auth"
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl bg-background text-foreground font-semibold hover:opacity-90 transition"
          >
            ابدأ مجاناً
            <ArrowLeft className="h-4 w-4" />
          </Link>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-5xl px-4 py-8 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2">
          <div className="h-7 w-7 rounded-lg bg-primary/15 grid place-items-center text-primary font-bold text-xs">
            م
          </div>
          <span className="font-semibold text-foreground">منجز</span>
          <span className="opacity-70">© {new Date().getFullYear()}</span>
        </div>
        <div className="flex items-center gap-4">
          <Link to="/guide" className="hover:text-foreground transition">
            الدليل
          </Link>
          <Link to="/auth" className="hover:text-foreground transition">
            تسجيل دخول
          </Link>
        </div>
      </div>
    </footer>
  );
}
