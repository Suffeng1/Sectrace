# Stable project context

## Main case

SecTrace has one fixed main case: a synthetic, de-identified suspected account-compromise incident. It is a safe demonstration only, not a connection to any real environment.

## Implemented Agents

| Agent | Input | Output | Safety boundary |
| --- | --- | --- | --- |
| Commander | incident intake and available evidence references | scoped work plan and routing | preserves `trace_id`; does not invent facts or authorize action |
| Evidence | provided synthetic/de-identified artefacts | evidence assessment with provenance | uses only supplied evidence; does not invent evidence |
| Response | scoped findings and risk context | advice-only response options | no security action; high risk is human-gated |
| Audit | Agent messages and decisions | traceable audit summary | preserves `trace_id`; no secrets in reports |

Contract v1.0, AgentTeams collaboration resources, and the canonical hash-chained
audit ledger are implemented. Runtime and live readiness still require the
current lowest-necessary preflight; historical PASS evidence is point-in-time.

## Six-role workflow

00 owns shared coordination, followed by 01 Commander, 02 Evidence, 03 Response, 04 Audit, and 05 verification. Shared-contract questions are handed to 00 for resolution.

## Safety boundaries

- Synthetic or de-identified data only.
- No attacks, scans, real-system connections, or security action.
- High-risk output is advice-only and human-gated.
- Do not invent evidence; preserve `trace_id`; do not put secrets in reports.
