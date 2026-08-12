# Handoff: R-08BC

- Result: `BOUNDARY_RESTORED_QA_PENDING`
- Authorized change: removed only Manager `mcpServers.sectrace`
- Other configuration semantics: unchanged by before-rest/after semantic SHA-256 equality
- Manager policy probe: `Unknown MCP server 'sectrace'`
- Commander policy probe: six SecTrace tools available, including approval logging
- Runtime health after mutation: `READY_RUNTIME`
- Restarts: 0
- Existing contaminated trace: preserved unchanged and not eligible for clean V-08 evidence
- Next: independent QA of the restoration, then design a distinct synthetic trace/run without overwriting `tr_s01`
- Evidence: `docs/verification/R-08BC-manager-route-only-restoration.md`
