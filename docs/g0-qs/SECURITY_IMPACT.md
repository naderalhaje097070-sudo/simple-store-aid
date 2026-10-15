# G0-QS-01 security impact

Target GHSA-x5fp-wj9c-mxmx strict comma/bracket array limit and GHSA-4mjr-xmp4-gh2g non-callable constructor.isBuffer parse→stringify. Three direct regressions must be red on actual6.15.3 and green on6.16.0; exact serialized data is preserved under both prototype options. No large denial-of-service load, inferred application exploitability or waiver. Keep Hono/all prior floors and raw audit exit.
