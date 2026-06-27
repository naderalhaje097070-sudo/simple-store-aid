export const BUSINESS_TYPES = [
  { value: "grocery", label: "بقالة / سوبر ماركت" },
  { value: "clothing", label: "ملابس وأقمشة" },
  { value: "electronics", label: "إلكترونيات وموبايلات" },
  { value: "cosmetics", label: "مستحضرات تجميل وعطور" },
  { value: "jewelry", label: "مجوهرات" },
  { value: "other", label: "أخرى" },
] as const;

export type BusinessType = (typeof BUSINESS_TYPES)[number]["value"];

export function businessTypeLabel(value: string | null | undefined): string {
  if (!value) return "غير محدد";
  return BUSINESS_TYPES.find(b => b.value === value)?.label ?? value;
}
