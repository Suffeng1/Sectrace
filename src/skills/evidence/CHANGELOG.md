# Changelog

## 1.0.0 - 2026-08-13

- Documented the existing Evidence callable with strict input/output schemas,
  synthetic golden/badcase fixtures, and deterministic boundary tests.
- Added fail-closed callable validation for malformed inputs while preserving
  the existing sourced fact path and insufficient-evidence behavior.
- Added release, dependency, evaluation-scope, and rollback boundaries. No MCP
  tool, public Contract, ledger, registry, runtime, or live behavior changed.

### Corrected owner cycle after V-OPT2-03B QA_FAIL

- Added one shared free-text value policy for schema and callable validation;
  it rejects secret-assignment and local/absolute/temp-path values without
  returning the supplied value.
- Required unique event/source references before correlation and added
  `uniqueItems` to applicable input/output arrays.
- Rejected non-JSON and hostile Mapping inputs before traversal so malformed
  keys cannot escape as raw exceptions.
- Added the owner-00-approved Skill-local `trace_id` format and 1–128 length
  bound to the callable and input/output schemas; this does not change the
  public Contract.

### Second corrected owner cycle after corrected QA_FAIL

- Replaced Python-specific inline case-insensitive schema regexes with portable
  explicit-case Draft 2020-12 / ECMA-262-compatible patterns.
- Added mixed-case secret-assignment and temporary-path regression coverage at
  all seven safe-text input locations.
- Clarified that schema `uniqueItems` compares complete event objects while
  runtime separately enforces `event_ref` identity uniqueness.
