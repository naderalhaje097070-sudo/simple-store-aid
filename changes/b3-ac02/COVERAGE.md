# B3 / AC-02 decision coverage

Executable source117f59289a01c56aeb764be27acfbb45663ec439; native39568502042. Actual fresh240, upgrade52 baseline +211 corrected controls. These are named checks, not a vulnerability percentage. See RESULT, native receipts and independent review.

| Decision | Actor / entry | Invariant | Evidence planned | Status |
|---|---|---|---|---|
| Original composition | all346 protected paths /46SQL | byte+mode exact; four additive protected paths only | Git tree and original source identities | Source PASS |
| Protected fields | owner JWT REST INSERT/PATCH | five fields, explicit/null/same value denied42501; all public/closure rows unchanged | native matrix | Runtime PASS |
| Atomic writes | owner REST mixed/bulk/upsert | permitted name never commits when protected column included | native snapshots | Runtime PASS |
| SQL DEFAULT | actual authenticated role and valid user | INSERT/UPDATE DEFAULT rejected42501 for each protected column | transactional SQL | Runtime PASS |
| Upsert default safety | owner REST conflict/insert branches | malicious payload denied; safe metadata conflict never resets protected defaults | real PostgREST | Runtime PASS |
| Legitimate onboarding | new real Auth user | minimal name/owner insert succeeds; original14day defaults, owner role and profile trigger link | REST and stored SQL | Runtime PASS |
| Settings | two owners/new owner | name/business_type/timezone succeed; protected values unchanged | REST + stored values | Runtime PASS |
| Trusted billing metadata | service_role | all five PATCH persist before and after denied batch; INSERT persists after batch | actual local service JWT REST | Runtime PASS |
| Other tenant and staff | two staff/distinct tenant owners | protected fields ACL deny; ordinary settings remain RLS restricted | JWT REST + snapshots | Runtime PASS |
| Inactive account | banned/self-closed owners and disabled employee old JWT | protected writes denied; legitimate settings/minimal INSERT do not mutate rows; active employee A unaffected | real state transitions | Runtime PASS |
| Anonymous | anon JWT REST | explicit42501 on protected writes, no mutation | native | Runtime PASS |
| Entitlement observation | expired trial/no subscriptions | baseline false→client extension true; fixed denial keepsfalse; trusted write true | actual helper RPC + stored values | Runtime PASS |
| Upgrade preservation | synthetic populated46→47 | only tenant ACL changes; all row fingerprints/defaults/functions/policies/triggers/constraints/other ACLs preserved | native before/after | Runtime PASS |
| Effective privileges | PUBLIC/inherited role grants | protected ten client column rights absent; other seven and service rights retained | native has_column_privilege + catalog memberships/grantors | Runtime PASS |
| B2 regression | ordinary owner | scanner remains42501 forbidden_platform_admin | native RPC and exact B2 source | Runtime PASS |
| Evidence boundary | isolated UID and reviewed publication guard | no private keys/state uploaded; cleanup and upload output gate failclosed | native cleanup + independent source review | Runtime PASS |

No financial histories populated; no provider, paywall-enforcement, concurrent billing, production or package-B acceptance claim. The seven other tenant columns preserve their existing privileges intentionally; future column grants require explicit review. B4/B5/B6 remain subsequent gates.

The explicit and same_value labels repeat the same stored non-null fixture value; with null, this is two distinct payload values per field, not three. Homogeneous bulk is tested; arbitrary heterogeneous bulk is not. Actual advisors report45 performance WARNs per mode, not a clean result. Current G0 audit fails with8 distinct advisories/3 High (DEP-20261021); known A source manifest also remains red. This ledger accepts no whole-head merge or package-B/RC gate.
