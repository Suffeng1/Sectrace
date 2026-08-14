# V-OPT2-03E Skill Registry Independent QA

- Task: `V-OPT2-03E`
- Owner: `05` independent QA
- Base commit: `445dd00`
- Scope: current uncommitted OPT2-03E repository-only candidate
- Preflight: `code` -> `READY_CODE`
- Result: **QA_FAIL**

## Blocking finding

The registry's positive data is internally consistent, but the required
fail-closed registry boundary is not implemented. Independent mutations against
`docs/skills/skill-registry.schema.json` produced:

| Mutation | Schema result | Required result |
| --- | --- | --- |
| duplicate Skill `name` | ACCEPT | REJECT |
| duplicate `role` | ACCEPT | REJECT |
| unknown Skill `name` | ACCEPT | REJECT |
| nonexistent repository-relative `skill_path` | ACCEPT | REJECT |
| syntactically valid but nonexistent `entrypoint` | ACCEPT | REJECT |
| bad version `2.0.0` | REJECT | REJECT |
| bad role `Operator` | REJECT | REJECT |
| unknown item field | REJECT | REJECT |

`scripts/check-skill-registry.py` only validates the document against that
schema. It does not verify exact frozen membership/order, uniqueness, path
existence, frontmatter/version parity, schema identity, importability, or that
the callable belongs to the registered role. Consequently the checker cannot
close the five accepted-negative gaps above. The committed registry contract
tests exercise the positive registry and unknown fields, but do not mutate and
reject duplicates, unknown names, missing paths, or nonexistent/wrong-role
entrypoints.

This is release-blocking because the frozen OPT2-03E requirement explicitly
requires duplicate/unknown/bad-path/bad-entrypoint cases to fail closed. A
green check of only the current known-good file is insufficient evidence for
that boundary.

## Verified non-blocking requirements

- The current registry contains exactly four entries in stable Commander ->
  Evidence -> Response -> Audit order. Its names, versions, roles, paths,
  lifecycle, status, evaluation limits, and current entrypoints match the four
  local artifacts.
- All declared paths in the current registry are repository-relative and
  exist. No local absolute path, user directory, credential, or secret claim
  was found in the candidate artifacts.
- All four `SKILL.md` frontmatter blocks contain only `name` and `description`;
  registry names/descriptions and `1.0.0` versions match SKILL/CHANGELOG. The
  Intake diff is exactly the five-line standards-compliance frontmatter
  insertion; its body and callable behavior are unchanged.
- Each current entrypoint imports as a callable and corresponds to its stated
  role. Registry MCP lists are empty. The artifacts do not claim that a Skill
  is an MCP tool, an official Alibaba Cloud Skill, currently live, installed,
  or independently scored per Skill.
- The registry schema is Draft 2020-12, uses required fields and
  `additionalProperties: false`, and correctly rejects bad version, bad role,
  and unknown fields. Those strengths do not compensate for the accepted
  negative cases.
- The checker is deterministic, read-only on the inspected successful run,
  and emits only a fixed non-sensitive result. Its semantic coverage is the
  blocker described above.
- `docs/skills/compatibility-and-release.md` accurately limits compatibility
  to public Contract `1.0` and the fixed four-role chain, requires the release
  gates plus owner-05 QA and separate authorization, describes atomic Skill +
  registry rollback, and disclaims official/current-live/per-Skill results.
- Diff, staged, and untracked inspection found no four-Skill business-logic,
  MCP, public Contract, ledger, runtime, submission, PPT, or README expansion.
  The staged index is empty. Git's inaccessible user-ignore warning is an
  environment-only warning; explicit untracked enumeration succeeded.

## Reproduced checks

| Command/check | Result |
| --- | --- |
| `pwsh -File scripts/sectrace-preflight.ps1 -Mode code` | `READY_CODE` |
| `python scripts/check-skill-registry.py` | `Skill registry is valid.` |
| `python -m pytest -q -p no:cacheprovider tests/skills/test_registry_contract.py` | `6 passed` |
| `python -m pytest -q -p no:cacheprovider tests/commander tests/evidence tests/response tests/audit tests/skills` | `199 passed` |
| four skill-creator `quick_validate.py` runs | `4/4 Skill is valid!` |
| `python -m pytest -q -p no:cacheprovider tests/security/test_repository_hygiene.py` | `16 passed` |
| `python -m pytest -q -p no:cacheprovider` | `380 passed` |
| independent eight-case registry mutation matrix | five improper ACCEPTs; three expected REJECTs |
| `git diff --check` / `git diff --cached --check` | PASS / PASS |
| staged audit | empty |
| untracked audit | only OPT2-03E registry/docs/checker/test/Handoff plus this QA record |

## Minimum repair only

1. Freeze the four ordered entries in the schema (for example with exact
   `prefixItems` constants and no additional items) so duplicate/unknown
   name/role and mismatched frozen metadata reject structurally.
2. Extend the read-only checker to enforce repository-contained existing
   paths, exact SKILL frontmatter and CHANGELOG version parity, valid local
   schemas, importable callables, and the exact role-to-entrypoint mapping.
3. Add focused negative tests for duplicate name/role/entrypoint, unknown
   Skill, missing/traversal/absolute paths, bad version/role, unknown fields,
   nonexistent entrypoint, and an importable but wrong-role entrypoint; prove
   the checker returns nonzero with fixed non-leaking output.
4. Re-run every recorded gate and request a new owner-05 independent QA. Do
   not broaden into Skill business logic, MCP, Contract, ledger, runtime, or
   release activity.

## Controller status

TASK_ID: V-OPT2-03E
STATUS: QA_FAIL
FILES_CHANGED: `docs/verification/V-OPT2-03E-skill-registry-independent-qa.md`
RUNTIME_LIVE_NETWORK: none
COMMIT_PUSH: none
