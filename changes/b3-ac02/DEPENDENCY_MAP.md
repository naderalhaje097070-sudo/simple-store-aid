# B3 / AC-02 dependency map

tenants table grant → column privileges → owner/live-actor RLS → existing tenant trigger → role/profile linkage. Onboarding/settings use authenticated. Webhook uses service_role. Existing tenant_has_active_subscription reads trial expiry/subscriptions; five protected field writes must never be delegated to a client. Preserve B2 scanner correction and all46 existing migrations.
