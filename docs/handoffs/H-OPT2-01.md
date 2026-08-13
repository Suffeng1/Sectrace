# Handoff: OPT2-01 value baseline and competition evidence

- Owner: 00
- Status: `CORRECTED_OWNER_COMPLETE_REQA_PENDING`
- Plan commit: `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`
- Base commit: `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`
- Final commit: `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Code preflight: `READY_CODE`
- Runtime/live activity: none; current runtime remains unknown

## Delivered

- Added one judge-readable journey from synthetic/de-identified event intake,
  through Evidence and the Response pending gate, to human approval and Audit.
- Added a clearly labeled synthetic manual-chat/spreadsheet comparator. It is a
  benchmark protocol with no customer, enterprise or measured-benefit result.
- Defined six recalculable metrics with formula or distribution rule, numerator,
  denominator/sample population, applicability, per-metric zero/empty policy,
  evidence source and explicit limitations.
- Added a competition evidence manifest that maps narrow claims to concrete
  source/test/verification files and distinguishes repository-only,
  point-in-time, design/protocol and runtime-unknown scopes.
- Added an industry portability matrix separating invariant Contract/gate/ledger/
  Audit governance from replaceable data-source, prompt, approval-source and
  gateway adapters.
- Added focused tests for the complete seven-field contract of every metric,
  manifest path resolution, semantic production/current-live/quantified-benefit
  claim rules, bounded point-in-time/unknown/TODO/negative statements, local
  paths and credential-like content.

## RED / GREEN

- Initial RED: `tests/test_competition_evidence.py` -> `3 failed`; all three
  target competition documents were absent.
- First GREEN attempt: `2 passed, 1 failed`; C-01 linked to the existing
  `src/agents` directory, while the evidence gate requires concrete files.
- Final GREEN: changed C-01 to the four real role service files;
  `tests/test_competition_evidence.py` -> `3 passed`.

### Corrected owner cycle after V-OPT2-01 FAIL

- Independent QA `docs/verification/V-OPT2-01-independent-qa.md` remains an
  unchanged historical FAIL for the first owner candidate.
- Corrected RED: the strengthened metric/claim suite produced `11 passed,
  3 failed`: the uniform metric field contract exposed the missing
  denominator/evidence/zero fields, and two QA percentage counterexamples
  exposed an end-boundary defect in the new semantic rule.
- Additional hardening RED: after the first correction, compound-clause and
  noun-form benefit fixtures produced `17 passed, 2 failed`, preventing a broad
  `unknown` exemption and a verb-only benefit detector from being accepted.
- Corrected GREEN: all six metric sections use the same seven explicit fields;
  claim analysis splits contrast clauses and covers QA's common bypass forms
  while allowing bounded historical, unknown, TODO and negative statements.
  Focused result: `19 passed`.

## Claim and measurement boundaries

- `docs/competition/value-baseline.md` records **no measured result**. Its
  proposed nine manual actions are a workflow hypothesis that the user must
  validate before any comparison.
- E2E time and handoff count are distributions, not percentages. They explicitly
  emit `sample_size=0` plus `not_applicable` statistics for an empty sample. The
  four rates state their denominators and per-metric `not_applicable` policy.
- Historical live PASS records are linked only as point-in-time evidence. No
  Docker, AgentTeams, MCP transport, Matrix, S01, credential or external-service
  state was inspected.
- No business logic, runtime configuration, local submission artifact or
  production data was modified.

## Manual TODO retained

The following absent user inputs are explicit TODOs and do not block this
repository-only documentation baseline:

1. validate or replace the proposed manual chat/spreadsheet workflow;
2. provide publishable real-process timing only with provenance, consent, sample
   size and de-identification, otherwise keep the synthetic protocol;
3. state whether the project began from zero or extends prior work, plus member
   contribution boundaries;
4. provide public team name, repository URL and registration metadata during the
   release/material synchronization task.

## Independent QA request

Owner 05 should write only under `docs/verification/` and independently verify:

1. all six metric definitions are recalculable and do not encode results;
2. the proposed manual comparator is visibly synthetic and its unknown inputs
   remain manual TODOs;
3. every evidence-manifest link resolves and each claim stays within its listed
   repository-only or point-in-time scope;
4. the portability matrix preserves the Contract, human gate, canonical ledger,
   independent Audit and safety boundaries;
5. no unsupported production benefit/current-live claim, local absolute path,
   secret or credential-like value exists;
6. focused tests, hygiene, full pytest, diff/staged checks and untracked audit.

Do not treat this owner Handoff as independent QA. Do not modify business code
or sync local `outputs/submission` while reviewing OPT2-01.

## Final owner validation

- `scripts/sectrace-preflight.ps1 -Mode code` -> `READY_CODE`.
- `python -m pytest -q -p no:cacheprovider tests/test_competition_evidence.py`
  -> `19 passed`.
- `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py`
  -> `16 passed`.
- `python -m pytest -q -p no:cacheprovider` -> `144 passed`.
- `git diff --check` and `git diff --cached --check` -> pass.
- Tracked and staged audits -> no files; no existing tracked file was modified.
- Untracked audit -> the five owner OPT2-01 files plus owner-05's unchanged
  `docs/verification/V-OPT2-01-independent-qa.md`.
- HEAD remained `65d932d17f281de564a8b0a5379c93fcdc7fd1bc`; no commit or push was performed.

All corrected results above must be independently repeated by owner 05 in a new
corrected re-QA record; the original FAIL must not be overwritten.
