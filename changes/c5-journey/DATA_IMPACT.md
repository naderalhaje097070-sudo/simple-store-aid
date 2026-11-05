# Data impact

New synthetic tenants/actors only, disposable fresh/upgrade stacks. Reference product price100/cost40/stock10, customer and courier seeded privately. Business writes exclusively actual UI adapters. Other populated tenant's order/product unchanged. Admin keys/session/password remain private files/in-memory; only bounded booleans/counters/expected fixture amounts published. No production/customer records or cross-repository data. Existing upgrade snapshot checked before new rows. Cleanup stops owned local stack and removes private files even on failure.
