# Primary source evidence

Official repository cloudflare/workers-sdk, tag wrangler@4.149.0 (tag object05933a22d7c58ffad81fa390d7699abe6c7c279d; immutable target commit84c4e959bbd349b1d0f88ffe64679aff69c6328a). Read-only inspection, no provider request.

| Source path | Git blob | Finding |
| --- | --- | --- |
| packages/miniflare/src/cf.ts | 5a4f9d45f84f057d05d6ec053bf40452f1a161f5 | setupCf optional metadata endpoint; official env opt-out returns existing fallback before read/fetch |
| packages/miniflare/src/index.ts | 1284d267928101762c1eda9425c781e48a7aceca | startup calls setupCf |
| packages/wrangler/src/api/startDevWorker/LocalRuntimeController.ts | 0f9d3c850737c712e9973301dfa42942cb034841 | local options construction passes no explicit cf override |
| packages/wrangler/src/dev/miniflare/index.ts | da6c613fc7d33e1e13c90c692edb03ce7b8e72ba | local emulator option builder reviewed, no explicit cf |
| packages/workers-utils/src/environment-variables/misc-variables.ts | 1f709e84494740298e52ee96038cb4d9f0063e17 | documents official opt-out for wrangler dev |

Sources are browsable at https://github.com/cloudflare/workers-sdk/tree/wrangler%404.149.0 . This source inspection supports the intervention; actual installed package fixture and full runtime must still establish behavior. No inferred update or telemetry cause is used.

Exact public hostname SHA256 workers.cloudflare.com =7dbcc823da096fc40bbb5e5d75d7d8620c2cd6a471931b27e49c020690cafb41, matching both Node and native DNS records. SHA256127.0.0.1 =12ca17b49af2289436f303e0166030a21e525d266e209267433801a8fd4071a0. The former is not a packet destination: observed packet-path resolver endpoint is127.0.0.53:53; no public resolved address/TLS/request content is captured. The diagnostic Node hook lacks JS callers for that name; source plus controlled correction carries causal attribution, with this limitation retained.
