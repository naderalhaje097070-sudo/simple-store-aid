// Classifies a sign-up attempt for an email that already has an account.
// - HTTP 422 with code "user_already_exists" (or "email_exists"): observed on a
//   local GoTrue v2.188.1 for a confirmed email, with confirmations on and off.
// - With email-enumeration protection, a success-shaped reply whose user has no
//   identities and no session (documented GoTrue behaviour; not observed here).
// Both mean "this email is already registered"; neither means "account created".

export const EXISTING_ACCOUNT_MESSAGE =
  "هذا البريد مسجّل مسبقًا. سجّل الدخول بكلمة المرور، وإن لم تكن فعّلت الحساب فاستخدم «إعادة إرسال رسالة التفعيل».";

export const SIGNUP_FAILED_MESSAGE = "تعذّر إنشاء الحساب الآن. تحقّق من الاتصال وحاول مرة أخرى.";

type SignUpReply = {
  user?: { identities?: unknown[] | null } | null;
  session?: unknown;
} | null;

export function isExistingAccountError(code: string, message: string): boolean {
  return (
    code === "user_already_exists" ||
    code === "email_exists" ||
    /already (been )?registered/i.test(message)
  );
}

export function isExistingAccountReply(data: SignUpReply): boolean {
  const identities = data?.user?.identities;
  return (
    Boolean(data?.user) && !data?.session && Array.isArray(identities) && identities.length === 0
  );
}
