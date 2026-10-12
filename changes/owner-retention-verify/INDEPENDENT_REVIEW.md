# Independent limited source/evidence review — OWNER-RETENTION-VERIFY-01

Reviewer: separate agent /root/owner_retention_catalog_review, explicitly requested
by the owner for this batch. No file authorship or branch mutation by the reviewer.
Reviewed runnable source:9a5a58f6a8556f009880437c0cf95ac91c38c770, Draft PR66.
Outcome: **accepted for catalog evidence and planning handoff only**. No closure
behavior, populated financial retention, human merge or release approval.

## Independently performed

- Read SQL/probe/focused tests/workflow and reused snapshot, target, UID firewall,
  read-only psql, HTTP prohibition and secret/quarantine boundaries.
- Fetched immutable probe/workflow from GitHub and matched the reviewed local bytes.
- Reran13focused offline oracle tests, allPASS (after the prepublication fix).
- Fetched original catalog job115028337892/run38314670848 and Qualityjob115028337953/
  run38314670777 logs and statuses directly. BothSUCCESS; only those2runs returned
  for this source. Quality66tests/159assertions/67browser scenarios verified from logs.
- Independently verified artifactZIP SHA256da00685345c6ad613c016d702a150cb043168de39d17b1b8bbfd9a36f0793bb0
  and all4extracted files against ZIP entries.
- Replayed the pure offline reconciliation against the recorded real catalog:
  reproduced239rows/234MATCH/5DIFFERENCE. Verified43migration hashes, actual ordered
  versions, source-map hash, public22stable digests, counts, network and cleanup receipts.
- Inspected effective grants, nullable SETNULL actor references, Auth/Storage objects,
  active-actor functions and named CHECK expressions. Fetched later20260626233231
  dynamicVALIDATE block lines158–175 from GitHub to explain the five initial-expectation
  differences on the fresh empty stack.
- Read the next-batch proposal; requested actual fixture counter snapshots and explicit
  account/store scope + safe idempotent repeat design. Those recommendations were added.

**Not performed:** liveDB/Actions/Quality/browser/lifecycle replay. The reviewer read
the original successful logs and replayed data processing offline, not the provider run.
No production, nonempty fixture, deletion or ban ran in this independent review.

## Findings/dispositions

1. P2, fixed before first live publication: whitespace normalization could equate
   different SQL string literals. Exact body.strip comparison now preserves interior
   whitespace; literal-whitespace regression passes. No evidence was accepted from
   the preliminary unpublished tool object.
2. Recorded oracle limitation: CHECK_METADATA compares name/type/validation, not full
   semantic expressions. Five initialNOTVALID expectations become validated in the
   complete fresh chain. Preserve raw5differences with full-chain interpretation;
   do not manufacture239automatic matches. Seven named expressions manually reviewed.
3. Provider objects, inline/PK/UNIQUE constraints, memberships/default/schema ACLs are
   observed inventory without a previous complete source expectation. Standalone
   indexes and full provider behavior are outside the query, explicitly unverified.
4. Next design: order fixtures can populate tenant_counters; compare actual baseline,
   not forced zero. Account-wide/store-specific semantics and idempotent closed-caller
   result need explicit contract before implementation. No future fixture/implementation
   approval follows from this review. Later-added TRUNCATE disposition is planning-only.

No unresolved tool safety bug identified within catalog-only scope. Effective grant
evidence confirms authenticatedTRUNCATE on21publictables andDELETE on4emailinfra
tables, not an executed attack or demonstrated normal-userAPI reachability. Financial7
zero;21publicdigests empty and originalemail_send_state seedstable; cleanup3/3true,
unexpectedUIDegress0 with backend-provider-service egress caveat retained.

Remaining policy/code gap: no persisted closure state in inspected active predicate;
CASCADE/SETNULL remain. Structure does not prove hard-delete outcomes or safe closure.
Keep closure_verified=false and integration_accepted=false. Final documentation-only
commit must preserve all runnable blobs; its source-equivalence is checked at closure,
not treated as a new live run or an automatic merge review.
