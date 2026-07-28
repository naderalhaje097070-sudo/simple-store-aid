import { readFileSync } from "node:fs";

const dbSource = readFileSync("src/lib/db.ts", "utf8");
const marker = 'create_sale_with_items_v2';
const markerIndex = dbSource.indexOf(marker);

if (markerIndex < 0) {
  console.log(
    "FIN_IDEM_G4_D1_DEPENDENCY_BLOCKED: create_sale_with_items_v2 is not present; target idempotency contract cannot yet be bound to the canonical sale write",
  );
  process.exit(43);
}

// Read only the local canonical-v2 call region. An unrelated comment, future
// operation, or legacy helper mentioning idempotency must not create false-green.
const canonicalRegion = dbSource.slice(
  Math.max(0, markerIndex - 900),
  Math.min(dbSource.length, markerIndex + 1800),
);
const hasIdempotencyKeyNearCanonicalV2 =
  /idempotency_key|idempotencyKey/i.test(canonicalRegion);

if (!hasIdempotencyKeyNearCanonicalV2) {
  console.log(
    "FIN_IDEM_G4_E2_EXPECTED_RED: canonical sale client path exists but exposes no nearby idempotency-key contract",
  );
  process.exit(42);
}

console.log("FIN_IDEM_G4_TARGET_READY: canonical sale path exposes an idempotency-key contract");
process.exit(0);
