# Proven baseline

On PR53 candidate source, the existing resolver accepted missing configuration and selected the known production project. The original Gate4 probe returned 42 with E1/E2/E3 expected-red sentinels, saved in proof/baseline-probe.log. This was a pure configuration test; no production connection occurred.

Reusing PR48 head initially passed 56 unit tests but Gate4 returned 1/E7 because the positive preflight inherited host Proxy variables. The guard correctly rejected them. proof/environment-probe.log preserves that result.

A new public-key regression returned 3 failures/1 pass before correction: secret-format, service_role JWT and authenticated JWT fixtures were accepted for browser publication. All fixtures are synthetic.
