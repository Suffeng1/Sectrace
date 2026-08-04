# SecTrace MVP Specification

## Purpose

SecTrace is a safe, deterministic demonstration of four role-separated Agents auditing a synthetic security-event chain. The fixed demonstration chain is anomalous foreign-region login, privilege elevation, and bulk sensitive-data access. It produces structured evidence, an advice-only response plan, and a replayable audit bundle.

## Domain language and boundaries

An **incident case** scopes a synthetic scenario and its immutable `trace_id`. An **event reference** identifies scenario-local input only. An **evidence item** classifies a sourced statement as `fact`, `inference`, or `unknown`; insufficient corroboration must remain `unknown` and be expressed as “无法确认”. A **response plan** is advice, never an executable command. An **approval record** is the human decision for a plan. An **audit bundle** is the deterministic projection of the validated ledger and its referenced outputs.

All handoffs use Contract v1.0 and preserve the same `trace_id`. All scenario inputs are synthetic. The MVP does not scan, attack, connect to a real system, use credentials, change an account or permission, delete data, or invoke remediation APIs.

## Required workflow

1. Commander normalizes a synthetic case into `IncidentCase`.
2. Evidence Worker returns sourced `EvidenceItem` values and a deterministic risk path.
3. Response Worker returns an advice-only `ResponsePlan`.
4. Audit Worker validates ledger integrity, redacts sensitive material, and returns `AuditBundle`.

A high-risk plan always has `requires_approval: true`, may be only `draft` or `pending_approval`, and cannot be `executed` in the MVP. Missing evidence or approval is recorded explicitly, never inferred or filled in.

## Acceptance criteria

- S01 completes the fixed synthetic chain under one `trace_id` and reaches a high-risk `pending_approval` plan.
- Every public handoff validates against the five Contract v1.0 models.
- Ledger replay from validated records is deterministic and hash-verifiable.
- The eventual T-05 evidence includes a real AgentTeams/HiClaw Manager, all four Workers, Matrix-visible S01 handoffs, and a human approval interaction. Otherwise V-05 is `FAIL`.

## Non-goals

The MVP is not a security operations platform, an autonomous remediation system, a production connector, an enterprise middleware deployment, or a substitute for human judgment.
