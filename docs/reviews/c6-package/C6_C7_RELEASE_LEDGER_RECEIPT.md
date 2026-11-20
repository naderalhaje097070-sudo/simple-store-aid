# C6/C7 item 3.4 — release source and ledger reconciliation

Verified on 2026-11-20 against integration `09089be291a56fd2a76ba8c0943564c30e5a4eb8`, main `1c5276fae77cb71f49d868fe71d17d84c5d3c6b3`, migration tree `08d0c94e060d3ea44b23759e41ed193adf979c0e`. The [merged integration release-finance run](https://github.com/naderalhaje097070-sudo/simple-store-aid/actions/runs/44784220945) passed all nine jobs and all three synthetic backup/restore legs. This receipt is source and offline verification only. The direct legacy verifier and live release decisions remain open.

## Source files and recorded ledger

- The 50 main migration paths, Git blob SHAs, and modes match integration exactly. Integration has 13 additional files.
- Both reviewed bundles embed ten ordered sources. Extracted each literal and matched its version, name, and full bytes against the committed file. All 20 existing apply manifest entries passed SHA-256 verification. Bundle hashes are `22fa12b535c34de58812bbd09d3f2969d895ea7664b37e427409e5f2670e03a0` (plain) and `e740a7f245d015dcd90c3ae4c1fd2a9a289e07ef76884876826742206d17addf` (legacy unblock).
- The recorded 2026-11-16 ledger has 52 distinct versions. Comparison by recorded statement MD5 finds 26 with matching version and content, 21 with the same content under a different version, and five with no byte-identical file. The [earlier ledger review](../C6_PROD_LEDGER_READ_RESULT.md) records their individual dispositions and the open audit-table discrepancy. A matching file count would not establish ledger identity.
- The email repair `20261107214500` is already present in that ledger, with matching statement MD5 `1dd79d44723e13923699fe6461676c35`. Carry its source in the release. No second application is proposed.

| Additional migration file over main | Disposition | SHA-256 |
| --- | --- | --- |
| `20260815170000_fin_courier_pr_a.sql` | C6 bundle stage C1 | `e42aad2a9d18e761e07a890339b794ad378474b27ef8b1380f230144b57ac7a5` |
| `20260815171000_fin_idem_sale_create.sql` | C6 bundle stage C2 | `8f39292aab92d8eef397890de46f325848bd465972bf3cc53591402c661c92f4` |
| `20261028213608_fractional_quantity_01.sql` | C6 bundle stage C3 | `81b0a1ed16608cc9eafc737a06cbeb00efcd72ec8d21ec9a37a0c4a0cc66cb55` |
| `20261029044024_c3_reconcile_financial_adapters.sql` | C6 bundle stage C4 | `01c95bd6144d1913d43d696c69a822fad9c7ca3d4bc2d9fd7edbbcb00bc2ce2a` |
| `20261103060658_c5_keyed_debt_collection.sql` | C6 bundle stage C5 | `56722df52970332a1e978bb5703a75a851034287a4678a05fd064601b14a78d8` |
| `20261106145346_c5_day_close_profit_report.sql` | C6 bundle stage C6 | `0a64bbd48716ca3feceb6a825587bf11ba55892e1b7e92ebc7b83639aff6d6dd` |
| `20261107214500_sec_email_queue_service_only.sql` | Already present in recorded ledger | `5dc684f81e36760a0ac50c0f6781be4da05c28d74ec2b7f6c6c533d5b59d18b0` |
| `20261110090000_courier_settle_custody_01.sql` | C6 bundle stage C7 | `1087773f0a0faa6ade5d00f2bb6b8f8891800ce0a9be2311e30fc6e7fb684a67` |
| `20261110130000_paddle_webhook_no_key_update_01.sql` | C6 bundle stage C8 | `e98fc3fadb3a3842189f11a378a0b80863c2b8d44144c328e82461be8b697b53` |
| `20261110140000_tenants_narrow_client_grants_01.sql` | C6 bundle stage C9 | `c9b483cfca357678fe13f6fccdb2373354abe2ed6abbff90db89aaacd2d9a249` |
| `20261110150000_defpriv_function_execute_01.sql` | C6 bundle stage C10 | `c1c17b1560c51a7ed18db00c8285b182987aef8dcdcfa5109d66976ac00cd0a3` |
| `20261120140000_guard_courier_custody_settlement.sql` | Separate C7 migration | `e14b9f03582b79b83e4334bb8c8ae32eb2ecde6e0669c20a872cb74060e0a2a7` |
| `20261120150000_close_day_courier_debt_balance.sql` | Separate C7 migration | `4f48a50379a0a215d52069f0062049c833b4d255e35ea65ec4370e1bdeacf8a5` |

The saved ledger file has SHA-256 `277292ef2e84ed7c0a2d33c0f8217d2810526a27ee849bea0b391e7ff8f4abae`. The following are offline expectations using the bundle verifier's sorted version and version-to-statement-MD5 algorithms. The after-C7 row assumes inserting each C7 version with the full original file as its statement, as the existing C6 wrapper does. A different ledger writer may serialize statements differently and must be rehearsed before adopting these expectations.

| Ledger state | Rows | Versions MD5 | Versions and statement hashes MD5 |
| --- | ---: | --- | --- |
| Recorded baseline | 52 | `9235c3834be88ce50dba444bb15b5262` | `a3de2f506b1da505ae41c9fd553c87d7` |
| Expected after ten C6 migrations | 62 | `8eec91642011d297ca5504cebda430ef` | `1e6c4c7ce50bf9c8f9526de2888df919` |
| Expected after both C7 migrations | 64 | `a6ca71705682237fc4bc6b93c4f782b5` | `1c671404c3969bc09f451c3cea7b608b` |

## Remaining release gates

- *As of `09089be`, before #103 (historical; superseded by the update below):* On the exact integration commit, `release_gate_v1` passed with 63 migrations and preservation of main. The direct B5 identity verifier still refuses with `Protected source path set changed`. Its 29 historical unit tests passed. Existing B5 lifecycle, SSR, billing, and natural-expiry callers retain their historical identities. The [option record](C6_PACKAGE_PREP.md#24-الخلاصة) reserves selection of a source-bound current profile and any change to acceptance controls for the owner. Proposed scope preserves frozen A41 and B50 fixtures, checks all paths and modes, tests changed/missing base files and mismatched ledgers, and validates fresh and populated callers with the keyed sale route.
- The ten-stage C6 bundle contains the earlier custody repair and omits the two new forward C7 migrations. The C7 order is `20261120140000` then `20261120150000`. Review and rehearse an atomic combined apply, or hold financial writes and drain in-flight operations through both C6 and atomic C7 commits in a single approved window. Run the final ledger, function/ACL, and financial checks before reopening writes. Keep writes quiescent on failure until the reviewed recovery path is complete. No combined production payload was run or approved here.
- Live platform identity and ledger recheck, actual production backup and isolated restore, apply method, duration of legacy grants, main merge, and deployment need their own approved steps. Synthetic acceptance does not attest to current production. Historical closes and disputed custody remain for explicit reconciliation.

## Update after #103 (integration `d4616d06e7a3ccf6541c75af232780bb6011a3ed`, 2026-11-20)

- **#103 merged into integration only.** The merge commit is `d4616d0`. The exact head `0a622ce43cb118da5c68c86c1afb87e44abc0dba` passed all 14 required checks, including release-finance 9/9, and both reviews: Codex found no findings, and Strix reported no open findings. No production access, no main merge and no deployment.
- **Source is unchanged by #103.** #103 changed no migration. At `d4616d0` the migrations tree is still `08d0c94e060d3ea44b23759e41ed193adf979c0e`, with 63 source files. The 50 main paths, blobs and modes listed above still hold.
- **The direct B5 identity path** now uses the additive verifier `tests/g01-acceptance/candidate_identity.py`, with its manifest `candidate-63-source.json`. It pins:
  - the protected paths, blobs and modes against HEAD, the index and the worktree;
  - the ordered 63-entry ledger against `09089be`;
  - the B50 files as an exact ordered subsequence against the B base `59c8a0c`;
  - the original41 as the exact prefix;
  - the migrations directory read from the filesystem.

  The frozen verifier `integrated_identity.py`, the A41/B50 manifests and their 29 tests are unchanged. The refusal recorded above (`Protected source path set changed`) is that frozen verifier's result. It is no longer on the B5/B50 path.
- **Post-merge acceptance is still pending.** The first B5 composed run on `d4616d0` (run 44798187106: lifecycle fresh and upgrade, SSR, billing) and the first B50 natural-expiry run (44798187438) were still in progress when this update was written. Neither is accepted until it is green on that commit.
- **The 41→63 upgrade evidence in #103 is archival and local.** It is `docs/reviews/item-3.4/upgrade-result.json` and `upgrade-migration-up.txt`, from runs at `60b4411` and `4ead923`. That helper was removed from #103 before merge. The current upgrade acceptance is the CI `lifecycle (upgrade)` job on `d4616d0`.
- **The ledger expectation is unchanged and still conditional.** 52 → 62 → 64 remains an offline expectation. It holds only if the live ledger matches the recorded 52-row baseline and the indicated statement format is used. It is distinct from Git's 63 source files, and it has not been checked against production.
