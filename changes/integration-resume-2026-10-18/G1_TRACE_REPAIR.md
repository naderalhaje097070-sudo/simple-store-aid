# G1 observer repair — bounded candidate

Parent tested source: 44df8e888c966e12ae26900e254b41c7fe1b17d0.

G0 run39171846911 passed. G1 run39171846934 failed: 39/40 required checks, only bounded_egress_trace_collected false. Conflict process lineage read_failed was true; trace parsing was complete, unmapped nonloopback TIDs empty, native packet counters unchanged (IPv4 1→1, IPv6 0→0). SSR/Auth, exact named configuration500,22table fingerprints, secret scan and cleanup4/4 passed. This is a failed G1, not acceptance. Artifact12152967146 SHA25603a8366bf79cd9ce83efd87b02a85170116ce3d4a2543c2e957090b22906fd9e remains preserved with original logs.

Historical read-failure cause is unknown: the prior receipt stored only a boolean. Separately, a reproduced ProcessMap bug marks a terminal zombie as unreadable, and misses live threads when their group leader has terminated. Original7fixture tests:5pass,2fail; updated10fixtures:10pass. Existing9privacy/delegation tests pass locally. Local live-strace is blocked by host PTRACE_TRACEME policy, not passed; native CI retains that mandatory precredential check.

Repair: enumerate individual task status before executable lookup; resolve live task exe; confirmed terminal tasks get bounded typed lifecycle metadata without fabricated identity rows. Vanished task races remain unmapped. Live unreadable identity, timeouts, malformed metadata and scan failures still latch failure. Failure receipts contain only bounded enum categories and integer TIDs, never stderr/cmdline/env/raw executable paths. A terminal observation cannot satisfy nonloopback attribution. All runtime.py/firewall/counter/completeness/cleanup assertions are unchanged. Parent app, SQL, lock and dependency versions are untouched.

Native followup result pending at this commit. Do not infer the historical cause from a later successful replay. Overall integration_accepted=false. No merge/deploy/production/provider call. Rollback: forward revert these observer/workflow/test changes plus a matching exact manifest, preserving this failed evidence.
