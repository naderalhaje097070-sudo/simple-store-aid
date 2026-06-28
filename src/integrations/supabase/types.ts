export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  // Allows to automatically instantiate createClient with right options
  // instead of createClient<Database, { PostgrestVersion: 'XX' }>(URL, KEY)
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      couriers: {
        Row: {
          created_at: string
          id: string
          is_active: boolean
          name: string
          phone: string | null
          tenant_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id?: string
          is_active?: boolean
          name: string
          phone?: string | null
          tenant_id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          is_active?: boolean
          name?: string
          phone?: string | null
          tenant_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "couriers_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      customers: {
        Row: {
          created_at: string
          id: string
          name: string
          notes: string | null
          phone: string | null
          tenant_id: string
          updated_at: string
        }
        Insert: {
          created_at?: string
          id?: string
          name: string
          notes?: string | null
          phone?: string | null
          tenant_id: string
          updated_at?: string
        }
        Update: {
          created_at?: string
          id?: string
          name?: string
          notes?: string | null
          phone?: string | null
          tenant_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "customers_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      day_closes: {
        Row: {
          closed_for: string
          collected: number
          created_at: string
          created_by: string | null
          customer_debts: number
          expenses: number
          id: string
          note: string | null
          realized_profit: number
          sales: number
          tenant_id: string
          unsettled_custody: number
        }
        Insert: {
          closed_for: string
          collected?: number
          created_at?: string
          created_by?: string | null
          customer_debts?: number
          expenses?: number
          id?: string
          note?: string | null
          realized_profit?: number
          sales?: number
          tenant_id: string
          unsettled_custody?: number
        }
        Update: {
          closed_for?: string
          collected?: number
          created_at?: string
          created_by?: string | null
          customer_debts?: number
          expenses?: number
          id?: string
          note?: string | null
          realized_profit?: number
          sales?: number
          tenant_id?: string
          unsettled_custody?: number
        }
        Relationships: [
          {
            foreignKeyName: "day_closes_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      expenses: {
        Row: {
          amount: number
          created_at: string
          created_by: string | null
          id: string
          method: Database["public"]["Enums"]["payment_method"]
          note: string | null
          tenant_id: string
          type: string
        }
        Insert: {
          amount: number
          created_at?: string
          created_by?: string | null
          id?: string
          method?: Database["public"]["Enums"]["payment_method"]
          note?: string | null
          tenant_id: string
          type: string
        }
        Update: {
          amount?: number
          created_at?: string
          created_by?: string | null
          id?: string
          method?: Database["public"]["Enums"]["payment_method"]
          note?: string | null
          tenant_id?: string
          type?: string
        }
        Relationships: [
          {
            foreignKeyName: "expenses_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      financial_audit_log: {
        Row: {
          action: string
          after: Json | null
          before: Json | null
          created_at: string
          entity_id: string | null
          entity_type: string
          id: string
          tenant_id: string
          user_id: string | null
        }
        Insert: {
          action: string
          after?: Json | null
          before?: Json | null
          created_at?: string
          entity_id?: string | null
          entity_type: string
          id?: string
          tenant_id: string
          user_id?: string | null
        }
        Update: {
          action?: string
          after?: Json | null
          before?: Json | null
          created_at?: string
          entity_id?: string | null
          entity_type?: string
          id?: string
          tenant_id?: string
          user_id?: string | null
        }
        Relationships: [
          {
            foreignKeyName: "financial_audit_log_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      order_items: {
        Row: {
          created_at: string
          id: string
          name: string
          order_id: string
          product_id: string | null
          qty: number
          tenant_id: string
          unit_cost: number
          unit_price: number
        }
        Insert: {
          created_at?: string
          id?: string
          name: string
          order_id: string
          product_id?: string | null
          qty: number
          tenant_id: string
          unit_cost?: number
          unit_price: number
        }
        Update: {
          created_at?: string
          id?: string
          name?: string
          order_id?: string
          product_id?: string | null
          qty?: number
          tenant_id?: string
          unit_cost?: number
          unit_price?: number
        }
        Relationships: [
          {
            foreignKeyName: "order_items_order_id_fkey"
            columns: ["order_id"]
            isOneToOne: false
            referencedRelation: "orders"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "order_items_product_id_fkey"
            columns: ["product_id"]
            isOneToOne: false
            referencedRelation: "products"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "order_items_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      orders: {
        Row: {
          collected_by_courier: number
          courier_id: string | null
          courier_state: Database["public"]["Enums"]["courier_state"] | null
          created_at: string
          created_by: string | null
          customer_id: string | null
          delivery: Database["public"]["Enums"]["delivery_kind"]
          id: string
          notes: string | null
          number: number
          paid: number
          status: Database["public"]["Enums"]["order_status"]
          tenant_id: string
          tenant_number: number | null
          total: number
          updated_at: string
        }
        Insert: {
          collected_by_courier?: number
          courier_id?: string | null
          courier_state?: Database["public"]["Enums"]["courier_state"] | null
          created_at?: string
          created_by?: string | null
          customer_id?: string | null
          delivery?: Database["public"]["Enums"]["delivery_kind"]
          id?: string
          notes?: string | null
          number?: number
          paid?: number
          status?: Database["public"]["Enums"]["order_status"]
          tenant_id: string
          tenant_number?: number | null
          total?: number
          updated_at?: string
        }
        Update: {
          collected_by_courier?: number
          courier_id?: string | null
          courier_state?: Database["public"]["Enums"]["courier_state"] | null
          created_at?: string
          created_by?: string | null
          customer_id?: string | null
          delivery?: Database["public"]["Enums"]["delivery_kind"]
          id?: string
          notes?: string | null
          number?: number
          paid?: number
          status?: Database["public"]["Enums"]["order_status"]
          tenant_id?: string
          tenant_number?: number | null
          total?: number
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "orders_courier_id_fkey"
            columns: ["courier_id"]
            isOneToOne: false
            referencedRelation: "couriers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "orders_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "orders_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      payments: {
        Row: {
          amount: number
          courier_id: string | null
          created_at: string
          created_by: string | null
          customer_id: string | null
          id: string
          kind: Database["public"]["Enums"]["payment_kind"]
          method: Database["public"]["Enums"]["payment_method"]
          note: string | null
          order_id: string | null
          tenant_id: string
        }
        Insert: {
          amount: number
          courier_id?: string | null
          created_at?: string
          created_by?: string | null
          customer_id?: string | null
          id?: string
          kind: Database["public"]["Enums"]["payment_kind"]
          method: Database["public"]["Enums"]["payment_method"]
          note?: string | null
          order_id?: string | null
          tenant_id: string
        }
        Update: {
          amount?: number
          courier_id?: string | null
          created_at?: string
          created_by?: string | null
          customer_id?: string | null
          id?: string
          kind?: Database["public"]["Enums"]["payment_kind"]
          method?: Database["public"]["Enums"]["payment_method"]
          note?: string | null
          order_id?: string | null
          tenant_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "payments_courier_id_fkey"
            columns: ["courier_id"]
            isOneToOne: false
            referencedRelation: "couriers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payments_customer_id_fkey"
            columns: ["customer_id"]
            isOneToOne: false
            referencedRelation: "customers"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payments_order_id_fkey"
            columns: ["order_id"]
            isOneToOne: false
            referencedRelation: "orders"
            referencedColumns: ["id"]
          },
          {
            foreignKeyName: "payments_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      platform_admin_audit_log: {
        Row: {
          action: string
          created_at: string
          details: Json
          id: string
          user_id: string
        }
        Insert: {
          action: string
          created_at?: string
          details?: Json
          id?: string
          user_id: string
        }
        Update: {
          action?: string
          created_at?: string
          details?: Json
          id?: string
          user_id?: string
        }
        Relationships: []
      }
      platform_admins: {
        Row: {
          created_at: string
          note: string | null
          user_id: string
        }
        Insert: {
          created_at?: string
          note?: string | null
          user_id: string
        }
        Update: {
          created_at?: string
          note?: string | null
          user_id?: string
        }
        Relationships: []
      }
      products: {
        Row: {
          category: string | null
          cost: number
          created_at: string
          id: string
          is_active: boolean
          is_discount: boolean
          name: string
          price: number
          sku: string | null
          stock: number
          tenant_id: string
          updated_at: string
        }
        Insert: {
          category?: string | null
          cost?: number
          created_at?: string
          id?: string
          is_active?: boolean
          is_discount?: boolean
          name: string
          price?: number
          sku?: string | null
          stock?: number
          tenant_id: string
          updated_at?: string
        }
        Update: {
          category?: string | null
          cost?: number
          created_at?: string
          id?: string
          is_active?: boolean
          is_discount?: boolean
          name?: string
          price?: number
          sku?: string | null
          stock?: number
          tenant_id?: string
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "products_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      profiles: {
        Row: {
          created_at: string
          display_name: string | null
          id: string
          phone: string | null
          tenant_id: string | null
          updated_at: string
        }
        Insert: {
          created_at?: string
          display_name?: string | null
          id: string
          phone?: string | null
          tenant_id?: string | null
          updated_at?: string
        }
        Update: {
          created_at?: string
          display_name?: string | null
          id?: string
          phone?: string | null
          tenant_id?: string | null
          updated_at?: string
        }
        Relationships: [
          {
            foreignKeyName: "profiles_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      security_scan_findings: {
        Row: {
          detail: string | null
          fingerprint: string
          first_seen_at: string
          id: string
          last_run_id: string | null
          last_seen_at: string
          level: string
          metadata: Json
          name: string
          resolved_at: string | null
          scanner: string
          title: string
        }
        Insert: {
          detail?: string | null
          fingerprint: string
          first_seen_at?: string
          id?: string
          last_run_id?: string | null
          last_seen_at?: string
          level: string
          metadata?: Json
          name: string
          resolved_at?: string | null
          scanner: string
          title: string
        }
        Update: {
          detail?: string | null
          fingerprint?: string
          first_seen_at?: string
          id?: string
          last_run_id?: string | null
          last_seen_at?: string
          level?: string
          metadata?: Json
          name?: string
          resolved_at?: string | null
          scanner?: string
          title?: string
        }
        Relationships: [
          {
            foreignKeyName: "security_scan_findings_last_run_id_fkey"
            columns: ["last_run_id"]
            isOneToOne: false
            referencedRelation: "security_scan_runs"
            referencedColumns: ["id"]
          },
        ]
      }
      security_scan_runs: {
        Row: {
          error: string | null
          finished_at: string | null
          id: string
          new_count: number
          started_at: string
          status: string
          total_count: number
          triggered_by: string
        }
        Insert: {
          error?: string | null
          finished_at?: string | null
          id?: string
          new_count?: number
          started_at?: string
          status?: string
          total_count?: number
          triggered_by?: string
        }
        Update: {
          error?: string | null
          finished_at?: string | null
          id?: string
          new_count?: number
          started_at?: string
          status?: string
          total_count?: number
          triggered_by?: string
        }
        Relationships: []
      }
      subscriptions: {
        Row: {
          cancel_at_period_end: boolean | null
          created_at: string
          current_period_end: string | null
          current_period_start: string | null
          environment: string
          id: string
          paddle_customer_id: string
          paddle_subscription_id: string
          price_id: string
          product_id: string
          status: string
          tenant_id: string
          updated_at: string
          user_id: string
        }
        Insert: {
          cancel_at_period_end?: boolean | null
          created_at?: string
          current_period_end?: string | null
          current_period_start?: string | null
          environment?: string
          id?: string
          paddle_customer_id: string
          paddle_subscription_id: string
          price_id: string
          product_id: string
          status?: string
          tenant_id: string
          updated_at?: string
          user_id: string
        }
        Update: {
          cancel_at_period_end?: boolean | null
          created_at?: string
          current_period_end?: string | null
          current_period_start?: string | null
          environment?: string
          id?: string
          paddle_customer_id?: string
          paddle_subscription_id?: string
          price_id?: string
          product_id?: string
          status?: string
          tenant_id?: string
          updated_at?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "subscriptions_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      tenant_counters: {
        Row: {
          last_order_number: number
          tenant_id: string
        }
        Insert: {
          last_order_number?: number
          tenant_id: string
        }
        Update: {
          last_order_number?: number
          tenant_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "tenant_counters_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: true
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
      tenants: {
        Row: {
          business_type: string | null
          created_at: string
          id: string
          name: string
          owner_user_id: string
          paddle_customer_id: string | null
          paddle_subscription_id: string | null
          subscription_plan: string | null
          subscription_status: string | null
          timezone: string
          trial_ends_at: string | null
          updated_at: string
        }
        Insert: {
          business_type?: string | null
          created_at?: string
          id?: string
          name: string
          owner_user_id: string
          paddle_customer_id?: string | null
          paddle_subscription_id?: string | null
          subscription_plan?: string | null
          subscription_status?: string | null
          timezone?: string
          trial_ends_at?: string | null
          updated_at?: string
        }
        Update: {
          business_type?: string | null
          created_at?: string
          id?: string
          name?: string
          owner_user_id?: string
          paddle_customer_id?: string | null
          paddle_subscription_id?: string | null
          subscription_plan?: string | null
          subscription_status?: string | null
          timezone?: string
          trial_ends_at?: string | null
          updated_at?: string
        }
        Relationships: []
      }
      user_roles: {
        Row: {
          created_at: string
          id: string
          role: Database["public"]["Enums"]["app_role"]
          tenant_id: string
          user_id: string
        }
        Insert: {
          created_at?: string
          id?: string
          role: Database["public"]["Enums"]["app_role"]
          tenant_id: string
          user_id: string
        }
        Update: {
          created_at?: string
          id?: string
          role?: Database["public"]["Enums"]["app_role"]
          tenant_id?: string
          user_id?: string
        }
        Relationships: [
          {
            foreignKeyName: "user_roles_tenant_id_fkey"
            columns: ["tenant_id"]
            isOneToOne: false
            referencedRelation: "tenants"
            referencedColumns: ["id"]
          },
        ]
      }
    }
    Views: {
      [_ in never]: never
    }
    Functions: {
      _assert_owner: { Args: { _tid: string }; Returns: undefined }
      _assert_platform_admin: { Args: never; Returns: undefined }
      _assert_staff: { Args: { _tid: string }; Returns: undefined }
      _log_platform_admin_action: {
        Args: { p_action: string; p_details?: Json }
        Returns: undefined
      }
      close_day: { Args: { p_note: string }; Returns: Json }
      collect_order_debt: {
        Args: {
          p_amount: number
          p_method: Database["public"]["Enums"]["payment_method"]
          p_order_id: string
        }
        Returns: Json
      }
      create_sale_with_items: {
        Args: {
          p_courier_id: string
          p_customer_id: string
          p_delivery: Database["public"]["Enums"]["delivery_kind"]
          p_items: Json
          p_method: Database["public"]["Enums"]["payment_method"]
          p_paid: number
        }
        Returns: Json
      }
      current_tenant_id: { Args: never; Returns: string }
      current_tenant_timezone: { Args: never; Returns: string }
      delete_order_with_restore_stock: {
        Args: { p_order_id: string }
        Returns: Json
      }
      delete_product_safe: { Args: { p_product_id: string }; Returns: Json }
      get_platform_admin_audit_log: {
        Args: { p_limit?: number; p_offset?: number }
        Returns: {
          action: string
          created_at: string
          details: Json
          id: string
          user_email: string
          user_id: string
        }[]
      }
      get_platform_admin_overview: { Args: never; Returns: Json }
      get_platform_courier_custody_health: {
        Args: never
        Returns: {
          courier_id: string
          courier_name: string
          oldest_age_days: number
          orders_count: number
          risk: string
          tenant_id: string
          tenant_name: string
          unsettled_amount: number
        }[]
      }
      get_platform_day_close_health: {
        Args: { p_limit?: number }
        Returns: {
          closed_for: string
          collected: number
          collected_diff: number
          created_at: string
          customer_debts: number
          expenses: number
          expenses_diff: number
          id: string
          realized_profit: number
          sales: number
          sales_diff: number
          status: string
          tenant_id: string
          tenant_name: string
          unsettled_custody: number
        }[]
      }
      get_platform_financial_health: {
        Args: never
        Returns: {
          affected_count: number
          check_key: string
          explanation_ar: string
          status: string
        }[]
      }
      get_platform_financial_health_rows: {
        Args: { p_check_key: string; p_limit?: number }
        Returns: Json
      }
      get_platform_system_health: { Args: never; Returns: Json }
      get_platform_tenants_health: {
        Args: never
        Returns: {
          created_at: string
          customers_count: number
          health: string
          last_activity: string
          open_debts: number
          orders_count: number
          owner_user_id: string
          products_count: number
          tenant_id: string
          tenant_name: string
          total_collected: number
          total_sales: number
          unsettled_custody: number
        }[]
      }
      get_tenant_today_estimate: { Args: never; Returns: Json }
      has_owner_role: { Args: { _tid: string; _uid: string }; Returns: boolean }
      has_role: {
        Args: {
          _role: Database["public"]["Enums"]["app_role"]
          _tenant_id: string
          _user_id: string
        }
        Returns: boolean
      }
      has_staff_or_owner_role: {
        Args: { _tid: string; _uid: string }
        Returns: boolean
      }
      is_platform_admin: { Args: never; Returns: boolean }
      next_order_number: { Args: { _tid: string }; Returns: number }
      return_courier_order: { Args: { p_order_id: string }; Returns: Json }
      run_security_scan: { Args: { p_triggered_by?: string }; Returns: Json }
      settle_courier_orders: {
        Args: { p_courier_id: string; p_order_ids: string[] }
        Returns: Json
      }
      tenant_has_active_subscription: {
        Args: { _check_env?: string; _tenant_id: string }
        Returns: boolean
      }
      tenant_today: { Args: { _tid: string }; Returns: string }
      update_courier_order_state: {
        Args: { p_collected?: number; p_order_id: string; p_state: string }
        Returns: Json
      }
    }
    Enums: {
      app_role: "owner" | "staff"
      courier_state:
        | "pending"
        | "delivered_full"
        | "delivered_partial"
        | "delivered_none"
        | "returned"
      delivery_kind: "direct" | "courier"
      order_status: "paid" | "partial" | "debt"
      payment_kind: "sale" | "debt_collection" | "courier_settlement"
      payment_method: "cash" | "transfer"
    }
    CompositeTypes: {
      [_ in never]: never
    }
  }
}

type DatabaseWithoutInternals = Omit<Database, "__InternalSupabase">

type DefaultSchema = DatabaseWithoutInternals[Extract<keyof Database, "public">]

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (DefaultSchema["Tables"] & DefaultSchema["Views"])
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
        DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? (DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] &
      DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends {
      Row: infer R
    }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (DefaultSchema["Tables"] &
        DefaultSchema["Views"])
    ? (DefaultSchema["Tables"] &
        DefaultSchema["Views"])[DefaultSchemaTableNameOrOptions] extends {
        Row: infer R
      }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Insert: infer I
    }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Insert: infer I
      }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof DefaultSchema["Tables"]
    | { schema: keyof DatabaseWithoutInternals },
  TableName extends DefaultSchemaTableNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends {
      Update: infer U
    }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof DefaultSchema["Tables"]
    ? DefaultSchema["Tables"][DefaultSchemaTableNameOrOptions] extends {
        Update: infer U
      }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof DefaultSchema["Enums"]
    | { schema: keyof DatabaseWithoutInternals },
  EnumName extends DefaultSchemaEnumNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof DefaultSchema["Enums"]
    ? DefaultSchema["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof DefaultSchema["CompositeTypes"]
    | { schema: keyof DatabaseWithoutInternals },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends {
    schema: keyof DatabaseWithoutInternals
  }
    ? keyof DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends {
  schema: keyof DatabaseWithoutInternals
}
  ? DatabaseWithoutInternals[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof DefaultSchema["CompositeTypes"]
    ? DefaultSchema["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = {
  public: {
    Enums: {
      app_role: ["owner", "staff"],
      courier_state: [
        "pending",
        "delivered_full",
        "delivered_partial",
        "delivered_none",
        "returned",
      ],
      delivery_kind: ["direct", "courier"],
      order_status: ["paid", "partial", "debt"],
      payment_kind: ["sale", "debt_collection", "courier_settlement"],
      payment_method: ["cash", "transfer"],
    },
  },
} as const
