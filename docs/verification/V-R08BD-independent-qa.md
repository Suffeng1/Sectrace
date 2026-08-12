# V-R08BD Independent QA

- Date: 2026-08-11
- Scope: optional bounded intake `run_id`, repository/code only
- Conclusion: **PASS**
- Live runtime activation: not tested and not implied
- Runtime action: none

## Decision

The existing intake tool safely supports a distinct synthetic replay identity without changing the scenario identity or overwriting an append-only trace. `scenario_id=S01, run_id=R08BD` deterministically produces `tr_s01_r08bd`; the persisted file, Incident model, ledger records, envelope, and restarted adapter all preserve that same trace while Incident `scenario_id` remains `S01`.

Run IDs are constrained to 1–32 ASCII alphanumeric/underscore/hyphen characters with an alphanumeric first character and are normalized to lowercase. Duplicate normalized traces fail before state mutation. The MCP tool count and names remain unchanged.

## Original trace preservation

The formal `data/mcp-state/tr_s01.json` SHA-256 was measured immediately before and after all independent probes:

```text
formal_tr_s01_byte_unchanged=true
```

The formal file was never opened for writing. A separate temporary-state probe also created a base `tr_s01`, captured its exact bytes, created `tr_s01_r08bd`, and confirmed the base bytes remained identical.

This proves preservation only. The existing `tr_s01` remains contaminated historical evidence and is not made reusable by R-08BD.

## Distinct trace and restart

```text
distinct_file_model_ledger_trace=true
original_temp_bytes_unchanged=true
restart_loads_both=true
```

Independent checks confirmed:

- separate `tr_s01.json` and `tr_s01_r08bd.json` files;
- derived trace in envelope, top-level persisted state, IncidentCase, and every ledger record;
- Incident scenario identity remained `S01`;
- ledger hash chain was valid;
- adapter reconstruction loaded both traces without collision.

## Duplicate and normalization matrix

| Case | Result |
|---|---|
| Same run ID after restart | Rejected — PASS |
| Case-only collision (`R08BD` versus normalized lowercase) | Rejected — PASS |
| Existing base S01 trace recreated | Covered by focused test; rejected without overwrite |
| Files after duplicate attempts | Byte-identical — PASS |
| Duplicate error | Fixed `trace already exists`; no supplied value echoed |

Lowercase normalization makes case-only aliases converge on one trace identity instead of producing ambiguous parallel files.

## Run-ID boundary matrix

Accepted cases included:

- one-character alphanumeric;
- exactly 32 characters;
- leading digit;
- internal/trailing underscore and internal hyphen;
- uppercase input with deterministic lowercase trace derivation.

Rejected cases included:

- empty string and 33 characters;
- leading underscore or hyphen;
- dot and double-dot;
- forward- and backslash paths;
- dotted, colon, whitespace, and newline forms;
- non-ASCII/Unicode input;
- percent-encoded path-like input.

All 15 rejected probes returned only `invalid run_id`, did not echo the supplied value, and did not create a state directory or file.

## FastMCP schema

An in-process FastMCP registry was constructed without starting transport or importing the executable live server state.

```text
schema_exact_six=true
schema_run_id_present_optional=true
schema_run_id_nullable_string=true
```

- Tool names exactly matched the existing six-name allowlist.
- `scenario_id` remained required.
- `run_id` appeared as optional nullable string on `sectrace.intake.create_incident`.
- No seventh tool or execution capability was introduced.

The currently running MCP process was intentionally not restarted. Therefore this confirms the schema that FastMCP will expose after a separately authorized reload, not that the already-running old process has loaded R-08BD.

## TDD and regressions

The reported RED (`3 failed / 9 passed`) is mechanically credible: the preceding implementation ignored `run_id`, overwrote a duplicate trace, and therefore could not satisfy the new preservation/path rejection tests.

Fresh execution:

```text
code preflight: READY_CODE
persistence + MCP focused suite: 24 passed in 1.11s
full suite: 66 passed in 1.43s
git diff --check: passed (line-ending warnings only)
independent run-id/persistence/schema matrix: all checks passed
```

The full suite used process-local `GIT_CONFIG_COUNT` safe-directory injection only. No global or repository Git configuration was modified.

## Scope boundary

PASS covers repository implementation, temporary persistence, and the in-process FastMCP schema only. It does not authorize or prove an MCP reload, live schema change, creation of `tr_s01_r08bd` in formal state, Matrix/S01 dispatch, approval, Audit, configuration change, smoke action, commit, or push. R-08BB and V-08 remain unchanged until a separately authorized clean live run satisfies their evidence and governance gates.
