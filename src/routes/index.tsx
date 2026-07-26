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
  Check,
  X,
  Wallet,
  TrendingUp,
  Sparkles,
  Store,
  Clock,
  Quote,
} from "lucide-react";
import { supabase } from "@/integrations/supabase/client";

export const Route = createFileRoute("/")({
  ssr: false,
  head: () => ({
    meta: [
      { title: "منجز — دفتر ذكي لمحلك الصغير | Mongezz" },
      {
        name: "description",
        content:
          "منجز: تطبيق بسيط لإدارة محلك الصغير. بيع سريع، متابعة ديون العملاء، عهدة المندوب، وتسويات يومية — كل شي في مكان واحد.",
      },
      { property: "og:title", content: "منجز — دفتر ذكي لمحلك الصغير | Mongezz" },
      {
        property: "og:description",
        content:
          "بِع، حصّل، تابع الديون والعهدة — بدون تعقيد ERP. مصمم لصاحب المحل الصغير.",
      },
      { property: "og:url", content: "https://www.fin-biz.shop/" },
      { property: "og:image", content: "https://www.fin-biz.shop/og-image.jpg" },
      { property: "og:image:width", content: "1200" },
      { property: "og:image:height", content: "630" },
      { property: "og:image:alt", content: "منجز — دفتر ذكي لمحلك الصغير" },
      { name: "twitter:title", content: "منجز — دفتر ذكي لمحلك الصغير | Mongezz" },
      {
        name: "twitter:description",
        content:
          "بِع، حصّل، تابع الديون والعهدة — بدون تعقيد ERP. مصمم لصاحب المحل الصغير.",
      },
      { name: "twitter:image", content: "https://www.fin-biz.shop/og-image.jpg" },
    ],
    links: [{ rel: "canonical", href: "https://www.fin-biz.shop/" }],
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
    return <LandingSkeleton />;
  }

  return (
    <div dir="rtl" className="min-h-screen bg-background text-foreground overflow-x-hidden animate-fade-in">
      <NavBar />
      <main>
        <Hero />
        <TrustBar />
        <Features />
        <ScreensShowcase />
        <Comparison />
        <HowItWorks />
        <Testimonials />
        <FAQ />
        <FinalCTA />
      </main>
      <Footer />
    </div>
  );
}

/** Light skeleton mirroring the real hero + stats layout to avoid flash/layout shift. */
function LandingSkeleton() {
  return (
    <div dir="rtl" className="min-h-screen bg-background overflow-x-hidden" aria-busy="true" aria-label="جاري التحميل">
      {/* Nav */}
      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/70 backdrop-blur-xl">
        <div className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2.5">
            <div className="h-9 w-9 rounded-xl bg-muted animate-pulse" />
            <div className="h-4 w-16 rounded bg-muted animate-pulse" />
          </div>
          <div className="flex items-center gap-2">
            <div className="h-8 w-14 rounded-lg bg-muted animate-pulse" />
            <div className="h-9 w-24 rounded-lg bg-muted animate-pulse" />
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="px-4 pt-12 pb-16 md:pt-20 md:pb-24">
        <div className="mx-auto max-w-6xl grid md:grid-cols-2 gap-12 items-center">
          <div className="space-y-5">
            <div className="h-7 w-52 rounded-full bg-muted animate-pulse mx-auto md:mx-0" />
            <div className="space-y-3">
              <div className="h-11 md:h-14 w-3/4 rounded-lg bg-muted animate-pulse mx-auto md:mx-0" />
              <div className="h-11 md:h-14 w-2/3 rounded-lg bg-muted animate-pulse mx-auto md:mx-0" />
            </div>
            <div className="space-y-2 max-w-lg mx-auto md:mx-0">
              <div className="h-4 w-full rounded bg-muted animate-pulse" />
              <div className="h-4 w-5/6 rounded bg-muted animate-pulse" />
            </div>
            <div className="flex gap-3 justify-center md:justify-start pt-2">
              <div className="h-[52px] w-40 rounded-xl bg-muted animate-pulse" />
              <div className="h-[52px] w-32 rounded-xl bg-muted animate-pulse" />
            </div>
            <div className="flex gap-4 justify-center md:justify-start pt-1">
              {[0, 1, 2].map((i) => (
                <div key={i} className="h-3.5 w-24 rounded bg-muted animate-pulse" />
              ))}
            </div>
          </div>

          {/* Phone mockup placeholder */}
          <div className="mx-auto w-full max-w-[320px]">
            <div className="rounded-[2.5rem] border border-border bg-card p-4 pt-5 space-y-3">
              <div className="h-4 w-full rounded bg-muted animate-pulse" />
              <div className="h-24 rounded-2xl bg-muted animate-pulse" />
              <div className="grid grid-cols-2 gap-2">
                <div className="h-14 rounded-xl bg-muted animate-pulse" />
                <div className="h-14 rounded-xl bg-muted animate-pulse" />
              </div>
              <div className="grid grid-cols-3 gap-2">
                {[0, 1, 2, 3, 4, 5].map((i) => (
                  <div key={i} className="aspect-square rounded-xl bg-muted animate-pulse" />
                ))}
              </div>
              <div className="h-11 rounded-xl bg-muted animate-pulse" />
            </div>
          </div>
        </div>
      </section>

      {/* Stats grid */}
      <section className="px-4 py-6 border-y border-border bg-muted/20">
        <div className="mx-auto max-w-5xl grid grid-cols-2 md:grid-cols-4 gap-4">
          {[0, 1, 2, 3].map((i) => (
            <div key={i} className="flex flex-col items-center gap-2">
              <div className="h-7 w-20 rounded bg-muted animate-pulse" />
              <div className="h-3 w-16 rounded bg-muted animate-pulse" />
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}


function NavBar() {
  return (
    <header className="sticky top-0 z-40 backdrop-blur-xl bg-background/70 border-b border-border/60">
      <div className="mx-auto max-w-6xl px-4 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <div className="h-9 w-9 rounded-xl bg-gradient-to-br from-primary to-primary/70 grid place-items-center text-primary-foreground font-black shadow-lg shadow-primary/20">
            م
          </div>
          <span className="font-black text-lg tracking-tight">منجز</span>
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
            className="px-4 py-2 text-sm font-semibold rounded-lg bg-primary text-primary-foreground hover:opacity-90 transition shadow-md shadow-primary/20"
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
    <section className="relative px-4 pt-12 pb-16 md:pt-20 md:pb-24 overflow-hidden">
      {/* Ambient background */}
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 right-1/4 h-96 w-96 rounded-full bg-primary/10 blur-3xl" />
        <div className="absolute bottom-0 left-1/4 h-96 w-96 rounded-full bg-primary/5 blur-3xl" />
        <div
          className="absolute inset-0 opacity-[0.03]"
          style={{
            backgroundImage:
              "radial-gradient(circle at 1px 1px, currentColor 1px, transparent 0)",
            backgroundSize: "24px 24px",
          }}
        />
      </div>

      <div className="mx-auto max-w-6xl grid md:grid-cols-2 gap-12 items-center">
        <div className="text-center md:text-right">
          <div
            className="animate-fade-up inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-semibold mb-5"
            style={{ animationDelay: "0ms" }}
          >
            <Sparkles className="h-3.5 w-3.5" />
            مصمم لصاحب المحل الصغير
          </div>
          <h1 className="text-4xl md:text-6xl font-black leading-[1.1] tracking-tight">
            دفتر ذكي
            <br />
            <span className="bg-gradient-to-l from-primary to-primary/60 bg-clip-text text-transparent">
              لمحلك الصغير
            </span>
          </h1>
          <p className="mt-5 text-base md:text-lg text-muted-foreground leading-relaxed max-w-lg mx-auto md:mx-0">
            بِع بسرعة، وفي نهاية اليوم اعرف فلوسك وين بالضبط:{" "}
            <span className="text-foreground font-semibold">محصّل</span>،{" "}
            <span className="text-foreground font-semibold">ديون عملاء</span>، و
            <span className="text-foreground font-semibold">عهدة مندوب</span>.
          </p>
          <div className="mt-7 flex flex-wrap gap-3 justify-center md:justify-start">
            <Link
              to="/auth"
              className="group px-6 py-3.5 rounded-xl bg-primary text-primary-foreground font-bold hover:opacity-90 transition inline-flex items-center gap-2 shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:-translate-y-0.5"
            >
              ابدأ مجاناً
              <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
            </Link>
            <Link
              to="/guide"
              className="px-6 py-3.5 rounded-xl border border-border bg-card text-foreground font-semibold hover:bg-muted transition"
            >
              شوف الدليل
            </Link>
          </div>
          <div className="mt-5 flex flex-wrap gap-4 justify-center md:justify-start text-xs text-muted-foreground">
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-3.5 w-3.5 text-primary" /> بدون بطاقة ائتمان
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-3.5 w-3.5 text-primary" /> جاهز خلال دقيقة
            </span>
            <span className="inline-flex items-center gap-1.5">
              <Check className="h-3.5 w-3.5 text-primary" /> عربي RTL بالكامل
            </span>
          </div>
        </div>
        <HeroMockup />
      </div>
    </section>
  );
}

function HeroMockup() {
  return (
    <div className="relative mx-auto w-full max-w-[320px] animate-fade-in">
      {/* Glow */}
      <div className="absolute -inset-8 bg-gradient-to-br from-primary/20 via-primary/5 to-transparent rounded-[3rem] blur-3xl" />

      {/* Floating stat card - top */}
      <div className="absolute -top-4 -right-6 z-20 hidden sm:block animate-fade-in">
        <div className="bg-card border border-border rounded-2xl shadow-xl px-4 py-3 flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-primary/15 grid place-items-center">
            <TrendingUp className="h-4 w-4 text-primary" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground">مبيعات اليوم</div>
            <div className="text-sm font-black" style={{ direction: "ltr" }}>
              +18%
            </div>
          </div>
        </div>
      </div>

      {/* Floating stat card - bottom */}
      <div className="absolute -bottom-4 -left-6 z-20 hidden sm:block">
        <div className="bg-card border border-border rounded-2xl shadow-xl px-4 py-3 flex items-center gap-3">
          <div className="h-9 w-9 rounded-xl bg-primary/15 grid place-items-center">
            <Wallet className="h-4 w-4 text-primary" />
          </div>
          <div>
            <div className="text-[10px] text-muted-foreground">المحصّل</div>
            <div className="text-sm font-black" style={{ direction: "ltr" }}>
              940 د.ل
            </div>
          </div>
        </div>
      </div>

      {/* Phone frame */}
      <div className="relative rounded-[2.5rem] border border-border bg-card shadow-2xl overflow-hidden ring-1 ring-black/5">
        <div className="px-5 pt-3 pb-2 flex items-center justify-between text-[10px] text-muted-foreground">
          <span className="font-semibold">9:41</span>
          <div className="h-4 w-16 rounded-full bg-foreground/10" />
          <span>●●●</span>
        </div>
        <div className="px-4 pb-5">
          <div className="flex items-center justify-between mb-3">
            <div>
              <div className="text-[10px] text-muted-foreground">مساء الخير 👋</div>
              <div className="text-sm font-bold">محل النور</div>
            </div>
            <div className="h-8 w-8 rounded-full bg-primary/15 grid place-items-center text-primary text-xs font-bold">
              أ
            </div>
          </div>

          <div className="rounded-2xl bg-gradient-to-br from-primary to-primary/80 text-primary-foreground p-4 mb-3 shadow-lg shadow-primary/20">
            <div className="text-[10px] opacity-80">صافي اليوم</div>
            <div className="text-3xl font-black mt-1" style={{ direction: "ltr" }}>
              1,240 د.ل
            </div>
            <div className="mt-2 flex items-center gap-1 text-[10px] opacity-90">
              <TrendingUp className="h-3 w-3" /> +18% عن أمس
            </div>
          </div>

          <div className="grid grid-cols-2 gap-2 mb-3">
            <div className="rounded-xl bg-muted/50 border border-border p-2.5">
              <div className="text-[10px] text-muted-foreground">ديون</div>
              <div className="text-sm font-bold" style={{ direction: "ltr" }}>
                320 د.ل
              </div>
            </div>
            <div className="rounded-xl bg-muted/50 border border-border p-2.5">
              <div className="text-[10px] text-muted-foreground">عهدة</div>
              <div className="text-sm font-bold" style={{ direction: "ltr" }}>
                180 د.ل
              </div>
            </div>
          </div>

          <div className="grid grid-cols-3 gap-2 mb-3">
            {["شاي", "قهوة", "ماء", "كيك", "تمر", "حليب"].map((p, i) => (
              <div
                key={p}
                className="aspect-square rounded-xl bg-gradient-to-br from-muted/60 to-muted/20 border border-border grid place-items-center text-xs font-medium text-foreground/80 hover:scale-105 transition"
                style={{ animationDelay: `${i * 50}ms` }}
              >
                {p}
              </div>
            ))}
          </div>
          <button className="w-full py-3 rounded-xl bg-foreground text-background text-sm font-bold shadow-lg">
            + فاتورة جديدة
          </button>
        </div>
      </div>
    </div>
  );
}

function TrustBar() {
  const stats = [
    { v: "< 10 ث", l: "لإصدار فاتورة" },
    { v: "100%", l: "عربي RTL" },
    { v: "0 د.ل", l: "للتجربة" },
    { v: "24/7", l: "متاح دائماً" },
  ];
  return (
    <section className="px-4 py-6 border-y border-border bg-muted/20">
      <div className="mx-auto max-w-5xl grid grid-cols-2 md:grid-cols-4 gap-4">
        {stats.map((s) => (
          <div key={s.l} className="text-center">
            <div className="text-xl md:text-2xl font-black text-primary" style={{ direction: "ltr" }}>
              {s.v}
            </div>
            <div className="text-xs text-muted-foreground mt-0.5">{s.l}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

const FEATURES = [
  {
    icon: Zap,
    title: "بيع سريع",
    desc: "أصدر فاتورة كاملة بأقل من 10 ثوانٍ.",
    accent: "from-primary/20 to-primary/5",
  },
  {
    icon: Users,
    title: "ديون العملاء",
    desc: "اعرف من عليه كم، وحصّل بثقة.",
    accent: "from-primary/20 to-primary/5",
  },
  {
    icon: Truck,
    title: "عهدة المندوب",
    desc: "تابع ما خرج وما رجع، بدون لخبطة.",
    accent: "from-primary/20 to-primary/5",
  },
  {
    icon: ClipboardCheck,
    title: "تسويات يومية",
    desc: "أقفل يومك بضغطة، واعرف ربحك الحقيقي.",
    accent: "from-primary/20 to-primary/5",
  },
];

function Features() {
  return (
    <section className="px-4 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-12">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 text-primary text-xs font-semibold mb-3">
            المزايا
          </div>
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            كل ما يحتاجه محلك — فقط
          </h2>
          <p className="mt-3 text-muted-foreground max-w-lg mx-auto">
            بدون شاشات معقدة، بدون مصطلحات محاسبية. أدوات عملية لصاحب المحل.
          </p>
        </div>
        <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-4">
          {FEATURES.map((f, i) => (
            <div
              key={f.title}
              className="group relative rounded-2xl border border-border bg-card p-6 hover:shadow-xl hover:-translate-y-1 hover:border-primary/30 transition-all duration-300"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${f.accent} opacity-0 group-hover:opacity-100 transition-opacity`} />
              <div className="relative">
                <div className="h-12 w-12 rounded-xl bg-primary/15 text-primary grid place-items-center mb-4 group-hover:scale-110 transition-transform">
                  <f.icon className="h-5 w-5" />
                </div>
                <div className="font-bold text-lg mb-1.5">{f.title}</div>
                <div className="text-sm text-muted-foreground leading-relaxed">
                  {f.desc}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function ScreensShowcase() {
  const screens = [
    {
      icon: Store,
      title: "الرئيسية",
      desc: "ملخص يومك في نظرة واحدة: مبيعات، محصّل، ديون، عهدة.",
    },
    {
      icon: Wallet,
      title: "التحصيل والديون",
      desc: "افتح ملف كل عميل، شوف تاريخ ديونه، وحصّل بضغطة.",
    },
    {
      icon: TrendingUp,
      title: "الربح الحقيقي",
      desc: "ربحك محسوب من النقد المحصّل فعلياً، مش من مبيعات معلّقة.",
    },
  ];
  return (
    <section className="px-4 py-16 md:py-24 bg-muted/30">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            ثلاث شاشات، تحكّم كامل
          </h2>
          <p className="mt-3 text-muted-foreground">
            صُممت بلغة صاحب المحل، مش بلغة المحاسب.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-5">
          {screens.map((s) => (
            <div
              key={s.title}
              className="rounded-2xl border border-border bg-card p-6 hover:shadow-lg transition"
            >
              <div className="h-11 w-11 rounded-xl bg-primary/15 text-primary grid place-items-center mb-4">
                <s.icon className="h-5 w-5" />
              </div>
              <div className="font-bold text-lg mb-2">{s.title}</div>
              <div className="text-sm text-muted-foreground leading-relaxed">
                {s.desc}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Comparison() {
  const rows = [
    { l: "الوقت لإصدار فاتورة", mongezz: "< 10 ثواني", other: "دقائق" },
    { l: "تدريب مطلوب", mongezz: "لا", other: "أيام" },
    { l: "فصل الديون عن المحصّل", mongezz: true, other: false },
    { l: "متابعة عهدة المندوب", mongezz: true, other: false },
    { l: "يعمل على الجوال", mongezz: true, other: "أحياناً" },
    { l: "بالعربية RTL", mongezz: true, other: false },
  ];
  return (
    <section className="px-4 py-16 md:py-24">
      <div className="mx-auto max-w-4xl">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            ليش منجز؟
          </h2>
          <p className="mt-3 text-muted-foreground">
            الفرق بين دفتر ذكي وأنظمة ERP الثقيلة.
          </p>
        </div>
        <div className="rounded-2xl border border-border bg-card overflow-hidden shadow-sm">
          <div className="grid grid-cols-3 bg-muted/50 border-b border-border">
            <div className="p-4 text-sm font-bold">الميزة</div>
            <div className="p-4 text-sm font-bold text-center border-r border-l border-border bg-primary/5 text-primary">
              منجز
            </div>
            <div className="p-4 text-sm font-bold text-center text-muted-foreground">
              أنظمة تقليدية
            </div>
          </div>
          {rows.map((r, i) => (
            <div
              key={r.l}
              className={`grid grid-cols-3 ${i !== rows.length - 1 ? "border-b border-border" : ""}`}
            >
              <div className="p-4 text-sm">{r.l}</div>
              <div className="p-4 text-sm text-center border-r border-l border-border bg-primary/5 font-semibold">
                {typeof r.mongezz === "boolean" ? (
                  r.mongezz ? (
                    <Check className="h-5 w-5 text-primary inline" />
                  ) : (
                    <X className="h-5 w-5 text-muted-foreground inline" />
                  )
                ) : (
                  <span className="text-primary">{r.mongezz}</span>
                )}
              </div>
              <div className="p-4 text-sm text-center text-muted-foreground">
                {typeof r.other === "boolean" ? (
                  r.other ? (
                    <Check className="h-5 w-5 text-muted-foreground inline" />
                  ) : (
                    <X className="h-5 w-5 text-muted-foreground/60 inline" />
                  )
                ) : (
                  r.other
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const STEPS = [
  {
    n: "1",
    t: "اشترك بحسابك",
    d: "أنشئ حساب محلك في أقل من دقيقة، بدون بطاقة.",
    icon: Smartphone,
  },
  {
    n: "2",
    t: "أضف منتجاتك وعملاءك",
    d: "ابدأ بقائمة بسيطة، وزِد لاحقاً وقت ما تحتاج.",
    icon: Store,
  },
  {
    n: "3",
    t: "ابدأ البيع والمتابعة",
    d: "من جوالك، أينما كنت، مع تحديث فوري لأرقامك.",
    icon: Zap,
  },
];

function HowItWorks() {
  return (
    <section className="px-4 py-16 md:py-24 bg-muted/30">
      <div className="mx-auto max-w-5xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            ثلاث خطوات فقط
          </h2>
          <p className="mt-3 text-muted-foreground">من الصفر إلى أول بيع في دقائق.</p>
        </div>
        <div className="grid md:grid-cols-3 gap-5 relative">
          {STEPS.map((s, i) => (
            <div
              key={s.n}
              className="relative rounded-2xl border border-border bg-card p-6 text-center md:text-right hover:shadow-lg transition"
            >
              <div className="flex items-center gap-3 mb-4 justify-center md:justify-start">
                <div className="h-12 w-12 rounded-2xl bg-gradient-to-br from-primary to-primary/70 text-primary-foreground grid place-items-center font-black text-lg shadow-lg shadow-primary/20">
                  {s.n}
                </div>
                <s.icon className="h-5 w-5 text-muted-foreground" />
              </div>
              <div className="font-bold text-lg mb-1.5">{s.t}</div>
              <div className="text-sm text-muted-foreground leading-relaxed">
                {s.d}
              </div>
              {i < STEPS.length - 1 && (
                <div className="hidden md:block absolute top-1/2 -left-3 h-px w-6 bg-border" />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

const TESTIMONIALS = [
  {
    name: "أبو محمد",
    role: "بقالة، طرابلس",
    text: "أول مرة أعرف بالضبط كم دين ورا العملاء. قبل كنت أخسر أرقام في الدفتر.",
  },
  {
    name: "خالد",
    role: "محل ملابس، بنغازي",
    text: "المندوب صار يرجّع لي حساب دقيق كل يوم. وفّرت عليّ ساعة يومياً.",
  },
  {
    name: "أم يوسف",
    role: "مكتبة، مصراتة",
    text: "بسيط جداً. ابني الصغير علّمني عليه في 5 دقائق.",
  },
];

function Testimonials() {
  return (
    <section className="px-4 py-16 md:py-24">
      <div className="mx-auto max-w-6xl">
        <div className="text-center mb-12">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            كلام أصحاب المحلات
          </h2>
          <p className="mt-3 text-muted-foreground">
            تجارب حقيقية من محلات صغيرة في ليبيا.
          </p>
        </div>
        <div className="grid md:grid-cols-3 gap-5">
          {TESTIMONIALS.map((t) => (
            <div
              key={t.name}
              className="rounded-2xl border border-border bg-card p-6 hover:shadow-lg hover:-translate-y-1 transition-all"
            >
              <Quote className="h-6 w-6 text-primary/40 mb-3" />
              <p className="text-sm leading-relaxed text-foreground/90 mb-4">
                «{t.text}»
              </p>
              <div className="flex items-center gap-3 pt-4 border-t border-border">
                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary/30 to-primary/10 grid place-items-center text-primary font-bold">
                  {t.name[0]}
                </div>
                <div>
                  <div className="font-bold text-sm">{t.name}</div>
                  <div className="text-xs text-muted-foreground">{t.role}</div>
                </div>
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
  {
    q: "هل يعمل بدون إنترنت؟",
    a: "منجز يحتاج إنترنت للمزامنة والحفظ الآمن، لكنه سريع جداً وخفيف على البيانات.",
  },
];

function FAQ() {
  const [open, setOpen] = useState<number | null>(0);
  return (
    <section className="px-4 py-16 md:py-24 bg-muted/30">
      <div className="mx-auto max-w-3xl">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-black tracking-tight">
            أسئلة شائعة
          </h2>
          <p className="mt-3 text-muted-foreground">كل ما تحتاج تعرفه قبل ما تبدأ.</p>
        </div>
        <div className="space-y-3">
          {FAQS.map((f, i) => {
            const isOpen = open === i;
            return (
              <div
                key={i}
                className={`rounded-xl border bg-card overflow-hidden transition-all ${
                  isOpen ? "border-primary/40 shadow-md" : "border-border"
                }`}
              >
                <button
                  onClick={() => setOpen(isOpen ? null : i)}
                  className="w-full flex items-center justify-between px-5 py-4 text-right hover:bg-muted/50 transition"
                >
                  <span className="font-semibold">{f.q}</span>
                  <ChevronDown
                    className={`h-4 w-4 text-muted-foreground transition-transform shrink-0 ${
                      isOpen ? "rotate-180 text-primary" : ""
                    }`}
                  />
                </button>
                {isOpen && (
                  <div className="px-5 pb-4 text-sm text-muted-foreground leading-relaxed animate-fade-in">
                    {f.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </section>
  );
}

function FinalCTA() {
  return (
    <section className="px-4 py-16 md:py-24">
      <div className="mx-auto max-w-4xl">
        <div className="relative rounded-3xl bg-gradient-to-br from-primary via-primary to-primary/80 text-primary-foreground p-8 md:p-14 text-center overflow-hidden shadow-2xl shadow-primary/25">
          {/* Decorative circles */}
          <div className="absolute top-0 right-0 h-64 w-64 rounded-full bg-white/10 blur-3xl -translate-y-1/2 translate-x-1/2" />
          <div className="absolute bottom-0 left-0 h-64 w-64 rounded-full bg-white/5 blur-3xl translate-y-1/2 -translate-x-1/2" />

          <div className="relative">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/15 backdrop-blur text-xs font-semibold mb-4">
              <Clock className="h-3.5 w-3.5" />
              جاهز خلال دقيقة
            </div>
            <ShieldCheck className="h-10 w-10 mx-auto mb-4 opacity-90" />
            <h3 className="text-2xl md:text-4xl font-black mb-3">
              جرّب منجز اليوم
            </h3>
            <p className="opacity-90 mb-7 text-sm md:text-base max-w-md mx-auto">
              أنشئ حساب محلك مجاناً، وابدأ خلال دقيقة. بدون بطاقة، بدون التزام.
            </p>
            <div className="flex flex-wrap gap-3 justify-center">
              <Link
                to="/auth"
                className="group inline-flex items-center gap-2 px-7 py-3.5 rounded-xl bg-background text-foreground font-bold hover:opacity-95 transition shadow-lg hover:-translate-y-0.5"
              >
                ابدأ مجاناً
                <ArrowLeft className="h-4 w-4 group-hover:-translate-x-1 transition-transform" />
              </Link>
              <Link
                to="/guide"
                className="inline-flex items-center gap-2 px-7 py-3.5 rounded-xl border border-white/30 text-primary-foreground font-semibold hover:bg-white/10 transition"
              >
                شوف الدليل
              </Link>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-border bg-background">
      <div className="mx-auto max-w-6xl px-4 py-10 flex flex-col md:flex-row items-center justify-between gap-4 text-sm text-muted-foreground">
        <div className="flex items-center gap-2.5">
          <div className="h-8 w-8 rounded-xl bg-gradient-to-br from-primary to-primary/70 grid place-items-center text-primary-foreground font-black text-xs">
            م
          </div>
          <span className="font-bold text-foreground">منجز</span>
          <span className="opacity-70">© {new Date().getFullYear()}</span>
        </div>
        <div className="flex items-center gap-5">
          <Link to="/guide" className="hover:text-foreground transition">
            الدليل
          </Link>
          <Link to="/auth" className="hover:text-foreground transition">
            تسجيل دخول
          </Link>
          <Link
            to="/auth"
            className="px-4 py-2 rounded-lg bg-primary text-primary-foreground font-semibold hover:opacity-90 transition"
          >
            ابدأ مجاناً
          </Link>
        </div>
      </div>
    </footer>
  );
}
