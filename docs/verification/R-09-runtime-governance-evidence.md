# R-09 Current AgentTeams and Higress governance evidence

- Date: 2026-08-11
- Result: `PASS_CURRENT_READONLY_PROJECTION`
- Scope: current production AgentTeams readiness/membership and local
  Higress/model-gateway governance
- Data boundary: synthetic probe only; no credential values, Matrix content,
  room IDs, raw logs, or real security action
- Mutation boundary: no start, stop, restart, apply, send, approval, trace change,
  configuration change, commit, or push

## Runtime preflight

The first sandboxed invocation returned `BLOCKED_DOCKER_ENGINE` even though Docker
Desktop was visibly running. A bounded diagnostic proved that the Docker CLI was
installed but the restricted execution identity could not read the Docker client
configuration or connect to the Docker named pipe.

The same read-only preflight was rerun with approved host access and returned
`READY_RUNTIME` in 5.8 seconds. It passed:

- Docker Engine, Controller, Manager, and all four SecTrace Worker containers;
- Controller API TCP, model-gateway TCP, and Manager API TCP;
- all four Worker resources and the production Team resource;
- Host MCP listener/TCP/initialize;
- Commander container/DNS/MCP TCP/initialize.

The optional local demo UI on port 19080 was not reachable and did not block the
documented runtime mode.

## AgentTeams readiness and membership projection

`sectrace-audit-team` currently reports:

- phase: `Active`;
- leader: `sectrace-commander`;
- leader ready: `true`;
- ready workers / total workers: `3 / 3`;
- members: `sectrace-evidence`, `sectrace-response`, `sectrace-audit`.

The four resources `sectrace-commander`, `sectrace-evidence`,
`sectrace-response`, and `sectrace-audit` each report:

- phase/state/container state: `Running` / `Running` / `running`;
- Team: `sectrace-audit-team`;
- runtime: `openclaw`;
- model: `deepseek-chat`;
- MCP server names: exactly `sectrace`.

Commander is the `team_leader`; the other three are `worker` members. This closes
the current readiness/membership evidence gap without relying on a historical
screen or historical PASS.

## Higress/model-gateway governance projection

The bounded local probes returned:

- Higress internal `/status`: HTTP 200;
- host gateway request to `/v1/chat/completions` without credentials: HTTP 401;
- Manager default model: `deepseek-chat`;
- Manager provider name: `deepseekv4flash`;
- Manager OpenClaw primary: `agentteams-gateway/deepseek-chat`;
- all four Worker OpenClaw primaries:
  `agentteams-gateway/deepseek-chat`.

This proves current gateway health, authentication enforcement for an
unauthenticated request, and consistent Manager/Worker model selection through
the AgentTeams gateway. No credential-bearing request was sent, so this ticket
does not independently re-prove the upstream provider response body or provider
account validity.

## Remaining limits

- The running MCP process was not restarted after the S-09 repository fixes and
  therefore is not claimed to have loaded them.
- S-09 remains on hold because shared MCP clients can still self-assert the human
  approval role; a trusted approval identity/attestation design must be selected.
- This ticket does not perform live Matrix work or a new S01.
- V-05 still requires the S-09 decision and final status/handoff/demo
  reconciliation.

## Subsequent closure

The limits above describe the point-in-time R-09 projection. R-09B6 later
reloaded the hardened MCP runtime, R-09B7 and R-09BB closed the verifier and live
approval-tool gates, and `docs/verification/V-05-final-reconciliation.md`
completed the final reconciliation. R-09's runtime facts remain authoritative;
its former downstream blockers are now closed.
