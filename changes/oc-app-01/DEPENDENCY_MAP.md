# DEPENDENCY_MAP

paddle.ts getPaddlePriceId -> payments.functions.ts -> requireSupabaseAuth/generated bearer context -> current_tenant_id -> assert_active_actor -> actor_is_active. Then unchanged gatewayFetch/getEnv. Source search found only one createServerFn.

See CHANGE_INTAKE.md for exact authorization, source, boundaries and acceptance.

Global start.ts registers generated attachSupabaseAuth client middleware, which attaches a session Bearer in browser calls. The direct test sends the real OAuth Bearer using the compiler wire protocol; actual requireSupabaseAuth runs on server. Both generated files stay unchanged. No application serializationAdapters are configured.
