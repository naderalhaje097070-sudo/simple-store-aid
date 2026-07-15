import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { supabase } from "@/integrations/supabase/client";

export type PendingSettlementRequest = {
  id: string;
  amount: number;
  createdAt: string;
};

export type CourierAccount = {
  courierId: string;
  name: string;
  phone?: string;
  isActive: boolean;
  userId?: string;
  email?: string;
  displayName?: string;
  custody: number;
  pendingOrders: number;
  pendingRequest?: PendingSettlementRequest;
};

export type EmployeePortalOrder = {
  id: string;
  number: string;
  total: number;
  paid: number;
  courierState: "pending" | "delivered_full" | "delivered_partial" | "delivered_none";
  collectedByCourier: number;
  createdAt: string;
  customer?: { name: string; phone?: string };
  items: { name: string; qty: number; unitPrice: number }[];
};

export type EmployeePortal = {
  courier: { id: string; name: string; phone?: string };
  tenantName: string;
  custody: number;
  pendingOrders: number;
  orders: EmployeePortalOrder[];
  settlementRequests: {
    id: string;
    amount: number;
    status: "pending" | "approved" | "rejected" | "cancelled";
    createdAt: string;
    resolvedAt?: string;
  }[];
};

function employeeRpcMessage(error: unknown): string {
  const raw = String((error as { message?: string })?.message ?? error ?? "");
  const messages: Record<string, string> = {
    forbidden_role: "هذه العملية متاحة لصاحب المحل فقط",
    courier_not_found: "المندوب غير موجود",
    employee_email_required: "اكتب بريد الموظف",
    employee_account_not_found: "يجب أن ينشئ الموظف حسابًا في منجز بهذا البريد أولًا",
    employee_profile_not_found: "حساب الموظف غير مكتمل",
    employee_already_in_other_tenant: "هذا الحساب مرتبط بمتجر آخر",
    employee_already_linked: "هذا الحساب مرتبط بمندوب آخر",
    employee_is_tenant_owner: "لا يمكن ربط حساب صاحب متجر كموظف",
    owner_cannot_be_employee: "لا يمكن ربط حساب المالك كمندوب",
    employee_account_disabled: "حساب الموظف غير مفعّل",
    order_not_assigned_to_employee: "هذا الطلب غير مسند إلى حسابك",
    invalid_partial_collection: "التحصيل الجزئي يجب أن يكون أكبر من صفر وأقل من المتبقي",
    cannot_return_partially_paid_order: "لا يمكن إرجاع طلب يحتوي على مبلغ محصّل",
    no_custody_to_settle: "لا توجد عهدة جاهزة لطلب التسوية",
    settle_courier_first: "سوِّ عهدة المندوب أولًا ثم اعتمد الطلب",
    settlement_request_not_found: "طلب التسوية غير موجود أو تمت معالجته",
  };
  for (const [key, message] of Object.entries(messages)) {
    if (raw.includes(key)) return message;
  }
  return "تعذّر إتمام العملية";
}

export function useCourierAccounts(tenantId: string | null | undefined, enabled: boolean) {
  return useQuery({
    queryKey: ["courier_accounts", tenantId],
    enabled: !!tenantId && enabled,
    queryFn: async (): Promise<CourierAccount[]> => {
      const { data, error } = await supabase.rpc("list_courier_accounts" as never);
      if (error) throw new Error(employeeRpcMessage(error));
      return ((data ?? []) as Record<string, unknown>[]).map((row) => {
        const request = row.pending_request as Record<string, unknown> | null;
        return {
          courierId: String(row.courier_id),
          name: String(row.name),
          phone: row.phone ? String(row.phone) : undefined,
          isActive: Boolean(row.is_active),
          userId: row.user_id ? String(row.user_id) : undefined,
          email: row.email ? String(row.email) : undefined,
          displayName: row.display_name ? String(row.display_name) : undefined,
          custody: Number(row.custody ?? 0),
          pendingOrders: Number(row.pending_orders ?? 0),
          pendingRequest: request
            ? {
                id: String(request.id),
                amount: Number(request.amount ?? 0),
                createdAt: String(request.created_at),
              }
            : undefined,
        };
      });
    },
  });
}

export function useLinkCourierAccount(tenantId: string | null | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { courierId: string; email: string }) => {
      const { error } = await supabase.rpc(
        "link_courier_account" as never,
        {
          p_courier_id: input.courierId,
          p_email: input.email.trim(),
        } as never,
      );
      if (error) throw new Error(employeeRpcMessage(error));
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["courier_accounts", tenantId] }),
  });
}

export function useUnlinkCourierAccount(tenantId: string | null | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (courierId: string) => {
      const { error } = await supabase.rpc(
        "unlink_courier_account" as never,
        {
          p_courier_id: courierId,
          p_disable_courier: true,
        } as never,
      );
      if (error) throw new Error(employeeRpcMessage(error));
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["courier_accounts", tenantId] });
      queryClient.invalidateQueries({ queryKey: ["couriers", tenantId] });
    },
  });
}

export function useResolveSettlementRequest(tenantId: string | null | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: { requestId: string; status: "approved" | "rejected" }) => {
      const { error } = await supabase.rpc(
        "resolve_courier_settlement_request" as never,
        {
          p_request_id: input.requestId,
          p_status: input.status,
        } as never,
      );
      if (error) throw new Error(employeeRpcMessage(error));
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["courier_accounts", tenantId] }),
  });
}

export function useEmployeePortal(tenantId: string | null | undefined, enabled: boolean) {
  return useQuery({
    queryKey: ["employee_portal", tenantId],
    enabled: !!tenantId && enabled,
    refetchInterval: 30_000,
    queryFn: async (): Promise<EmployeePortal> => {
      const { data, error } = await supabase.rpc("get_my_courier_portal" as never);
      if (error) throw new Error(employeeRpcMessage(error));
      const raw = data as unknown as Record<string, unknown>;
      const courier = raw.courier as Record<string, unknown>;
      return {
        courier: {
          id: String(courier.id),
          name: String(courier.name),
          phone: courier.phone ? String(courier.phone) : undefined,
        },
        tenantName: String(raw.tenant_name ?? "المحل"),
        custody: Number(raw.custody ?? 0),
        pendingOrders: Number(raw.pending_orders ?? 0),
        orders: ((raw.orders ?? []) as Record<string, unknown>[]).map((order) => ({
          id: String(order.id),
          number: String(order.number),
          total: Number(order.total ?? 0),
          paid: Number(order.paid ?? 0),
          courierState: String(
            order.courier_state ?? "pending",
          ) as EmployeePortalOrder["courierState"],
          collectedByCourier: Number(order.collected_by_courier ?? 0),
          createdAt: String(order.created_at),
          customer: order.customer
            ? {
                name: String((order.customer as Record<string, unknown>).name),
                phone: (order.customer as Record<string, unknown>).phone
                  ? String((order.customer as Record<string, unknown>).phone)
                  : undefined,
              }
            : undefined,
          items: ((order.items ?? []) as Record<string, unknown>[]).map((item) => ({
            name: String(item.name),
            qty: Number(item.qty ?? 0),
            unitPrice: Number(item.unit_price ?? 0),
          })),
        })),
        settlementRequests: ((raw.settlement_requests ?? []) as Record<string, unknown>[]).map(
          (request) => ({
            id: String(request.id),
            amount: Number(request.amount ?? 0),
            status: String(
              request.status,
            ) as EmployeePortal["settlementRequests"][number]["status"],
            createdAt: String(request.created_at),
            resolvedAt: request.resolved_at ? String(request.resolved_at) : undefined,
          }),
        ),
      };
    },
  });
}

export function useEmployeeOrderState(tenantId: string | null | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async (input: {
      orderId: string;
      state: "pending" | "delivered_full" | "delivered_partial" | "delivered_none" | "returned";
      collected?: number;
    }) => {
      const { error } = await supabase.rpc(
        "courier_update_my_order_state" as never,
        {
          p_order_id: input.orderId,
          p_state: input.state,
          p_collected: input.collected ?? null,
        } as never,
      );
      if (error) throw new Error(employeeRpcMessage(error));
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employee_portal", tenantId] }),
  });
}

export function useRequestCustodySettlement(tenantId: string | null | undefined) {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => {
      const { error } = await supabase.rpc("request_my_custody_settlement" as never);
      if (error) throw new Error(employeeRpcMessage(error));
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["employee_portal", tenantId] }),
  });
}
