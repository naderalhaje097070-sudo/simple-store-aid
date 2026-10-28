# B3 / AC-02 impact analysis

Root cause: authenticated has table INSERT/UPDATE; owner RLS admits writes to every tenant column. Table grant must be removed before column grants can constrain writes. Explicitly revoke the five protected column writes; grant only the other seven existing columns. No new function, trigger, table or RLS policy. Future columns require deliberate grants. Review effective inherited/PUBLIC permissions at runtime.
