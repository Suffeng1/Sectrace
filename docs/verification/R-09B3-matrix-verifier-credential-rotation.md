# R-09B3 Matrix verifier credential rotation

- Date: 2026-08-11
- Result: `STOPPED_CREDENTIAL_NOT_ROTATED`
- Authorized mutations: delete `sverify` once; recreate `sverify` once
- Delete calls: one
- Create calls: one
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Preconditions

The current runtime preflight returned `READY_RUNTIME`. A secret-suppressing
wrapper asserted that exactly one `sverify` Human existed, was Active, used
permission level 1, and had accessible Worker exactly `sectrace-commander`.

## Rotation attempt

The wrapper deleted `sverify` once, then used an in-process Human projection to
confirm that the resource was absent. It recreated `sverify` once with the same
short name, display name, permission level 1, and Commander-only Worker scope.
All command responses were captured under the restricted, Git-external
`%LOCALAPPDATA%\SecTrace` directory. Only a fixed metadata projection was allowed
to reach task output.

## Failure gate

The recreated Human was Active and its scope matched the requested least
privilege boundary. However, an in-process comparison showed that the recreated
Human's initial password was identical to the compromised password from R-09B2.
No credential value or digest was printed or written to the repository.

This proves that deleting and recreating the AgentTeams Human does not rotate the
underlying Matrix credential for this identity. The credential remains
compromised and must not be used as MCP verifier configuration.

## Stop boundary

No further delete/create attempt, password login, password change, access-token
issuance, environment write, MCP process stop/start or reload, Matrix message,
S01, or approval occurred. The temporary rotation script was removed.

Continuation requires a separately authorized supported Matrix credential reset
or password-change flow whose new password and resulting access token are captured
directly into the restricted Git-external store and never emitted through a Human
resource projection. A successful reset must be followed by a secret-free login
control and an old-password rejection control before MCP configuration is
considered.

Read-only capability discovery after the stop showed that `agt rotate` supports
only Matrix AppService token rotation, not Human credentials. The local Matrix
client versions endpoint at `http://localhost:18080/_matrix/client/versions`
returned HTTP 200 with `application/json`. Therefore the next bounded candidate is
the standard Matrix client password-change flow, not another AgentTeams Human
delete/create cycle.
