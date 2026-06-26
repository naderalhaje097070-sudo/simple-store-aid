import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

/* ---------- tenant ---------- */
export function useTenantId() {
  return useQuery({
    queryKey: ["tenant_id"],
    queryFn: async () => {
      const { data: u } = await supabase.auth.getUser();
      if (!u.user) return null;
      const { data, error } = await supabase
        .from("profiles")
        .select("tenant_id")
        .eq("id", u.user.id)
        .maybeSingle();
      if (error) throw error;
      return data?.tenant_id ?? null;
    },
    staleTime: 60_000,
  });
}

/* ---------- products ---------- */
export type DBProduct = {
  id: string;
  name: string;
  price: number;
  cost: number;
  stock: number;
  lowAt: number;
  sku: string | null;
  category: string | null;
  is_active: boolean;
};

export function useProducts(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["products", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBProduct[]> => {
      const { data, error } = await supabase
        .from("products")
        .select("id,name,price,cost,stock,sku,category,is_active")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r: any) => ({
        id: r.id,
        name: r.name,
        price: Number(r.price),
        cost: Number(r.cost),
        stock: Number(r.stock),
        lowAt: 3, // local default until column added
        sku: r.sku,
        category: r.category,
        is_active: r.is_active,
      }));
    },
  });
}

export function useAddProduct(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string; price: number; cost: number; stock: number }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("products").insert({
        tenant_id: tenantId,
        name: input.name,
        price: input.price,
        cost: input.cost,
        stock: input.stock,
      });
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products", tenantId] }),
  });
}

export function useUpdateProductActive(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { id: string; is_active: boolean }) => {
      const { error } = await supabase
        .from("products")
        .update({ is_active: input.is_active })
        .eq("id", input.id);
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products", tenantId] }),
  });
}

/* ---------- customers ---------- */
export type DBCustomer = { id: string; name: string; phone?: string };

export function useCustomers(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["customers", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBCustomer[]> => {
      const { data, error } = await supabase
        .from("customers")
        .select("id,name,phone")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r: any) => ({ id: r.id, name: r.name, phone: r.phone ?? undefined }));
    },
  });
}

export function useAddCustomer(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string; phone?: string }): Promise<DBCustomer> => {
      if (!tenantId) throw new Error("no tenant");
      const { data, error } = await supabase
        .from("customers")
        .insert({ tenant_id: tenantId, name: input.name, phone: input.phone ?? null })
        .select("id,name,phone")
        .single();
      if (error) throw error;
      return { id: data.id, name: data.name, phone: data.phone ?? undefined };
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["customers", tenantId] }),
  });
}

/* ---------- expenses ---------- */
export type DBExpense = {
  id: string;
  type: string;
  amount: number;
  method: "cash" | "transfer";
  time: string;
  note?: string;
};

// Note: Phase 2 keeps expenses in local state alongside invoices/payments.
// A dedicated expenses table will land with Phase 3 financial persistence.
