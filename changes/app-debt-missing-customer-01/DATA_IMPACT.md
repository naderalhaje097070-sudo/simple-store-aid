# Data impact

No database reads/writes/RPC payloads, financial formulas, invoice/custody/inventory data or SQL changed. List aggregation and selectors are identical. Details match the existing selected ID, independent from missing customer metadata. Known positive invoice debt stays visible; absent metadata plus no matched invoices does not render an invented zero. Missing selection does not match unassigned invoices. Fixtures are synthetic and all browser traffic is blocked. No deletion assertion or invented customer/ID.
