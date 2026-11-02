# Data impact

No application schema/data mutation. Isolated hosted job creates fresh synthetic Auth users/tenants and reuses the unchanged nonfinancial G1 flow. It checks public-state digests and finance-zero at end. Only local loopback schema_migrations history is read. Credentials remain runner-temp/private, excluded from receipts; all containers/processes removed by existing always cleanup. No production or customer data.
