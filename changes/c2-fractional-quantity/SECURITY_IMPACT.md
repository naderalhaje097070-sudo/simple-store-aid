# Security

Preserve original active-actor/staff/tenant checks, function owner/ACL through CREATE OR REPLACE, every old migration and all unrelated source. No new SECURITY DEFINER entrypoint or schema visibility. Constraints also protect direct product writes; client validation is supplementary.

Native test reuses existing loopback write-harness guard, local Auth tokens/real REST/RPC, UID egress firewall, secret quarantine/cleanup and pinned disposable Supabase2.101.0. Probe checks active owner/staff, foreign product and banned-old-token refusals with stored invariance. No external provider/production data/token. CLI telemetry initially auto-review blocked; source/docs verify supported opt-out. All subsequent CLI calls use task-local disabled state plus SUPABASE_TELEMETRY_DISABLED=1/DO_NOT_TRACK=1; Go canSend/TS effective consent explicitly deny capture. No permission/bypass waiver inferred.
