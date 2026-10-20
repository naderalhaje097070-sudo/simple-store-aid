# Independent focused review — G1-EGRESS-TRACE-01

Overall PR outcome: **Blocked pending missing evidence** for the broader gates. **The bounded G1-EGRESS-TRACE-01 correction passes this focused review** on executed source `dbc870fcc278781b650860273ac4e1116f629f85`. Actual hosted40/40 results close this packet's zero-egress blocker without relaxing containment or acceptance. This does not grant full G0/G1/G2 acceptance, human merge approval, deployment, launch, a G0 exception or PR48 closure.

## Independence and actual work

The reviewer implemented no application, harness, workflow or GitHub mutation; this REVIEW.md is the only file edited. Read AGENTS.md, current PROJECT_STATE/TASKS/DECISIONS, governance protocols, and the previous cli-cleanup report/review/network diagnosis. Reviewed tracing design before publication and reported limitations: pointer-only send syscalls, no arbitrary path/hostname logging, explicit versus inferred destinations, asynchronous socket errors, resolver-hook coverage and process-identity read failures. The implementation subsequently retained these distinctions and made incomplete/read/lineage failures block its trace gate.

After the usage interruption, actual independent review resumed: fetched live GitHub trees, runtime/environment/Quality logs and artifact metadata; checked the local ZIP and its receipts; reran safe local fixtures. No CI dispatch, application/DB/Auth replay, financial operation, production/provider access, DNS request or GitHub write was performed by this reviewer.

Actually reexecuted locally with PYTHONDONTWRITEBYTECODE=1:

- `python tests/g01-acceptance/test_egress_trace.py`: 9 tests PASS, including parser/privacy cases and Node-VM/native-resolver-stub delegation, hostname hashes and log failure. No external resolver call is needed by these fixtures.
- `python tests/g01-acceptance/test_cleanup.py`: 6 tests PASS.
- `python tests/g01-acceptance/test_g1_contracts.py`: 17 tests PASS; generic500, wrong named guard and partial mismatch remain rejected.
- `git diff --check`: PASS before publication.

The hosted pointer-only strace preflight was inspected in actual logs; it was not independently reexecuted locally. The actual installed Miniflare bundle fixture is source-reviewed and its hosted execution inspected, not locally executed: that vendor bundle is absent locally. After the evidence-backed VM alias correction, reran the9 local trace fixtures again (PASS) and `node --check tests/g01-acceptance/test_cf_fetch.cjs` (PASS).

## Diagnostic identity and evidence

Fetched nontruncated GitHub trees for starting `b4a6440d712eab3c347cd8924292fc4676df3552`, diagnostic `e3be246e` and Quality's synthetic merge `0006d4d957241ab154187a6d3bcd5fdd808f87b8`. The synthetic merge has exact tree equality with the diagnostic source; no protected branch merge occurred. Starting461 blobs become467: six new trace/intake paths and six changed harness/workflow/checkpoint paths. Application, dependency files and all41 migrations are unchanged. All executable local blobs match the fetched diagnostic tree. Four prior delivery-only files are absent or differ locally (old REPORT and three archived ZIPs); this is not a claim of full467-file local identity.

Directly read runtime job116333095995 and environment116333096274 in run38708299333, plus Quality job116333117056/run38708305619. Artifact API digest and local archive SHA256 both equal `2449f73f033ebda6e8c0ebe71fb2c541b1d2d9f7bbacb7fc4952c1a810715ecd`; every one of its eight members matches the local receipt bytes.

Diagnostic runtime executed40 checks/39PASS; only native_unexpected_outbound_zero failed. Named runtime/baked Supabase mismatch ANDHTTP500 passed, matching SSR/Auth desktop/mobile passed, all22 before/after public-table digests matched, financial-zero/source/secret checks passed and cleanup4/4 passed. Installer completed all12 phases with the unchanged pins. Environment succeeded with17 tests/six sentinels. Quality succeeded with60 unit tests/125 expectations,8 offline actual-wrapper cases and67 dummy browser transport cases; these are bounded checks, not full lint/audit or release acceptance.

## Proven diagnostic facts and source-supported correction

IPv4 REJECT remains1→matching-ready9→afterAuth9→after-conflict17; IPv6 stays0. Matching and conflict traces each have zero unparsed/incomplete syscall lines, preserved lineage metadata and eight `sendmmsg` calls returningEPERM. Native getaddrinfo events and timestamps map these calls to Node's resolver threads in UID999, targeting the configured local resolver127.0.0.53:53. That loopback address is correctly outside the unchanged exact127.0.0.1/32 allowance. Each phase has eight additional rejected packets. Eight syscall invocations, eight packets, resolver invocations and unique connections are different quantities; no DNS payload or A/AAAA query count was captured.

The queried hostname hash `7dbcc823da096fc40bbb5e5d75d7d8620c2cd6a471931b27e49c020690cafb41` independently equals SHA256 of the public hostname `workers.cloudflare.com`. The other observed hash `12ca17b4…` equals127.0.0.1. The failed-host Node stack is empty; native module offset and process identity alone do not establish the JavaScript fetch caller.

Independently fetched primary source at Wrangler4.149.0: Miniflare `src/cf.ts`, Wrangler `dev/miniflare/index.ts` and `api/startDevWorker/LocalRuntimeController.ts`, plus workers-utils environment-variable definitions. setupCf's default fetch endpoint is `https://workers.cloudflare.com/cf.json`; when cache lookup fails it fetches with a3s timeout and falls back on failure. The official `CLOUDFLARE_CF_FETCH_ENABLED=false` option makes undefined cf resolve tofalse and return the same fallback before cache access/fetch. No explicit cf override was found in the reviewed Wrangler construction path; no application request.cf usage was found by focused source search.

The correction is one clean-environment literal on the test emulator command. The actual-vendor VM fixture extracts the four installed functions and requires: unset flag reaches one trapped cache read and one trapped fetch; false performs neither and returns identical fallback; explicit object retains priority. It executes before credentials. Real runtime DNS is not stubbed. The verified corrected-source results follow below.

## Corrective preflight failure, retained

Independently fetched runtime116444626626 in corrective run38741656393/source `87c5d97283685fa346d19559a61d8091fba3b4b6`, environment116444627182 and Quality116444656624/run38741665550. The actual installed-vendor fixture failed before CLI setup, user creation, database startup or SSR/Auth. Its original catch emitted only a generic FAIL, so those logs do not identify the fixture cause or test the runtime correction. Cleanup4/4, credential scan, environment and Quality succeeded; they do not replace missing corrected runtime evidence.

Independently fetched runtime116445843504/run38742012852 on `251d608684093ab2c7d7a06aadc8eff6f4bf3297`: the public-source-only error stack identifies ReferenceError:dim2 is not defined in the extracted setupCf catch. Cleanup reports user_absent/4PASS, confirming this second failure also occurred before the real emulator sequence. The subsequent correction supplies observed bare esbuild numeric aliases of readFile, fetch and dim with the same offline traps/identity formatter; the extracted vendor functions and all three assertions remain unchanged. These two failed preflights are retained separately from the emulator diagnostic. They are not zero-egress passes or repeated emulator trials.

## Final actual corrected result

Directly fetched runtime116446791417/environment116446791036 in run38742289056 and Quality116446823747/run38742298220. All completed SUCCESS on executed source `dbc870fcc278781b650860273ac4e1116f629f85`. Fetched nontruncated corrected468-blob tree and Quality's synthetic merge `e4f8e1fa7f4edcc484d52eadf3bd23c09d405455`; their path/mode/blob entries match exactly. Compared211 local executable/contract blobs under src/supabase/tests/.github and the relevant root configuration/dependency files with the corrected tree: zero mismatches. Relative to diagnostic e3be, only the official env literal/comment, precredential vendor fixture/workflow and focused impact note changed. No application, financial, auth or migration change is included.

The runtime artifact11977205340 has GitHub API digest and local SHA256 `038c71a72b94f451316cfd6d15144856f748645d14d149a2239db0f7b3f2c3d2`; all eight copied JSON members match their ZIP bytes. Environment artifact11975579508 has recorded API digest `5b0fbb4b6f3f77e8412cb38f3fe14790c03af6f92d152f300b77f3e881ccd704`.

| Boundary | Independently inspected result |
| --- | --- |
| Actual installed-vendor oracle |3 cases PASS; Miniflare5.20261006.1-alpha; bundle SHA256 `141080338caec736dd681d442ed6d00b28406dbb68a10e4acaad5265acc41482`; extracted functions SHA256 `c7efad92f23815df33dd320d4426a08bfe5d26d461f4991f37ad251236cbd095` |
| Runtime checks |40/40 PASS; matching SSR200 and actual Auth desktop/mobile PASS |
| Required denial |HTTP500 AND full named mismatch PASS; only build_runtime_supabase_mismatch classified; no unclassified error |
| Actual counters |IPv4 remains1 from canary baseline through matching-ready, Auth and conflict shutdown; IPv6 remains0; no counter reset/exception |
| Trace comparison |Both phases complete; zero unparsed/unfinished lines, no process-map read failure, zero DNS-port53 events, zeroEPERM and no native resolver events; Node lookup hashes are only127.0.0.1, three each phase |
| Data/source/secrets |22 public-table before/after count/digests equal; financial-zero, tracked-source and credential-free receipt checks PASS; hosted artifact scan PASS |
| Cleanup |4/4 PASS: no g01-app processes, no isolated containers, env/status removed |
| Mandatory affected checks |Environment17tests/six checks PASS; Quality60unit/125expectations,8 offline wrapper and67 dummy browser cases PASS; typecheck/build/changed-source lint PASS |

The untraced historical source819 produced16 blocked packets; diagnostic e3be with preloads also produced16. The corrected run retains the same trace/preload instrumentation and changes the official cf-fetch setting, then produces zero additional packets while preserving SSR/Auth/data/denial results. Together with the hostname hash and pinned-source/vendor-function evidence, this supports the optional Request.cf metadata fetch as the cause of the observed startup attempts. No fabricated missing JS stack is asserted. A corrected run without tracing/preload was not performed and is not claimed.

## Limits and remaining gate

No successful external delivery is established by UDP connect0, EINPROGRESS or any syscall count. Raw send syscalls are pointer-only; their destinations are not silently inferred across descriptor reuse or threads. Resolver hooks cover the documented APIs only; absent events are not universal proof of noDNS. Trace evidence does not retroactively prove the old CLI stall's cause.

The previous Medium finding on this packet's native zero-unexpected-packet gate is closed by the actual corrected40/40 result, unchanged firewall and original-baseline equality. No new Critical/High finding was found within the bounded harness/CI scope. This does not close broader planning-owned gate findings.

G0 lint/advisory blockers and inherited G2 account-lifecycle defect remain separate. Rollback is an additive revert of this batch's test/CI/checkpoint changes on the same draft; no schema/data compensation applies.
