# HiClaw / AgentTeams compatibility record

Date: 2026-08-04

## Installed runtime

- Docker client/server: `29.4.0` / `29.4.0`.
- `agentteams-controller`: installed and running; image tag `latest`; host ports `18001`, `18080`, and `18088` are published.
- `agentteams-manager`: installed and running; image tag `latest`; Manager is published at `127.0.0.1:18888`.
- `agt version`: Controller `dev`, mode `embedded`.
- `agt` is installed at `/usr/local/bin/agt` in both AgentTeams containers; it is not on the host PATH.

Only names, versions, boolean health, and published localhost ports were inspected. Container configuration, environment variables, credentials, and operator-local startup files were not read.

## Authoritative installed schema

The installed CRDs are:

- `/opt/agentteams/config/crd/workers.agentteams.io.yaml`
- `/opt/agentteams/config/crd/teams.agentteams.io.yaml`

They prove the following resource contract:

| Resource | API | Required/minimal fields used by H-01 |
| --- | --- | --- |
| Worker | `agentteams.io/v1beta1`, kind `Worker` | `metadata.name`, `spec.model`; H-01 also pins `spec.runtime: openclaw` and `spec.state: Running` |
| Team | `agentteams.io/v1beta1`, kind `Team` | `metadata.name`, `spec.workerMembers`; every member has `name` and `role`, with exactly one `team_leader` |

The installed Worker CRD defines `spec.mcpServers[]` entries with required `name` and full endpoint `url`; optional `transport` is `http` or `sse` and defaults to `http`. H-01 does not attach an MCP server because the smoke proof must be minimally privileged.

The model reference `qwen3.6-plus` is documented by the installed CRD and `agt apply worker --help`; the smoke resource uses that exact ID. The runtime reference `openclaw` is accepted by the installed Worker CRD and CLI.

## Supported lifecycle commands

```text
agt apply -f <resource.yaml>
agt get workers <name> -o json
agt get teams <name> -o json
agt delete team <name>
agt delete worker <name>
```

`agt apply -f -` is not supported by this build; `-` is treated as a filename. A real file path is required.

Worker status exposes `phase`, `matrixUserID`, and `roomID`. Team status exposes `phase`, `leaderReady`, `teamRoomID`, `leaderDMRoomID`, and member readiness. These are the Manager/Matrix visibility proof fields used by H-01.

## Lifecycle defect found by H-01

Creation and visibility succeed, but deletion is not currently end-to-end correct in the installed embedded runtime. `agt delete team sectrace-smoke-team` returned success twice while both Controller and Manager continued to return the Team. Subsequent Worker deletion returned HTTP 409 because the Worker remained a member of that Team. No raw REST workaround, force deletion, controller restart, or configuration inspection was attempted.

The schema, creation, Manager visibility, and Matrix-room proof are sufficient for the H-01 handoff. Cleanup is tracked separately as the non-blocking environment risk `H-01-RUNTIME-CLEANUP`; it does not block T-01 or later code tickets.
