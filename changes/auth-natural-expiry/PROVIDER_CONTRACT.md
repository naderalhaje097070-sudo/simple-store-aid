# Version-pinned contract and source provenance

CLI2.101.0 apps/cli-go/pkg/config/templates/config.toml: auth.jwt_expiry seconds default3600.
apps/cli-go/internal/start/start.go passes GOTRUE_JWT_EXP from Auth.JwtExpiry.
Authv2.188.1 internal/tokens/service.go GenerateAccessToken sets issuedAt+config.JWT.Exp,
signed by provider configured key; OAuth service uses the same token service.
Auth internal/api/auth.go uses golang-jwt/v5.2.2 with valid methods but no WithLeeway, default0.
PostgRESTv14.10 src/PostgREST/Auth/Jwt.hs: allowedSkewSeconds30,
floor(now)-30 > exp. Error.hs: JwtClaimsErr PGRST303, JWTExpired message JWT expired, HTTP401.
Existing SDK0.20.1 source inspects jwtVerify issuer/audience, explicit clockToleranceSeconds fallback and its default declaration;
jose6.2.3 jwt_claims_set default0, overridden by the unchanged SDK setting in diagnostic verification. Fail closed if installed source cannot be reconciled.
Reference source URLs:
- https://github.com/supabase/cli/blob/v2.101.0/apps/cli-go/pkg/config/templates/config.toml
- https://github.com/supabase/cli/blob/v2.101.0/apps/cli-go/internal/start/start.go
- https://github.com/supabase/auth/blob/v2.188.1/internal/tokens/service.go
- https://github.com/supabase/auth/blob/v2.188.1/internal/api/auth.go
- https://github.com/PostgREST/postgrest/blob/v14.10/src/PostgREST/Auth/Jwt.hs
- https://github.com/PostgREST/postgrest/blob/v14.10/src/PostgREST/Error.hs
Current official docs confirm supported local auth.jwt_expiry; tagged/installed sources authoritative.
Current changelog OAuth-token HTTP200 change is consistent with pinned existing exchange.
No provider token minted locally or time changed. Config TTL180 is verified against actual signed claims.


Actual SDK default30 verified in native-44a0 artifact. Auth OAuthServerGetAuthorization auto-approves existing consent and returns ConsentResponse redirect_url; same callback/state/code/PKCE checks apply. Source: https://github.com/supabase/auth/blob/v2.188.1/internal/api/oauthserver/authorize.go
