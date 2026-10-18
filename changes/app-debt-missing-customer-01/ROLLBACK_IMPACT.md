# Rollback

Withdraw the application change using an additive commit restoring only src/routes/_authenticated/app.tsx from42ef3866e2c6772b5aa6f0b230df2d562cf5d4ed. Keep prior security fixes/dependency graph/esbuild exception/docs/evidence/history. This reintroduces the known missing-customer crash/false-zero; do not deploy it as a remedy. No database compensation. Do not reset/force-push/merge/deploy. New tests should fail on the withdrawn behavior and must not be weakened.
