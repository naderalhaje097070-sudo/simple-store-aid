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
