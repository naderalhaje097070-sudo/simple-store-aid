# Rollback Impact

For an unmerged candidate, use additive commits reverting only this batch constraints/complete lock/security fixtures and checkpoints to starting5cbf198. Do not rewrite history, revert prior Hono/qs/DOMPurify/Babel fixes or deploy a vulnerable rollback. Re-run frozen/graph/affected checks after any reversion. Preserve evidence. Planning owns esbuild/lint/integration next; final-source identity reconciliation and affected G1 rerun remain mandatory.

For a reviewed pre-merge candidate rollback, inspect the intended branch then
restore only the product dependency delta and its new guard from the start:

```bash
git restore --source=5cbf198d88b0f091a30371676fb09abf92903dc8 -- package.json bun.lock tests/unit/dependency-security.test.ts
bun install --frozen-lockfile
bun run test:unit
```

Review and commit that additive change, recording that it reintroduces the
adapter advisory and invalidates this candidate verification. Retain this
evidence packet and focused fixtures for analysis; no vulnerable deployment.
Any subsequent candidate requires new graph/audit/affected runtime proof.
