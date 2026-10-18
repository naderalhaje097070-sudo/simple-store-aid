# Changed source paths

Exact GitHub compare original72 6da4dad…tested823cbcaf;60 paths. Additive final report/evidence/three state documents are documentation only, listed by their publication commit. This list describes source changes, not an independent approval. No bun.lock, SQL or dependency-version delta.

| Path | Reason |
|---|---|
| .github/workflows/g01-runtime-retry.yml | Actual native acceptance/coverage/invariance; manual retirement of temporary preparation preserves its assertions |
| .github/workflows/integration-g0-inventory.yml | Actual native acceptance/coverage/invariance; manual retirement of temporary preparation preserves its assertions |
| .github/workflows/integration-verification.yml | Actual native acceptance/coverage/invariance; manual retirement of temporary preparation preserves its assertions |
| .github/workflows/quality.yml | Actual native acceptance/coverage/invariance; manual retirement of temporary preparation preserves its assertions |
| changes/integration-g0-g1/GENERATED_INTAKE.md | Intake/scope/history/failure evidence |
| changes/integration-g0-g1/INTAKE.md | Intake/scope/history/failure evidence |
| changes/integration-g0-g1/TYPE_INTAKE.md | Intake/scope/history/failure evidence |
| changes/integration-resume-2026-10-18/G1_TRACE_REPAIR.md | Intake/scope/history/failure evidence |
| docs/g0-node-server/review-guard-replay.cjs | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| package.json | Repeatable generated-output normalization and real build failure/argument propagation; no dependency version change |
| scripts/build.mjs | Repeatable generated-output normalization and real build failure/argument propagation; no dependency version change |
| scripts/format-generated.mjs | Repeatable generated-output normalization and real build failure/argument propagation; no dependency version change |
| scripts/generated-format-manifest.json | Repeatable generated-output normalization and real build failure/argument propagation; no dependency version change |
| src/components/DateRangeFilter.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/domain/finance/invoice-selectors.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/inventory/AddProductSheet.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/invoices/InvoiceDetailScreen.tsx | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/features/layout/TopBar.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/shared/EmptyState.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/shared/Sheet.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/shared/StatusChip.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/shared/Toast.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/features/shared/types.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/hooks/useTheme.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/integrations/lovable/index.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/integrations/supabase/auth-attacher.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/integrations/supabase/auth-middleware.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/integrations/supabase/client.server.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/integrations/supabase/client.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/lib/business-types.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/db.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/lib/invoice-pdf.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/lib/mcp/tools/list-customers.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/mcp/tools/list-products.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/mcp/tools/list-recent-orders.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/mcp/tools/today-summary.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/paddle.server.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/lib/paddle.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/lib/pwa-register.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/routes/[.]lovable.oauth.consent.tsx | Deterministic handwritten formatter-only; source/type/runtime/meaningfulJSX/comments preserved |
| src/routes/[.mcp]/invoke-tool/$tool.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/routes/[.mcp]/list-tools.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/routes/[.well-known]/oauth-protected-resource.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| src/routes/_authenticated/app.tsx | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/routes/_authenticated/billing.tsx | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/routes/api/public/payments/webhook.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/routes/guide.tsx | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| src/routes/lovable/email/queue/process.ts | Locked contract/type refinement; nullable stored-item propagation; proven emitted-runtime equivalence except explicit TypeError messages/aliases; formatter where applicable |
| src/routes/mcp.ts | Known generator output normalized through reviewed postprocessor; source/type/runtime equivalence |
| tests/g0-integrated-types/runtime.cjs | Type/runtime callback and build failure regression proof |
| tests/g0-integrated-types/test_build_entry.py | Type/runtime callback and build failure regression proof |
| tests/g01-acceptance/capture.py | Exact committed source snapshot and negative identity fixtures; legacy guard retained |
| tests/g01-acceptance/dns_trace.cjs | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| tests/g01-acceptance/egress_trace.py | Bounded live-task lineage observer and privacy/fail-closed regressions; runtime gates unchanged |
| tests/g01-acceptance/integrated-source.json | Exact committed source snapshot and negative identity fixtures; legacy guard retained |
| tests/g01-acceptance/integrated_identity.py | Exact committed source snapshot and negative identity fixtures; legacy guard retained |
| tests/g01-acceptance/test_cf_fetch.cjs | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
| tests/g01-acceptance/test_integrated_identity.py | Exact committed source snapshot and negative identity fixtures; legacy guard retained |
| tests/g01-acceptance/test_process_map.py | Bounded live-task lineage observer and privacy/fail-closed regressions; runtime gates unchanged |
| tests/unit/invoice-selectors.test.ts | Deterministic formatter-only; source/type/runtime/JSX/comments and existing suppressions preserved |
