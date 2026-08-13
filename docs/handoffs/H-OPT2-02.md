# Handoff: OPT2-02 deterministic offline evaluation harness

- Owner: 00
- Status: `FOURTH_CORRECTED_OWNER_COMPLETE_REQA_PENDING`
- Plan commit: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Base commit: `9b725e48df05e78b20713d523c1af3f627572a4e`
- Final commit: `NO_COMMIT`
- Branch: `codex/adopt-apache-license`
- Code preflight: `READY_CODE`
- Runtime/live activity: none

## Delivered

- Added a pure-local, deterministic harness in `evaluation/`; it invokes only
  local Python code and never starts an MCP server, calls Matrix, reads
  credentials, accesses a network, or uses an LLM judge.
- Versioned the fixed dataset (`1.1.0`) and dataset/result schemas (`1.0`).
  Case ordering and metric ordering are fixed; runner exit codes are `0` for a
  fully passing evaluation, `1` for metric mismatch, `2` for an expected
  input/output boundary failure, and `3` for an unexpected internal evaluator
  failure.
- Reframed historical S02/S03 and related single-signal scenarios as a single
  case with explicit provenance and corroboration fields. The runner does not
  read a source scenario title or legacy `expected` field to select an oracle.
- Covered normal/corroborated, insufficient, conflicting, invalid approval,
  and tampered-ledger cases. The conflicting case is deliberately reported as
  `expected_fail_closed` and `capability_boundary: true`: the local repository
  implementation does not include the OPT2-04 conflicting-evidence terminal,
  and this task did not implement one. Runtime/live status is unknown.
- Added eight metric records. Every record emits `applicable_cases`, numerator,
  denominator, zero-denominator policy, evidence source, failure class and a
  pass flag. JSON and Markdown reports use the same metric records and display
  the same numerator/denominator values.

## RED / GREEN

- RED: focused evaluation tests could not import the absent runner.
- GREEN: `tests/evaluation/` passed after the minimal runner and metric builder
  were added.
- Hardening RED: the first implementation tried to write beneath a pre-existing
  inaccessible pytest temporary directory. It was changed to use a temporary
  directory that is deleted after every run, keeping high-frequency artifacts
  out of the repository.
- Hardening RED: an insufficient case's terminal oracle did not match the
  current local source-code audit projection. The dataset records the local
  `qualified` terminal while retaining the low-risk, observation-only branch
  expectation; this is a repository implementation description, not a
  runtime/live or production observation and not a new business rule.

## Run contract and report policy

Run from repository root:

```powershell
python -m evaluation.runner --json-out <path-to-result.json> --markdown-out <path-to-report.md>
```

The runner writes only caller-selected output paths. It does not track generated
JSON/Markdown reports because they are high-frequency verification artifacts.
For a release candidate, owner 05 may independently generate and write a stable
verification record under `docs/verification/`; that record must identify the
exact revision and must not be mistaken for current runtime/live evidence.

## Unchanged safety boundaries

- No public Contract, six-tool allowlist, canonical ledger event sequence or
  persistence behavior was changed.
- No 01–04 role business logic was changed.
- No runtime/live preflight, Matrix/S01 action, credential access, official
  Skill, OTel work, commit, or push occurred.

## Known limitations

- The conflicting case is a declared OPT2-04 boundary, not evidence that a
  persisted conflicting terminal exists.
- The harness evaluates local deterministic services and explicit semantic
  fixtures only. It does not measure live latency, cost, availability, or
  external approval delivery.

## Independent QA request (owner 05)

Owner 05 must write only under `docs/verification/` and independently:

1. run the focused evaluation tests and the CLI runner twice, comparing JSON
   and Markdown metric numerator/denominator values;
2. verify dataset/schema versions, ordering and exit codes;
3. confirm no oracle branch uses source scenario ID, title or legacy `expected`;
4. confirm all five case kinds and all eight required metrics are present;
5. confirm conflicting remains an explicitly bounded expected fail-closed case;
6. run hygiene, full pytest, diff/staged checks, and an untracked-file audit.

## Corrected owner cycle after V-OPT2-02 FAIL

- The initial owner candidate and the independent FAIL record are preserved.
  This correction changes only `evaluation/`, its tests, and this handoff.
- Invalid approval now executes a local `SafeMCPAdapter` trace with a real
  high-risk plan and calls `sectrace.ledger.log_approval`. The deterministic
  verifier rejects an unbound event with the production boundary's fixed
  `approval event is not authorized` error. Valid, invalid, and tampered
  approval-required traces are all counted in the approval-binding denominator.
- Dataset version `1.1.0` introduces unique, emitted trace identities. Startup
  performs Draft 2020-12 schema validation plus semantic validation: exactly
  the five required kinds, unique case/trace IDs, and kind/provenance/
  corroboration/approval/ledger consistency. Provenance and corroboration now
  jointly construct the fixture and are independently invariant-checked.
- The result schema constrains nested case results, exactly eight ordered
  metrics, summary integer types, and only exit codes `0` or `1`; it is
  executed before CLI output is written. Dataset schema validation is also
  executed by the runner, not just supplied as documentation.
- `scenario_run` now means pipeline completion and applies only to cases that
  actually execute it. The conflicting capability boundary is explicitly
  `expected_fail_closed`, has no trace, and is excluded from pipeline/trace/
  ledger denominators. `ledger_integrity_rate` declares `unique_trace`
  aggregation and deduplicates using the emitted trace ID.
- Core metrics have `zero_denominator_policy: fail`; therefore an empty core
  population cannot become a vacuous passing result. Each metric has a specific
  failure class.
- Malformed input, schema failure, and either output-write failure emit only
  `evaluation failed: invalid input or output` to stderr and exit `2`, without
  a traceback. Focused tests cover every V-OPT2-02 probe, including missing
  category, duplicate case/trace, nested schema error, semantic contradiction,
  malformed result, wrong oracle exit `1`, zero core population, and each CLI
  failure path.

## Corrected re-QA request (owner 05)

Keep `docs/verification/V-OPT2-02-independent-qa.md` unchanged. Write a new
corrected re-QA record under `docs/verification/` and independently verify the
nine findings from that record, especially the real adapter approval rejection,
the `3/3` approval denominator, unique-trace ledger denominator, schema
execution, non-leaking CLI exit `2`, and that the conflicting case is still a
non-executed capability boundary rather than an OPT2-04 implementation.

## Second corrected owner cycle after V-OPT2-02 corrected FAIL

- The first and corrected independent FAIL records remain unchanged. Dataset
  version is consistently `1.1.0`; all capability wording in this handoff is
  scoped to local repository implementation, with runtime/live state unknown.
- The deterministic verifier is initialized only after the adapter has created
  the real trace and plan, then requires exact event ID, trace ID, plan ID and
  decision. The invalid-approval evaluation calls the actual
  `sectrace.ledger.log_approval` entry point for three probes: wrong trace ID,
  wrong plan reference, and an unbound event. Each has a fixed expected
  rejection; focused tests also exercise the verifier's exact trace/plan rules.
- Scenario-run applicability is a declared semantic property of every
  non-conflicting case, independent of observed completion. A failed attempted
  run therefore remains in the denominator and fails the metric rather than
  disappearing from it.
- Exit `2` is now limited to JSON/schema/input and output I/O failures. An
  unexpected evaluator exception emits the distinct non-leaking message
  `evaluation failed: internal error` and exits `3`; it cannot be relabeled as
  malformed input/output.

## Third independent QA request (owner 05)

Do not edit either existing FAIL record. Write a new third re-QA record under
`docs/verification/` and independently reproduce: adapter rejection for wrong
trace and plan reference, exact verifier binding, failed-attempt scenario
denominator retention, malformed input/output exit `2`, internal failure exit
`3`, dataset version `1.1.0`, and repository-only wording. Re-run focused,
hygiene, full, determinism, report-consistency, diff/staged and untracked
audits.

## Third corrected owner cycle after V-OPT2-02 second-corrected FAIL

- Exit-code classification is now staged. Only dataset file read/JSON parsing,
  declared schema validation, and explicit result-output I/O boundaries map to
  the fixed non-leaking `exit 2` message. Any TypeError, RuntimeError,
  AssertionError, or other unexpected failure originating within evaluation
  execution maps to the separate non-leaking `exit 3` internal-error message.
  Focused tests cover internal TypeError and malformed schema data whose type
  is invalid, proving those two categories remain distinct.
- The formal invalid-approval case now executes four `SafeMCPAdapter`
  `sectrace.ledger.log_approval` probes before it can count as a successful
  approval-binding rejection: wrong trace, wrong plan, wrong decision, and an
  unbound event. All use only stable rejection names; the result emits the
  ordered probe names, not event content or other sensitive values.
- The primary run contract above is authoritative and lists all four fixed exit
  codes: `0` PASS, `1` metric gate fail, `2` expected input/output boundary,
  and `3` unexpected internal evaluator failure.

## Fourth independent QA request (owner 05)

Do not modify the three retained FAIL records. Write a new fourth re-QA record
under `docs/verification/` and independently verify staged exception handling
(including internal TypeError and malformed-schema type input), four formal
adapter probes recorded by the invalid-approval case, the 0/1/2/3 contract,
and the existing dataset/metric/schema/determinism safety boundaries. Repeat
focused, hygiene, full, determinism, JSON/Markdown consistency, diff/staged,
and untracked audits.

## Fourth corrected owner cycle after V-OPT2-02 third-corrected FAIL

- All four retained independent FAIL records remain unchanged. The conflicting
  expected-fail-closed case now has a complete semantic invariant: provenance
  is exactly two sources, same subject, and not an ordered risk sequence;
  corroboration is conflicting with contradictory claims; approval is exactly
  `required=false`, `decision=not_requested`, `binding_valid=null`; and the
  ledger is not tampered.
- Focused negative tests mutate each conflicting approval field, a combined
  approval object, and each declared provenance field. Every probe is repeated
  with the conflicting case first, middle, and last. The tests also structure
  check the approval triple for each of the other four case kinds, without
  changing their existing evaluation semantics.

## Fifth independent QA request (owner 05)

Do not edit the four retained FAIL records. Write a new fifth re-QA record
under `docs/verification/` and independently replay conflicting approval
field/combined and provenance mutations in first/middle/last order, verify the
other four approval invariants, and repeat focused, hygiene, full,
determinism, JSON/Markdown consistency, diff/staged, and untracked audits.
