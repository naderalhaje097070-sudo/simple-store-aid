import { isQuantity } from "@/domain/finance/quantity";
import { getSaleTotal } from "@/domain/finance/invoice-selectors";

export const SALE_EVENT = "mongezz-sale-operation";
export const SALE_ENVIRONMENT = import.meta.env.VITE_SUPABASE_URL;
const PREFIX = "mongezz.sale-operation.v2:";
const LEGACY = "mongezz.pending-sale-idempotency.v1";
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;

export type SaleInput = {
  operationId: string;
  expectedActorId?: string;
  items: { productId: string; name: string; qty: number; price: number; cost: number }[];
  total: number;
  paid: number;
  customerId?: string;
  delivery: "direct" | "courier";
  courierId?: string;
  method: "cash" | "transfer";
};
export type SaleScope = { environment: string; tenantId: string; actorId: string };
export type CreatedSale = { orderId: string; number: string };
export type SaleRecord = {
  version: 2;
  scope: SaleScope;
  input: SaleInput;
  fingerprint: string;
  createdAt: number;
  status: "pending" | "completed";
  result?: CreatedSale;
};
export type SaleReply = {
  data: unknown;
  error: { message: string; code?: string } | null;
  status: number;
};
export class SaleOperationError extends Error {}
const unavailable = () =>
  new SaleOperationError("تعذّر حفظ هوية البيع بأمان. لم يبدأ بيع جديد؛ تحقّق من إعدادات المتصفح.");
const unresolved = () =>
  new SaleOperationError(
    "توجد عملية بيع لم تُحسم نتيجتها. استعد العملية المحفوظة قبل بدء بيع آخر.",
  );
export function saleErrorMessage(error: unknown): string {
  return error instanceof SaleOperationError
    ? error.message
    : "لم تتأكد نتيجة الحفظ. أعد المحاولة من العملية المحفوظة.";
}
export function newSaleOperationId(): string {
  if (!globalThis.crypto?.randomUUID) throw unavailable();
  return globalThis.crypto.randomUUID();
}
export function saleScope(environment: string, tenantId: string, actorId: string): SaleScope {
  const url = new URL(environment);
  if (
    !["http:", "https:"].includes(url.protocol) ||
    url.username ||
    url.password ||
    url.search ||
    url.hash ||
    !UUID.test(tenantId) ||
    !UUID.test(actorId)
  )
    throw unavailable();
  return { environment: url.href.replace(/\/$/, ""), tenantId, actorId };
}
export function saleStorageKey(scope: SaleScope): string {
  return PREFIX + JSON.stringify([scope.environment, scope.actorId, scope.tenantId]);
}
export function validateSaleInput(value: unknown): asserts value is SaleInput {
  if (!value || typeof value !== "object") throw unavailable();
  const input = value as SaleInput;
  if (
    typeof input.operationId !== "string" ||
    !UUID.test(input.operationId) ||
    (input.expectedActorId !== undefined &&
      (typeof input.expectedActorId !== "string" || !UUID.test(input.expectedActorId))) ||
    !Array.isArray(input.items) ||
    !input.items.length ||
    !input.items.every(
      (item) =>
        item &&
        typeof item === "object" &&
        typeof item.productId === "string" &&
        UUID.test(item.productId) &&
        typeof item.name === "string" &&
        isQuantity(item.qty) &&
        isQuantity(item.price) &&
        isQuantity(item.cost, true),
    ) ||
    !isQuantity(input.total) ||
    !isQuantity(input.paid, true) ||
    input.paid > input.total ||
    input.total !== getSaleTotal(input.items) ||
    !["cash", "transfer"].includes(input.method) ||
    !["direct", "courier"].includes(input.delivery) ||
    (input.customerId !== undefined &&
      (typeof input.customerId !== "string" || !UUID.test(input.customerId))) ||
    (input.courierId !== undefined &&
      (typeof input.courierId !== "string" || !UUID.test(input.courierId))) ||
    (input.delivery === "direct" && input.courierId !== undefined) ||
    (input.delivery === "courier" && !input.courierId)
  )
    throw new SaleOperationError("بيانات البيع غير صالحة. راجع الكميات والدفع.");
}
export function saleRequest(input: SaleInput) {
  validateSaleInput(input);
  return {
    p_idempotency_key: input.operationId,
    p_customer_id: input.customerId ?? null,
    p_delivery: input.delivery,
    p_courier_id: input.courierId ?? null,
    p_paid: input.paid,
    p_method: input.method,
    p_items: input.items.map((item) => ({ productId: item.productId, qty: item.qty })),
    p_courier_state:
      input.delivery === "direct"
        ? null
        : input.paid === 0
          ? ("pending" as const)
          : input.paid === input.total
            ? ("delivered_full" as const)
            : ("delivered_partial" as const),
  };
}
function fingerprint(input: SaleInput): string {
  return JSON.stringify({ ...saleRequest(input), p_idempotency_key: undefined });
}
function storage(): Storage {
  if (typeof window === "undefined") throw unavailable();
  // Old unscoped candidate data cannot safely be assigned to the current actor.
  if (window.sessionStorage.getItem(LEGACY) !== null) throw unresolved();
  return window.localStorage;
}
export function loadSale(scope: SaleScope): SaleRecord | null {
  try {
    const raw = storage().getItem(saleStorageKey(scope));
    if (raw === null) return null;
    const entry = JSON.parse(raw) as SaleRecord;
    validateSaleInput(entry.input);
    if (
      entry.version !== 2 ||
      JSON.stringify(entry.scope) !== JSON.stringify(scope) ||
      entry.fingerprint !== fingerprint(entry.input) ||
      (entry.input.expectedActorId !== undefined &&
        entry.input.expectedActorId !== scope.actorId) ||
      !Number.isFinite(entry.createdAt) ||
      entry.createdAt < 0 ||
      !["pending", "completed"].includes(entry.status) ||
      (entry.status === "completed" &&
        (!entry.result ||
          !UUID.test(entry.result.orderId) ||
          !/^[1-9]\d*$/.test(entry.result.number)))
    )
      throw unavailable();
    return entry;
  } catch (error) {
    if (error instanceof SaleOperationError && error.message === unresolved().message) throw error;
    throw unavailable();
  }
}
function save(entry: SaleRecord): void {
  const key = saleStorageKey(entry.scope),
    raw = JSON.stringify(entry);
  try {
    const store = storage();
    store.setItem(key, raw);
    if (store.getItem(key) !== raw) throw unavailable();
    window.dispatchEvent(new Event(SALE_EVENT));
  } catch {
    throw unavailable();
  }
}
function forgetFreshRollback(scope: SaleScope): void {
  try {
    const store = storage(),
      key = saleStorageKey(scope);
    store.removeItem(key);
    if (store.getItem(key) !== null) throw unavailable();
    window.dispatchEvent(new Event(SALE_EVENT));
  } catch {
    throw unavailable();
  }
}
export function validateSaleResult(data: unknown): CreatedSale {
  if (!data || typeof data !== "object") throw unresolved();
  const result = data as { success?: unknown; order_id?: unknown; number?: unknown };
  if (
    result.success !== true ||
    typeof result.order_id !== "string" ||
    !UUID.test(result.order_id) ||
    typeof result.number !== "number" ||
    !Number.isSafeInteger(result.number) ||
    result.number < 1
  )
    throw unresolved();
  return { orderId: result.order_id, number: String(result.number) };
}
const FIRST_ROLLBACK =
  /^(empty_items|invalid_item|invalid_paid|customer_not_found|courier_id_must_be_null_for_direct|courier_requires_courier|courier_not_found|product_not_found|product_inactive|insufficient_stock|paid_exceeds_total|customer_required_for_debt|invalid_paid_for_courier_state)(?::|$)/;

export async function executeSale(
  scope: SaleScope,
  input: SaleInput,
  send: (request: ReturnType<typeof saleRequest>) => PromiseLike<SaleReply>,
  verifyActor: () => Promise<void>,
  formatError: (error: unknown) => string,
): Promise<CreatedSale> {
  validateSaleInput(input);
  // Snapshot before awaiting the browser lock; caller mutations cannot alter retry.
  const snapshot: SaleInput = JSON.parse(JSON.stringify(input));
  if (typeof navigator === "undefined" || !navigator.locks) throw unavailable();
  return navigator.locks.request(saleStorageKey(scope), async () => {
    await verifyActor();
    const prior = loadSale(scope);
    const sameOperation = prior?.input.operationId === snapshot.operationId;
    if (
      (prior?.status === "pending" && !sameOperation) ||
      (sameOperation && prior.fingerprint !== fingerprint(snapshot))
    )
      throw unresolved();
    const entry: SaleRecord = {
      version: 2,
      scope,
      input: snapshot,
      fingerprint: fingerprint(snapshot),
      createdAt: sameOperation ? prior.createdAt : Date.now(),
      status: "pending",
    };
    save(entry);
    // A local receipt is never sufficient: all retries reach the server's key.
    const reply = await send(saleRequest(snapshot));
    if (reply.error) {
      // A later denial cannot rule out a prior committed-but-unseen attempt.
      if (
        !sameOperation &&
        reply.status >= 400 &&
        reply.status < 500 &&
        reply.error.code === "P0001" &&
        FIRST_ROLLBACK.test(reply.error.message)
      )
        forgetFreshRollback(scope);
      throw new SaleOperationError(formatError(reply.error));
    }
    if (reply.status < 200 || reply.status >= 300) throw unresolved();
    const result = validateSaleResult(reply.data);
    await verifyActor();
    save({ ...entry, status: "completed", result });
    return result;
  });
}
