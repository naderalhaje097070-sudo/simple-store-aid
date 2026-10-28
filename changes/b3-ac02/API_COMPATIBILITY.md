# B3 / AC-02 api compatibility

Actual callers: onboarding.tsx client inserts name+owner_user_id and selects id; src/lib/db.ts updates name, business_type and timezone independently. All remain permitted. Client attempts to write protected fields intentionally return42501. Webhook uses SUPABASE_SERVICE_ROLE_KEY; its five-field PATCH remains permitted. Webhook persistence handling is deferred to B4.
