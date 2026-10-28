// Read-only verification of genuine provider tokens. No signing or clock overrides.
import { createRemoteJWKSet, compactVerify, jwtVerify } from "jose";
import { readFileSync } from "node:fs";
import { createHash } from "node:crypto";

const input = JSON.parse(readFileSync(0, "utf8"));
const issuer = "http://127.0.0.1:54321/auth/v1";
const jwks = createRemoteJWKSet(new URL(issuer + "/.well-known/jwks.json"));
const raw = input.token;
if (
  !Number.isInteger(input.clock_tolerance) ||
  input.clock_tolerance < 0 ||
  input.clock_tolerance > 120
) {
  throw new Error("UNVERIFIED_CLOCK_TOLERANCE");
}
const digest = createHash("sha256").update(raw).digest("hex");
let receipt = { digest, signature_verified: false, identity_verified: false, expired: false };
try {
  // Signature verification also works after exp, isolating time from key/claim drift.
  const verified = await compactVerify(raw, jwks);
  const claims = JSON.parse(new TextDecoder().decode(verified.payload));
  receipt.signature_verified = true;
  receipt.identity_verified =
    claims.sub === input.uid &&
    claims.client_id === input.client_id &&
    claims.iss === issuer &&
    claims.aud === "authenticated";
  receipt.iat = claims.iat;
  receipt.exp = claims.exp;
  receipt.session_id = claims.session_id;
  receipt.checked_at = Date.now() / 1000;
  try {
    await jwtVerify(raw, jwks, {
      issuer: [issuer, issuer + "/"],
      audience: "authenticated",
      requiredClaims: ["sub", "exp"],
      clockTolerance: input.clock_tolerance,
    });
    receipt.time_valid = true;
  } catch (error) {
    receipt.time_valid = false;
    receipt.expired =
      error.code === "ERR_JWT_EXPIRED" && error.claim === "exp" && error.reason === "check_failed";
    receipt.error_code = receipt.expired ? "ERR_JWT_EXPIRED" : "OTHER_VERIFIER_ERROR";
  }
} catch {
  receipt.error_code = "SIGNATURE_OR_CLAIM_FAILURE";
}
// stdout is read privately by Python; digest/session identity are never published.
process.stdout.write(JSON.stringify(receipt));
