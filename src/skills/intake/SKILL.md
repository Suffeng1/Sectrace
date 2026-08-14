---
name: sectrace-intake
description: Validate and normalize supplied synthetic SecTrace scenarios before Commander creates an IncidentCase, without external access or actions.
---

# SecTrace Intake Skill

- Version: `1.0.0`
- Owner: `01` (Commander / intake)
- Entrypoint: `src.skills.intake.normalize.normalize_scenario(scenario: dict) -> dict`
- Dependencies: Python 3.11+ at runtime; `jsonschema>=4,<5` is declared in
  the root development dependency set and is used only by schema contract tests.

## Purpose and executable boundary

This Skill validates and normalizes a scenario payload before Commander builds
an `IncidentCase`. It returns a deeply copied payload with
`expected.severity_hint` defaulted to `low`. It never mutates the caller's
payload. `src/agents/commander/service.py::build_incident` is the production
consumer of this function.

It is not an MCP tool and does not add to, rename, or invoke the six-tool
allowlist. It does not create an `IncidentCase`, select a response, contact a
system, scan a target, send a message, approve an action, write the ledger, or
execute remediation.

## Contract

- Input schema: [`schema/input.schema.json`](schema/input.schema.json)
- Output schema: [`schema/output.schema.json`](schema/output.schema.json)
- Input requires exactly the declared root, event, and `expected` properties;
  each object has `additionalProperties: false`. `scenario_id` is bounded to
  64 characters; events require bounded `event_ref`, `event_type`, UTC RFC3339
  `at`, and bounded `subject`. The three supported event types are
  `anomalous_login`, `privilege_elevation`, and `bulk_sensitive_data_access`.
- `real_data` must be the JSON boolean `false`. `true`, absent values, strings,
  numbers, arrays, and objects all fail with the fixed non-leaking
  `ValueError`. The callable itself enforces this contract; it does not rely on
  a caller having run JSON Schema validation.
- `classification: "unknown"` is an allowlisted semantic value. An unknown
  property is not accepted. Path- or secret-like *undeclared fields* are also
  rejected rather than copied downstream. The synthetic corpus's allowlisted
  `note` field remains bounded data, not a secret field.
- Output is a deep copy, preserves allowed field values and event order, and
  guarantees `expected.severity_hint`.

Golden fixture: [`fixtures/golden-synthetic-login.json`](fixtures/golden-synthetic-login.json).
The paired normalized output makes the default explicit. The schema-shaped
rejection fixture is [`fixtures/badcase-real-data.json`](fixtures/badcase-real-data.json).

## Failure injection and quality gates

Contract tests inject every missing root/event required field; extra/path-like/
secret-like fields; overlong IDs; non-scalar enum values; unsupported event
types; invalid or non-UTC RFC3339 timestamps; and all non-boolean or true
`real_data` values. All malformed inputs fail before output with the exact
non-leaking `ValueError("invalid intake payload")`; invalid `real_data` values
use the fixed data-safety error. Tests also prove deterministic deep-copy
behavior and run the complete synthetic S01–S24 corpus, retaining its four
intentional intake rejections (S09–S12).

Before release run:

```powershell
python -m pytest -q -p no:cacheprovider tests/commander tests/skills/intake
python -m pytest -q -p no:cacheprovider
git diff --check
git diff --cached --check
git status --porcelain=v1 --untracked-files=all
```

Release requires all commands to pass, a compatible shared registry entry from
owner 00, and independent verification by owner 05. Do not publish or claim
registry integration until those owners complete their work.

## Evaluation evidence

OPT2-02's committed local deterministic evaluation is dataset version `1.1.0`
and reports eight passing metrics in its revision-scoped verification record
[`docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md`](../../../docs/verification/V-OPT2-02-fourth-corrected-independent-qa.md).
Those metrics evaluate the full local pipeline, not Intake in isolation. This
Skill makes no invented per-Skill accuracy, latency, cost, runtime, or live
claim.

## Release and rollback

`1.0.0` is the initial documented release. A compatible patch release may add
documentation or preserve the schemas and function behavior. Any input/output
schema or error-behavior change requires a SemVer compatibility assessment and
owner 00 registry review.

To roll back, restore the last released `src/skills/intake/` directory together
with its matching registry entry, then re-run the quality gates. Do not alter
historical ledger records, Contracts, or trace data to perform a rollback.
