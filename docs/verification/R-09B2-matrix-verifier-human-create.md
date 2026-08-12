# R-09B2 Matrix verifier Human creation

- Date: 2026-08-11
- Result: `STOPPED_CREDENTIAL_EXPOSURE_AFTER_CREATE`
- Authorized mutation: one supported Human creation call
- Human creation calls: one
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Preconditions

The current runtime preflight returned `READY_RUNTIME`. A supported read-only
query had established that no Human existed before the call. The fixed request
used name `sverify`, display name `SecTrace Verifier`, permission level 1, and
accessible Worker exactly `sectrace-commander`.

## Creation result

The Controller accepted the single request. A post-call resource projection
showed exactly one Human with the expected name, display name, permission level,
Commander-only Worker scope, Active phase, Matrix user ID, and one room.

The local wrapper then failed while trying to load the PowerShell security module
for a file-specific ACL. The response had already been saved under the previously
restricted, Git-external `%LOCALAPPDATA%\SecTrace` directory. No create retry was
performed.

## Security stop

The supported post-create `agt get humans -o json` projection unexpectedly
included the Human's initial password. That command output reached the task tool
transcript. The value is intentionally omitted from all repository evidence and
must be treated as compromised.

The compromised password was not copied into MCP environment configuration and
was not used to authenticate. No MCP process stop/start or reload, Matrix message,
S01, or approval occurred. Work stopped immediately rather than continuing with a
known-exposed credential.

## Required next authorization

Continuation requires a separately authorized supported credential revocation or
rotation operation. The replacement credential must never be returned through a
resource-list projection or task output; it must be captured directly into a
restricted Git-external store, followed by a metadata-only projection that omits
all credential fields. Only after a clean credential exists may MCP configuration
and reload be considered under their own runtime gate.
