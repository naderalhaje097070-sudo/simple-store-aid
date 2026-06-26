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
  id: string; name: string; price: number; cost: number;
  stock: number; lowAt: number; sku: string | null;
  category: string | null; is_active: boolean;
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
        id: r.id, name: r.name, price: Number(r.price), cost: Number(r.cost),
        stock: Number(r.stock), lowAt: 3, sku: r.sku, category: r.category, is_active: r.is_active,
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
        tenant_id: tenantId, name: input.name, price: input.price, cost: input.cost, stock: input.stock,
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
      const { error } = await supabase.from("products").update({ is_active: input.is_active }).eq("id", input.id);
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
      const { data, error } = await supabase.from("customers").select("id,name,phone").order("created_at", { ascending: false });
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
        .select("id,name,phone").single();
      if (error) throw error;
      return { id: data.id, name: data.name, phone: data.phone ?? undefined };
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["customers", tenantId] }),
  });
}

/* ---------- couriers ---------- */
export type DBCourier = { id: string; name: string; phone?: string };

export function useCouriers(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["couriers", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBCourier[]> => {
      const { data, error } = await supabase.from("couriers").select("id,name,phone").eq("is_active", true).order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r: any) => ({ id: r.id, name: r.name, phone: r.phone ?? undefined }));
    },
  });
}

export function useAddCourier(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string; phone?: string }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("couriers").insert({ tenant_id: tenantId, name: input.name, phone: input.phone ?? null });
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["couriers", tenantId] }),
  });
}

/* ---------- invoices (orders + items) ---------- */
export type DBInvoiceItem = { productId: string; name: string; qty: number; price: number; cost: number };
export type DBInvoice = {
  id: string; number: string;
  items: DBInvoiceItem[];
  total: number; paid: number;
  customerId?: string;
  delivery: "direct" | "courier";
  courierId?: string;
  status: "paid" | "partial" | "debt";
  courierState?: "pending" | "delivered_none" | "delivered_partial" | "delivered_full" | "returned";
  collectedByCourier?: number;
  time: string;
  createdAt: string;
};

const fmtTime = (iso: string) =>
  new Date(iso).toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit", hour12: false });

export function useInvoices(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["invoices", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBInvoice[]> => {
      const { data, error } = await supabase
        .from("orders")
        .select("id,number,total,paid,customer_id,status,delivery,courier_id,courier_state,collected_by_courier,created_at,order_items(product_id,name,qty,unit_price,unit_cost)")
        .order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []).map((r: any) => ({
        id: r.id, number: String(r.number),
        total: Number(r.total), paid: Number(r.paid),
        customerId: r.customer_id ?? undefined,
        delivery: r.delivery,
        courierId: r.courier_id ?? undefined,
        status: r.status,
        courierState: r.courier_state ?? undefined,
        collectedByCourier: Number(r.collected_by_courier ?? 0),
        time: fmtTime(r.created_at),
        createdAt: r.created_at,
        items: (r.order_items ?? []).map((it: any) => ({
          productId: it.product_id, name: it.name,
          qty: Number(it.qty), price: Number(it.unit_price), cost: Number(it.unit_cost),
        })),
      }));
    },
  });
}

/* ---------- payments ---------- */
export type DBPayment = {
  id: string;
  kind: "sale" | "debt_collection" | "settlement";
  method: "cash" | "transfer" | "settlement";
  amount: number;
  invoiceId?: string;
  invoiceNumber?: string;
  customerId?: string;
  courierId?: string;
  time: string;
};

export function usePayments(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["payments", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBPayment[]> => {
      const { data, error } = await supabase
        .from("payments")
        .select("id,kind,method,amount,order_id,customer_id,courier_id,created_at,orders(number)")
        .order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []).map((r: any) => {
        const kind = r.kind === "courier_settlement" ? "settlement" : r.kind;
        const method = r.kind === "courier_settlement" ? "settlement" : r.method;
        return {
          id: r.id, kind, method,
          amount: Number(r.amount),
          invoiceId: r.order_id ?? undefined,
          invoiceNumber: r.orders?.number != null ? String(r.orders.number) : undefined,
          customerId: r.customer_id ?? undefined,
          courierId: r.courier_id ?? undefined,
          time: fmtTime(r.created_at),
        };
      });
    },
  });
}

/* ---------- expenses ---------- */
export type DBExpense = { id: string; type: string; amount: number; method: "cash" | "transfer"; time: string; note?: string };

export function useExpenses(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["expenses", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBExpense[]> => {
      const { data, error } = await supabase.from("expenses").select("id,type,amount,method,note,created_at").order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []).map((r: any) => ({
        id: r.id, type: r.type, amount: Number(r.amount), method: r.method, note: r.note ?? undefined, time: fmtTime(r.created_at),
      }));
    },
  });
}

export function useAddExpense(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { type: string; amount: number; method: "cash" | "transfer"; note?: string }) => {
      if (!tenantId) throw new Error("no tenant");
      const { data: u } = await supabase.auth.getUser();
      const { error } = await supabase.from("expenses").insert({
        tenant_id: tenantId, type: input.type, amount: input.amount, method: input.method,
        note: input.note ?? null, created_by: u.user?.id ?? null,
      });
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["expenses", tenantId] }),
  });
}

/* ---------- sales / debt / settlement / undo ---------- */
async function nextOrderNumber(tenantId: string): Promise<number> {
  const { data, error } = await supabase
    .from("orders").select("number").eq("tenant_id", tenantId)
    .order("number", { ascending: false }).limit(1).maybeSingle();
  if (error) throw error;
  return (data?.number ?? 1040) + 1;
}

export type CreateSaleInput = {
  items: { productId: string; name: string; qty: number; price: number; cost: number }[];
  total: number; paid: number;
  customerId?: string;
  delivery: "direct" | "courier";
  courierId?: string;
  method: "cash" | "transfer";
};

export function useCreateSale(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: CreateSaleInput): Promise<{ orderId: string; number: string }> => {
      if (!tenantId) throw new Error("no tenant");
      const { data: u } = await supabase.auth.getUser();
      const number = await nextOrderNumber(tenantId);
      const status: "paid" | "partial" | "debt" = input.paid >= input.total ? "paid" : input.paid > 0 ? "partial" : "debt";
      const { data: order, error } = await supabase.from("orders").insert({
        tenant_id: tenantId, number, total: input.total, paid: input.paid,
        customer_id: input.customerId ?? null, status,
        delivery: input.delivery, courier_id: input.courierId ?? null,
        courier_state: input.delivery === "courier" ? "pending" : null,
        collected_by_courier: 0, created_by: u.user?.id ?? null,
      }).select("id,number").single();
      if (error) throw error;

      const itemsRows = input.items.map(it => ({
        tenant_id: tenantId, order_id: order.id, product_id: it.productId,
        name: it.name, qty: it.qty, unit_price: it.price, unit_cost: it.cost,
      }));
      const { error: itemsErr } = await supabase.from("order_items").insert(itemsRows);
      if (itemsErr) throw itemsErr;

      // decrement stock
      for (const it of input.items) {
        const { data: prow } = await supabase.from("products").select("stock").eq("id", it.productId).maybeSingle();
        if (prow) {
          await supabase.from("products").update({ stock: Math.max(0, Number(prow.stock) - it.qty) }).eq("id", it.productId);
        }
      }

      if (input.delivery === "direct" && input.paid > 0) {
        const { error: payErr } = await supabase.from("payments").insert({
          tenant_id: tenantId, kind: "sale", method: input.method, amount: input.paid,
          order_id: order.id, customer_id: input.customerId ?? null, created_by: u.user?.id ?? null,
        });
        if (payErr) throw payErr;
      }
      return { orderId: order.id, number: String(order.number) };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["payments", tenantId] });
      qc.invalidateQueries({ queryKey: ["products", tenantId] });
    },
  });
}

export function useDeleteInvoice(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (orderId: string) => {
      // restore stock
      const { data: items } = await supabase.from("order_items").select("product_id,qty").eq("order_id", orderId);
      for (const it of items ?? []) {
        if (!it.product_id) continue;
        const { data: prow } = await supabase.from("products").select("stock").eq("id", it.product_id).maybeSingle();
        if (prow) await supabase.from("products").update({ stock: Number(prow.stock) + Number(it.qty) }).eq("id", it.product_id);
      }
      await supabase.from("payments").delete().eq("order_id", orderId);
      await supabase.from("order_items").delete().eq("order_id", orderId);
      const { error } = await supabase.from("orders").delete().eq("id", orderId);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["payments", tenantId] });
      qc.invalidateQueries({ queryKey: ["products", tenantId] });
    },
  });
}

export function useCollectDebt(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { orderId: string; customerId?: string; amount: number; method: "cash" | "transfer" }) => {
      if (!tenantId) throw new Error("no tenant");
      const { data: u } = await supabase.auth.getUser();
      const { data: order } = await supabase.from("orders").select("total,paid").eq("id", input.orderId).maybeSingle();
      if (!order) throw new Error("order not found");
      const newPaid = Math.min(Number(order.total), Number(order.paid) + input.amount);
      const status: "paid" | "partial" | "debt" = newPaid >= Number(order.total) ? "paid" : newPaid > 0 ? "partial" : "debt";
      await supabase.from("orders").update({ paid: newPaid, status }).eq("id", input.orderId);
      const { error } = await supabase.from("payments").insert({
        tenant_id: tenantId, kind: "debt_collection", method: input.method, amount: input.amount,
        order_id: input.orderId, customer_id: input.customerId ?? null, created_by: u.user?.id ?? null,
      });
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["payments", tenantId] });
    },
  });
}

export function useSettleCourier(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { courierId: string; orders: { id: string; customerId?: string; collected: number }[] }) => {
      if (!tenantId) throw new Error("no tenant");
      const { data: u } = await supabase.auth.getUser();
      for (const o of input.orders) {
        if (o.collected <= 0) continue;
        const { data: row } = await supabase.from("orders").select("total,paid").eq("id", o.id).maybeSingle();
        if (!row) continue;
        const newPaid = Math.min(Number(row.total), Number(row.paid) + o.collected);
        const status: "paid" | "partial" | "debt" = newPaid >= Number(row.total) ? "paid" : newPaid > 0 ? "partial" : "debt";
        await supabase.from("orders").update({
          paid: newPaid, status, delivery: "direct", courier_id: null,
          courier_state: null, collected_by_courier: 0,
        }).eq("id", o.id);
        await supabase.from("payments").insert({
          tenant_id: tenantId, kind: "courier_settlement", method: "cash",
          amount: o.collected, order_id: o.id, customer_id: o.customerId ?? null,
          courier_id: input.courierId, created_by: u.user?.id ?? null,
        });
      }
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["payments", tenantId] });
    },
  });
}

export function useUpdateCourierState(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      orderId: string;
      state: "delivered_full" | "delivered_partial" | "delivered_none" | "returned" | "pending";
      collected?: number;
    }) => {
      if (!tenantId) throw new Error("no tenant");
      const { data: row } = await supabase.from("orders").select("total").eq("id", input.orderId).maybeSingle();
      if (!row) throw new Error("order not found");
      const total = Number(row.total);
      let collected = 0;
      if (input.state === "delivered_full") collected = total;
      else if (input.state === "delivered_partial") collected = Math.max(0, Math.min(total, input.collected ?? 0));
      else collected = 0;
      const { error } = await supabase.from("orders").update({
        courier_state: input.state,
        collected_by_courier: collected,
      }).eq("id", input.orderId);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
    },
  });
}
