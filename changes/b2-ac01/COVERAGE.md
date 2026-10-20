# B2 / AC-01 decision coverage

Exact final executable candidate: `7a4fb5811c35a053109860c3155074087b930489`. Runtime receipts remain tied to their actual source; earlier00b465 results are historical. This ledger is not a project-wide security percentage.

| Decision / operation | Actor and state | Invariant | Evidence | Result / limit |
|---|---|---|---|---|
| Preserve foundation composition | Original B1 source | All original paths/blobs/modes and45 SQL exact; one new46th migration | Complete Git tree + CLI artifact comparison | PASS source preservation; no inherited B5 acceptance |
| Privileged scanner invocation | Active platform admin | Existing response, durable success row, only scanner tables change | Native REST RPC, before and after denial batch | PASS on final-source native |
| Approved service execution | service_role with no user subject | Existing service contract and scanner-only side effects preserved | Actual local service-key REST RPC | PASS on final-source native |
| Scheduled SQL identity | Stored cron postgres identity | Schedule/command retained; exact SQL succeeds | Catalog + actual trusted SQL call | PASS on final-source native; no scheduled tick observed |
| Ordinary owners | Two live owners in distinct tenants | Explicit42501 forbidden_platform_admin; all public/closure rows unchanged | Real Auth login + RPC + full fingerprints | PASS on final-source native |
| Employees | Two live employees across tenants | No global scanner access; successful independent active-user control remains | Real Auth/RPC + fingerprints | PASS on final-source native |
| Anonymous caller | anon bearer | Function EXECUTE denied42501; no changes | Actual local REST RPC and catalog ACL | PASS on final-source native |
| Trigger/user-metadata spoofing | Ordinary owner with fake admin metadata; cron/service trigger labels | Client data confers no authorization | Actual Auth metadata/login/RPC | PASS on final-source native |
| JWT role-text spoofing | Real authenticated SQL role, service_role text in claims | Runtime connection role governs; reject42501 before writes | Direct transactional SQL + fingerprint invariance | PASS on final-source native; no forged signed JWT used |
| Inactive admins | Banned admin and self-closed admin, preexisting tokens |42501 account_inactive before scanner writes; active admin unaffected | Real Auth ban/owner-closure transitions and old-token RPCs | PASS on final-source native; broader lifecycle remains B5 |
| Populated upgrade | Synthetic users/tenants/scan history |45-state reproduces unauthorized200;46-state preserves data/OID/owner/ACL/signature/non-target catalogs | Before/after actual local migration | PASS on final-source native; financial tables intentionally empty |
| Safe catalog namespace | Global definer scanner | pg_catalog first, pg_temp last; qualified app objects; body after first INSERT unchanged | Source diff and actual catalog config | Structure proof; no runtime temp-shadow exploit test |
| Artifact failure boundary | Synthetic invalid JWT and known test password | Detected bytes leave entire upload sink; safe digest-only receipt; failed guard cannot set upload output | Independent old-flaw reproduction + five oracle/sink tests | PASS five oracle/sink tests plus22 independent checks; Medium finding closed on final source |

Data fingerprints cover all22 public tables and the private closure marker table, excluding Auth session bookkeeping. No financial/provider flow runs. Official CLI advisor invocation/availability is recorded in native logs; detailed advisor output is private and no clean-advisor claim is made. No production, merge, deployment, PR closure or policy change. B3/B4/B5/B6/B7 and inherited OC-EVID-02 remain open.
