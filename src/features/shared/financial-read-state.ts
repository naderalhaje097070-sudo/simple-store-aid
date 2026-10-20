export type FinancialRead = {
  hasData: boolean;
  complete: boolean;
  phase: "loading" | "error" | "refreshing" | "ready";
};

type ReadQuery = {
  data: unknown;
  status: "pending" | "error" | "success";
  fetchStatus: "fetching" | "paused" | "idle";
  isPlaceholderData: boolean;
};

function dataReadState(
  query: ReadQuery,
  tenantAvailable: boolean,
  tenantError: boolean,
  dataAvailable: boolean,
): FinancialRead {
  const hasData = tenantAvailable && dataAvailable && !query.isPlaceholderData;
  const complete =
    hasData && !tenantError && query.status === "success" && query.fetchStatus === "idle";
  const phase =
    tenantError || query.status === "error"
      ? "error"
      : complete
        ? "ready"
        : hasData
          ? "refreshing"
          : "loading";
  return { hasData, complete, phase };
}

// These hooks return whole arrays. A successful empty array is data; absence is not.
export function financialReadState(
  query: ReadQuery,
  tenantAvailable: boolean,
  tenantError: boolean,
): FinancialRead {
  return dataReadState(query, tenantAvailable, tenantError, Array.isArray(query.data));
}

export function tenantTimezoneReadState(
  query: ReadQuery,
  tenantAvailable: boolean,
  tenantError: boolean,
): FinancialRead {
  return dataReadState(
    query,
    tenantAvailable,
    tenantError,
    typeof query.data === "object" && query.data !== null && !Array.isArray(query.data),
  );
}

export function combineFinancialReads(reads: FinancialRead[]): FinancialRead {
  const hasData = reads.every((read) => read.hasData);
  const complete = reads.every((read) => read.complete);
  const phase = reads.some((read) => read.phase === "error")
    ? "error"
    : complete
      ? "ready"
      : hasData
        ? "refreshing"
        : "loading";
  return { hasData, complete, phase };
}

export function requireFinancialReads(reads: FinancialRead[]): void {
  if (!reads.every((read) => read.complete)) {
    throw new Error("أكمل تحديث البيانات المالية قبل تنفيذ هذه العملية.");
  }
}
