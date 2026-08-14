# Requirements

## Objective

Maintain a safe, inspectable multi-Agent audit-demo workspace for the Agent Infra competition. The demo coordinates four bounded Agents around fixed synthetic incident cases and makes their reasoning traceable.

## P-00 acceptance criteria

- Establish the required repository layout and Python project metadata.
- Record collaboration ownership, safety boundaries, and stable project context.
- Keep the scope to planning and infrastructure: no Agent runtime, contracts, Tickets, scenarios, or tests.
- Initialize Git on `codex/sectrace-bootstrap` with the required bootstrap commit.

## P-01 acceptance criteria

- Define and test the five Pydantic v2 Contract v1.0 models before business-Agent implementation.
- Preserve the high-risk human approval gate: a high-risk plan cannot omit approval or be `executed`.
- Specify deterministic, append-only, hash-chained JSONL audit replay and redaction.
- Provide 24 synthetic-only cases, including S01's main chain, malformed inputs, approval gates, and audit-integrity variants.
- Specify real AgentTeams/HiClaw T-05 evidence; the Python adapter is test support only and cannot satisfy V-05.

## R-00 acceptance criteria

- No credential-like value is tracked in eligible Python, Markdown, YAML, JSON, or `.env.example` files.
- Runtime examples contain variable names only; operator-provided values stay outside Git.
- Repository hygiene findings disclose only a path and rule name, never matched content.
- The scanner does not read user-owned HiClaw local configuration.
- Runtime inventory records only service roles and localhost ports.

## T-05 acceptance criteria

- Replay S01 through Commander, Evidence, Response, and Audit with one unchanged `trace_id`.
- Expose exactly six synthetic/read-only MCP tools with v1.0 envelopes and reject unsupported execution names. The authoritative names are `src/app/mcp_adapter.py::TOOL_NAMES`.
- Keep high-risk response plans `pending_approval`; local human approval records never execute an action.
- Validate a canonical SHA-256 ledger and project an `AuditBundle`.
- Provide a judge-visible local UI, four production Worker prompts/YAML, one Team YAML, tests, and reproduction materials.
- Do not deploy the production Workers, read runtime credentials, or handle `H-01-RUNTIME-CLEANUP` in this ticket.
- The offline implementation uses installed Starlette for the thin ASGI UI boundary; FastAPI remains an optional development dependency.
