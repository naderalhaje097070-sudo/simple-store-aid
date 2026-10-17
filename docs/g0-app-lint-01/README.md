# G0-APP-LINT-01 evidence

- REPORT.md: outcome, exact tested source, native Quality, limits/deferred issue/rollback.
- INDEPENDENT_REVIEW.md: separate review, direct source/run/log identity checks and actual replay scope.
- evidence.zip: exact captured source snapshots,17->0local diagnostics, baseline native lint/candidate native log excerpt, whole native Quality log/run/job/tree identity, complete static proof and focused independent reviewer diagnostic. Archive141352bytes, SHA2562d3a83fdc5de8c890a959d936bc0d16c83e41506e49893d8da1afa1892253404; Gitblob299e15219c6d3acb542732be89dd10e7e3bc832d.
- SHA256SUMS.json: per-file hashes and sizes inside archive plus archive digest. No credentials or real tenant data used.

Native [Quality39072945731](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/39072945731) succeeds on executable sourcee58bc5db; synthetic checkout4691f1c has identical treee8cb804c. Documentation-head identity is supplied by final70/55/PR72, not inferred as a native rerun.

Extract archive in a disposable directory; it creates app-lint-work/. The proof needs TypeScript and Babel parser from an existing verified project dependency tree: from extraction parent, set APP_LINT_MODULES to the absolute node_modules directory with trailing slash and run `node app-lint-work/evidence/behavior-proof.cjs`. Reviewer diagnostic is `node app-lint-work/review/independent-replay.mjs`; it resolves its preserved snapshots relative to itself. These ephemeral diagnostics do not install dependencies or contact a database. Local parser7.29.2 is disclosed; native Quality uses the actual frozen graph.

Failed proof/control collection details are retained; no financial/RPC/Hook/source changes followed the tested source. No full lint reclassification, liveG1/advisory-suite/audit rerun or merge/deploy. Existing Medium missing-customer fault and useMemo warning remain separate; Quality success does not close G0.
