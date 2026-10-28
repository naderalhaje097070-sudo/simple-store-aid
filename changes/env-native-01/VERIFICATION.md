# ENV-NATIVE-01 preparation verification

Candidate only, not an authorization fix, isolation acceptance, merge or release.
Exact baseline PR56 b9aa56bc3bb30948d95961c06fd493dfb866f476; final published
SHA/check/PR identities are recorded in issue #55 and this batch's draft PR.

## Actual scoped execution

Python3.12 scratch runtime, UID0, no database target contacted:

```text
python -m unittest discover -s tests/account-lifecycle -v
9 test methods passed; 25 parameterized subcases included.

python tests/account-lifecycle/evidence_guard.py \
  changes/primary-env-001/native-runner/auth-tenant-probe.json \
  --expected-source 84c3444fcdf5fa2825809192cda5b15561c950cf
exit1: ENV_NATIVE_01_PRE_BAN_JWT_STILL_READS_OWN_TENANT
```

The expected failing assertion consumes unchanged historical evidence. It is not a
new Auth/RLS execution or an accepted clean Gate4 baseline. The fixture conflicts
stay22/2. CLI wrong-source validation returns2, distinguished from security failure1.
Unit cases cover contradictory acceptance, missing controls, corrupt counters/types,
duplicate names, unexpected5xx and successful bounded denial without integration
acceptance. 15 corrupt-evidence +8 failed-prerequisite +2 CLI subcases; other tests
are separate named methods. Synthetic cases are oracle tests, not real user sessions.

Inventory generation actually executed from the source-pinned scratch snapshot:

```text
python build_inventory.py --source-root source --tree remote-tree.json \
  --output candidate/changes/env-native-01/source-inventory.json
python candidate/changes/env-native-01/inventory-generator.py \
  --source-root source --tree remote-tree.json --output inventory-reproduced.json
```

Output identical byte-for-byte. A deliberately wrong migration blob hash was rejected
before output. To reproduce from a full checkout, fetch the recursive GitHub tree
for the exact PR56 baseline into an external JSON file, then run the committed
generator with `--source-root <baseline-checkout> --tree <tree-json> --output <path>`.
Generator checks complete migration/app file sets and every selected blob; discovery
is lexical and retains historical/dynamic events, not an effective SQL catalog.

195 locally available scoped source blobs matched PR56; required current AGENTS,
state/tasks/decisions and claim comments were read directly from GitHub. Archived
probe blob3d46821edf9fdeae9f4f9b8299904c107bc3b7a9 was independently matched.
Inventory:41 migrations,380 discovery events,73 app sites. All scoped CREATE FUNCTION/
CREATE POLICY/DROP POLICY lines were reconciled against discovery locations.
Python AST parsing passed. Publication validator checks prior document-byte retention,
allowed file scope, inventory provenance, relative Markdown targets, secret patterns,
source hashes and changed-diff whitespace. Actual result in evidence.json.

## Retained failures and limits

Initial scratch verification invoked relative paths from the wrong directory:
the archive copy failed, then seven tests errored on missing fixture. After copying
the source-matched archive, seven tests passed. A later wrong-directory discovery
failed before tests; correcting working directory ran the final nine successfully.
These are scratch harness errors, never application expected-red or passing evidence.

Existing Quality342 attempt2 and Quality343 are successful historical runs on their
own exact heads. No manual rerun or application-wide local suite repeated. A new
automatic Quality run, if triggered by this draft, is reported separately; it does
not discover these Python tests or prove live lifecycle behavior.

Not executed: new database/HTTP/MCP/RPC/Auth-refresh/disabled-staff/admin integration,
fresh/upgraded migration, performance, in-flight disable, financial write/concurrency/
idempotency/rollback suites. No migration, runtime permission fix, generated app
edit, cloud project restore/create, production data/secrets, cost, merge or deploy.
Independent review is pending. High lifecycle blocker remains open.

## Acceptance and next action

Preparation packet, offline oracle and source discovery: implemented/tested in draft.
Live Gate4 baseline, authorization correction and isolation acceptance: not verified.
Rollback: close draft, or additive packet revert after any separately approved merge.
ONE NEXT: owner approve CHANGE_INTAKE and L01–L15 scope, then clean isolated lifecycle
baseline on a verified disposable runner. Financial writes still await isolation.
