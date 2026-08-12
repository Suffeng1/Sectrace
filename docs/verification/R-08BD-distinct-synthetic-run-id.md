# R-08BD Distinct Synthetic Run ID

- Date: 2026-08-11
- Result: `PASS_CODE_ONLY`
- Runtime action: none

## Problem and design

The governance-invalid `tr_s01` ledger is append-only and must remain preserved. Calling the original S01 intake again would derive the same trace ID and the previous implementation would overwrite its in-memory and persisted state. Duplicating the S01 scenario under another scenario identity would weaken provenance.

The intake tool therefore retains `scenario_id=S01` and accepts an optional bounded `run_id`. A run ID such as `R08BD` derives `tr_s01_r08bd` while the IncidentCase continues to identify scenario S01. Run IDs are limited to one leading alphanumeric character followed by at most 31 alphanumeric, underscore, or hyphen characters.

## Strict TDD

RED:

```text
3 failed, 9 passed
```

The previous implementation ignored `run_id`, allowed duplicate trace creation to overwrite state, and accepted a path-like value because it was unused.

GREEN:

```text
state persistence: 12 passed in 1.13s
MCP adapter + persistence: 24 passed in 1.17s
full pytest: 66 passed in 1.71s
```

The tests prove that:

- `S01 + R08BD` creates `tr_s01_r08bd` while preserving `scenario_id=S01`;
- the original `tr_s01` file remains byte-for-byte unchanged;
- the distinct trace receives its own persisted JSON file;
- duplicate trace creation fails before mutation;
- path-like run IDs fail before the state directory is created.

## Boundary

The number and names of MCP tools remain six. The currently running MCP process was not restarted and therefore has not loaded this code. No live trace, Docker resource, AgentTeams configuration, Matrix message, approval, Audit call, smoke action, commit, or push was performed. A live reload/restart and clean run each require separate authorization.

## Independent QA

Independent QA passed in `docs/verification/V-R08BD-independent-qa.md`. It confirmed the formal `tr_s01` SHA-256 was unchanged, both base and derived traces reload together, all Incident and ledger trace references match, the ledger verifies, duplicate and case-collision attempts do not write, 1/32-character legal boundaries pass, 15 invalid/path/Unicode/encoded/whitespace classes fail with a fixed non-leaking error, and the in-memory FastMCP registry remains exactly six tools with optional nullable `run_id` on intake. Focused 24/24, full 66/66, and diff check passed.
