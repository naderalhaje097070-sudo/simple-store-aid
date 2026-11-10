// Sign-up and resend messages that never reveal whether an email has an account.
// Observed on a local GoTrue v2.188.1 with email confirmations on (2026-11-10):
//   - sign-up, new email:                 200, user with 1 identity, no session
//   - sign-up, existing unconfirmed:      200, the same shape
//   - sign-up, existing confirmed:        422 code "user_already_exists"
//   - resend, confirmed / none / pending: 200 {} in all three cases
// GoTrue's enumeration protection may also answer an existing email with a
// success-shaped user that has no identities (documented, not observed here).
// The screen shows one neutral message and one state for all of these, so it
// never confirms that an account exists, nor that an email was sent.
// Note: the 422 itself is visible to anyone calling the API directly; this keeps
// the app's own screen from adding to that, it does not change the server.

export const SIGNUP_NEUTRAL_MESSAGE =
  "إذا كان هذا البريد غير مسجّل، فقد طلبنا إرسال رابط التفعيل إليه — افحص بريدك وصندوق Spam ثم سجّل الدخول. وإذا كان لديك حساب بهذا البريد، فسجّل الدخول بكلمة المرور.";

export const RESEND_NEUTRAL_MESSAGE =
  "إذا كان لهذا البريد حساب لم يُفعَّل بعد، فقد طلبنا إرسال رسالة التفعيل من جديد. افحص بريدك وصندوق Spam.";

export const SIGNUP_FAILED_MESSAGE = "تعذّر إنشاء الحساب الآن. تحقّق من الاتصال وحاول مرة أخرى.";

export function isExistingAccountError(code: string, message: string): boolean {
  return (
    code === "user_already_exists" ||
    code === "email_exists" ||
    /already (been )?registered/i.test(message)
  );
}
