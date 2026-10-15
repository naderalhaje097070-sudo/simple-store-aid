# Preserved actual-vendor oracle failures

87c5d97283685fa346d19559a61d8091fba3b4b6 / run38741656393 / job116444626626 failed before credentials, UID,CLI,DB,SSR because the new oracle printed generic FAIL only. Environment and Quality passed; neither proves runtime. Cleanup4/4 passed for absent test user.

251d608684093ab2c7d7a06aadc8eff6f4bf3297 changed only failure diagnostics. Run38742012852/job116445843504 stopped at the same precredential fixture and exposed ReferenceError dim2 is not defined at extracted setupCf catch, called by baseline case. Esbuild had renamed a bundled formatting import, absent from VM globals. No emulator was started. This is a proven new test-oracle binding defect, separate from the already completed emulator diagnosis and from the old CLI stall. No success was inferred.

Correction dbc870fcc278781b650860273ac4e1116f629f85 binds actual extracted readFile/fetch/dim numeric import aliases to the same offline traps; original vendor function text and all three expectations are unchanged. No real runtime DNS stub. The subsequent actual fixture and runtime result are reported separately. The two failures remain in GitHub and archived receipts; no published history rewrite.
