# APP-02 PostgREST serialization retry diagnosis

Actual diagnostic sourcef4e24001/run39612546949: the stream is absent after a rejected updated callback; created returns200 with receipt request/resolved cancel flagsfalse, yet the public flag istrue. This disproves an explanation based only on the created normalizer, independently verified to producefalse. The first updated503 did not establish that its database work was canceled.

The native stack uses ghcr.io/supabase/postgrest:v14.10 (preserved first-native runtime-images). Supabase official troubleshooting documents custom SQLSTATE40001 triggering internal transaction retries onv14, fixed inv16; P0001/PT codes avoid that loop. The observed later update is consistent with a retried missing-stream transaction succeeding after created. This diagnosis is supported by the runtime witness and upstream behavior, not an independently captured pg_stat_activity trace.

Primary sources read21October2026:
- https://supabase.com/docs/guides/troubleshooting/high-cpu-and-infinite-transaction-retries-when-using-custom-error-codes-in-rpc-functions-77326b
- https://github.com/PostgREST/postgrest/issues/3673
- https://github.com/PostgREST/postgrest/pull/4222

Correction: all ten application-domain40001 raises becomeP0001 in a new CLI-generated50 forward replacement. Actual engine serialization failures remain database concerns; application ambiguity exits the RPC, and the existing route returns503 for provider retry. No database/provider/runtime package upgrade or production action is introduced. Applied48/49 remain exact. Each final native stack is newly created, so no old looping request survives. The new regression asserts the refused updated event has no late receipt when created is committed, preserves createdfalse, and only the explicit replay then changes the flagtrue. Existing whole-transaction and ordering assertions remain unchanged.
