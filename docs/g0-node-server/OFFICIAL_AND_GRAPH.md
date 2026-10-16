# Official availability and minimal compatible choice

Official reviewed advisory:
https://github.com/advisories/GHSA-frvp-7c67-39w9
Affected <1.19.15 and >=2.0.0 <2.0.5; first fixed 1.19.15 and 2.0.5.
Official fix: https://github.com/honojs/node-server/commit/cd076e117cfe4cb8d31f9eb11d2e8f38a6cb8faf
adds rejection of a single decoded backslash before filesystem resolution.

Preparation run38949922667 at fad7332022725282639ff71c9e98596d2b9db0cf
obtained the complete npm packument with HTTP200, enumerated stable fixed 1.x
versions1.19.15 and1.19.17, downloaded both old1.19.14 and fixed1.19.15 actual
tarballs with HTTP200, and independently verified SHA512 against registry integrity.
1.19.15 was published2026-07-24T00:46:09.652Z, outside the unchanged 24h guard.
Its tarball is28918bytes, integrity
`sha512-Za2ai6TLdKjUvnur+eenO6nuYYipVAEhyCAdaV8IRvmU9kK8crOZUSYvIXn72E4f8fJqyAbpcJuTsYYmZp9Deg==`.
This proves actual availability; initial local403 and GitHub tag404 were not
treated as absence. Therefore2.0.5 is unnecessary and is not adopted.

Actual installed SDK1.31.0 declares `^1.19.9 || ^2.0.5`, satisfied by1.19.15.
Both adapter versions require Node>=18.14.1 and peer Hono^4; Node22.23.3 and
preserved Hono4.13.7 satisfy them. No export removed; no SDK/app update required.
Published distributions and manifests are saved in preparation evidence; compare
actual built files as part of review, rather than relying only on a version label.

Approved official npm Bun1.4.0+34cbb9a40, checked against the existing approved
integrity before execution, generated a complete lock in a disposable directory
from exact5cbf198 input with paired1.19.15 constraints. Full diff changes only
the adapter package record and its override. Every other graph record and
workspace constraint is identical, including Hono/qs/DOMPurify/Babel/esbuild.
Lockformat1, original CI Bun1.2.14 and supply-chain config remain unchanged.
No direct dependency, manual generated entry or broader compatibility change.

Preparation ZIP12067079686 SHA256:
77854013e68cce505394ae5d2aa08dcecc2259f79aef6e82de862bc2d2953ff5.
Native Windows expected-red behavior must be saved before root dependency adoption.

Published-file comparison covers all55files in each tarball: only package.json
version and dist/serve-static.js + .mjs differ. No files added or removed, exports
and declarations identical. The built fix exactly matches the official commit.
The chosen1.x patch avoids the2.x Node>=20/removed vercel export changes.

Generated complete lock blob `1a0791b4bfb849e2345d087ddfebde2c33a59f74`;
SHA256 is recorded exactly in sha256.txt and checked before adoption.

Initial native Windows run38950329394 froze the old lock successfully but failed
before contracts: Python inherited cp1252 while reading UTF8 SDK source, raising
UnicodeDecodeError. This is harness encoding, not an adapter result. The failed
ZIP and log are preserved. Explicit UTF8 reads/PYTHONUTF8 correct only evidence
collection; security assertions, packages and application remain unchanged.

Second native Windows run38950795504 froze the old lock and executed8cases:5PASS,
2expected security failures (HTTP200 protected-marker with zero prefix calls),
and1unexpected SDK fixture failure (reusing a single-use stateless transport).
The SDK1.31.0 built webStandard transport explicitly rejects reuse, and its
published simpleStatelessStreamableHttp example constructs a fresh pair for
each request. A local existing copy of exactlySDK1.31.0 was read for diagnosis
only, not executed or credited as candidate verification. The corrected fixture
follows that per-request lifecycle, logs RPC responses and fails on unexpected
transport/cleanup errors. Fresh CI saves installed source for hash reconciliation.
No SDK/application upgrade or static-security oracle change. Failed ZIP/log
retained; this run is not labeled a successful expected-red baseline.

Native Windows baseline38951595338 at80d2b11be455f2050b2001de8c6b85ea64a3f218
completed with all8cases:6PASS and exactly2documented security FAIL; raw Node
exit1 retained, controller/job success only after validating that exact failure
set. Both variants return200/protected-marker with zero prefix calls. Benign
static, auth, HEAD/range, negative paths, adapter errors and real SDKRPC pass.
ZIP12069042774 SHA256edb020fb51c6e5d16cf1ea8d4bd2a16408a61130f53d41023a89dbca5d835ef6.
All3actual installedSDKsource hashes match the previously read diagnostic copy.
The complete generated lock is now adopted without byte edits, only after
this baseline proof. Patched Windows/Linux checks and full audit follow.

First corrected matrix38952058603:Linux passes all behavioral/guard/lint checks,
then full audit exits1 for sole remaining esbuildLow. Windows frozen succeeds
but exact bunfig byte comparison fails before contracts because Git checkout
converts LF to CRLF. Native1.19.15 behavior is not credited for this failed run.
Set core.autocrlf=false only on the disposable Windows runner before checkout;
the byte assertion and all contract oracles remain unchanged. This preserves
canonical source bytes rather than relaxing identity. Failed artifact/log are
retained. New matrix and Quality will identify their own exact source.
