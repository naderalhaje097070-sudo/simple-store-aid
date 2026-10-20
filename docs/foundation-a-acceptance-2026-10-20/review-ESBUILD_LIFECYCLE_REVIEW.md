# A7 addendum — historical esbuild workflow lifecycle

**Outcome: Approved for human merge within package A** for source **51b09a6f33a672704f8424cbf2bbed7a2be682ca**, tree `923cd6035c5ee102e159e8035d520ba7e6fd1a3f`. No new Critical/High/Medium/Low defect was established. The earlier application review and exact c789 documentation verification remain preserved; this addendum reviews the subsequent bounded CI change.

I independently fetched the c789→51 comparison, complete trees, workflow, verifier, original/current manifests, dependency guard, original proof records and actual failure logs. Both jobs in run39396201730 checked out c789, completed frozen installation, then failed at `tests/g0-esbuild/evidence.py:48`, which requires the entire package manifest to equal baseline1b7a after removing the esbuild pins. The preceding lock-graph assertions passed; installed-consumer, native security and later proof steps were skipped. This remains a failed current-head historical-proof run.

The original accepted candidate73e133 and current51 package manifests differ only in scripts: the reviewed build wrapper and generated-format command. Dependency fields, overrides/resolutions, complete lock and bunfig are unchanged. Original native proof39026053191 is independently confirmed SUCCESS on exact73e133; its results are not relabeled as current-source Windows execution.

The new workflow has only `workflow_dispatch`, no arbitrary source input, an explicit historical name, and one checkout pinned to `73e133b25a8a5167c6730eb82cf364268ad44373`. After accounting for that checkout, the full permissions/jobs/commands/assertions text is identical. Linux/Windows matrix, raw child exits, audit failure handling and invariance checks remain. Every esbuild proof test/helper and the exact all-copy/26-platform security guard is byte-identical to the original proof source. Current PR Quality and integrated G0/G1 workflows, frozen installs, full audit and current dependency guard remain unchanged.

Retiring this one-time whole-manifest proof from automatic current-head pushes is justified for this unchanged graph; its manual run proves only the pinned historical candidate. It is not a replacement acceptance gate for later dependency changes or a fresh Windows compatibility claim for51.

| Independent verification | Result |
|---|---|
| Complete protected set and modes |288→288; sole protected blob change is this workflow, same100644 mode|
| Source manifest |Only that workflow entry changes; all288 entries match the51 tree; new manifest blob `b79640f400a32924f114e19ec51a728be94b6afd`|
| App, tests, package/lock/config, all41 SQL and original28 design documents |Unchanged from accepted c789|
| Native G0run39444611013 / attempt1 on51 |SUCCESS, quality+audit; actual read replay43/43, Chromium10/10 with no errors/requests, identity288/41, raw full audit `{}`|
| Native G1run39444611354 / attempt1 on51 |SUCCESS, environment+runtime; actual40/40,22 identical before/after table fingerprints, all four cleanup removals true|

I independently read the G0 quality/audit and G1 runtime logs and actual artifact files. All five downloaded G0/G1 ZIP digests match GitHub artifact metadata for51. In particular quality ZIP SHA256 is `cee93a67e5209d2e3ad5bf2dae81107292eab6df27a7c86ca489ba53b03a6858`; runtime ZIP is `2dc347165776ba8d312e18825be5c271c9a32d2e1d679264b405375ac4955288`. G1 retains `integration_accepted=false` and `financial_flow_executed=false`.

No test, workflow, installation or native replay was started by this reviewer. No source/GitHub mutation occurred. Final evidence-only publication must separately preserve the exact51 protected set/modes, updated manifest and41 SQL. A8 merge remains the owner's decision; B/C and release acceptance remain outside this review.
