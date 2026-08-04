# H-01 smoke evidence

Date: 2026-08-04

All evidence below is a redacted command summary. No login value, Matrix identifier, credential, endpoint secret, or container environment value is recorded.

## Resource tests

Initial RED:

```text
python -m pytest -q tests/runtime/test_hiclaw_resource_files.py
3 failed: smoke-worker.yaml and smoke-team.yaml were missing
```

GREEN after adding CRD-derived resources:

```text
python -m pytest -q -p no:cacheprovider tests/runtime
5 passed
```

## Create and visibility proof

```text
worker/sectrace-smoke created
name=sectrace-smoke
phase=Running
runtime=openclaw
model=qwen3.6-plus
matrix_user_present=true
room_present=true
```

```text
team/sectrace-smoke-team created
initial_phase=Pending
settled_phase=Active
leader_ready=true
team_room_present=true
leader_dm_room_present=true
```

This proves that the Manager can observe the Worker and Team and that the installed runtime created the Worker room, Team room, and Leader DM room.

## Delete proof: currently failing

```text
agt delete team sectrace-smoke-team
reported=deleted
manager_still_sees_team=true
controller_still_sees_team=true

agt delete worker sectrace-smoke
result=HTTP 409
reason=worker remains a member of sectrace-smoke-team
```

The identical Team delete was retried once, as permitted by the installed lifecycle guidance, with the same result. The cleanup defect is deferred as the non-blocking environment risk `H-01-RUNTIME-CLEANUP`. The two residual smoke resources must not be mistaken for production Workers; schema, creation, Manager visibility, and Matrix proof remain accepted for the H-01 handoff.
