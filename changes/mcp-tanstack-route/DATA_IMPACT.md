# Data impact
Only fresh disposable Supabase local fixtures A/B, two tenants, public OAuth client, local sessions and B ban. Admin access limited to setup/ban and SQL observations; MCP calls use genuine user access tokens.
After fixture setup, snapshot all22publictables; compare after protocol and conflict tests. All7financialtables must remain empty. Auth timestamps/sessions/client/ban changes are expected and outside public fingerprints.
No nonempty tenant-isolation or financial correctness inference. Cleanup stops server UID processes and disposable stack with --no-backup, removes private status; runner disposal removes transient fixtures. No public cleanup RPC.
