# EXPECTED BEHAVIOR

Each logical UI sale gets one explicit secure UUID, reused for every retry. Persist input before financial RPC with environment/actor/tenant scope. Pending records have no TTL; different operation or mismatched payload cannot replace one. Recover exact saved request after reload/account return; only validated success becomes a receipt. Server always verifies repeated UUID, local receipt never substitutes. Account switching cannot send captured recovery as another user. No auto-abandon/reset of uncertain outcomes.
