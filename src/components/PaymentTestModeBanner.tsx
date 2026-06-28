import { getPaddleEnvironment } from "@/lib/paddle";

export function PaymentTestModeBanner() {
  if (getPaddleEnvironment() !== "sandbox") return null;
  return (
    <div
      dir="rtl"
      className="w-full bg-orange-100 border-b border-orange-300 px-4 py-2 text-center text-sm text-orange-800"
    >
      كل المدفوعات في المعاينة وضع تجريبي — لا يتم خصم مبالغ حقيقية.{" "}
      <a
        href="https://docs.lovable.dev/features/payments#test-and-live-environments"
        target="_blank"
        rel="noopener noreferrer"
        className="underline font-medium"
      >
        اقرأ المزيد
      </a>
    </div>
  );
}
