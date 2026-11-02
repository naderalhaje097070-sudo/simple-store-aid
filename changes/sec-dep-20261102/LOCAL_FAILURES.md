# Development failures retained —2November2026

The first graph-negative suite exposed that package-version equivalence alone admitted an unrelated physical dependency path rename. The negative control was retained and the guard now requires exact removed/added physical path sets, as well as retained metadata and the four new official records. The expanded16case suite passes.

A subsequent locator mutation fixture assumed the locked Supabase record had an empty registry locator. That assertion failed because the actual record uses its preserved registry URL. The test now parses the real row and mutates only its locator, proving denial; no production graph was changed.

The new exact-version unit test first failed on a doubly escaped String.raw regex. The regex was corrected, preserving every assertion. Final25dependency tests/116expect pass. These were local development failures before candidate publication, not hosted application failures, and were not relabeled successful original attempts.
