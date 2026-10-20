# Security impact

Official advisory GHSA-qx66-fv34-fjm8 (CVE-2026-102989) describes unauthenticated reflected XSS through crafted Start server-function inputs. Affected react-start>=1.143.12<1.168.60 and start-server-core>=1.143.12<1.169.39. Upgrade the actual graph; do not substitute a header check or disable security enforcement.

Regression checks all occurrences of both package tuples in bun.lock against patched thresholds, including nested resolutions. It proves locked version boundaries, not exploit reproduction or a complete security audit. Existing routes/auth/tenant policies are unchanged and require isolated integration proof later. No real tokens/data or provider secrets are used.

## Serializer and broader scan

GHSA-p6vx-979v-rg4c affects Seroval>=0.12.0<=1.6.0; the maintainer identifies1.6.2 as patched. Use1.6.7 to satisfy Start's required serializer API range. The guard now checks all3 package names. The final wider registry audit remains non-green:2Critical/33High/25Moderate/5Low package/advisory records, untriaged for reachability. Its coverage does not replace direct upstream advisory verification.
