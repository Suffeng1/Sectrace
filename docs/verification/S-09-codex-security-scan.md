# S-09 Codex Security scan and remediation

- Date: 2026-08-11
- Scan ID: `eda8ee4f-aa71-450d-94cd-f09d59881656`
- Scan mode: Codex Security Standard repository scan
- Scan result: 3 medium, 2 low, 0 high, 0 critical
- Remediation outcome: `CODE_FIXED_LIVE_VERIFIER_AND_MCP_TOOL_PASS`
- S-09 verdict: `PASS`
- Runtime boundary: hardened MCP reloaded; verifier controls and one fresh
  synthetic Commander-owned approval-tool flow passed; no Audit, real action,
  commit, or push

## Canonical scan artifacts

The completed scan is sealed under:

`<local-security-scan-temp>/project_005_SecTrace安全事件多Agent协同审计系统/<scan-id>`

The bundle contains `report.md`, `scan-manifest.json`, `findings.json`,
`coverage.json`, and `exports/results.sarif`. Completion was performed exactly
once. The scan covered the application, MCP boundary, contracts, tests, runtime
resources, and selected release documents. Exhaustive historical-document review
and live Higress governance were deferred.

## Finding disposition

### Fixed: credential-bearing release documents bypassed hygiene

- Finding: `csf_c311060efef19a3490655fb5` (medium)
- Vulnerable path: non-ignored handoff documents were untracked, while the
  repository gate scanned only tracked files plus a small allowlist.
- Invariant: every tracked or non-ignored formal release candidate must be
  scanned without reading ignored operator-local configuration; findings must
  disclose only path and rule.
- Patch: scan tracked files plus non-ignored files under formal release roots;
  report a tracked local-configuration path without reading it; add precise
  assignment, password literal, Bearer, and query-token rules; remove the generic
  long-hex heuristic that misclassified canonical SHA-256 ledger hashes.
- Data cleanup: 10 credential-bearing values were mechanically replaced by
  redaction markers in two handoff documents. No matched value was printed.
- External credential rotation: not run and not implied by this repository fix.

### Fixed: repeated or out-of-order stages poisoned persisted state

- Finding: `csf_fb2c2b6d625c3ce154d166b5` (medium)
- Vulnerable path: Evidence, Response, Audit, and post-Audit approval mutators
  could append duplicate or impossible events before restart-time validation.
- Invariant: each stage is single-use and later stages cannot be followed by an
  earlier mutation; rejection must leave the in-memory and persisted state
  unchanged.
- Patch: enforce stage guards before mutation for Evidence, Response, Audit, and
  approval-after-Audit.

### Fixed: scenario path traversal

- Finding: `csf_2b3d00f37bd47933972f44db` (low)
- Vulnerable path: caller-controlled `scenario_id` was joined directly to a JSON
  path.
- Invariant: only the approved `S01` through `S24` identifiers may resolve to a
  file directly inside `data/scenarios`.
- Patch: exact identifier validation plus resolved-parent containment check.
  Positive coverage preserves all S01-S24 behaviors, including the expected S11
  real-data rejection.

### Fixed: unbounded trace creation

- Finding: `csf_69347d2253115a570b4dd542` (low)
- Vulnerable path: unique `run_id` values could grow memory and state files
  without a bound.
- Invariant: the adapter has a deterministic hard capacity and refuses a new
  trace before creating state or a file.
- Patch: default capacity 256, configurable downward for tests; startup fails
  closed if persisted state already exceeds the configured capacity.

### Code fixed; live verifier passed; MCP tool gate pending: clients could self-assert human approval

- Finding: `csf_df3939280f62a0c7898f8d54` (medium)
- Vulnerable path: any client that can reach the shared MCP server can call
  `sectrace.ledger.log_approval` and supply the accepted
  `approver=human_operator` value.
- Required invariant: an approval mutation must be authorized by a server-side
  identity and Matrix event that an MCP caller cannot mint for itself and that is
  bound to trace, current plan, decision, and a unique human event.
- Preserved behavior: the user makes the decision in the visible Matrix flow;
  Manager remains route-only; Commander records the decision; rejected and
  approved outcomes remain auditable.
- Selected strategy: the user chose trusted Matrix event attestation. MCP now
  accepts only `approval_event_id`, trace, current plan, and decision. The server
  fetches that immutable event with server-held credentials from one configured
  room; verifies the configured human sender, exact JSON body binding, event ID,
  text type, and server timestamp; then stores only event/reason SHA-256 digests.
  Caller-supplied approver and reason fields were removed from the tool schema.
- Fail-closed behavior: with no verifier configured, approval is rejected before
  state mutation; a partial environment configuration stops server startup; all
  event or binding failures return one non-disclosing error.
- Compatibility: existing historical ledger payloads remain read-only loadable;
  every newly recorded approval uses the event-attested payload format.
- Live status: a least-privilege replacement verifier identity is DPAPI-protected;
  the running MCP has been reloaded once with the four complete verifier settings;
  live schema exposes only the four hardened arguments. A new admin-origin exact
  JSON event passes the verifier, while missing, historical natural-language,
  trace-mismatched, and plan-mismatched events fail closed.
- Remaining gate: the live `sectrace.ledger.log_approval` tool has not yet consumed
  an attested event for a fresh synthetic pending trace. Direct verifier success is
  not represented as a ledger mutation.

## Verification

Applicability and buildability:

- `python -m pytest tests/security/test_matrix_approval_verifier.py tests/security/test_mcp_security_boundaries.py tests/integration/test_mcp_adapter.py tests/integration/test_mcp_state_persistence.py tests/runtime/test_production_agent_resources.py tests/security/test_repository_hygiene.py -q -p no:cacheprovider`
  -> `80 passed`
- `git diff --check` -> pass

Security closure:

- Duplicate Evidence/Response/Audit and approval-after-Audit calls are rejected
  and the serialized state remains byte-for-byte equivalent at the model level.
- `../outside` is rejected as `invalid scenario_id` before scenario parsing.
- A second trace at capacity is rejected and creates no second state file.
- Repository hygiene now scans the formerly missed formal handoffs and returns no
  credential-like finding after redaction.

Preserved behavior and repository checks:

- All approved identifiers S01-S24 retain their expected intake behavior.
- Existing pending, approved, rejected, persistence, hash-chain, and derived Audit
  behaviors remain covered.
- `python -m pytest -q -p no:cacheprovider` -> `114 passed`.
- Original self-assertion PoC plus legitimate Matrix-event control -> `2 passed`.
- R-09B6 post-reload runtime preflight -> `READY_RUNTIME`; live tool count and
  approval schema exact; historical and missing events fail closed.
- R-09B7 admin-origin structured event -> exact acceptance; trace and plan
  mismatches fail closed; state hash unchanged and no control trace file.
- R-09BB fresh synthetic S01 -> one admin Matrix event, one Commander-owned
  `log_approval`, exact event/reason digest binding, valid four-event canonical
  ledger, unique human approval, and no Audit or execution.

## Remaining uncertainty

- The hardened source and schema are live-loaded. Verifier identity/event
  controls and the fresh live MCP approval-tool attestation have passed. Caller
  input cannot supply the approver or reason facts; the verifier server-fetches
  and binds them from the Matrix event.
- The initially exposed verifier credential was replaced with a distinct identity;
  the replacement credential is DPAPI-protected and the compromised Human was
  deleted. Historical unrelated external credentials are outside this proof.
- Current AgentTeams and Higress/model-gateway governance is recorded separately
  in `docs/verification/R-09-runtime-governance-evidence.md`.
