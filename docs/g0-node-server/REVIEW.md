# Independent review — G0-NODE-SERVER-01

Reviewer: separate read-only agent `/root/node_server_review`. Starting head
`5cbf198d88b0f091a30371676fb09abf92903dc8`; current executable source
`15688194725fdb2c25e53d55d63cfe605295ec68`, tree
`a2405b8051fbeeba6e966188369c180c7e3e57c6`. This report is outside
the candidate and does not change GitHub or implementation files.

## Outcome

**Blocked pending missing evidence** for overall G0/integration acceptance.
No new bounded engineering finding remains in G0-NODE-SERVER-01. The minimum
official compatible1.x patch, real Windows before/after oracle, SDK contracts,
all-copy guard and supported audit are substantiated by the evidence below.
This is not G0, integration, merge or release approval. Esbuild, inherited lint,
final-source identity reconciliation and affected live G1 verification remain
outside this completed bounded review. A final docs-only delivery reconciliation
will be recorded separately after publication; this report reviews the exact
executable source above.

## Independently executed so far

- Read AGENTS, current top state/task/decision records, CMF, delivery, security,
  database, testing and review policies, all current `docs/g0-node-server`
  intake/impact records, both preparation/baseline workflows and the new fixtures.
- Recomputed preparation ZIP SHA256
  `77854013e68cce505394ae5d2aa08dcecc2259f79aef6e82de862bc2d2953ff5`.
- Recomputed both real npm tarballs' SHA512 and matched registry integrity.
  Verified every extracted published byte against the corresponding tarball:
  55 files per version, no additions/removals. Only `package.json`,
  `dist/serve-static.js` and `dist/serve-static.mjs` differ. Package manifest
  changes only version; exports, engines `>=18.14.1` and Hono peer `^4` remain.
  Both built entry points add rejection of any decoded single backslash before
  filesystem resolution, addressing the documented re-segmentation boundary.
- Independently parsed complete old/generated lock JSONC. Only package record
  `@hono/node-server` changes 1.19.14→1.19.15; the new adapter override is the
  only other graph difference. All other records, workspaces and graph metadata
  match exactly. Generated lock SHA256
  `540c5f2823b0116ab497819432ba54246dde1b7c9ad6cd085338829d85bde8d8`,
  Git blob `1a0791b4bfb849e2345d087ddfebde2c33a59f74`.
- Inspected saved npm HTTP200 metadata and actual tarball receipts. Registry
  lists stable fixed 1.x versions 1.19.15 and 1.19.17; 1.19.15 is the minimum
  published choice. The old local HTTP403 and GitHub tag404 are explicitly
  inconclusive and do not justify a major upgrade.
- Read the actual SDK1.31.0 manifest range `^1.19.9 || ^2.0.5` and saved Node
  22.23.3 parent check. 1.19.15 fits without SDK/app changes; 2.x is unnecessary.
- Ran Node syntax checks on both new CommonJS fixtures and Python AST parsing
  of `evidence.py`; all passed without importing candidate packages.
- Reviewed the test oracle: native OS assertion, real temporary filesystem,
  raw Node loopback HTTP preserving `%5C`/`%5c`, actual SDK-resolved adapter,
  prefix middleware-call counter, benign/authorized/unauthorized/HEAD/range,
  malformed/traversal/missing paths and real SDK initialize/list/call/errors.
  The same two security assertions must fail specifically on Windows1.19.14;
  baseline harness requires protected-marker exposure with zero guard calls.

## Native Windows baseline and harness corrections

I independently recalculated successful Windows baseline ZIP SHA256
`edb020fb51c6e5d16cf1ea8d4bd2a16408a61130f53d41023a89dbca5d835ef6`,
validated both command receipts against their raw stdout/stderr hashes, and
read the raw TAP, observations, installed-copy and platform evidence. Run
38951595338 at `80d2b11be455f2050b2001de8c6b85ea64a3f218` actually ran
8 tests on native win32/Node22.23.3/adapter1.19.14: six pass, exactly the two
encoded-backslash security assertions fail, zero skipped. Node exits1; the
expected-red controller recognizes precisely that result and exits0. Both
`%5C` and `%5c` return HTTP200/protected-marker with zero prefix guard calls.
The five recorded SDK requests return initialize200/list200/call200/
invalid-call200-with-isError/malformed-JSON400. This proves the library defect
under its Windows preconditions, not an application exposure.

Two earlier unsuccessful attempts remain failures: run38950329394 stops after
frozen install on Python cp1252 decoding of a UTF8 SDK source file, before
contracts; explicit UTF8 reads/PYTHONUTF8 fix the harness only. Run38950795504
runs8 with five pass/two security failures/one SDK harness failure from reusing
a stateless transport. I reviewed the correction to create one McpServer and
transport per request, idempotent cleanup and an assertion of no unexpected
errors. The fresh CI SDK vendor files' SHA256 match all three diagnostic source
hashes exactly. `webStandardStreamableHttp.js` explicitly rejects stateless
transport reuse; its shipped `simpleStatelessStreamableHttp.js` creates each
server/transport per request. The correction retains both static security
assertions and SDK negative cases, with no SDK or application change.

## Security guard and source reconciliation

I actually replayed the current `dependency-security.test.ts` source through
an explicit Node VM assertion adapter: Bun imports/readFileSync and TypeScript
non-null syntax were adapted, but guard logic was unchanged. Twelve controls:
patched1.19.15, newer stable1.19.17 and an extra safe nested copy pass all19
guard tests. Old1.19.14, prerelease, unreviewed2.x, extra old nested copy,
absence and each prior Hono/qs/DOMPurify/Babel regression fail exactly the
intended guard test. This is a Node assertion replay, not actual Bun execution.
Scripts/results: `ns-review-guard-replay.cjs` and `.json`, outside candidate.

I verified all683 blobs in the first executable tree against local bytes.
Compared with the644-blob Babel final manifest, the42 changed/added paths are
restricted to adapter constraints/lock, one unit guard, focused fixtures,
workflows and evidence packet. All122 src files,41 migrations and every other
preexisting blob except package.json/bun.lock/security guard remain identical.
The adopted root lock is byte-for-byte the official preparation artifact.
Current shared HTTP fixture Git blob:
`ab7d4969e08fdd217807608469f62ffc2bdc4cb7`.

## Final corrected execution and audit evidence

I independently fetched GitHub trees for the successful baseline and final
executable commit. Both HTTP fixture blob `ab7d4969e08fdd217807608469f62ffc2bdc4cb7`
and controller/helper blob `75ccb0e2954c46b92ef265dcb37b7d90b25b5624` are identical.
Thus the before/after comparison uses the same eight cases and the same
strict count/observation oracle; no result is obtained by weakening assertions.
Compared all700 blobs of the final executable manifest against the working
snapshot: every executable/config/application/migration blob matches. At review
time only three packet evidence files were being replaced for docs-only delivery.

A first corrected Windows attempt at the earlier source stops before contracts
on the strict `bunfig.toml` byte equality check because checkout converted LF
to CRLF. I recomputed its ZIP SHA256
`a55306788a220c5c36d5b0bfcf81caccd5a1eb56cea4f36a5d605a5041c5aa2f`,
confirmed it has frozen/platform/source evidence but no contract results, and
read the failing raw log. The final Windows workflow sets
`git config --global core.autocrlf false` before checkout. It retains exact-byte
checks, package/lock/helper/fixture blobs and all security assertions unchanged.
This failed run receives no behavior credit.

Final run38952644379 at the exact source above:

| Platform | Job | Actual result |
| --- | --- | --- |
| Native Windows |117147589438|SUCCESS; frozen/whole graph/actual copy/SDK peer/engine checks; 8/8 HTTP contracts, zero skipped; source intact|
| Ubuntu |117147589979|FAIL only at complete audit with actual exit1; frozen/graph/actual copy, 8/8 HTTP contracts, all10 Bun mutation controls, affected lint and source intact pass|

I independently recalculated both artifact ZIP SHA256:

- Windows artifact12069590089:
  `cd3b61170cc04acf968d7ec44621624ac25bab373d451377e194aa9bfcfd79e5`.
- Linux artifact12068253846:
  `7402333fe4bc4ef5d3949507eb7a08e586540e521a19c57736baf0ae90a2e802`.

All15 final command receipts' stdout/stderr hashes match their raw bytes. Both
platform observations identify actual installed1.19.15, one locked/physical copy,
SDK1.31.0, Hono4.13.7 and Node22.23.3. Both `%5C` and `%5c` now return404 with
zero prefix middleware calls and no protected marker on native Windows. The
benign/authorized/HEAD/range/POST/error and SDK contracts remain green. All
three actual installed SDK vendor files match baseline bytes and diagnostic
hashes on both final platforms.

I independently parsed the complete raw final audit JSON rather than trusting
the summary: exactly one esbuild Low advisory GHSA-g7r4-m6w7-qqqr remains,
GHSA-frvp-7c67-39w9 is absent, no new advisory and no Critical/High record. The
delta removes exactly the target from the previous full audit. The real Bun1.4.0
scanner exit1 and Linux job failure remain preserved; no waiver or suppression.
Raw Bun mutation outputs show patched19 pass/0 fail; all nine negative controls
show18 pass/1 fail specifically at the intended package guard. These are CI
executions inspected by the reviewer, distinct from my independent Node replay.

I directly fetched GitHub verification and Quality job/step metadata and read
the saved Quality log. Quality38952653426/job117147620305 is SUCCESS:65 unit
tests/145 expectations including all four existing MCP cases, eight actual
wrapper scenarios using a stub entry and67 dummy browser containment scenarios,
typecheck, changed-source lint and both approved builds. GitHub commit metadata
for its synthetic checkout `7cdcfd1871a9f54a533567f7ef308908cb0c35af` gives
tree `a2405b8051fbeeba6e966188369c180c7e3e57c6`, exactly the tested source tree.
This is a test-only synthetic ref, not a merge. Existing lint debt is not erased
by changed-source lint success.

Independent remote proof is saved outside candidate as
`ns-review-remote-proof.json`; Node guard replay remains separately saved.

## Findings and remaining gate blockers

No new Critical/High/Medium/Low engineering finding in this bounded delta.
The three harness/checkout failures above are corrected with preserved raw
evidence and zero product/SDK/security-oracle relaxation. They are not passed
runtime evidence. Existing residual esbuild/lint and unaccepted G0/G1 are
recorded blockers, not introduced findings or approval exceptions.

## Execution limits

No local Bun or candidate node_modules exists. I did not independently run
frozen install, actual adapter/SDK HTTP execution, native Windows tests, Bun
security tests, audit, application typecheck/build, browser, database or live G1.
I did not borrow another project's dependencies. I inspected the supplied final
CI records, raw streams, receipts and remote job metadata; these CI commands were
not independently rerun by the reviewer.

## Scope and acceptance limits

Hono, qs, DOMPurify, Babel and esbuild remain unchanged in the generated graph.
No application, SQL, finance, production, merge or deploy activity is authorized.
Esbuild, inherited lint and overall G0 remain separate; final-source identity
reconciliation and affected G1 rerun on the final lock remain prerequisites.
Historical live G1 evidence must not be attributed to this lock. Library
reproduction does not establish that the application exposes the vulnerable
static configuration.
