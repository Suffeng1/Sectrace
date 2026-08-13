# SecTrace release facts draft

Status: `DRAFT_OPT2_00_AWAITING_INDEPENDENT_QA`
Candidate base: `d60792e197c0339ec0fa7ce507710dbaacc3d46c`
Candidate branch: `codex/adopt-apache-license`
Generated from the OPT2-00 working tree on 2026-08-13 (Asia/Shanghai).

This is a repository-only draft, not a release attestation. It records the
current candidate facts separately from historical point-in-time evidence and
does not assert current Docker, AgentTeams, MCP, Matrix, S01, or external service
state.

## Current candidate facts

| Fact | Current candidate value | Authoritative source | Limitation |
| --- | --- | --- | --- |
| Project package | `sectrace` `1.0.0` | `pyproject.toml` plus `tests/test_project_metadata.py` | Version identifies the completed initial repository release; no package publication was performed. |
| Production roles | Commander, Evidence, Response, Audit | `src/agents/`, production Worker resources, README | Manager remains route-only and is not a fifth business Agent. |
| MCP tools | Exactly six names listed below | `src/app/mcp_adapter.py::TOOL_NAMES` plus MCP integration/security tests | No runtime/live schema was queried in OPT2-00. |
| Typed models | Five shared Contract models plus derived `AuditReview` | `src/app/contracts.py`, `src/agents/audit/service.py`, `docs/contracts/system-contract.md` | Schema version and package version are different concepts. |
| Repository suite | `125 passed` | `python -m pytest -q -p no:cacheprovider` on this candidate working tree | Must be rerun on the frozen release candidate; not an independent QA result. |
| Repository hygiene | PASS on this candidate working tree | `tests/security/test_repository_hygiene.py` | Scans repository-eligible files; intentionally does not read operator-local HiClaw configuration. |
| Code preflight | `READY_CODE` | `scripts/sectrace-preflight.ps1 -Mode code` run for OPT2-00 | Proves repository/Git/Python access only; not runtime/live readiness. |
| Historical clean live chain | V-08 PASS on distinct `R08BF` trace | `docs/verification/R-08BG-clean-s01-final-closure.md`, `docs/verification/V-R08BF-R08BG-independent-qa.md` | Point-in-time historical evidence; not current runtime state and not rerun here. |
| Historical security gate | S-09 PASS | `docs/verification/S-09-codex-security-scan.md` | Point-in-time scan/remediation record; restored from existing sanitized Git history, not regenerated. |
| Historical verifier reload | R-09B6 fail-closed live valid event pending | `docs/verification/R-09B6-mcp-verifier-reload.md` | Point-in-time precursor restored from sanitized Git history; its pending gate was later superseded by R-09BB and V-05. |
| Historical final gate | V-05 PASS | `docs/verification/V-05-final-reconciliation.md` | Point-in-time release reconciliation; its `114 passed` remains the result at that time. |

## Exact MCP tool names

1. `sectrace.intake.create_incident`
2. `sectrace.evidence.analyze_case`
3. `sectrace.response.create_plan`
4. `sectrace.audit.build_bundle`
5. `sectrace.ledger.get_trace`
6. `sectrace.ledger.log_approval`

Historical T-05 material that says “five tools” is explicitly scoped to commit
`9048681`, before the approval logging tool was added. It is not the current
allowlist.

## Test-number lineage

| Result | Scope |
| --- | --- |
| `114 passed` | Historical S-09/V-05 point-in-time repository suite. |
| `122 passed` | Phase 2 planning-time working-tree baseline. |
| `125 passed` | Current OPT2-00 candidate after adding one metadata test and two release-documentation tests. |

The newest candidate number supersedes earlier numbers only as the current
working-tree baseline. It does not rewrite what the historical commands returned.

## Git and remote baseline

- Local base commit: `d60792e197c0339ec0fa7ce507710dbaacc3d46c`.
- Local branch: `codex/adopt-apache-license`.
- Configured remote: `origin` at the public SecTrace repository URL recorded by
  Git configuration.
- Remote default branch, remote current heads, and merge state: **unverified in
  OPT2-00**. Read-only `git ls-remote` failed at the network boundary before any
  ref was returned. The cached local `origin/main` ref was therefore not used as
  proof.
- No fetch, commit, push, or Git mutation was performed.

## Safety and release limitations

- Synthetic or de-identified input only.
- No scanning, connection to, or action against real systems.
- Response output is advice only; high-risk plans require a human gate and never
  become `executed`.
- `trace_id` continuity, Manager route-only separation, server-side Matrix event
  verification, append-only ledger semantics, and fail-closed state loading are
  unchanged by OPT2-00.
- OPT2-00 performed no runtime/live preflight, Matrix/S01 action, credential
  access, service mutation, official cloud Skill installation, commit, or push.
- Independent owner-05 QA is still required before this draft can be promoted.
