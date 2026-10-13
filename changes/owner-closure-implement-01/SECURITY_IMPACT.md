# SECURITY IMPACT

Authenticated self-owner only, deny by default, no target argument, safe definer search_path, private table no client DML, active-state lookup ignores user_metadata. Closed actor token remains valid at Auth provider but application RLS/RPC/full-route tools deny access. Repeat constant result cannot override ban/delete. No destructive privilege regrant.

Contract and authorization: [IMPLEMENTATION_INTAKE.md](IMPLEMENTATION_INTAKE.md).
