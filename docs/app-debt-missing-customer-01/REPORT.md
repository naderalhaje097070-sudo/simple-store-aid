# APP-DEBT-MISSING-CUSTOMER-01

Bounded UI repair on existing Draft PR72 in `naderalhaje097070-sudo/simple-store-aid`.
Base `42ef3866e2c6772b5aa6f0b230df2d562cf5d4ed`; executable source
`82623c7189de21c0a03c5e4b3b6539ff5c74320e`, tree
`cdcd9d3ecc16785fa578a7afefe24c6cb6e58431`. Application blob
`6c73cdc377a9bbf9f2566ff5570b925c0af115ff`, SHA256
`2ca5387bfba5b4a1d48fc0e46ca4131f8ac7bbdbed18db7dd7a16656172770a5`.
Final documentation-head identity belongs in the #70/#55 handoff; do not equate its
changed documentation tree with the executable test tree. No main-branch fix or
release is claimed.

## Behavior and scope

The existing debt list groups invoices by customer ID. Its metadata lookup could
return undefined, and clicking the row threw TypeError. The detail screen also
matched invoices through the optional customer lookup, so missing metadata made a
known debt look like zero. This was reproduced using actual extracted React
screens and synthetic invoice100/paid40/debt60, not production data. The first
probe had an incorrect expected text occurrence count; it was corrected to count
both total and invoice remainder. Product code was not changed to pass that probe.
The original failed behavior, diagnostic scripts and receipts are archived.

Only `src/routes/_authenticated/app.tsx` changes in application source:

- Existing query `isLoading` flows into the local screen context, without changing
  shared AppCtx, query data/keys/options or calling another data source.
- Missing customer rows retain their amount and contribution to the total; they
  show actual loading or unavailable copy and block invalid activation. The click
  handler also returns safely before setter/navigation.
- Details associate invoices with the already selected customer ID, preserving
  the existing finance selector and sum. Missing/disappearing metadata leaves the
  known60 visible, shows a status and Back, and disables collection/contact
  controls. The collection handler returns before invalid navigation.
- Without a customer or matching invoice evidence, the unavailable screen does
  not invent a zero or fallback customer/ID. No claim of deletion is made.
- Present customer setter/navigation order and financial operations stay intact.

No formulas, data calls, RPC payloads, financial contracts, sale, collection
backend, settlement, inventory, SQL/migration, permissions, dependencies/lock,
esbuild exception, generated file, Hook dependency, lint rule or ignore change.
Focused tests and the required intake/impact/evidence/checkpoint documents are
added. No extra lint cleanup, audit, historical advisory suite or G1 rerun.

## Actual local verification

All commands run from the repository root using Bun1.2.14/Node24.19.0:

| Check | Actual result |
| --- | --- |
| `bun install --frozen-lockfile` | PASS on original unchanged lock after verified package cache population |
| affected ESLint and changed-source Quality ESLint relative to base57fb508b | PASS,0errors/1 existing tenantTz useMemo warning |
| `bun run typecheck` | PASS |
| `bun run test:unit` | 66PASS/0FAIL/174expect |
| `bun tests/gate4/sec-env/server-boundary.ts` | 8 actual wrapper scenarios PASS; stub app/no DB |
| existing browser-network.py | 67 scenarios/0FAIL, dummy loopback fixtures |
| existing mode-env build and normal isolated build | both PASS |
| `git diff --exit-code --` after generation | PASS, no tracked generation changes |
| new component UI build.ts/browser.py | 9/9PASS,0pageerrors/0HTTP or WebSocket attempts |
| independent reviewer replay | own9/9PASS, same application hash |

New UI scenarios: absent row/retained60, initial loading then appearance, loading
ending persistently absent, present customer normal navigation, absent details
with Back/retained60, disappearance in details, detail recovery, absent selection
without an invented zero, and exclusion of other-customer/unassigned/returned/
pending-courier invoices. Exact setter/navigation effects are asserted. The real
screen declarations and actual Money/TopBar/EmptyState/finance selector are
bundled with synthetic props, not copied implementations. No backend is imported.
See `tests/app-debt-missing-customer/README.md` for runnable commands.

Installation/bootstrap limits: initial original-lock fetches from Lovable cache
returned403. An external manifest/lock copy redirected only artifact prefixes to
public registry.npmjs.org, retaining all versions/integrity hashes; its frozen
install succeeded. The subsequent original-lock frozen install succeeded using
that verified cache. This is not a second clean remote original-registry install.
No TLS/integrity verification was disabled and no repository lock was edited.

First local browser-containment attempt failed because the expected Playwright
headless-shell executable was absent. The repository-supported
`MONGEZZ_BROWSER_TEST_EXECUTABLE=/usr/bin/chromium` override succeeded on Chromium
154.0.8037.57. Initial global Python had greenlet3.5.5; all pinned requirements were
then installed in an external venv (Playwright1.62.0, pyee13.0.1, greenlet3.5.6,
typing-extensions4.16.0), and affected67+9 browser cases passed there. Local
system-browser runs are distinguished from native hosted browser installation.
Build warnings, including PWA zero-precache warnings, are retained; offline
behavior and visual/accessibility parity are not newly accepted here.

## Native hosted Quality

Unchanged existing workflow [Quality39120188797](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39120188797),
attempt1, job117654045458: **SUCCESS** on source82623c7,
2026-10-18T10:40:36Z–10:42:27Z. Actual API job/step metadata confirms every required
step completed successfully: original-lock frozen install, typecheck,
changed-source lint, unit tests, offline server boundary, pinned Python/browser
installation, browser containment, both isolated builds and tracked generation
invariance. The new standalone nine-case UI regression is local and independently
replayed; unchanged hosted CI does not execute it automatically.

Raw native job logs could not be downloaded: the Actions API redirects to
productionresultssa13.blob.core.windows.net, blocked403 by the network proxy.
Signed redirect URLs are not saved. Thus native exact test counts and checkout
SHA are not claimed from logs; the66/8/67 counts above are directly captured local
results. Full step metadata and local raw outputs are retained. No synthetic
passing log was substituted for the unavailable native log.

Read-only Git/API comparison independently verifies the current PR synthetic
merge3e122695fe40d546812b098574f4a722c8f94edb, parents57fb508b+82623c7, has tree
cdcd9d3ecc16785fa578a7afefe24c6cb6e58431 exactly matching source82623c7. This is
current merge-ref reconciliation, not a log-derived proof of the exact checkout
used by that job and not an actual merge. Final documentation commits preserve
all tested application/test bytes; they are not credited as a new native run.

## Review and acceptance limits

Independent reviewer read the implementation and ran the nine cases separately,
verified actual locked QueryObserver isLoading semantics, and inspected the
unchanged finance/data/dependency/config paths. No introduced blocker found in
this authorized UI scope. See INDEPENDENT_REVIEW.md for exact commands, hashes and
limits. This is not overall G0/integration/release approval.

The component harness does not run full MongezzApp/authentication/live Supabase,
the complete app navigation stack, invoice-detail collection/RPC or stored-money
journeys. Present-customer collection evidence proves unchanged navigation
intent, not successful financial writes. Query status plumbing is source-reviewed
and typechecked; QueryObserver semantics are independently checked, not credited
as a live app query lifecycle test. Unrelated invoice-read failures and their
potential false-zero display remain a separate existing risk. No production
secrets/customer records were used.

## Source/claim and rollback

Owner supplied #55/6241881817 and #70/6241876391 to permit local implementation
while API was blocked. Access later actually recovered: read all105 comments in55
and21 in70, verified OPEN/DRAFT72/head42ef3866/base57fb508b and no newer claim.
Known financial candidates49/50 still had the unrepaired pattern. Registered sole
claim55/6248860942 before fast-forward publishing executable source82623c7 to the
same draft branch; no new PR or history rewrite. Only Quality was triggered;
path-filtered G1/historical advisory workflows did not run. Do not attribute API
readiness merely to a saved draft setting.

Rollback is an additive commit restoring app.tsx alone from42ef3866 while retaining
prior security fixes, lock, evidence and history. It reintroduces the demonstrated
fault; no database compensation. No merge/deploy/production/main changes.

ONE NEXT after this delivery: planning resumes remaining bounded G0 lint cleanup;
.cjs coverage and source identity/affectedG1 reconciliation remain separate. G0,
integration and release acceptance stay open.
