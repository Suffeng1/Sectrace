# V-OPT2-03B Evidence Skill second-corrected independent QA

- Task: `V-OPT2-03B` second-corrected cycle
- Owner: 05 independent QA
- Date: 2026-08-14
- Status: `QA_PASS`
- Plan/base/final commit: `21079e03d88bed8f3a5a2066f5d2fe2281000414`
  / `21079e03d88bed8f3a5a2066f5d2fe2281000414` / `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Scope: current unstaged and untracked second-corrected OPT2-03B artifacts;
  owner Handoff results were not accepted as evidence.

## Conclusion

The second correction passes independent QA for the Evidence Skill artifact and
the requested repository gates. The prior two `QA_FAIL` records remain unchanged
and continue to describe their revision-scoped failures; this PASS supersedes
neither history nor any runtime/live/external claim.

Pre-QA content hashes for the preserved records were:

- original QA_FAIL: `da16326935e0c14a5a839b302764d7fadc1fd7c9`
- corrected-cycle QA_FAIL: `67bb21186aef023bac2d8ef5c8b83415e562fcda`

The same hashes were rechecked after this record was created.

## Independent evidence

### Draft 2020-12 and safe-text parity

- Extracted all 13 input-Schema regex patterns and compiled them with the Node
  ECMAScript `RegExp` implementation in Unicode mode: zero compilation failures.
- A targeted scan found zero Python-only inline mode-flag forms. Legal
  non-capturing groups were not misclassified as flags.
- Ran 70 independently constructed in-memory combinations across all seven
  allowed free-text locations: scenario title; event region, subject, and note;
  and expected conclusion, report-contains, and report-excludes. The matrix
  covered mixed-case secret-assignment categories, local absolute/UNC/parent
  paths, and lower/mixed-case temporary-directory categories.
- All 70 combinations were rejected by the Schema and by the callable with the
  exact non-leaking `ValueError("invalid evidence payload")`; no probe value was
  printed or stored. Seven benign controls were accepted by both layers.

### Previous blockers and boundaries

- Hostile Mapping objects with unhashable iterated keys at scenario, event, and
  expected positions all returned the fixed invalid-payload error. No raw
  `TypeError` or `KeyError` escaped.
- A duplicate `event_ref` across otherwise different event objects was rejected
  before correlation/output. The complete input Schema also rejected the paired
  duplicate raw references. Output Schema probes independently rejected
  duplicated risk-path entries, related references, and identical evidence
  objects.
- `SKILL.md` accurately states that JSON Schema `uniqueItems` covers identical
  full event objects while runtime additionally enforces property-level
  `event_ref` uniqueness across otherwise different objects.
- The Evidence-local trace policy accepted valid identifiers at lengths 1 and
  128 in callable/input/output Schema. Empty, length 129, invalid-character,
  numeric, and boolean identifiers were rejected with exact callable/Schema
  parity. The shared Pydantic Contract was not changed, and the Skill correctly
  labels this as a local boundary.

### Behavior, fixtures, corpus, and scope

- S01 serialized output exactly matched its golden fixture. Repeated calls were
  deterministic, the input remained deeply unchanged, and all source/risk/
  related references were unique and tied to supplied input.
- The real-data badcase returned the exact fixed synthetic/de-identified-only
  error without producing evidence or disclosing input.
- Independent safe changes to title, valid expected metadata, and matching
  scenario identity left evidence semantics unchanged. No scenario identifier,
  title, or expected business-oracle branch was observed.
- S01-S08 and S13-S24 remained accepted; intake-invalid S09-S12 remained
  rejected. Fact/unknown output and risk-path distribution matched the frozen
  corpus behavior.
- The callable continues to emit only its existing fact/unknown paths; it did
  not add OPT2-04 sufficient/insufficient/conflicting state or re-analysis.
- Modified production files remain confined to Evidence service and its
  compatibility README. Untracked artifacts remain confined to the owner-02
  Evidence Skill/tests/Handoff and owner-05 verification records. No shared
  Contract, MCP tool/allowlist, canonical ledger, registry, Intake, Response,
  Audit, runtime, or live artifact changed.
- `SKILL.md` frontmatter contains only `name` and `description`; its trigger,
  permission, release, rollback, local-trace, uniqueness, evaluation, and
  no-live/no-official-Skill statements match the inspected facts.

## Gates run

| Gate | Independent result |
| --- | --- |
| code preflight | `READY_CODE` |
| focused Evidence + Skill | `69 passed` |
| system Skill Creator quick validation | PASS |
| repository hygiene after this record | `16 passed` |
| complete pytest after this record | `311 passed` |
| ECMAScript regex compile/flag scan | 13 patterns; 0 failures; 0 Python-only flags |
| mixed-case safe-text matrix | 70/70 rejected with Schema/fixed-callable parity |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS; index empty |
| staged audit | no staged files |
| untracked audit | expected owner artifacts plus three owner-05 QA records |

Git emitted a read-only warning for an inaccessible user-level ignore file;
explicit status and untracked enumeration still completed. No commit, push,
runtime/live, Matrix, network, or external action occurred.

## Handoff

Owner 00 may proceed with its separate registry/integration review for this
revision, subject to its own scope and release gates. This QA_PASS covers only
the current local code/Skill artifacts and deterministic repository evidence;
it establishes no runtime/live, production, third-party, or official external
Skill state.
