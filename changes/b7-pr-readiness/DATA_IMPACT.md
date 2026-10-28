# Data impact

No app/customer/production data change. The expiry job uses new synthetic local Auth users/tenants and read operations under the existing guard. It performs no financial transaction, revocation, ban or refresh. Preserve public22 plus private3/Auth identity links before/after. Genuine expiry requires elapsed wall time; do not change the clock or token claims. Historical benchmarks are not executed in this batch.
