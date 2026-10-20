# Security Impact

Fail closed using invoker role, not SECURITY DEFINER owner or client fields. Ordinary authenticated users keep EXECUTE grant for legitimate platform-admin use but are denied inside the function before first INSERT. Existing activity guard remains first; trusted service/cron identities preserve their preexisting exemption. Explicit42501 error. No new roles, grants, exposed helper or cleanup RPC.
