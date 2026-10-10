# Rollback

Before merge: close/delete only the new draft branch if rejected; leave PR48/PR53/main unchanged. No published history rewrite. After an authorized human merge: revert this additive ENV commit through another reviewed PR and rebuild the previous accepted artifact; retain prior known-good environment-specific configuration. Do not relax guards on a live release to work around missing configuration. No DB writes/migrations occurred, so this packet needs no data rollback. Actual deployment rollback remains untested.
