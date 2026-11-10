# FIN-IDEM-001 — Current Behavior

Baseline: `main = 983b746e5c6639dcdc5e6557381ad5619abaa046`

## Sale write boundary

The client invokes server-side Supabase financial RPCs from `src/lib/db.ts`. The current sale flow uses a transactional database RPC for sale creation, but the request contract contains no request-level idempotency key.

## Duplicate retry behavior

FIN-COURIER Gate-4 intentionally defines E3 as a known baseline rather than a FIN-COURIER fix:

- execute the same logical sale-create request twice;
- two distinct order IDs are returned;
- two distinct tenant order numbers are allocated;
- stock is decremented twice.

This proves transaction atomicity for each call is not sufficient to make repeated calls idempotent.

## Existing protections that do not solve this problem

- Stock locking/validation can prevent overselling but cannot identify two retries as one logical request when stock is sufficient.
- UI busy/disabled state cannot protect against network retry, refresh, multiple clients, or concurrent duplicate requests.
- Unique order IDs and tenant numbers identify effects after they occur; they do not deduplicate the logical request.
- A database transaction prevents partial writes within one call but two successful transactions can both commit.

## Settlement/return/day-close context

Other financial writes also require retry review. Some operations already reject a second call because state changes make the operation invalid, but that is not a general request-idempotency contract and may not return the original successful result.

## Current gap

There is no canonical server-side record binding:

`tenant + operation + idempotency_key + request_hash → committed result`

Therefore the caller cannot safely retry after an ambiguous network outcome without risking duplicate effects.