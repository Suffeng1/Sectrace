# Changelog

All notable changes to the SecTrace Intake Skill are documented here.

## 1.0.0 - 2026-08-13

- Established the versioned Skill package for the existing
  `normalize_scenario` Commander boundary.
- Added Draft 2020-12 input and output JSON Schemas, golden and badcase
  fixtures, and schema/safety/failure-injection contract tests.
- Formalized non-mutating normalization, required boundary validation, allowed
  severity hints, and the pre-output real-data rejection gate.
- Added release gates, dependency declaration, evaluation-scope disclosure,
  and rollback guidance. No MCP tool, public Contract, ledger, or runtime
  behavior was added.

### Corrected owner cycle after independent QA FAIL

- Tightened input/output objects to `additionalProperties: false` and froze
  their allowlisted synthetic-corpus fields, types, and length limits.
- Required event semantics, supported event type enumeration, and strict UTC
  RFC3339 timestamps at both the Schema and runtime boundary.
- Made `real_data` accept only the JSON boolean `false`; all other values use
  the fixed non-leaking rejection. Normalization now returns a deterministic
  deep copy.
- Added QA counterexample coverage for unknown fields, sensitive-looking field
  names, bounds, type bypasses, timestamps, unknown semantic values, and the
  S01–S24 corpus. Root dependency declaration remains a 00-owned handoff.
