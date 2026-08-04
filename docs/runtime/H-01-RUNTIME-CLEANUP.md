# H-01-RUNTIME-CLEANUP

Status: deferred, non-blocking environment risk  
Date: 2026-08-04

## Scope

The H-01 smoke Worker and Team were created successfully and became visible to both Controller and Manager. Their Matrix resources were reported present. Cleanup through the installed supported CLI is defective in this embedded runtime.

Residual smoke-only resources:

- Team: `sectrace-smoke-team`
- Worker: `sectrace-smoke`

No production SecTrace Worker was created.

## Reproduction

1. `agt delete team sectrace-smoke-team` returns exit code 0 and reports deleted.
2. Exact-name `agt get teams sectrace-smoke-team -o json` still returns the Active Team after waiting and after restarting only `agentteams-controller`.
3. `agt delete worker sectrace-smoke` returns HTTP 409 because the Worker remains a member of the Team.
4. Controller and Manager both continue to see the same two exact names.

The installed CLI exposes no force flag. The embedded Kubernetes API rejects unauthenticated exact-resource requests with HTTP 401. No token, certificate, environment value, local startup script, or resource BLOB was read. Database mutation and further cleanup exploration were stopped when the delivery priority changed.

## Follow-up boundary

An operator/runtime-maintenance task may later repair the Team deletion reconciler or provide a supported exact-name cleanup mechanism. It must list matching `sectrace-smoke*` resources before and after and must not touch any other Team or Worker.

This environment risk does not block H-01 documentation/schema acceptance, T-01, MCP work, prompts, or core code.
