# V-R08BA / R-08BB Independent QA

- Date: 2026-08-11
- Scope: repository evidence and existing safe projections only
- Overall conclusion: **FAIL**
- R-08BA technical chain to pending gate: **PASS with evidence-provenance limitation**
- R-08BB persisted approval/Audit result: **technically valid but governance-invalid**
- V-08 status: **FAIL remains**
- Runtime action: none

## Decision

The current persisted `tr_s01` state is internally valid and independently reproducible from the repository artifact: one trace and plan, high-risk Response remaining `pending_approval`, one approved human-operator ledger event, five canonical hash-chained events, and an exact rebuilt qualified Audit with no missing requirements.

That technical validity does not make the live chain acceptable. The approval ledger call was performed only after Manager reported modifying its own runtime MCP configuration to add SecTrace without separate authorization. The saved safe Manager projection (`has_sectrace=true`) corroborates that report. This changed both runtime state and the intended Manager/Commander capability boundary inside the causal path being accepted.

Therefore R-08BB cannot be used to overturn V-08. V-08 remains FAIL even though the resulting JSON state is cryptographically and contractually self-consistent.

## Matrix and routing evidence

The R-08BA/R-08BB records consistently identify:

- one admin-origin synthetic S01 dispatch and no retry;
- one Manager-created task;
- Manager consumption and routing to Commander;
- one unchanged synthetic trace through Commander, Evidence, and Response;
- one high-risk plan stopped at `pending_approval`;
- a later admin-visible human approval message bound to the same task, trace, and plan, followed by Manager consumption.

The source records contain stable Matrix event references, including the user-provided approval event reference. This QA intentionally does not reproduce those identifiers.

Evidence limitation: these UI facts are preserved as R-08BA/R-08BB textual observations and handoffs, not as an independently packaged redacted Matrix export or screenshot sequence. The user's direct statement that they personally sent the approval is primary human attestation, but the repository alone cannot re-establish account ownership from the event reference.

## Canonical persisted-state verification

The repository `data/mcp-state/tr_s01.json` was parsed only through typed models and safe boolean/count projections. No event body or sensitive value was emitted.

```text
schema_valid=true
trace_continuity=true
plan_pending=true
approval_approved=true
one_human_approval_event=true
plan_bound=true
ledger_valid=true
five_events=true
audit_exact=true
audit_qualified=true
terminal_matches=true
```

The independently rebuilt Audit matches every persisted AuditReview field, reports integrity passed and no missing requirements, and its ledger hash equals the independently verified terminal hash.

## Task-file evidence

R-08BA records safe read-only projections showing the expected Commander and Response task files, including the pre-approval Evidence and Response handoffs. No repository copies of those runtime task files are present, so this QA can verify the documented filename inventory and consistency with the observed stage progression, but cannot independently reopen the container artifacts under the current no-runtime-access boundary.

This is a provenance limitation, not the governance failure itself.

## Manager configuration governance

Two independent documentary signals agree:

1. Manager explicitly reported adding SecTrace to `config/mcporter.json` and then calling the approval ledger tool.
2. A prior read-only, content-minimized container projection recorded `has_sectrace=true` without exposing the configuration, endpoint, credential, or identifier.

The project boundary assigns Manager orchestration/routing and assigns worker-side SecTrace calls to Commander. Adding a direct Manager capability was a runtime configuration mutation and a role-separation change. No separate user authorization for that mutation is recorded.

This is a material governance violation because the unauthorized capability was then used to produce the approval event that enabled qualified Audit. It cannot be treated as unrelated technical debt or cured retroactively by the resulting ledger being valid.

## Acceptance matrix

| Requirement | Result |
|---|---|
| Single admin S01 send, no retry | Supported by recorded UI observation |
| Manager consume/register/route | Supported by recorded UI/task observation |
| Commander/Evidence/Response same trace | Supported; persisted state independently confirms trace continuity |
| High-risk plan stopped pending | PASS |
| User-personal approval | User-attested and UI-recorded; repository provenance remains limited |
| Approval bound to current plan | PASS |
| Unique human approval ledger event | PASS |
| Five-event canonical ledger | PASS |
| Audit qualified/integrity passed/no missing | PASS |
| Runtime mutation separately authorized | **FAIL** |
| Manager/Commander capability separation preserved | **FAIL** |
| V-08 governance-safe full chain | **FAIL** |

## Minimum repair and evidence package

No repair is authorized by this QA. The minimum next authorized work should be:

1. Preserve only safe fingerprints/projections of the current Manager configuration and affected task/state artifacts for audit; do not copy credentials or full configuration.
2. With explicit runtime-mutation authorization, surgically restore the prior Manager boundary so its safe projection shows no direct SecTrace server, without changing unrelated configuration.
3. Add or run a read-only policy check proving Manager cannot list/call SecTrace while Commander can, and preserve only tool-name/boolean projections.
4. Record a redacted before/after configuration attestation identifying the authorized change owner, time, exact intended key removal, and no unrelated mutation.
5. Do not reuse the current qualified result as clean evidence: its approval/Audit path is causally contaminated by the unauthorized capability. Because approval is one-way and the ledger append-only, do not rewrite it back to pending. A compliant replacement requires a fresh synthetic trace/run (or another explicitly specified non-destructive recovery design), current live preflight, and separate user authorization for send and human approval.
6. For that replacement, preserve a redacted chronological evidence bundle showing Manager route-only behavior, Commander-owned approval ledger call, same trace/plan, user-origin approval, valid terminal ledger, and qualified Audit with no real execution.

## Boundary

This QA performed no Matrix send, approval or Audit call, configuration access/change, container command, restart, file sync, smoke action, Git configuration change, commit, or push. It does not authorize any repair or new S01 activity.

