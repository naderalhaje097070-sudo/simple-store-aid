// Recording React Query boundary only; native test uses the actual Supabase SDK.
export function useQuery<T>(options: T): T {
  return options;
}
export function useMutation<T>(options: {
  mutationFn: (value: T) => Promise<{ orderId: string; number: string }>;
}) {
  return { mutateAsync: options.mutationFn };
}
export function useQueryClient() {
  return { invalidateQueries() {} };
}
