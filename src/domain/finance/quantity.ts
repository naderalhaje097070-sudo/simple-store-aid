// Quantities use the existing order-item precision; money rules are separate.
export const MAX_QUANTITY = 9_999_999_999.99;
export const QUANTITY_ERROR = "أدخل كمية صالحة حتى منزلتين عشريتين";

export function parseQuantityText(raw: string): number | null {
  if (!/^(?:\d+(?:\.\d{0,2})?|\.\d{1,2})$/.test(raw.trim())) return null;
  const value = Number(raw);
  return Number.isFinite(value) && value <= MAX_QUANTITY ? value : null;
}

export function isQuantity(value: number, allowZero = false): boolean {
  return parseQuantityText(String(value)) === value && (allowZero ? value >= 0 : value > 0);
}

export function stepQuantity(value: number, wholeUnits: number): number {
  if (!isQuantity(value, true) || !Number.isInteger(wholeUnits)) throw new Error(QUANTITY_ERROR);
  return Math.max(0, Math.round(value * 100) + wholeUnits * 100) / 100;
}

export function sumQuantities(values: number[]): number {
  const units = values.reduce((sum, value) => {
    if (!isQuantity(value, true)) throw new Error(QUANTITY_ERROR);
    const next = sum + Math.round(value * 100);
    if (!Number.isSafeInteger(next)) throw new Error(QUANTITY_ERROR);
    return next;
  }, 0);
  return units / 100;
}
