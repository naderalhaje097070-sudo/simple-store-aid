import { expect, test } from "bun:test";
import { rpcMessage } from "../../src/lib/db";

const GENERIC = "تعذّر إتمام العملية";

test("courier refusal codes from the server map to their Arabic messages", () => {
  const cases: Array<[string, string]> = [
    [
      "courier_custody_exceeds_remaining",
      "المبلغ أكبر من المتبقي على الفاتورة بعد ما دُفع في المتجر",
    ],
    ["invalid_transition", "لا يمكن نقل الطلب إلى هذه الحالة من حالته الحالية"],
    ["custody_cannot_decrease", "لا يمكن إنقاص المبلغ الذي في عهدة المندوب"],
  ];
  for (const [code, message] of cases) {
    // PostgREST error shape: the RAISE EXCEPTION text is the message.
    expect(rpcMessage({ message: code })).toBe(message);
    expect(rpcMessage(new Error(code))).toBe(message);
  }
});

test("the new codes do not shadow existing mappings or the generic fallback", () => {
  expect(rpcMessage({ message: "amount_exceeds_remaining" })).toBe(
    "المبلغ المدخل أكبر من المتبقّي على الفاتورة",
  );
  expect(rpcMessage({ message: "collected_exceeds_remaining" })).toBe(
    "المحصّل أكبر من المتبقّي على الفاتورة",
  );
  expect(rpcMessage({ message: "order_not_in_courier_custody" })).toBe(
    "هذه الفاتورة ليست ضمن عهدة المندوب",
  );
  expect(rpcMessage({ message: "invalid_paid" })).toBe("المبلغ المدفوع غير صحيح");
  expect(rpcMessage({ message: "something_unmapped" })).toBe(GENERIC);
  expect(rpcMessage(null)).toBe(GENERIC);
});
