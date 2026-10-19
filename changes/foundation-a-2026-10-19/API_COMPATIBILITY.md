# API COMPATIBILITY

RPC names, arguments and mutation payloads remain unchanged. TenantSettings gains trial_ends_at:string|null; tenantTodayKey accepts an optional Date while preserving one-argument callers. AppCtx carries read state, retry and shared todayKey. Test fixture AppCtx is updated for the existing missing-customer regression.
