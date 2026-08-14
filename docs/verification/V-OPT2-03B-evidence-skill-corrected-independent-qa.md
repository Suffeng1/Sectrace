# V-OPT2-03B Evidence Skill corrected independent QA

- Task: `V-OPT2-03B` corrected cycle
- Owner: 05 independent QA
- Date: 2026-08-14
- Status: `QA_FAIL`
- Plan/base/final commit: `21079e03d88bed8f3a5a2066f5d2fe2281000414`
  / `21079e03d88bed8f3a5a2066f5d2fe2281000414` / `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Preflight: `READY_CODE`
- Scope: current unstaged and untracked corrected OPT2-03B artifacts; owner
  assertions were not accepted as evidence.

## Conclusion

The correction closes the original runtime blockers, but Schema/callable parity
is still incomplete, so OPT2-03B remains unsuitable for owner-00 registry
integration.

The blocking reproduction is case handling for temporary-directory-shaped free
text. The callable compiles its local-path policy case-insensitively, while the
three JSON Schema `safe_text_*` path patterns are case-sensitive. An uppercase
temporary-directory category was accepted by the input Schema but rejected by
the callable with the fixed invalid-payload error in all seven applicable free
text locations: scenario title; event region, subject, and note; and expected
conclusion, report-contains, and report-excludes. This violates the documented
same-boundary claim even though the runtime rejection itself is safe.

The Schema's secret-assignment pattern also uses the Python-specific inline
case-insensitive extension. It works with the repository's Python validator,
but is not portable ECMAScript regular-expression syntax for a declared Draft
2020-12 Schema. This should be corrected with the same portable case-explicit
pattern rather than relying on validator-specific behavior.

## Original FAIL preservation and hygiene redaction

The original
`V-OPT2-03B-evidence-skill-independent-qa.md` remains `QA_FAIL`, with every
finding, reproduction category, impact statement, and repair recommendation
substantively preserved. Owner 05 changed only the two hygiene-triggering probe
examples to generic category/placeholders and appended a dated preservation
note. No historical result was erased or upgraded.

## Independent corrected-cycle evidence

### Previous blockers

- Secret-assignment, local absolute, parent-relative, and lower-case temporary
  path categories were rejected by both Schema and callable across all seven
  safe-text fields with the exact non-leaking
  `ValueError("invalid evidence payload")`. No suspect probe value was printed.
- Hostile Mapping objects with unhashable iterated keys at root, event, and
  expected positions all returned the fixed invalid-payload error; no raw
  `TypeError` or `KeyError` escaped.
- Duplicate event references were rejected before correlation/output by the
  callable. Input arrays have `uniqueItems` where standard JSON Schema can
  express whole-item uniqueness; output evidence, risk-path, and related-ref
  arrays also declare uniqueness. The output Schema rejected independently
  duplicated items/references.
- A duplicate event reference across otherwise different event objects is
  accepted structurally by standard `uniqueItems` but rejected by the callable's
  property-level identity check. This deliberate callable-strengthening is
  documented in the owner Handoff; it did not produce an output. It is not the
  first failing layer in this cycle, but the Skill should avoid claiming literal
  equality between Schema and callable boundaries unless this distinction is
  stated.
- The Evidence-local trace policy accepted exactly 1- and 128-character valid
  identifiers in callable plus input/output Schema. Empty, 129-character,
  invalid-character, numeric, and boolean values were rejected by both input
  layers with the fixed error; invalid serialized output values were rejected by
  the output Schema. `src/app/contracts.py` was unchanged, and no global/public
  Contract claim was made.

### Behavioral and scope checks

- S01 golden output remained exact. Two calls were deterministic and deeply
  non-mutating, with trace/source/related references tied to supplied input.
- Independent changes to safe title, valid expected metadata, and matching
  scenario identity did not change evidence semantics, confirming no observed
  `scenario_id`, title, or expected business-oracle branch.
- Corpus replay accepted S01-S08 and S13-S24 and rejected intake-invalid S09-S12.
  The fact/unknown and risk-path distribution matched the frozen behavior.
- No inference output was invented because the current callable supports only
  its existing fact and unknown branches. No sufficient/insufficient/conflicting
  decision, re-analysis state, MCP/public Contract/canonical ledger/registry,
  Intake/Response/Audit, runtime, or live expansion was found.
- `SKILL.md` frontmatter still contains only `name` and `description`; system
  Skill Creator quick validation passed. The Evidence-local trace wording and
  no-live/no-official-Skill/evaluation limitations remain accurate.

## Gates run

| Gate | Independent result |
| --- | --- |
| code preflight | `READY_CODE` |
| focused Evidence + Skill | `55 passed` |
| repository hygiene after historical redaction | `16 passed` |
| complete pytest | `297 passed` |
| system Skill Creator quick validation | PASS |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS; index empty |
| staged audit | no staged files |
| untracked audit | owner artifacts plus the two owner-05 verification records |

Git continued to emit a read-only warning for an inaccessible user-level ignore
file; explicit status and untracked enumeration still completed. No commit,
push, runtime/live, Matrix, network, or external action occurred.

## Minimum owner-02 repair and re-QA

Make Schema path matching case-insensitive in a Draft-2020-12-portable way and
keep it exactly aligned with callable behavior for all `safe_text_*` definitions.
Replace the validator-specific inline case modifier in the secret-assignment
pattern with portable explicit case handling at the same time. Add mixed-case
temporary-path and mixed-case secret-category parity regressions without storing
or printing suspect values. Clarify in `SKILL.md` that property-level event-ref
uniqueness is an additional callable check if the standard Schema cannot encode
it directly.

Then rerun focused, hygiene, full, diff/cached, staged, and untracked gates and
request another owner-05 corrected-cycle QA. Preserve both historical records.
