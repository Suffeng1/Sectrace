# V-OPT2-01 Independent QA

- Owner: 05
- Date: 2026-08-13 (Asia/Shanghai)
- Result: **FAIL**
- Scope: OPT2-01 repository-only candidate working tree
- Plan commit: `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`
- Base commit: `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`
- Final commit: `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Handoff: `docs/handoffs/H-OPT2-01.md`
- Code preflight: `READY_CODE`
- Runtime/live activity: none; current runtime remains unknown

## Verdict

**FAIL**. The user journey, synthetic/protocol boundary, claim manifest and
portability boundary are materially consistent with the repository, and all
executed tests pass. However, two required acceptance gates are incomplete:

1. the six metric definitions do not identify an evidence source per metric,
   and the two distribution metrics do not state an explicit empty-sample/zero
   policy;
2. the new tests do not enforce the required metric fields and their
   unsupported-result/current-live claim filter is readily bypassed by common
   wording.

This is a specification-coverage failure, not a claim that a fabricated result
is currently present. No OPT2-01 benchmark result was found in the reviewed
documents.

## Blocking findings

### F-01: Metric definitions omit required evidence-source and zero policies

`docs/competition/value-baseline.md` defines all six requested metrics and gives
each a formula or distribution rule, population/denominator, applicability and
limitations. Its global `not_applicable` zero-denominator rule covers the four
rates. It does not, however, state the evidence source for any individual
metric. For example, trace completeness does not name the case manifest and
stage artifacts/event log as its evidence source, and approval correctness does
not name the verified decision and rejection records it would consume.

The E2E duration and manual-handoff count sections correctly explain that they
are distributions rather than fractions, but neither declares what is emitted
when no attempt is applicable or completes. The global zero-*denominator* rule
does not unambiguously cover an empty distribution.

Impact: an evaluator cannot implement all six metrics from a uniform declared
contract, and empty samples may be reported inconsistently. This fails the
explicit OPT2-01 requirement for formula, denominator/sample population,
applicability, zero policy, evidence source and limitation.

Minimum fix for owner 00:

- add an explicit `Evidence source` entry to every metric;
- add a per-metric `Zero/empty policy` entry, including `not_applicable` and an
  empty sample for both distributions;
- keep these as protocol definitions and publish no values.

### F-02: Focused tests do not prevent the required claim and metric regressions

`tests/test_competition_evidence.py` checks that six metric headings exist, but
does not parse each metric section or require Formula, Numerator/denominator or
sample population, Applicability, Zero/empty policy, Evidence source and Limits.
Consequently F-01 passes the focused suite.

The unsupported-claim patterns cover only a narrow set of English forms. A
read-only counterexample probe applied the exact patterns to four common
unsupported claims; all four went undetected:

```text
SecTrace is deployed in production.
SecTrace reduced mean response time by 40%.
The live runtime is healthy.
SecTrace cuts manual handoffs by 50%.
```

The second sentence bypasses the percentage rule because words occur between
`reduced` and the number; the other examples use equally ordinary production,
live and benefit wording outside the current alternations. Thus the test is not
sufficient to prevent unsupported production-benefit/current-live claims as
required, despite the present corpus being honestly bounded.

Minimum fix for owner 00:

- parse or delimit each metric section and require every declared field;
- add parameterized negative fixtures for deployed/in-production, live-runtime
  health/state and benefit/result wording, including intervening nouns and
  verbs such as `cuts`;
- retain the existing link-containment and repository-hygiene checks, which did
  successfully cover dangling local links, local machine paths and recognized
  credential forms.

## Non-blocking independent checks

### User journey and repository facts

- The journey follows Commander intake -> Evidence -> advice-only Response at
  `pending_approval` -> a verified human decision -> independent Audit.
- The current adapter exposes exactly six tools and no response-execution tool.
- Approval verification binds the decision to the current trace and plan,
  requires a trusted event source and refuses repeat/override decisions.
- Audit checks same-trace artifacts, evidence sources, missing requirements and
  ledger integrity, and exposes the verified ledger hash.
- The documents do not turn advice into execution or claim that a caller can
  self-attest approval.

### Synthetic comparator and retained unknowns

- The manual chat/spreadsheet comparison is prominently labeled
  `SYNTHETIC BENCHMARK PROTOCOL` and `PROTOCOL_ONLY_NO_MEASURED_RESULTS`.
- No elapsed-time, handoff-reduction, customer, enterprise or production result
  is published.
- Real workflow validation/timing, project origin, team contribution boundary,
  public team name, repository URL and registration metadata remain explicit
  manual TODOs.

### Evidence manifest

- The focused link check resolves every local Markdown target within the
  repository; no dangling or escaping path was found.
- Repository-only, design/protocol, runtime-unknown and point-in-time scopes are
  distinguished. Historical live evidence expressly does not attest current
  runtime, credentials, connectivity or service health.
- The narrow claims map to the referenced implementation/tests/verification
  records without converting historical live evidence into a current-live
  statement.

### Portability claims

- The invariant core matches the implemented typed Contract flow, human gate,
  canonical append path/hash verification and separate Audit projection.
- Data sources/normalization, role prompts and taxonomy, approval identity
  source/verifier policy, gateway/transport and organization policy are
  correctly treated as replaceable, acceptance-gated adapters.
- The matrix is labeled a design hypothesis and makes no external-deployment,
  official-Skill, OTel, RAG, regulator, fraud-accuracy or production-benefit
  claim.

### Diff, staged and untracked scope

- HEAD remained exactly `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`.
- Before this QA record, the dirty tree contained exactly the five owner files:
  three `docs/competition/` documents, `docs/handoffs/H-OPT2-01.md` and
  `tests/test_competition_evidence.py`.
- There were no tracked modifications and no staged files. `git diff --check`
  and `git diff --cached --check` passed.
- This QA report is the only file written by owner 05. No business code, test,
  material, configuration or runtime state was changed.

## Commands and results

| Command / check | Result |
| --- | --- |
| `scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python -m pytest -q -p no:cacheprovider tests/test_competition_evidence.py` | `3 passed` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `128 passed` |
| evidence-manifest local link check | PASS through focused test |
| unsupported-claim counterexample probe | FAIL: 4/4 unsupported forms bypassed patterns |
| `git diff --check` | PASS |
| `git diff --cached --check` | PASS |
| staged audit | 0 staged files |
| owner-candidate untracked audit before this record | exactly 5 expected files |

## Fixed completion report

```text
STATUS: FAIL
PLAN_COMMIT: 65d932d17f281de564a8b0a5379c93fcdc7fd1bc
BASE_COMMIT: 65d932d17f281de564a8b0a5379c93fcdc7fd1bc
FINAL_COMMIT: NO_COMMIT
FILES_CHANGED: docs/verification/V-OPT2-01-independent-qa.md
HANDOFF: docs/handoffs/H-OPT2-01.md
TESTS_RUN: code preflight; focused competition evidence; repository hygiene; full pytest; content/claim counterexample; diff/staged/untracked audits
TEST_RESULT: READY_CODE; 3 passed; 16 passed; 128 passed; FAIL on metric-contract completeness and unsupported-claim negative coverage
NEW_BEHAVIOR: none; independent repository-only QA record added
UNCHANGED_SAFETY_BOUNDARIES: synthetic/de-identified only; advice-only; human gate; no real action; trace continuity; no runtime/live/Matrix/external-system/credential access or mutation
KNOWN_LIMITATIONS: current runtime remains unknown; no benchmark was executed; no production benefit was measured; no official Skill, OTel, RAG or external deployment was verified
NEXT_HANDOFF: owner 00 should add per-metric Evidence source and Zero/empty policy fields, strengthen the focused metric/claim tests, rerun focused/hygiene/full/diff audits, and return a revised candidate to owner 05
```
