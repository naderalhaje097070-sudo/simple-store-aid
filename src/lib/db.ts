import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";
import type { SupabaseClient } from "@supabase/supabase-js";
import type { Database, Json } from "@/integrations/supabase/types";

// Refine only JSON results and SQL-nullable arguments missing from generated
// types. Definitions: 20260627201534 (today/sale), 20260628105459
// (delete_product_safe), 20260704105413 (close_day), and the unchanged
// update_courier_order_state SQL contract. This is the same client and wire API.
type GeneratedRpcs = Database["public"]["Functions"];
type RpcResults = {
  get_tenant_today_estimate: {
    today: string;
    timezone: string;
    sales: number;
    collected: number;
    expenses: number;
    realized_profit: number;
  };
  delete_product_safe: { deleted?: boolean; archived?: boolean; used_in?: number };
  create_sale_with_items: { success: boolean; order_id: string; number: number };
};
type NullableRpcArguments = {
  create_sale_with_items: "p_customer_id" | "p_courier_id";
  close_day: "p_note";
  update_courier_order_state: "p_collected";
};
type ApplicationRpcs = {
  [Name in keyof GeneratedRpcs]: {
    Args: GeneratedRpcs[Name]["Args"] extends never
      ? never
      : {
          [Arg in keyof GeneratedRpcs[Name]["Args"]]: Name extends keyof NullableRpcArguments
            ? Arg extends NullableRpcArguments[Name]
              ? GeneratedRpcs[Name]["Args"][Arg] | null
              : GeneratedRpcs[Name]["Args"][Arg]
            : GeneratedRpcs[Name]["Args"][Arg];
        };
    Returns: Name extends keyof RpcResults ? RpcResults[Name] : GeneratedRpcs[Name]["Returns"];
  };
};
type ApplicationDatabase = Omit<Database, "public"> & {
  public: Omit<Database["public"], "Functions"> & { Functions: ApplicationRpcs };
};
const rpcClient = supabase as SupabaseClient<ApplicationDatabase>;

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

/* ---------- tenant settings ---------- */
export type TenantSettings = {
  id: string;
  name: string;
  timezone: string;
  business_type: string | null;
  trial_ends_at: string | null;
};
export function useTenant(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["tenant", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<TenantSettings | null> => {
      const { data, error } = await supabase
        .from("tenants")
        .select("id,name,timezone,business_type,trial_ends_at")
        .eq("id", tenantId!)
        .maybeSingle();
      if (error) throw error;
      if (!data) return null;
      return {
        id: data.id,
        name: data.name,
        timezone: data.timezone ?? "Africa/Tripoli",
        business_type: data.business_type ?? null,
        trial_ends_at: data.trial_ends_at,
      };
    },
  });
}

export function useUpdateTenantName(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (name: string) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("tenants").update({ name }).eq("id", tenantId);
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenant", tenantId] }),
  });
}

export function useUpdateTenantBusinessType(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (business_type: string | null) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("tenants").update({ business_type }).eq("id", tenantId);
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["tenant", tenantId] }),
  });
}

export function useUpdateTenantTimezone(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (timezone: string) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("tenants").update({ timezone }).eq("id", tenantId);
      if (error) throw error;
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["tenant", tenantId] });
      qc.invalidateQueries({ queryKey: ["today_estimate", tenantId] });
    },
  });
}

/* ---------- today helpers (tenant timezone) ---------- */
export function tenantTodayKey(timezone: string | null | undefined, at: Date = new Date()): string {
  const tz = timezone || "Africa/Tripoli";
  // en-CA returns YYYY-MM-DD
  return new Intl.DateTimeFormat("en-CA", { timeZone: tz }).format(at);
}

export function useTenantTodayEstimate(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["today_estimate", tenantId],
    enabled: !!tenantId,
    refetchInterval: 30_000,
    queryFn: async () => {
      const { data, error } = await rpcClient.rpc("get_tenant_today_estimate");
      if (error) throw error;
      if (data === null) throw new TypeError("get_tenant_today_estimate returned no result");
      const d = data;
      return {
        today: String(d.today),
        timezone: String(d.timezone),
        sales: Number(d.sales ?? 0),
        collected: Number(d.collected ?? 0),
        expenses: Number(d.expenses ?? 0),
        realizedProfit: Number(d.realized_profit ?? 0),
      };
    },
  });
}

/* ---------- my role ---------- */
// Aligned with database enum public.app_role
export type AppRole = "owner" | "staff";
export function useMyRole(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["my_role", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<AppRole | null> => {
      const { data: u } = await supabase.auth.getUser();
      if (!u.user) return null;
      const { data, error } = await supabase
        .from("user_roles")
        .select("role")
        .eq("tenant_id", tenantId!)
        .eq("user_id", u.user.id)
        .maybeSingle();
      if (error) throw error;
      return (data?.role as AppRole) ?? null;
    },
    staleTime: 60_000,
  });
}

/* ---------- friendly RPC error mapper ---------- */
function rpcMessage(err: unknown): string {
  const raw = String((err as { message?: unknown } | null | undefined)?.message ?? err ?? "");
  const map: Record<string, string> = {
    forbidden_tenant: "ليست لديك صلاحية على هذا المتجر",
    forbidden_role: "ليست لديك صلاحية لتنفيذ هذه العملية",
    empty_items: "يجب إضافة صنف واحد على الأقل",
    invalid_paid: "المبلغ المدفوع غير صحيح",
    invalid_amount: "المبلغ غير صحيح",
    paid_exceeds_total: "المبلغ المدفوع لا يمكن أن يكون أكبر من إجمالي الفاتورة",
    customer_required_for_debt: "يجب اختيار عميل لأن هناك مبلغًا متبقّيًا",
    courier_requires_customer_and_courier: "توصيل المندوب يتطلّب عميلًا ومندوبًا",
    insufficient_stock: "الكمية المتاحة في المخزون غير كافية",
    product_inactive: "أحد المنتجات موقوف عن البيع",
    product_not_found: "لم يتم العثور على المنتج",
    amount_exceeds_remaining: "المبلغ المدخل أكبر من المتبقّي على الفاتورة",
    courier_not_found: "المندوب غير موجود",
    order_not_in_courier_custody: "هذه الفاتورة ليست ضمن عهدة المندوب",
    collected_exceeds_remaining: "المحصّل أكبر من المتبقّي على الفاتورة",
    not_a_courier_order: "هذه الفاتورة ليست توصيلًا بمندوب",
    cannot_return_partially_paid_order: "لا يمكن إرجاع فاتورة تم تحصيل جزء منها",
    settle_courier_first: "يجب تسوية عهدة المندوب أولًا قبل تحصيل هذه الفاتورة",
    cannot_collect_returned_order: "لا يمكن تحصيل مبلغ على فاتورة مُرجَعة",
    cannot_delete_paid_order: "لا يمكن التراجع عن فاتورة مدفوعة أو محصّلة",
    cannot_delete_courier_with_collected_money: "لا يمكن حذف طلب مندوب حُصِّل منه مبلغ",
  };
  for (const key of Object.keys(map)) {
    if (raw.includes(key)) return map[key];
  }
  return "تعذّر إتمام العملية";
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
  is_discount: boolean;
};

export function useProducts(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["products", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBProduct[]> => {
      const { data, error } = await supabase
        .from("products")
        .select("id,name,price,cost,stock,sku,category,is_active,is_discount")
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        name: r.name,
        price: Number(r.price),
        cost: Number(r.cost),
        stock: Number(r.stock),
        lowAt: 3,
        sku: r.sku,
        category: r.category,
        is_active: r.is_active,
        is_discount: !!r.is_discount,
      }));
    },
  });
}

export function useAddProduct(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      name: string;
      price: number;
      cost: number;
      stock: number;
      is_discount: boolean;
    }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase.from("products").insert({
        tenant_id: tenantId,
        name: input.name,
        price: input.price,
        cost: input.cost,
        stock: input.stock,
        is_discount: input.is_discount,
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

export function useUpdateProduct(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      id: string;
      name: string;
      price: number;
      cost: number;
      stock: number;
      is_discount: boolean;
    }) => {
      const { error } = await supabase
        .from("products")
        .update({
          name: input.name,
          price: input.price,
          cost: input.cost,
          stock: input.stock,
          is_discount: input.is_discount,
        })
        .eq("id", input.id);
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["products", tenantId] }),
  });
}

export function useDeleteProduct(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (
      productId: string,
    ): Promise<{ deleted?: boolean; archived?: boolean; usedIn?: number }> => {
      const { data, error } = await rpcClient.rpc("delete_product_safe", {
        p_product_id: productId,
      });
      if (error) throw new Error(rpcMessage(error));
      const d = data;
      return { deleted: !!d?.deleted, archived: !!d?.archived, usedIn: Number(d?.used_in ?? 0) };
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["products", tenantId] });
    },
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
      return (data ?? []).map((r) => ({
        id: r.id,
        name: r.name,
        phone: r.phone ?? undefined,
      }));
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

/* ---------- couriers ---------- */
export type DBCourier = { id: string; name: string; phone?: string };

export function useCouriers(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["couriers", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBCourier[]> => {
      const { data, error } = await supabase
        .from("couriers")
        .select("id,name,phone")
        .eq("is_active", true)
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        name: r.name,
        phone: r.phone ?? undefined,
      }));
    },
  });
}

export function useAddCourier(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { name: string; phone?: string }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await supabase
        .from("couriers")
        .insert({ tenant_id: tenantId, name: input.name, phone: input.phone ?? null });
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["couriers", tenantId] }),
  });
}

/* ---------- invoices (orders + items) ---------- */
export type DBInvoiceItem = {
  productId: Database["public"]["Tables"]["order_items"]["Row"]["product_id"];
  name: string;
  qty: number;
  price: number;
  cost: number;
};
export type DBInvoice = {
  id: string;
  number: string;
  items: DBInvoiceItem[];
  total: number;
  paid: number;
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
  new Date(iso).toLocaleTimeString("ar-LY", { hour: "2-digit", minute: "2-digit", hour12: false });

export function useInvoices(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["invoices", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBInvoice[]> => {
      const { data, error } = await supabase
        .from("orders")
        .select(
          "id,number,tenant_number,total,paid,customer_id,status,delivery,courier_id,courier_state,collected_by_courier,created_at,order_items(product_id,name,qty,unit_price,unit_cost)",
        )
        .order("created_at", { ascending: false });
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        number: String(r.tenant_number ?? r.number),
        total: Number(r.total),
        paid: Number(r.paid),
        customerId: r.customer_id ?? undefined,
        delivery: r.delivery,
        courierId: r.courier_id ?? undefined,
        status: r.status,
        courierState: r.courier_state ?? undefined,
        collectedByCourier: Number(r.collected_by_courier ?? 0),
        time: fmtTime(r.created_at),
        createdAt: r.created_at,
        items: (r.order_items ?? []).map((it) => ({
          productId: it.product_id,
          name: it.name,
          qty: Number(it.qty),
          price: Number(it.unit_price),
          cost: Number(it.unit_cost),
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
  createdAt: string;
};

export function usePayments(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["payments", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBPayment[]> => {
      const { data, error } = await supabase
        .from("payments")
        .select(
          "id,kind,method,amount,order_id,customer_id,courier_id,created_at,orders(number,tenant_number)",
        )
        .order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []).map((r): DBPayment => {
        const kind = r.kind === "courier_settlement" ? "settlement" : r.kind;
        const method = r.kind === "courier_settlement" ? "settlement" : r.method;
        const tnum = r.orders?.tenant_number ?? r.orders?.number;
        return {
          id: r.id,
          kind,
          method,
          amount: Number(r.amount),
          invoiceId: r.order_id ?? undefined,
          invoiceNumber: tnum != null ? String(tnum) : undefined,
          customerId: r.customer_id ?? undefined,
          courierId: r.courier_id ?? undefined,
          time: fmtTime(r.created_at),
          createdAt: r.created_at,
        };
      });
    },
  });
}

/* ---------- expenses ---------- */
export type DBExpense = {
  id: string;
  type: string;
  amount: number;
  method: "cash" | "transfer";
  time: string;
  createdAt: string;
  note?: string;
};

export function useExpenses(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["expenses", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBExpense[]> => {
      const { data, error } = await supabase
        .from("expenses")
        .select("id,type,amount,method,note,created_at")
        .order("created_at", { ascending: true });
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        type: r.type,
        amount: Number(r.amount),
        method: r.method,
        note: r.note ?? undefined,
        time: fmtTime(r.created_at),
        createdAt: r.created_at,
      }));
    },
  });
}

export function useAddExpense(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      type: string;
      amount: number;
      method: "cash" | "transfer";
      note?: string;
    }) => {
      if (!tenantId) throw new Error("no tenant");
      const { data: u } = await supabase.auth.getUser();
      const { error } = await supabase.from("expenses").insert({
        tenant_id: tenantId,
        type: input.type,
        amount: input.amount,
        method: input.method,
        note: input.note ?? null,
        created_by: u.user?.id ?? null,
      });
      if (error) throw error;
    },
    onSuccess: () => qc.invalidateQueries({ queryKey: ["expenses", tenantId] }),
  });
}

/* ---------- sales / debt / settlement / undo ---------- */

export type CreateSaleInput = {
  items: { productId: string; name: string; qty: number; price: number; cost: number }[];
  total: number;
  paid: number;
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
      const { data, error } = await rpcClient.rpc("create_sale_with_items", {
        p_customer_id: input.customerId ?? null,
        p_delivery: input.delivery,
        p_courier_id: input.courierId ?? null,
        p_paid: input.paid,
        p_method: input.method,
        p_items: input.items.map((it) => ({ productId: it.productId, qty: it.qty })),
      });
      if (error) throw new Error(rpcMessage(error));
      if (data === null) throw new TypeError("create_sale_with_items returned no result");
      const out = data;
      return { orderId: out.order_id, number: String(out.number) };
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
      const { error } = await rpcClient.rpc("delete_order_with_restore_stock", {
        p_order_id: orderId,
      });
      if (error) throw new Error(rpcMessage(error));
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
    mutationFn: async (input: {
      orderId: string;
      customerId?: string;
      amount: number;
      method: "cash" | "transfer";
    }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await rpcClient.rpc("collect_order_debt", {
        p_order_id: input.orderId,
        p_amount: input.amount,
        p_method: input.method,
      });
      if (error) throw new Error(rpcMessage(error));
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
    // Input keeps `orders[]` for backwards compatibility with current callers,
    // but only order ids are sent to the RPC. The settled amount is derived
    // server-side from each order's stored collected_by_courier.
    mutationFn: async (input: {
      courierId: string;
      orders: { id: string; customerId?: string; collected?: number }[];
    }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await rpcClient.rpc("settle_courier_orders", {
        p_courier_id: input.courierId,
        p_order_ids: input.orders.map((o) => o.id),
      });
      if (error) throw new Error(rpcMessage(error));
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["payments", tenantId] });
      qc.invalidateQueries({ queryKey: ["today_estimate", tenantId] });
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
      const { error } = await rpcClient.rpc("update_courier_order_state", {
        p_order_id: input.orderId,
        p_state: input.state,
        p_collected: input.collected ?? null,
      });
      if (error) throw new Error(rpcMessage(error));
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["invoices", tenantId] });
      qc.invalidateQueries({ queryKey: ["products", tenantId] });
    },
  });
}

/* ---------- day close snapshots ---------- */
export type DBDayClose = {
  id: string;
  closedFor: string;
  sales: number;
  collected: number;
  expenses: number;
  realizedProfit: number;
  customerDebts: number;
  unsettledCustody: number;
  note?: string;
  createdAt: string;
};

export function useDayCloses(tenantId: string | null | undefined) {
  return useQuery({
    queryKey: ["day_closes", tenantId],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBDayClose[]> => {
      const { data, error } = await supabase
        .from("day_closes")
        .select(
          "id,closed_for,sales,collected,expenses,realized_profit,customer_debts,unsettled_custody,note,created_at",
        )
        .order("closed_for", { ascending: false })
        .limit(30);
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        closedFor: r.closed_for,
        sales: Number(r.sales),
        collected: Number(r.collected),
        expenses: Number(r.expenses),
        realizedProfit: Number(r.realized_profit),
        customerDebts: Number(r.customer_debts),
        unsettledCustody: Number(r.unsettled_custody),
        note: r.note ?? undefined,
        createdAt: r.created_at,
      }));
    },
  });
}

export function useCloseDay(tenantId: string | null | undefined) {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: async (input: { note?: string }) => {
      if (!tenantId) throw new Error("no tenant");
      const { error } = await rpcClient.rpc("close_day", { p_note: input.note ?? null });
      if (error) throw new Error(rpcMessage(error));
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["day_closes", tenantId] });
      qc.invalidateQueries({ queryKey: ["today_estimate", tenantId] });
    },
  });
}

/* ---------- financial audit log (owner only) ---------- */
export type DBAuditEntry = {
  id: string;
  action: "INSERT" | "UPDATE" | "DELETE" | string;
  entityType: string;
  entityId: string | null;
  before: Json;
  after: Json;
  userId: string | null;
  createdAt: string;
};

export function useFinancialAuditLog(tenantId: string | null | undefined, limit = 100) {
  return useQuery({
    queryKey: ["fin_audit", tenantId, limit],
    enabled: !!tenantId,
    queryFn: async (): Promise<DBAuditEntry[]> => {
      const { data, error } = await supabase
        .from("financial_audit_log")
        .select("id,action,entity_type,entity_id,before,after,user_id,created_at")
        .order("created_at", { ascending: false })
        .limit(limit);
      if (error) throw error;
      return (data ?? []).map((r) => ({
        id: r.id,
        action: r.action,
        entityType: r.entity_type,
        entityId: r.entity_id,
        before: r.before,
        after: r.after,
        userId: r.user_id,
        createdAt: r.created_at,
      }));
    },
  });
}
