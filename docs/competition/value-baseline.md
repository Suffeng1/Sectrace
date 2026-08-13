# SecTrace value baseline and synthetic comparison protocol

Status: `PROTOCOL_ONLY_NO_MEASURED_RESULTS`

This document defines a reproducible competition baseline. It does not report
customer, enterprise, production, or live-runtime outcomes. SecTrace accepts
synthetic or de-identified inputs only, produces advice rather than executing a
security action, and requires a human gate for high-risk plans.

## Judge-readable user journey

The single journey is:

1. **synthetic/de-identified event intake** — a Commander intake creates an
   incident and a non-empty `trace_id`.
2. **Evidence** — Evidence derives fact/inference/unknown items from the supplied
   scenario while preserving the same `trace_id` and source references.
3. **Response pending gate** — Response creates an advice-only plan bound to the
   trace and stops at `pending_approval`; it does not execute the plan.
4. **human approval** — an allowed human decision must be verified and bound to
   the current `trace_id` and `plan_ref`. A caller cannot self-assert approval.
5. **Audit** — Audit independently checks the evidence, plan, approval and
   canonical ledger, reports missing requirements, and exposes the terminal
   ledger hash when integrity passes.

The repository proves individual controls and a deterministic local path. Any
historical live record is point-in-time evidence only and is not a statement
about the current runtime.

## Manual chat/spreadsheet comparison

### SYNTHETIC BENCHMARK PROTOCOL

The comparator is an honest exercise design, not observed enterprise data. A
facilitator gives the same synthetic or de-identified case packet to two paths:

- **manual path:** participants use only ordinary chat and a shared spreadsheet;
- **SecTrace path:** participants use the repository-defined journey above.

The proposed manual-path event log uses these observable actions. Each action is
logged, but its duration and count are not pre-filled:

1. receive and register the case in the spreadsheet;
2. send the case to an evidence analyst through chat;
3. copy evidence statements and source references back to the spreadsheet;
4. send the evidence summary to a response planner;
5. copy the proposed advice, risk and rollback notes into the sheet;
6. ask an allowed human approver for a decision;
7. copy the decision, case reference and plan reference into the sheet;
8. send the assembled record to an auditor;
9. reconcile missing or mismatched references before closing the exercise.

These are protocol steps, not a claim that every organization follows nine
steps. Before a competition result is published, the facilitator must validate
the manual workflow with the user and preserve the raw synthetic event log.

### Controlled execution

- Freeze one versioned case set and use the same ordered cases for both paths.
- Record path, case ID, run ID, expected terminal condition, timestamps and every
  manual handoff in a machine-readable event log.
- Use the same workstation class and facilitator instructions; state software
  versions and whether a warm-up run was excluded.
- Run enough repeated cases to publish the sample size and the full distribution,
  not only a favorable average. Do not pool cases with different applicability.
- For SecTrace, use a deterministic local/repository path unless separately
  authorized runtime evidence is collected. Label the execution mode.
- For the manual path, forbid hidden automation and log corrections instead of
  silently overwriting the spreadsheet.
- Preserve failed and rejected attempts. A retry is a new attempt linked to its
  original run ID.
- Redact operator identity and never place credentials or real incident content
  in the benchmark artifacts.

### Required human inputs

- **TODO (manual):** confirm whether the proposed chat/spreadsheet steps resemble
  the team's real baseline; otherwise replace them before measurement.
- **TODO (manual):** provide any publishable real-process timing only if its
  provenance, consent, sample size and de-identification can be documented.
- **TODO (manual):** confirm whether the project was built from zero or extended
  an earlier project, and state team-member contribution boundaries.
- **TODO (manual):** provide the public team name, repository URL and registration
  metadata during the release/material synchronization task.

## Metric specification

An **attempt** is one path/case/run tuple. The benchmark case manifest declares
the expected stages and invalid injections before execution. A stage is complete
only when its required artifact exists and passes the stated binding checks.
Unless stated otherwise, a zero denominator is reported as `not_applicable`, not
as zero or one. No target or observed result is recorded in this document.

### Trace completeness rate

- **Formula:** `complete_trace_attempts / applicable_trace_attempts`.
- **Numerator:** attempts in which every expected stage artifact has one non-empty
  `trace_id`, all values equal the intake trace, and all required references point
  to artifacts from the same attempt.
- **Denominator/sample population:** attempts whose case manifest expects at least two stage
  artifacts. A deliberately rejected pre-intake input is excluded.
- **Applicability:** both paths, after the manual spreadsheet is given an explicit
  trace field and the same expected-stage manifest.
- **Zero/empty policy:** if no attempt expects at least two stage artifacts,
  report `not_applicable`; do not emit a numeric rate.
- **Evidence source:** the frozen case manifest, per-attempt stage artifacts and
  the benchmark event log containing their trace and reference fields.
- **Limits:** the rate measures continuity and reference binding, not truth of the
  underlying evidence or production effectiveness.

### Approval binding correctness rate

- **Formula:** `correctly_bound_decisions / applicable_decision_attempts`.
- **Numerator:** accepted or rejected decisions with the expected trace, current
  plan reference, allowed human source and exactly one terminal decision; an
  invalid decision correctly refused is evaluated under the rejection metric.
- **Denominator/sample population:** attempts containing a plan that requires approval and a human
  decision submission.
- **Applicability:** both paths when the manual log captures plan, trace, source
  category and decision identifiers.
- **Zero/empty policy:** if no approval-required plan receives a human decision
  submission, report `not_applicable`; do not emit a numeric rate.
- **Evidence source:** plan artifacts, verified human-decision records, decision
  rejection records and the benchmark event log for the same attempt.
- **Limits:** identity assurance depends on the configured approval source. A
  synthetic verifier or spreadsheet field is not proof of enterprise identity.

### Invalid-state rejection rate

- **Formula:** `fail_closed_invalid_attempts / injected_invalid_attempts`.
- **Numerator:** injected invalid transitions or bindings rejected before partial
  state, approval or ledger mutation, with the rejection class logged.
- **Denominator/sample population:** all attempts declared invalid in the frozen case manifest
  before execution.
- **Applicability:** malformed or mismatched trace/plan decisions, duplicate or
  overriding decisions, out-of-order stages and tampered persisted/ledger state.
- **Zero/empty policy:** if the frozen manifest contains no invalid injection,
  report `not_applicable`; do not emit a numeric rate.
- **Evidence source:** the frozen invalid-injection manifest, pre/post state
  snapshots and rejection records with their declared failure class.
- **Limits:** only enumerated injections are covered; the metric is not a general
  security or adversarial-resilience score.

### Audit-chain completeness rate

- **Formula:** `complete_audit_chains / applicable_audit_attempts`.
- **Numerator:** attempts whose required incident, Evidence, Response, human
  decision and Audit records share the expected trace, whose canonical ledger
  order and hashes validate, and whose terminal hash matches the Audit output.
- **Denominator/sample population:** attempts where a plan requiring approval received an accepted
  human decision submission and Audit was requested. Rejected decisions remain
  auditable but must use a separately declared expected terminal condition.
- **Applicability:** runs that reach the declared Audit boundary.
- **Zero/empty policy:** if no attempt reaches its declared Audit boundary,
  report `not_applicable`; do not emit a numeric rate.
- **Evidence source:** the frozen case manifest, incident/Evidence/Response/
  decision/Audit artifacts, canonical ledger records and terminal-hash check.
- **Limits:** chain completeness proves integrity and linkage of recorded data;
  it does not prove that every real-world fact was captured.

### E2E elapsed time

- **Formula:** per completed attempt,
  `audit_terminal_monotonic_time - intake_accept_monotonic_time`; report sample
  size, median, p90, minimum and maximum rather than a single rate.
- **Numerator:** not applicable; each included attempt contributes one elapsed
  duration to the distribution.
- **Denominator/sample population:** all attempts that reach their declared
  terminal Audit condition; failures and timeouts are reported separately and
  are not silently dropped from the run summary.
- **Applicability:** both paths with timestamps from one monotonic clock. Publish
  wall-clock duration including human wait; optionally report system-active time
  separately, never substitute it for wall-clock time.
- **Zero/empty policy:** if no attempt reaches the declared terminal Audit
  condition, emit an empty sample with `sample_size=0` and all summary statistics
  as `not_applicable`; do not emit zeros for duration.
- **Evidence source:** the frozen case/run manifest and benchmark event-log
  timestamps for intake acceptance and the declared terminal Audit event.
- **Limits:** facilitator speed, human wait, hardware, warm-up and case complexity
  affect results. Cross-environment comparisons are invalid without disclosure.

### Manual handoff step count

- **Formula:** per attempt, `count(HANDOFF events)`; report the distribution and
  case-level counts.
- **Numerator:** not applicable; each included attempt contributes one count of
  qualifying `HANDOFF` events to the distribution.
- **Denominator/sample population:** all attempts admitted by the frozen case/run
  manifest, including attempts whose qualifying manual-handoff count is zero. A
  `HANDOFF` requires a person to copy, post, re-enter or reconcile case data
  between roles or tools; reading one's own prior entry does not count.
- **Applicability:** both paths using the same event taxonomy; automated role
  routing is logged separately and is not mislabeled as a manual handoff.
- **Zero/empty policy:** if no attempt is admitted, emit an empty sample with
  `sample_size=0` and all summary statistics as `not_applicable`. An applicable
  attempt with no qualifying handoff contributes the valid count `0`.
- **Evidence source:** the frozen case/run manifest and benchmark event log with
  actor, source, destination, tool and event-type fields for every transfer.
- **Limits:** the result depends on the validated workflow boundary. It does not
  measure cognitive load, decision quality or organizational staffing.

## Result publication gate

`NO RESULTS RECORDED`. Publish values only after the protocol, case set, raw
de-identified event log, computation script, exclusions and limitations are
available for independent recalculation. Until then, all six definitions are
measurement specifications, not achieved benefits.
