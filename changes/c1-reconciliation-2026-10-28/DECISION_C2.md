# C2 — quantity contract requiring a product choice

Observed schema: products.stock integer; order_items.qty numeric; current sale accepts numeric quantity before writing integer stock. Existing UI increments/decrements by whole units but numeric setters do not enforce whole units. Therefore intent cannot be proven from either schema or permissive API alone. No production data was inspected. FIN-01 remains open.

| Choice | Concrete behavior | Technical effect / required evidence |
|---|---|---|
| Whole units only — recommended for the current MVP/schema | qty1/2 accepted;0.25/0.5 rejected clearly and atomically, no money/stock/numbering/audit effect | Keep integer stock; validate original raw finite positive integer before numeric(12,2) coercion in canonical RPC and both UI paths; constrain new writes appropriately. Existing fractional historical rows require separate assessment, never silent rounding. |
| Fractional inventory too | Sales such as0.25 units have exact matching fractional stock decrement and return | Approved forward stock-type/quantity precision contract, compatible reads/writes/constraints, populated upgrade and exact cumulative/return/concurrent arithmetic. More scope than a guard. |

Underlying product question: are goods sold only by the piece, or also by weight/length/partial units? Recommendation is whole units to match the current integer-stock MVP, unless fractional selling is an actual requirement. AGENTS reserves core financial-contract choices to the owner. User continuation authorizes technical progress, but does not reveal this business fact. Do not silently select precision, round values or widen scope.
