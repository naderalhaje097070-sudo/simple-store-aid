# API compatibility

No HTTP route/RPC name or SQL definition changed in this integration delta. Nine-file emitted-runtime proof allows only same-client alias, queue local alias and two explicit null-result TypeError diagnostics. Ten scenarios exercise original and revised real query/mutation callbacks with identical calls/results, including errors/nulls; a p_paid mutation is rejected. This is not a real financial transaction test.

Three JSON RPC result contracts and nullable SQL arguments are refined against actual41migration definitions. Generated Database schema is unchanged. No any/ts-ignore/rule relaxation introduced. Stored invoice item productId may be null as the existing row schema already allows; new-sale item productId remains a string.

Build commands retain forwarded CLI arguments/modes and fail with the build or postprocessor exit. Three fixture contracts test success, build failure and postprocessor failure. Generated outputs are normalized only after a successful real build. ProcessMap receipt adds bounded read_failures and terminal_tasks; original read_failed/processes/monitor_stopped consumers and acceptance predicates are preserved.
