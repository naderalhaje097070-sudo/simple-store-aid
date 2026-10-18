# Data impact

All41migration blobs retain54 hashes; no table/schema/financial write/cleanup RPC/backfill/production access added. Existing G1 uses disposable local auth/tenant fixtures and requires22table fingerprint equality and seven empty financial tables. This cannot establish populated ledger/debt/custody/stock safety.

Types now reflect the stored nullable order-item product reference. Null RPC results for today estimate/create sale still throw TypeError; they cannot turn into zero/healthy finance. Callback replay uses a recording client with no database/provider connection and proves unchanged call payload/result behavior only.

No state transition changes. Sale≠cash; Delivered≠Settled; debt, courier custody, settlement and inventory remain separate. Financial PR49/50 are excluded. No production backup needed for this unpublished candidate; fresh/upgrade/restore and real financial concurrency remain mandatory later.
