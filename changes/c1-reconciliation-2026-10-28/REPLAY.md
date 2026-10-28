# Reproduce this C1 baseline without network

Extract replay.zip into an empty scratch directory. It contains exact selectively fetched source plus scripts and original outputs, including67 historical records;262 inputs are listed with immutable refs/Git blobs/SHA256 in source-identity.json. This is not a full package checkout and contains no installed dependencies.

With Python3 and Node24.22.1 (built-in stripTypeScriptTypes):

```bash
python3 source_order.py "$PWD" > source-order-reproduced.json
node replay_client.mjs "$PWD" > client-reproduced.json
```

Python scans bounded direct CREATE source order; it is not a PostgreSQL parser/executor. Node executes actual selected helpers/useCreateSale/error formatting in a VM with synthetic hooks/transport/clock/storage and dummy identities. No outbound network, database or provider call. Four reproduced unsafe boundaries are deliberately expected findings. Output order/count is not a vulnerability count or acceptance percentage. Actual source input blobs and ZIP hash must match; never replace a missing input with a newer unpinned file.

Prior local limitation: no Bun/Docker/psql and no credentialed clone; no runtime financial acceptance. Native environment/bootstrap/concurrency/restore is subsequent C scope. See TEST_IMPACT and REVIEW_REQUEST.
