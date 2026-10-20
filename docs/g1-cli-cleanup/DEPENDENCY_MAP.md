# Installer and verification dependencies

The existing branch-push workflow checks out setup-cli at the observed immutable SHA, installs its frozen production graph under the same Bun1.3.10, then invokes the checksum-verified phase-instrumented main. Official path/registry publication is preserved. The unchanged application controller consumes CLI2.101.0 and Wrangler4.149.0; cleanup.py independently classifies process/container state. No package or lock changes.
