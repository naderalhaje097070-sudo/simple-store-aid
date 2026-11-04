# SECURITY_IMPACT

C5-RESTORE-01 test-only scope and acceptance are specified in [INTAKE](INTAKE.md).

Fixed container/source/target guards, separate target must not exist, roles/ACL/RLS compared, actual synthetic token claims used only as SQL role context. No signature/API restore claim. Exact UID firewall and publication gate inherited; Docker privilege remains orchestration-only.
