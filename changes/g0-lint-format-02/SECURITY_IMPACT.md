# Security impact

No auth/permission/RLS/SQL/secret or dependency/security-exception change. Existing inline suppressions in platform-admin and Inventory are preserved verbatim; targeted suppressed diagnostics remain identical excluding shifted positions (5+6). No new/wider suppression or concealed diagnostics. Explicit isolated CI build fixtures only. No historical advisory/audit/G1 rerun or deployment.
