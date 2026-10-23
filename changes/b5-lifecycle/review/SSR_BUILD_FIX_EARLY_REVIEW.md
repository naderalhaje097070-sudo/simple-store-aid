# Independent bounded SSR build correction review

Disposition: no blocking source finding in f34f55072be5ae401e25c6cfaecd7986ff958aac. This is an early source/build-evidence disposition, not B5/B6 acceptance. Current same-source runtime and final independent evidence review remain required.

I independently fetched the actual GitHub f34f commit, its parent8c88ca7b06dbe80fc7d705bc09ed5103f8546eca and complete non-truncated tree ddccd95372cb7d086d75a8c40f3939b61bbdcf42. Local reviewed vite.config.ts, ssr_runtime.py, graph.mjs and B manifest bytes hash to the published Git blobs. All376 snapshot blob/mode entries match that tree. All50 SQL remain exact against accepted93fa source, and frozen A remains b79640f400a32924f114e19ec51a728be94b6afd. Relative to93fa there are no prior path deletions; only pre-existing vite.config.ts and the B manifest change. Package/lock, generated handlers, SQL, auth/business handlers and original historical workflows remain exact. Removing the newly introduced temporary graph experiment workflow retires no historical acceptance workflow.

The persisted correction is limited to vite.environments.ssr.build.rolldownOptions.output.codeSplitting=false plus explanatory comments. The actual B5 SSR default build now invokes the retained graph oracle on its own output before runtime scenarios and requires zero detected direct-eager helper cycles. Matching200, desktop/mobile authenticated UI, named target conflict, process/egress evidence and cleanup expectations remain present. No assertion was relaxed into a generic500 or static-only acceptance condition.

I independently read GitHub run39955964137, both successful source8c88 jobs120421750997/120421751144 and their upload logs. I independently recomputed raw archive SHA256s and checked every extracted member against each raw archive:

| Variant | Artifact | Raw SHA256 | Modules | Structural / direct-eager cycles |
| --- | --- | --- | --- | --- |
| baseline |12502751179|69c1fba2229ee2e91aa83634dcf84820cd0a7a3a1f042d30a6c90af2117f17ec|64|2 /2|
| single SSR |12502148249|b115ca89172b2bf8b4464fab4d8d0cf2c0ab1c722150da6bc3b7f248a7164b34|35|0 /0|

All49 public file paths/hashes are identical between the controlled variants. Emitted server JS bytes are5,224,870→5,229,436 (+4,566). Both record Vite8.1.6 with nested Rolldown1.1.5, Nitro3.0.260603-beta and root/Nitro-resolved Rolldown1.1.0. The experiment has no database/app/provider execution and restores the source configuration before strict identity verification.

Baseline emitted _ssr/ssr.mjs defines __commonJSMin with an ArrowFunctionExpression and exports it as r. Two consumers directly call the imported helper at module scope and participate in static backedges through router-core/react-router/react-query. Candidate moves the helper to _runtime.mjs, which has no local module dependencies or dynamic imports. It still imports external node:module; “dependency-free” should be corrected to “emitted-graph leaf without local module dependencies.” Parent acknowledged that documentation precision correction for the final packet. This shape plus the actual prior native TypeError strongly supports the initialization-cycle diagnosis; these graph records alone do not prove runtime success or universal evaluation-order properties.

All three earlier graph accuracy findings are addressed in actual published graph blob321a8729a9b712181c2892e44a81c345e3be2005: export-all static edges, separate direct module-call versus deferred-call scope, and Nitro-specific resolved Rolldown provenance. The oracle is intentionally bounded: IIFEs, unknown aliases and general interprocedural execution are not classified eager. It must retain that limitation and cannot replace native runtime coverage. Candidate helper placement eliminates the observed emitted local cycles, independently of those wider limitations.

Remaining gate: review f34f actual fresh/populated upgrade/billing/Cloudflare SSR results and raw artifacts, source identity, egress/cleanup plus current G0/B1/Bdep evidence. No claim of cold-start improvement, deployed Worker limit compliance, production/provider execution, PR readiness, whole-B acceptance, merge or deployment follows from this review.
