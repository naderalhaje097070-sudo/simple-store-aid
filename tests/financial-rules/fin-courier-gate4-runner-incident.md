# FIN-COURIER-001 — Gate 4 runner incident evidence

Status: infrastructure evidence only. No test assertion or production behavior is changed by this file.

## Affected exact head

`2e4fa066a16300e9641bb7fe11d721ba233eac73`

On this exact PR #27 head, the following GitHub Actions runs were created but their jobs failed before any workflow step started:

- Quality — run `30251464992`, job `quality`, `steps = None`.
- Ephemeral Financial Rules — run `30251465424`, job `financial-rules`, `steps = None`.
- Isolated Auth UI Smoke — run `30251464908`, job `authenticated-ui`, `steps = None`.
- FIN-COURIER Gate 4 Probe — run `30251464867`, jobs `backend-contract` and `ui-contract`, both `steps = None`.

The failed jobs were re-run on the same exact head. The re-runs reproduced the same pre-step failure pattern.

## Classification

This incident is classified as runner-acquisition / workflow-execution infrastructure failure, not as application, migration, SQL, browser, build, regression, or Gate-4 assertion evidence.

A Gate-4 expected-RED result is accepted only when the harness reaches its named sentinel. `steps = None` cannot satisfy that requirement.

## Purpose of this commit

This evidence-only commit creates a new exact PR head so the intended workflow set can receive a fresh scheduling attempt without weakening tests, editing financial logic, or changing production behavior.

The required workflow set remains:

1. Quality — must be GREEN.
2. Ephemeral Financial Rules — must be GREEN.
3. Isolated Auth UI Smoke — must be GREEN.
4. FIN-COURIER Gate 4 Probe — true-GREEN baselines must pass and target contracts must reach their approved expected-RED sentinels.
