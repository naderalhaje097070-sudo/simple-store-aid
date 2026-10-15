# Security impact

The installer emits only fixed phases, exit status and hashes; raw tool output stays private. It verifies the official source before modifying a scratch copy, restores it, and bounds the complete process group. Cleanup never treats user lookup/process-table/container-read errors as absence. Existing application UID IPv4/IPv6 firewall and browser exact-origin/redirect/WebSocket guards remain unchanged. No provider/Paddle access is authorized.
