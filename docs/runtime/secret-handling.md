# Secret handling

## Repository boundary

- Runtime credentials stay outside Git and outside Worker prompts.
- Repository hygiene findings disclose only a repository-relative path and a rule name.
- The hygiene scanner does not read user-owned HiClaw local configuration; under `hiclaw/`, only the repository-safe example and documentation paths are eligible.
- Screenshots, recordings, handoffs, and terminal transcripts must not contain credentials or matched values.

## TDD security summary

- RED command: `pytest tests/security/test_repository_hygiene.py -v`
- RED result: expected collection failure because `tests.security.repository_hygiene` did not exist.
- No credential-like value was printed or recorded.
- GREEN command: `pytest tests/security/test_repository_hygiene.py -v -p no:cacheprovider`
- GREEN result: 2 tests passed.
- Regression command: `pytest -v -p no:cacheprovider`
- Regression result: 4 tests passed.

## Operator action

Credential rotation is required outside this repository. Completion has not been asserted because authorization to edit the repository is not evidence that the operator performed rotation.


## QA remediation

- Regression added: tracked HiClaw Worker YAML and prompt-eligible files are scanned.
- Explicit local configuration exclusions: user-owned `hiclaw/start_hiclaw.py`, ignored environment files, secret/credential/token files, and `config.local.*`.
- Targeted result: 4 tests passed.
- Full regression result: 6 tests passed.
- QA verdict remains unchanged until independent re-verification.
