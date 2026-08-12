# T-05 evidence index

| Evidence | Location | What it proves |
| --- | --- | --- |
| S01 orchestration | `src/app/orchestrator.py` | Four deterministic stages share one trace and retain the human gate |
| Audit ledger | `src/app/ledger.py` | Canonical append-only SHA-256 chain |
| Safe MCP adapter | `src/app/mcp_adapter.py` | Exactly six synthetic/read-only tool names and a common safety envelope |
| MCP server entry | `src/app/mcp_server.py` | Local Streamable HTTP entry point on port 19090 |
| Local UI | `src/app/main.py` | Judge-visible S01 replay and “待人工审批” state |
| Integration tests | `tests/integration/` | Trace continuity, approval states, audit integrity, MCP allowlist |
| UI test | `tests/e2e/test_demo_flow.py` | Page/API replay behavior |
| Resource tests | `tests/runtime/test_production_agent_resources.py` | Installed-CRD schema, prompt parity, Team membership, no credential values |
| Worker prompts | `hiclaw/sectrace-agents/prompts/` | Four role-separated production instructions and refusal boundaries |
| Worker/Team YAML | `hiclaw/sectrace-agents/sectrace-*.yaml` | H-01-proven AgentTeams resource definitions, not deployed in T-05 |

## Live acceptance evidence

| Evidence | Location | What it proves |
| --- | --- | --- |
| Current production runtime | `docs/verification/R-09-runtime-governance-evidence.md` | Manager, four Workers, Team readiness/membership, and Higress governance |
| Clean live S01 chain | `docs/verification/V-R08BF-R08BG-independent-qa.md` | Visible four-role chain, same trace/plan, human approval, and qualified Audit |
| Live approval-tool boundary | `docs/verification/R-09BB-live-mcp-tool-attestation.md` | Server-fetched Matrix approval, Commander-owned call, digest binding, no execution |
| Final security/release gates | `docs/verification/S-09-codex-security-scan.md`, `docs/verification/V-05-final-reconciliation.md` | S-09 and V-05 PASS |

## MCP tool allowlist

1. `sectrace.intake.create_incident`
2. `sectrace.evidence.analyze_case`
3. `sectrace.response.create_plan`
4. `sectrace.audit.build_bundle`
5. `sectrace.ledger.get_trace`
6. `sectrace.ledger.log_approval`

Every response contains `schema_version: "1.0"`, the unchanged `trace_id`, `result`, and `Synthetic exercise only; no real action has been executed.`

## Runtime evidence boundary

T-05 itself does not deploy the production resources. Later authorized live
verification proved the current Manager, all four production Workers, the Team,
the visible clean S01 chain, and human approval. The durable, redacted evidence
is linked above. Demo replay remains local and synthetic; it must not be
presented as a substitute for those live records.
