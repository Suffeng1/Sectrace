# SecTrace competition evidence manifest

Status: `DRAFT_OPT2_01_REPOSITORY_ONLY`

This manifest maps narrowly worded competition claims to existing repository
artifacts. It is a navigation index, not a new verification result. The current
Docker, AgentTeams, MCP transport, Matrix, S01 and external-service runtime is
**runtime unknown** because OPT2-01 performed only a code preflight.

## Scope labels

- **repository-only:** supported by current code and local deterministic tests;
  it does not attest a deployed service.
- **point-in-time:** a dated historical verification record. It must not be
  presented as current runtime state.
- **design/protocol:** a definition or planned measurement with no result.
- **runtime unknown:** not inspected in OPT2-01.

## Claim-to-evidence index

| ID | Narrow external claim | Status and scope | Primary evidence | Limitations |
| --- | --- | --- | --- | --- |
| C-01 | SecTrace implements four business roles—Commander, Evidence, Response and Audit—while the Manager remains route-only. | Implemented; repository-only | [README role model](../../README.md), [Commander service](../../src/agents/commander/service.py), [Evidence service](../../src/agents/evidence/service.py), [Response service](../../src/agents/response/service.py), [Audit service](../../src/agents/audit/service.py), [current release facts](../release-facts.md) | Repository structure is current; runtime Worker/Team readiness is runtime unknown. |
| C-02 | The safe adapter exposes exactly six named MCP tools, with no response-execution tool. | Implemented and tested; repository-only | [MCP adapter allowlist](../../src/app/mcp_adapter.py), [MCP integration tests](../../tests/integration/test_mcp_adapter.py), [OPT2-00 independent QA](../verification/V-OPT2-00-independent-qa.md) | Tool availability over a running transport was not checked in OPT2-01. |
| C-03 | The deterministic local flow preserves one trace and stops Response at `pending_approval`. | Implemented and tested; repository-only | [orchestrator](../../src/app/orchestrator.py), [demo-flow test](../../tests/e2e/test_demo_flow.py), [system Contract](../contracts/system-contract.md) | This proves the repository path, not present AgentTeams or Matrix operation. |
| C-04 | Approval verification binds the submitted decision to the expected trace and plan and refuses an untrusted or mismatched event. | Implemented and tested; repository-only | [approval verifier](../../src/app/approval_verifier.py), [approval security tests](../../tests/security/test_matrix_approval_verifier.py), [adapter mutation-safety tests](../../tests/integration/test_mcp_adapter.py) | Tests use synthetic events/fakes. The configured approval identity source is runtime unknown. |
| C-05 | The Audit path validates same-trace inputs and canonical ledger integrity and reports missing requirements. | Implemented and tested; repository-only | [Audit service](../../src/agents/audit/service.py), [ledger verifier](../../src/skills/audit/verify.py), [Audit tests](../../tests/audit/test_service.py), [integrity test](../../tests/audit/test_integrity.py) | Integrity checks recorded linkage; they do not establish completeness or truth of real-world evidence. |
| C-06 | High-risk output is advice-only, requires a human gate and cannot enter `executed` under the current Contract. | Implemented and tested; repository-only | [Contract validation](../../src/app/contracts.py), [Contract tests](../../tests/contracts/test_contracts.py), [README safety boundary](../../README.md) | No claim is made about controls outside this application boundary. |
| C-07 | A clean four-role S01 chain with human approval and Audit was independently accepted in the recorded historical run. | Verified; point-in-time | [clean-chain independent QA](../verification/V-R08BF-R08BG-independent-qa.md), [final reconciliation](../verification/V-05-final-reconciliation.md) | Historical only; it does not attest current runtime, current credentials, connectivity or service health. Earlier FAIL records remain valid for their runs. |
| C-08 | The current candidate facts and historical test-number lineage were independently reviewed for OPT2-00. | Verified; point-in-time repository candidate | [release facts](../release-facts.md), [OPT2-00 independent QA](../verification/V-OPT2-00-independent-qa.md) | Counts are tied to the reviewed candidate and must be rerun on a frozen release candidate. They are not OPT2-01 benchmark results. |
| C-09 | Six value metrics and a manual chat/spreadsheet comparator now have a reproducible definition. | Design/protocol; repository-only | [value baseline protocol](value-baseline.md), [focused manifest tests](../../tests/test_competition_evidence.py) | No customer, enterprise, production, time-saving or efficiency result has been measured. |
| C-10 | The governance pattern has a documented portability boundary between an invariant core and replaceable adapters. | Design/protocol; repository-only | [portability matrix](portability-matrix.md) | This is an engineering migration hypothesis, not proof of deployment in another industry. |

## Evidence use rules

1. Quote only the narrow claim in the matching row; do not broaden a local test
   into a deployment, production or current-live claim.
2. Keep repository-only and point-in-time labels visible in slides and demos.
3. Re-run tests and regenerate release facts on the frozen release candidate.
4. Keep historical FAIL evidence and its superseding lineage; do not rewrite it.
5. If a path becomes missing or a claim exceeds its evidence, remove or downgrade
   the claim before release.
6. Do not copy local identifiers, credentials, raw Matrix content or real incident
   data into competition materials.

## Manual release TODO

- Confirm project origin, team contributions, public team name, repository URL
  and registration metadata with the user.
- Confirm whether any real manual-process baseline can be disclosed. If not,
  retain the clearly labeled synthetic benchmark protocol.
- Run independent OPT2-01 QA and later release-candidate checks before syncing
  these claims into local submission artifacts.
