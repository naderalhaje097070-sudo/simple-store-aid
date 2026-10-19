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

// These hooks return whole arrays. A successful empty array is data; absence is not.
export function financialReadState(
  query: ReadQuery,
  tenantAvailable: boolean,
  tenantError: boolean,
): FinancialRead {
  const hasData = tenantAvailable && Array.isArray(query.data) && !query.isPlaceholderData;
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

export function requireFinancialReads(reads: FinancialRead[]): void {
  if (!reads.every((read) => read.complete)) {
    throw new Error("أكمل تحديث البيانات المالية قبل تنفيذ هذه العملية.");
  }
}
