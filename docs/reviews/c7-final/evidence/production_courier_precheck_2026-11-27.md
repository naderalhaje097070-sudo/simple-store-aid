# Production read: courier custody state counts (read only)

- **Approval:** the owner's words in the Claude session, "موافق", given to run `PRECHECK_courier_custody_states.sql` (read only) on production. It covers this one read only: no apply, merge or Publish.
- **When:** about 2026-11-27T09:39:31Z, UTC.
- **Target identity**, from the Lovable connector `get_project`:

| Field | Value |
|---|---|
| Project | `1c38f21a-8f36-4a0b-8350-ee4be6901b8d`, the production project recorded in `docs/reviews/C6_PROD_LEDGER_READ_RESULT.md` |
| Published | `is_published=true`, `publish_audience=public` |
| Latest commit | `1c5276fae77cb71f49d868fe71d17d84c5d3c6b3` = main |

- **Method:** one `query_database` call through the Lovable connector. The SQL was the committed file `../PRECHECK_courier_custody_states.sql` at `836f4ca`, byte for byte: `begin transaction read only; … rollback;`.
- **Result** (aggregate counts only, no rows read out):

| Field | Value |
|---|---|
| `ro` | `on` |
| `courier_orders` | 3 |
| `pending_with_payment` | 0 |
| `none_with_payment` | 0 |
| `custody_over_remaining` | 0 |

- **Meaning:** at this observation, production has no courier order in a state that F1 (`20261120140000`) would newly refuse from the delivery dialog, and none whose stored custody exceeds total minus paid.
- **Limits:**
  - This is a snapshot at the observation time. Repeat it in the same read-only form immediately before any authorized apply.
  - It says nothing about the ledger. The ledger precheck is separate (#97, 2026-11-22).
