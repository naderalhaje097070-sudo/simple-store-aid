# Security impact

The original seven findings cover compressed-body trailing bytes, constrained-collection validation work, four URI-normalization boundaries and serializer function-source escaping. Their official patch versions are recorded in intake. Later qs comma serialization and returned-object prototype findings are addressed by qs6.16.1 and actual removal of deepmerge from the graph.

No advisory ignore, audit threshold, release-age exception, fake fixed version, downgrade or source-identity waiver is introduced. Official metadata, actual tar SHA512, release age of at least86400seconds and the pinned Bun generator are checked. The complete current supported audit must return{} with exit0.

Focused tests remain bounded and local, with normal-data controls. The first body-parser comparison failed honestly because32KiB did not reproduce; the official100KiB shape reproduces a native decoder failure on the exact old2.3.0 source, while patched health/raw-consumer assertions pass. All failed evidence is retained. This is local library evidence, not a live service exposure claim.
