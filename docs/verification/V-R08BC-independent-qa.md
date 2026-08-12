# V-R08BC Independent QA

- Date: 2026-08-11
- Scope: Manager route-only boundary restoration
- Conclusion: **PASS**
- Runtime action by QA: none
- Historical effect: none; R-08BB and V-08 remain FAIL

## Decision

The preserved R-08BC evidence is sufficient to verify that the explicitly authorized mutation removed only Manager's `mcpServers.sectrace` capability and restored the intended route-only boundary without an observed unrelated semantic configuration change.

The post-change capability split is correct:

- Manager cannot resolve a SecTrace MCP server.
- Commander still exposes exactly six live SecTrace tools, including approval logging.
- Runtime preflight was READY_RUNTIME both before and after the authorized write.

This PASS is prospective only. It does not retroactively legitimize the unauthorized Manager capability used during R-08BB, does not pass V-08, and does not make the existing `tr_s01` eligible for reuse as clean evidence.

## Authorization and write boundary

- User authorization specifically covered restoring Manager route-only by removing `mcpServers.sectrace`.
- Recorded mutation count was one.
- The removed path was exactly `mcpServers.sectrace`.
- No restart, message, S01, approval, Audit, file sync, smoke, commit, or push accompanied the change.

The mutation stayed within the granted scope.

## No-adjacent-change verification

The before projection recorded both the original file hash and a semantic hash of the complete configuration with only the target key removed. The after projection recorded a different file hash and a complete semantic hash exactly equal to that before-rest hash.

Independent consistency checks:

```text
hashes_well_formed=true
before_rest_equals_after_semantic=true
file_hash_changed=true
single_target_mutation=true
other_semantics_unchanged=true
no_temp_residue=true
```

This proves, within the minimized evidence model, that the serialized file changed while every JSON semantic outside the authorized key remained equal. The atomic write used one unique temporary file, flush/`fsync`, rename, preserved mode, and left no temporary residue.

No endpoint, credential, complete configuration value, or runtime identifier was required or exposed for this verification.

## Capability and health postconditions

```text
manager_denied=true
commander_six_tools=true
runtime_pre_after=true
no_restart=true
```

- The single Manager read-only probe stopped locally with unknown-server classification before transport. This is the expected proof that Manager no longer owns the SecTrace MCP capability.
- Commander independently retained the six-tool live schema, including `sectrace.ledger.log_approval`.
- The write-after runtime preflight remained READY_RUNTIME, including the recorded Host and Commander transport/initialize checks.

Together these demonstrate removal from Manager without removing the worker-owned Commander capability or degrading the checked runtime path.

## Contaminated trace preservation

The existing `tr_s01` artifact remains unchanged in governance meaning and was not rewritten or reused. A safe independent projection still confirms:

```text
approval_status=approved
ledger_event_count=5
ledger_integrity=valid
audit_status=qualified
```

These values prove preservation, not acceptability. The chain remains causally contaminated by the earlier unauthorized Manager configuration and approval call.

## Governance consequences

- R-08BC boundary restoration: **PASS**.
- R-08BB historical governance verdict: **FAIL unchanged**.
- V-08: **FAIL unchanged**.
- Existing `tr_s01`: append-only historical evidence only; **must not be reset, re-approved, or presented as a clean replacement run**.

A future clean V-08 candidate still requires a distinct synthetic trace/run, current live preflight, separate send and human-approval authorizations, Manager route-only evidence, and a Commander-owned approval ledger call.

## Evidence limitation

Under the no-runtime-access QA boundary, this review validates the saved minimized projections and their cryptographic/semantic consistency; it does not reread the full Manager configuration or rerun the container probes. That limitation does not weaken the no-adjacent-change conclusion materially because the evidence includes the exact before-rest/after semantic hash equality and independent capability split projections without exposing configuration content.

## Boundary

This QA changed only this verification file. It did not access or modify runtime configuration, invoke MCP, restart services, send Matrix messages, run S01, approve, audit, sync files, touch smoke, change Git configuration, commit, or push.

