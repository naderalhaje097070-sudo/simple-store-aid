-- Owner-run emergency containment only; do not restore the vulnerable guard.
BEGIN;
REVOKE EXECUTE ON FUNCTION public.run_security_scan(text) FROM authenticated;
COMMIT;
