import { saleScope, type SaleScope, type SaleReply } from "@/lib/sale-operation";

export const COLLECTION_EVENT = "mongezz-collection-operation";
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-8][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
export type CollectionInput = {
  operationId: string;
  expectedActorId: string;
  orderId: string;
  amount: number;
  method: "cash" | "transfer";
};
export type CollectionResult = {
  success: true;
  new_paid: number;
  status: "partial" | "paid" | "debt";
};
export type CollectionRecord = {
  version: 1;
  scope: SaleScope;
  input: CollectionInput;
  status: "pending" | "completed";
  result?: CollectionResult;
};
export class CollectionOperationError extends Error {}
const unavailable = () =>
  new CollectionOperationError("تعذّر حفظ هوية التحصيل بأمان. لم يبدأ تحصيل جديد.");
const unresolved = () =>
  new CollectionOperationError(
    "توجد عملية تحصيل لم تُحسم. استعد التحصيل المحفوظ قبل بدء دفعة جديدة.",
  );
export function collectionErrorMessage(error: unknown): string {
  return error instanceof CollectionOperationError
    ? error.message
    : "لم تتأكد نتيجة التحصيل. استعد العملية المحفوظة لإعادة المحاولة.";
}
export function newCollectionId(): string {
  if (!globalThis.crypto?.randomUUID) throw unavailable();
  return globalThis.crypto.randomUUID();
}
export function collectionKey(scope: SaleScope): string {
  const normalized = saleScope(scope.environment, scope.tenantId, scope.actorId);
  return (
    "mongezz.collection-operation.v1:" +
    JSON.stringify([normalized.environment, normalized.tenantId, normalized.actorId])
  );
}
export function collectionRequest(input: CollectionInput) {
  if (
    !input ||
    !UUID.test(input.operationId) ||
    !UUID.test(input.expectedActorId) ||
    !UUID.test(input.orderId) ||
    !Number.isFinite(input.amount) ||
    input.amount <= 0 ||
    !["cash", "transfer"].includes(input.method)
  )
    throw unavailable();
  return {
    p_idempotency_key: input.operationId,
    p_order_id: input.orderId,
    p_amount: input.amount,
    p_method: input.method,
  };
}
function result(data: unknown): CollectionResult {
  if (!data || typeof data !== "object") throw unresolved();
  const value = data as CollectionResult;
  if (
    value.success !== true ||
    !Number.isFinite(value.new_paid) ||
    value.new_paid < 0 ||
    !["partial", "paid", "debt"].includes(value.status)
  )
    throw unresolved();
  return { success: true, new_paid: value.new_paid, status: value.status };
}
export function loadCollection(scope: SaleScope): CollectionRecord | null {
  try {
    const raw = window.localStorage.getItem(collectionKey(scope));
    if (raw === null) return null;
    const record = JSON.parse(raw) as CollectionRecord;
    collectionRequest(record.input);
    if (
      record.version !== 1 ||
      JSON.stringify(record.scope) !== JSON.stringify(scope) ||
      record.input.expectedActorId !== scope.actorId ||
      !["pending", "completed"].includes(record.status)
    )
      throw unavailable();
    if (record.status === "completed") result(record.result);
    return record;
  } catch {
    throw unavailable();
  }
}
function save(record: CollectionRecord) {
  try {
    const key = collectionKey(record.scope),
      raw = JSON.stringify(record);
    window.localStorage.setItem(key, raw);
    if (window.localStorage.getItem(key) !== raw) throw unavailable();
    window.dispatchEvent(new Event(COLLECTION_EVENT));
  } catch {
    throw unavailable();
  }
}
function forget(scope: SaleScope) {
  try {
    const key = collectionKey(scope);
    window.localStorage.removeItem(key);
    if (window.localStorage.getItem(key) !== null) throw unavailable();
    window.dispatchEvent(new Event(COLLECTION_EVENT));
  } catch {
    throw unavailable();
  }
}
const FIRST_ROLLBACK =
  /^(invalid_amount|order_not_found|cannot_collect_returned_order|settle_courier_first|amount_exceeds_remaining)$/;
export async function executeCollection(
  scope: SaleScope,
  input: CollectionInput,
  send: (request: ReturnType<typeof collectionRequest>) => PromiseLike<SaleReply>,
  verifyActor: () => Promise<void>,
  formatError: (error: unknown) => string,
): Promise<CollectionResult> {
  collectionRequest(input);
  if (scope.actorId !== input.expectedActorId) throw unavailable();
  const snapshot: CollectionInput = JSON.parse(JSON.stringify(input));
  if (typeof navigator === "undefined" || !navigator.locks) throw unavailable();
  return navigator.locks.request(collectionKey(scope), async () => {
    await verifyActor();
    const prior = loadCollection(scope),
      same = prior?.input.operationId === snapshot.operationId;
    if (
      (prior?.status === "pending" && !same) ||
      (same &&
        JSON.stringify(collectionRequest(prior.input)) !==
          JSON.stringify(collectionRequest(snapshot)))
    )
      throw unresolved();
    const record: CollectionRecord = {
      version: 1,
      scope,
      input: snapshot,
      status: "pending",
    };
    save(record);
    const reply = await send(collectionRequest(snapshot));
    if (reply.error) {
      if (
        !same &&
        reply.status >= 400 &&
        reply.status < 500 &&
        reply.error.code === "P0001" &&
        FIRST_ROLLBACK.test(reply.error.message)
      )
        forget(scope);
      throw new CollectionOperationError(formatError(reply.error));
    }
    if (reply.status < 200 || reply.status >= 300) throw unresolved();
    const value = result(reply.data);
    await verifyActor();
    save({ ...record, status: "completed", result: value });
    return value;
  });
}
