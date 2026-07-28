import { readFileSync } from "node:fs";

const dbSource = readFileSync("src/lib/db.ts", "utf8");

const hasCanonicalV2 = dbSource.includes('create_sale_with_items_v2');
const hasIdempotencyKey = /idempotency[_A-Z]*key|idempotencyKey/i.test(dbSource);

if (!hasCanonicalV2) {
  console.log(
    "FIN_IDEM_G4_D1_DEPENDENCY_BLOCKED: create_sale_with_items_v2 is not present; target idempotency contract cannot yet be bound to the canonical sale write",
  );
  process.exit(43);
}

if (!hasIdempotencyKey) {
  console.log(
    "FIN_IDEM_G4_E2_EXPECTED_RED: canonical sale client path exists but exposes no idempotency key",
  );
  process.exit(42);
}

console.log("FIN_IDEM_G4_TARGET_READY: canonical sale path exposes an idempotency-key contract");
process.exit(0);
