# T-05 evidence index

| Evidence | Location | What it proves |
| --- | --- | --- |
| S01 orchestration | `src/app/orchestrator.py` | Four deterministic stages share one trace and retain the human gate |
| Audit ledger | `src/app/ledger.py` | Canonical append-only SHA-256 chain |
| Safe MCP adapter | `src/app/mcp_adapter.py` | Exactly five synthetic/read-only tool names and a common safety envelope |
| MCP server entry | `src/app/mcp_server.py` | Local Streamable HTTP entry point on port 19090 |
| Local UI | `src/app/main.py` | Judge-visible S01 replay and “待人工审批” state |
| Integration tests | `tests/integration/` | Trace continuity, approval states, audit integrity, MCP allowlist |
| UI test | `tests/e2e/test_demo_flow.py` | Page/API replay behavior |
| Resource tests | `tests/runtime/test_production_agent_resources.py` | Installed-CRD schema, prompt parity, Team membership, no credential values |
| Worker prompts | `hiclaw/sectrace-agents/prompts/` | Four role-separated production instructions and refusal boundaries |
| Worker/Team YAML | `hiclaw/sectrace-agents/sectrace-*.yaml` | H-01-proven AgentTeams resource definitions, not deployed in T-05 |

## MCP tool allowlist

1. `sectrace.intake.create_incident`
2. `sectrace.evidence.analyze_case`
3. `sectrace.response.create_plan`
4. `sectrace.audit.build_bundle`
5. `sectrace.ledger.get_trace`

Every response contains `schema_version: "1.0"`, the unchanged `trace_id`, `result`, and `Synthetic exercise only; no real action has been executed.`

## Runtime evidence boundary

H-01 already proved installed schema plus smoke Worker/Team creation and Manager/Matrix visibility. T-05 intentionally does not deploy the four production Workers. Therefore live four-Worker Matrix collaboration and a live human interaction remain items for V-05 to evaluate against the user-authorized no-deployment boundary; repository evidence must not claim they occurred.
