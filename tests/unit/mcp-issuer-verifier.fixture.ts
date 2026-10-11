// Isolated cryptographic unit boundary. Synthetic tokens here are NOT local
// Supabase lifecycle evidence; that probe uses real code/PKCE provider tokens.
import { exportJWK, generateKeyPair, SignJWT, type JWTPayload } from "jose";
import { createMcpProtocolHandler } from "@lovable.dev/mcp-js/protocols/mcp";

delete process.env.LOVABLE_API_KEY;
const { default: definition } = await import("../../src/lib/mcp/index");
const handler = createMcpProtocolHandler(definition);
const trusted = await generateKeyPair("ES256");
const foreign = await generateKeyPair("ES256");
const jwk = { ...(await exportJWK(trusted.publicKey)), kid: "unit-key", alg: "ES256" };
let jwksRequests = 0;
globalThis.fetch = async (input) => {
  const url = input instanceof Request ? input.url : String(input);
  if (url !== "http://127.0.0.1:54321/auth/v1/.well-known/jwks.json") {
    throw new Error("UNIT_AUTH_UNEXPECTED_NETWORK");
  }
  jwksRequests++;
  return Response.json({ keys: [jwk] });
};
const claims: JWTPayload = {
  sub: "synthetic-unit-user",
  client_id: "synthetic-unit-client",
  iss: "http://127.0.0.1:54321/auth/v1",
  aud: "authenticated",
  exp: Math.floor(Date.now() / 1000) + 300,
};
function signed(patch: JWTPayload = {}, key = trusted.privateKey) {
  return new SignJWT({ ...claims, ...patch })
    .setProtectedHeader({ alg: "ES256", kid: "unit-key", typ: "JWT" })
    .sign(key);
}
const valid = await signed();
const cases: Record<string, string> = {
  valid,
  bad_signature: await signed({}, foreign.privateKey),
  wrong_issuer: await signed({ iss: "https://foreign.supabase.co/auth/v1" }),
  wrong_audience: await signed({ aud: "foreign" }),
  expired: await signed({ exp: Math.floor(Date.now() / 1000) - 120 }),
  missing_client_claim: await signed({ client_id: undefined }),
};
const results: Record<string, { status: number; invalid_token: boolean }> = {};
for (const [name, token] of Object.entries(cases)) {
  const response = await handler(
    new Request("http://127.0.0.1:54325/mcp", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
        "Content-Type": "application/json",
        Accept: "application/json, text/event-stream",
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2025-03-26",
          capabilities: {},
          clientInfo: { name: "crypto-unit", version: "1.0.0" },
        },
      }),
    }),
  );
  results[name] = {
    status: response.status,
    invalid_token: (response.headers.get("WWW-Authenticate") ?? "").includes("invalid_token"),
  };
  await response.text();
}
console.log("UNIT_AUTH_RECEIPT:" + JSON.stringify({ results, jwksRequests }));
