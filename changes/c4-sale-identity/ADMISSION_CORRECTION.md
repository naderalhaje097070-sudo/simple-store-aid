# C4 redundant inventory correction — 2026-11-02

Executable 56122b609879d85bfe21eb11d1c42645a6f3441d was rejected before probe credentials by the unchanged exact source gate: `C additions differ`. The browser probe hash had been updated in protected_blobs but not the separate additions mapping. No behavior acceptance is claimed for that commit. The early native cleanup step also failed because firewall initialization never ran; no native probe credentials or database stack were created.

This correction updates only the redundant additions hash to the reviewed browser.py bytes. The verifier and all assertions remain unchanged. Before publication, every additions entry was checked against protected_blobs and each available local addition's actual Git blob hash; all intentional_changes after hashes and 430-entry/54-SQL counts were checked. Prior 41c33f1 native jobs passed all behavior and cleanup checks; final exact-head execution is still required.
