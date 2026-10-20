# Test impact

Run original tests with native Bun1.2.14, matching Quality workflow. Run frozen install, typecheck, full lint and isolated build. Preserve baseline failures rather than changing unrelated application code to make them pass. Add a locked dependency advisory guard before the update; demonstrate failure on the original lock then success on generated patched lock. No financial DB harness executes.

Final diff lint is a separate check from the repository-wide lint debt. Record each real exit code. Hosted checks that never start are unavailable evidence, not passing tests. Independently review the final tree and document missing runtime/tenant/exploit proof.

## Final evidence

Original native26 tests pass. Final29 tests pass, including3 locked-package guards. Seroval guard separately failed before its fix. Native typecheck/build/frozen install pass; full lint remains1117errors/13warnings. Changed-file lint still fails on /app's340pre-existing errors/1warning; direct before/after ESLint comparison proves zero added diagnostics. Preserve this failure, do not globally format or waive it. Bun1.3.14 generated the final lock with the existing release-age policy; Bun1.2.14 compatibility was checked but it cannot enforce that resolution policy. See VERIFICATION.md and evidence.json.
