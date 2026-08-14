# Handoff: OPT2-00 facts freeze

- Owner: 00
- Status: `OWNER_COMPLETE_QA_PENDING`
- Plan commit: `UNTRACKED_PLAN_AT_START`
- Base commit: `d60792e197c0339ec0fa7ce507710dbaacc3d46c`
- Final commit: `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Code preflight: `READY_CODE`
- Runtime/live activity: none

## Delivered

- Corrected current requirements and release facts to the exact six-tool
  `src/app/mcp_adapter.py::TOOL_NAMES` allowlist while preserving the historical
  five-tool T-05 record as point-in-time evidence.
- Added a focused project-metadata RED test, then changed `pyproject.toml` from
  `0.0.0`/Planned to the completed initial release metadata `1.0.0`.
- Added focused documentation RED tests for the six-tool/current-resource facts
  and the two required evidence records.
- Restored `S-09-codex-security-scan.md` and
  `R-08BG-clean-s01-final-closure.md` from the already-sanitized contents of Git
  commit `c1c2b6832059277b80d7337ac44205dfbf1bd55c`; no evidence was invented.
- Restored the additionally discovered dangling
  `R-09B6-mcp-verifier-reload.md` reference from the same sanitized commit.
- Added superseded-tail sections to stale Handoffs while keeping their original
  RED/GREEN, FAIL, QA_PENDING, test-count, and live facts intact.
- Corrected the HiClaw resource README from future tense to the current
  repository state.
- Corrected root `CONTEXT.md` planned/pending language and the Phase 2 typed-model
  list to match the implemented shared Contracts and derived `AuditReview`.
- Added `docs/release-facts.md` as the single current-candidate draft.

## RED / GREEN

- Metadata RED: `tests/test_project_metadata.py` failed because the version was
  `0.0.0`; GREEN: `1 passed` after the minimal metadata change.
- Release documentation RED: `tests/test_release_documentation.py` failed because
  `docs/release-facts.md` and both restored evidence files did not exist; GREEN
  is recorded in the final command list below.

## Fact lineage

- Historical `114 passed` remains attached to S-09/V-05.
- Phase 2 planning-time `122 passed` remains labeled point-in-time.
- Current candidate full suite is `125 passed`; it must be rerun on a frozen RC.
- Remote default branch/current heads/merge state remain unverified because the
  read-only `git ls-remote` attempt could not connect to GitHub. No cached ref was
  promoted to a remote fact.

## Independent QA request

Owner 05 should write only under `docs/verification/` and independently verify:

1. exact current six-tool names and historical five-tool scoping;
2. `pyproject.toml` version/description and focused RED/GREEN coverage;
3. byte-for-byte provenance of the three restored records against commit `c1c2b68`;
4. no dangling evidence references, local absolute paths, secrets, or unsupported
   current/live claims;
5. full pytest, repository hygiene, diff/staged checks, and untracked audit;
6. historical FAIL records and superseded chains remain clear and unmodified in
   meaning.

Do not treat this owner Handoff or release-facts draft as independent QA.

## Final owner validation

- `scripts/sectrace-preflight.ps1 -Mode code` -> `READY_CODE`.
- `python -m pytest -q -p no:cacheprovider tests/test_project_metadata.py tests/test_release_documentation.py` -> `3 passed`.
- `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` -> `16 passed`.
- `python -m pytest -q -p no:cacheprovider` -> `125 passed`.
- Restored evidence blob hashes against `c1c2b68` -> all three exact matches.
- Verification-record reference audit -> `0` missing Markdown records.
- Local absolute-path audit -> `0` findings.
- `git diff --check` and `git diff --cached --check` -> pass.
- Staged audit -> no staged files.
- Untracked audit -> 10 files: the three Phase 2 plan files already present at
  task start, plus this Handoff, release facts, three restored verification
  records, and two focused tests.

Git emitted a warning that the user-global excludes file could not be read under
the current sandbox. The explicit tracked/untracked enumeration still completed;
owner 05 should repeat it in the independent environment.
