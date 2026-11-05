# Independent first-assertion diagnosis review

Actual separate reviewer: `/root/assertion_review`; read-only. No source/test/financial changes, new native run or GitHub writes by reviewer.

Personally recomputed both original archive SHA256 digests and parsed the original run42125234643/source122d8aa4. First and sole false check: desktop_final_day_close_independent_oracle, ordinal58fresh/59upgrade; all57/58 earlier rows PASS. Five fields match (275sales,225collected,5expenses,0debt,0custody); only realized_profit130expected/135observed differs. Prior profit-display-after-expense and close_day_success PASS.

Independently scanned all55 migration files at exact executable122d8aa4. Seven historical close_day definitions; last is20261010223557_enforce_live_account_state.sql, no later mention. Current SQL stores payment-weighted item margin without subtracting expenses, while app.tsx370 and2546–2553 subtract expenses. Confirmed storage/UI semantic mismatch with difference5 equal to expense. DECISIONS/current C5 INTAKE do not explicitly authorize choosing a new canonical field meaning or changing SQL/oracle. No cash-loss/collection-defect conclusion.

Verdict: **diagnosis/extraction accepted in scope**. WholeC5 remains blocked; no fullC6, merge or release approval. Mobile and later network condition not accepted. Findings derive from saved isolated-run receipts and source inspection, not a live/production DB read or a new execution.
