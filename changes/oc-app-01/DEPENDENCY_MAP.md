# DEPENDENCY_MAP

paddle.ts resolvePriceId -> payments.functions.ts -> requireSupabaseAuth/generated bearer context -> current_tenant_id -> assert_active_actor -> actor_is_active. Then unchanged gatewayFetch/getEnv. Source search found only one createServerFn.

See CHANGE_INTAKE.md for exact authorization, source, boundaries and acceptance.
