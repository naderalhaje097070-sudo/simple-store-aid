# Source provenance

Repository: naderalhaje0970-droid/simple-store-aid only. main reference:43d6edbccb66fb06ce0fcb93734ad59532d1aeae. Base security source: PR53 head54c930166a776828566876771efdec86a997fa53/tree2a0d304a8257de7a4649847b5e02147633180986. Existing isolation source: PR48 head31958e53438b377a9896dd0bf7e9c268c1f14aef, still unmerged and unchanged by this batch.

The original dirty worktree was left intact. A separate detached worktree uses local synthetic baseline71422e5 to represent the verified PR53 candidate source. Remote commit must parent actual PR53 SHA and base its tree on actual PR53 tree, preserving remote evidence files absent from local scratch. Git fingerprints in evidence.json identify tested candidate files without self-referential commit claims. Remote PR body identifies resulting immutable head.

Reused paths: .env.example; four workflows (isolated-auth-smoke, quality, sec-ci-gate4-probe, sec-env-gate4-probe); config/supabase-build-config.ts; src/server.ts; tests/e2e README/auth/rapid/run/sale/shared guard; financial-rules/run.sh; gate4/sec-env/probe.ts; unit/supabase-build-config.test.ts; visual/mobile-rtl-smoke.py; vite.config.ts. Deviation paths/final fingerprints are listed in evidence.json and VERIFICATION.md.
