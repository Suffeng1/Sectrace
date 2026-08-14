# Skill compatibility and release check

The registry at `docs/skills/skill-registry.json` contains exactly the four
versioned local Skills: Commander/Intake, Evidence, Response, and Audit. Each
is at `1.0.0`, supports public Contract schema `1.0`, and is compatible only
with the ordered role chain `Commander -> Evidence -> Response -> Audit`.

This registry is discovery and verification metadata only. It does not install
a Codex Skill, add an MCP tool, or claim an official or current live Skill.
Evaluation evidence is limited to the recorded local full-pipeline scope; no
per-Skill score, runtime, or live result is published.

Before release, run `python scripts/check-skill-registry.py`, the focused role
tests, the four local Skill validations, repository hygiene, full pytest, both
diff checks, and an untracked-file audit. A release requires the registry test,
all gates, owner-05 independent QA, and a separately authorized release
decision. The current lifecycle is deliberately `qa_passed_registry_pending_release`.

The checker is read-only. It first validates the frozen Draft 2020-12 registry
schema, then validates only repository-contained existing paths, exact two-key
SKILL frontmatter, and callable role-bound entrypoints. For CHANGELOG parity,
the first heading matching `## <SemVer> - YYYY-MM-DD` is the declared current
version. It validates each input/output Schema's Draft 2020-12 marker, local
schema identity/version suffix, and schema structure. Failures return a
nonzero exit and only a fixed error category; they do not echo paths or data.

If a gate fails, do not publish. Roll back atomically by restoring the last
released Skill directory and its matching registry entry, then rerun every
release gate. Never rewrite public Contracts, trace data, canonical ledger
history, runtime state, or a historical verification record.
