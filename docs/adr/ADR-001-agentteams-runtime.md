# ADR-001: AgentTeams runtime for the visible multi-Agent demonstration

**Date**: 2026-08-04  
**Status**: accepted  
**Deciders**: 00 主控与集成

## Context

The competition requires a real AgentTeams (formerly HiClaw) run whose Manager coordinates four role-separated Workers with Matrix-visible task and context communication. A local Python adapter may support deterministic unit tests but cannot establish this delivery evidence. The system must remain synthetic-only and retain a human approval boundary.

The required Docker preflight was run by the main controller on 2026-08-04:

```text
docker version --format '{{.Client.Version}}|{{.Server.Version}}'
29.4.0|29.4.0

docker info --format '{{.NCPU}} CPUs|{{.MemTotal}} bytes memory|{{.ServerVersion}} server'
32 CPUs|7905968128 bytes memory|29.4.0 server
```

This meets the minimum two CPU / four GiB readiness threshold. No Docker image was pulled, no container was started, and no credential was entered. A local HiClaw Manager URL is not configured in the repository at P-01; it is an explicit T-05 operator prerequisite and must be recorded with the actual deployment evidence rather than invented here.

## Decision

T-05 will deploy one real local HiClaw Manager and four named Workers: `sectrace-commander`, `sectrace-evidence`, `sectrace-response`, and `sectrace-audit`. The required startup command is the locally installed HiClaw command documented by that deployment; it is not run or guessed in P-01. The Manager must create an S01 Matrix-visible chain carrying `trace_id`, `schema_version`, `scenario_id`, `input_refs`, `ledger_refs`, `task_id`, `worker`, `status`, and `output_ref` across the four Workers.

| Worker | Manager task message | Completion event | Human boundary |
| --- | --- | --- | --- |
| `sectrace-commander` | Normalize S01 and assign evidence, response, audit tasks. | `incident.created` | Cannot conclude or act. |
| `sectrace-evidence` | Correlate only the supplied S01 references. | `evidence.completed` | Must expose uncertainty. |
| `sectrace-response` | Produce advice-only plan from evidence. | `response.pending_approval` | High risk requires a human. |
| `sectrace-audit` | Verify ledger and project audit bundle. | `audit.completed` | Cannot approve or execute. |

T-05 acceptance evidence is: Manager page, all four named Workers, one visible S01 Matrix task chain, and a human intervention/approval record linked to the same trace. Absence of any item makes V-05 `FAIL`. No adapter is an acceptable final substitute.

## Alternatives considered

### Python adapter only

- **Pros**: simple unit-test execution and no runtime setup.
- **Cons**: does not provide the required visible AgentTeams coordination.
- **Why not**: it fails the competition's mandatory HiClaw evidence requirement.

### Deploy enterprise middleware in the MVP

- **Pros**: resembles a future production topology.
- **Cons**: adds operational complexity without improving the judged interaction.
- **Why not**: SQLite and JSONL cover local deterministic state; Nacos, Higress, PolarDB, and RocketMQ remain migration boundaries.

## Consequences

Unit tests can stay local and deterministic, while the final demonstration has a separate, verifiable runtime requirement. T-05 needs an operator to configure the genuine local Manager and perform the interactive credential action; until then, the evidence requirement remains unmet.
