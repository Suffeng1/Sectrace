# Requirements

## Objective

Prepare a safe, inspectable multi-Agent audit-demo workspace for the Agent Infra competition. The planned demo will coordinate four bounded Agents around one fixed, synthetic incident case and make its reasoning traceable.

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
