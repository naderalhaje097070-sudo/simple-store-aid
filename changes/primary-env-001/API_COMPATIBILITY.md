# Compatibility

No RPC, REST payload, generated schema or financial contract changes. resolveSupabaseBuildConfig still returns URL/public key/project but intentionally removes fallback compatibility: operators must provide deploy target and explicit values. Legacy anon JWT and modern publishable keys remain accepted; secret/service/user JWTs are intentionally rejected. Offline opaque placeholders remain accepted and are not evidence of valid provider credentials.

Worker bindings must match baked public identity. Promotion between environments requires rebuilding for the target and consistent runtime bindings. Lovable plugin wrapper is reused once, without duplicate core plugins. Real deployment compatibility is unverified.
