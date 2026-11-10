import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { ArrowLeft } from "lucide-react";
import { supabase } from "@/integrations/supabase/client";
import { lovable } from "@/integrations/lovable/index";
import {
  EXISTING_ACCOUNT_MESSAGE,
  SIGNUP_FAILED_MESSAGE,
  isExistingAccountError,
  isExistingAccountReply,
} from "@/lib/auth-signup";

type AuthFailure = {
  message?: unknown;
  code?: unknown;
};

function parseAuthFailure(error: unknown): { message: string; code: string } {
  const failure = error as AuthFailure;
  return {
    message: String(failure?.message ?? error),
    code: String(failure?.code ?? ""),
  };
}

export const Route = createFileRoute("/auth")({
  validateSearch: (s: Record<string, unknown>) => {
    const next =
      typeof s.next === "string" && s.next.startsWith("/") && !s.next.startsWith("//")
        ? s.next
        : undefined;
    return next === undefined ? {} : { next };
  },
  head: () => ({
    meta: [
      { title: "تسجيل الدخول — منجز" },
      {
        name: "description",
        content:
          "تسجيل الدخول إلى حساب محلك في منجز لإدارة المبيعات والديون والعهدة اليومية بسهولة.",
      },
    ],
  }),
  component: AuthPage,
});

function AuthPage() {
  const navigate = useNavigate();
  const { next } = Route.useSearch();
  const postAuthTarget = next ?? "/app";
  const [mode, setMode] = useState<"signin" | "signup">("signin");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [info, setInfo] = useState<string | null>(null);
  const [needsConfirm, setNeedsConfirm] = useState(false);
  const [resending, setResending] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Redirect away if already signed in
  useEffect(() => {
    let mounted = true;
    supabase.auth.getSession().then(({ data }) => {
      if (mounted && data.session) navigate({ to: postAuthTarget });
    });
    return () => {
      mounted = false;
    };
  }, [navigate, postAuthTarget]);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setInfo(null);
    setNeedsConfirm(false);
    setLoading(true);
    try {
      if (mode === "signup") {
        const signupRedirect = next
          ? `${window.location.origin}/auth?next=${encodeURIComponent(next)}`
          : window.location.origin;
        const { data, error } = await supabase.auth.signUp({
          email,
          password,
          options: {
            emailRedirectTo: signupRedirect,
            data: { display_name: displayName || email.split("@")[0] },
          },
        });
        if (error) throw error;
        if (isExistingAccountReply(data)) {
          setMode("signin");
          setPassword("");
          setInfo(EXISTING_ACCOUNT_MESSAGE);
          setNeedsConfirm(true);
          return;
        }
        // No session => email confirmation required. Do NOT navigate (the
        // protected gate would bounce the user back silently).
        if (!data.session) {
          setMode("signin");
          setPassword("");
          setInfo(
            "تم إنشاء حسابك ✅ — تحقّق من بريدك (وصندوق الـ Spam) واضغط رابط التفعيل، ثم ارجع للدخول من هنا.",
          );
          setNeedsConfirm(true);
          return;
        }
      } else {
        const { error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) throw error;
      }
      navigate({ to: postAuthTarget });
    } catch (caught: unknown) {
      const { message: msg, code } = parseAuthFailure(caught);
      console.error("auth error:", caught);
      if (code === "email_not_confirmed" || msg.includes("Email not confirmed")) {
        setNeedsConfirm(true);
        setError("بريدك لم يُؤكَّد بعد — افتح رسالة التفعيل ثم حاول الدخول.");
      } else if (code === "over_email_send_rate_limit" || msg.includes("rate limit")) {
        setError("تم إرسال الرابط مؤخراً، انتظر دقيقة قبل المحاولة مرة أخرى.");
      } else if (code === "weak_password" || msg.includes("weak") || msg.includes("pwned")) {
        setError("كلمة المرور ضعيفة جداً، استخدم كلمة أقوى (٨ أحرف+ مع أرقام ورموز).");
      } else if (mode === "signup" && isExistingAccountError(code, msg)) {
        setMode("signin");
        setPassword("");
        setInfo(EXISTING_ACCOUNT_MESSAGE);
        setNeedsConfirm(true);
      } else if (mode === "signup") {
        setError(SIGNUP_FAILED_MESSAGE);
      } else if (msg.includes("Invalid login")) {
        setError("بيانات الدخول غير صحيحة");
      } else if (msg.includes("Password should")) {
        setError("كلمة المرور قصيرة جداً (6 أحرف على الأقل)");
      } else {
        setError("حدث خطأ، حاول مرة أخرى");
      }
    } finally {
      setLoading(false);
    }
  };

  const onResendConfirm = async () => {
    if (!email) {
      setError("اكتب بريدك الإلكتروني أولاً");
      return;
    }
    setError(null);
    setInfo(null);
    setResending(true);
    try {
      const { error } = await supabase.auth.resend({
        type: "signup",
        email,
        options: { emailRedirectTo: window.location.origin },
      });
      if (error) throw error;
      setInfo("أرسلنا رسالة التفعيل من جديد، تحقّق من بريدك.");
    } catch (caught: unknown) {
      const { message: msg, code } = parseAuthFailure(caught);
      if (code === "over_email_send_rate_limit" || msg.includes("rate limit")) {
        setError("تم الإرسال مؤخراً، انتظر دقيقة قبل المحاولة.");
      } else {
        setError("تعذّر إعادة الإرسال، حاول لاحقاً.");
      }
    } finally {
      setResending(false);
    }
  };

  const onGoogle = async () => {
    setError(null);
    const googleRedirect = next
      ? `${window.location.origin}/auth?next=${encodeURIComponent(next)}`
      : window.location.origin;
    const result = await lovable.auth.signInWithOAuth("google", {
      redirect_uri: googleRedirect,
    });
    if (result.error) {
      setError("تعذّر الدخول عبر Google");
      return;
    }
    if (result.redirected) return;
    navigate({ to: postAuthTarget });
  };

  return (
    <div className="min-h-screen bg-background flex flex-col items-center px-5 py-10">
      <div className="w-full max-w-sm">
        <div className="flex items-center justify-start mb-4">
          <button
            onClick={() => navigate({ to: "/" })}
            aria-label="الرئيسية"
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="w-4 h-4 rotate-180" />
            <span>الرئيسية</span>
          </button>
        </div>
        <div className="text-center mb-6">
          <h1 className="text-3xl font-extrabold">تسجيل الدخول إلى منجز — دفتر محلك الذكي</h1>
          <p className="text-sm text-muted-foreground mt-1">إدارة المبيعات والديون والعهدة</p>
        </div>

        <div className="rounded-2xl bg-card border border-border p-5 shadow-sm">
          <div className="flex bg-muted rounded-xl p-1 mb-5 text-sm">
            <button
              onClick={() => setMode("signin")}
              className={`flex-1 py-2 rounded-lg ${mode === "signin" ? "bg-card font-semibold shadow-sm" : ""}`}
            >
              دخول
            </button>
            <button
              onClick={() => setMode("signup")}
              className={`flex-1 py-2 rounded-lg ${mode === "signup" ? "bg-card font-semibold shadow-sm" : ""}`}
            >
              حساب جديد
            </button>
          </div>

          <form onSubmit={onSubmit} className="space-y-3">
            {mode === "signup" && (
              <div>
                <label htmlFor="auth-name" className="block text-xs text-muted-foreground mb-1">
                  اسمك
                </label>
                <input
                  id="auth-name"
                  name="name"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
                  placeholder="مثال: أبو محمد"
                />
              </div>
            )}
            <div>
              <label htmlFor="auth-email" className="block text-xs text-muted-foreground mb-1">
                البريد الإلكتروني
              </label>
              <input
                id="auth-email"
                name="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
                dir="ltr"
                placeholder="name@example.com"
              />
            </div>
            <div>
              <label htmlFor="auth-password" className="block text-xs text-muted-foreground mb-1">
                كلمة المرور
              </label>
              <input
                id="auth-password"
                name="password"
                type="password"
                required
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full h-11 rounded-xl border border-input bg-background px-3 text-sm"
                dir="ltr"
                placeholder="••••••"
              />
            </div>

            {info && (
              <div className="text-xs text-emerald-700 bg-emerald-50 border border-emerald-200 rounded-lg px-3 py-2">
                {info}
              </div>
            )}
            {error && (
              <div className="text-xs text-destructive bg-destructive/10 rounded-lg px-3 py-2">
                {error}
              </div>
            )}
            {needsConfirm && (
              <button
                type="button"
                onClick={onResendConfirm}
                disabled={resending}
                className="w-full text-xs underline text-primary disabled:opacity-60"
              >
                {resending ? "..." : "إعادة إرسال رسالة التفعيل"}
              </button>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 rounded-xl bg-primary text-primary-foreground font-semibold disabled:opacity-60"
            >
              {loading ? "..." : mode === "signin" ? "دخول" : "إنشاء حساب"}
            </button>
          </form>

          <div className="flex items-center gap-3 my-4">
            <div className="flex-1 h-px bg-border" />
            <span className="text-[11px] text-muted-foreground">أو</span>
            <div className="flex-1 h-px bg-border" />
          </div>

          <button
            onClick={onGoogle}
            type="button"
            className="w-full h-11 rounded-xl border border-input bg-background font-medium text-sm flex items-center justify-center gap-2"
          >
            <GoogleIcon /> الدخول عبر Google
          </button>
        </div>

        <p className="text-center text-[11px] text-muted-foreground mt-5">
          <Link to="/guide" className="underline">
            دليل التطبيق
          </Link>
        </p>
      </div>
    </div>
  );
}

function GoogleIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24">
      <path
        fill="#4285F4"
        d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
      />
      <path
        fill="#34A853"
        d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.99.66-2.25 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
      />
      <path
        fill="#FBBC05"
        d="M5.84 14.1c-.22-.66-.35-1.36-.35-2.1s.13-1.44.35-2.1V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l3.66-2.83z"
      />
      <path
        fill="#EA4335"
        d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84C6.71 7.31 9.14 5.38 12 5.38z"
      />
    </svg>
  );
}
