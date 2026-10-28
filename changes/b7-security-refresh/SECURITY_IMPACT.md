# Security impact

Baseline: GHSA-27r3-jxmh-p828 body-parser High; GHSA-mrhx-c7xc-m3w5 Zod High; GHSA-w74x-v6f9-j3xg and GHSA-wjr9-j795-jxcr fast-uri Moderate; GHSA-xhq7-xmqj-769h and GHSA-333x-w4r6-6crp fast-uri Low; GHSA-m5mm-p8h7-m29v serialize-javascript Low. Official GitHub advisories give patches2.4.0/4.6.6/3.1.9/7.1.3 respectively. Preparation captures official registry time/integrity.

No ignored advisory, threshold waiver, release-age exception, test weakening or identity bypass. New audit findings remain blockers. Zod early constrainedcollection rejection and serializer function handling need focused compatibility regressions; no generic memory-DoS elimination claim.
