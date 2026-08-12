# R-09B5 replace compromised Matrix verifier

- Date: 2026-08-11
- Result: `REPLACED`
- Replacement create calls: one
- Compromised identity delete calls: one
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Preconditions

The current runtime preflight returned `READY_RUNTIME`. A fixed wrapper validated
current-user DPAPI and asserted exactly one compromised `sverify` Human and no
`sverify2` Human. The old Human was Active, permission level 1, Commander-only,
and had exactly one Commander room.

## Replacement sequence

The wrapper created `sverify2` exactly once with display name `SecTrace Verifier`,
permission level 1, and accessible Worker exactly `sectrace-commander`. In the same
process it immediately consumed the one-time Human projection, stripped all
credential fields from output, and persisted the password with current-user DPAPI
under the restricted, Git-external `%LOCALAPPDATA%\SecTrace` directory.

The new identity passed all gated controls:

- Human phase Active and least-privilege Worker scope exact;
- Matrix password login returned the expected user;
- access-token `whoami` returned the expected user;
- joined rooms included the same Commander room as the old verifier;
- password and access token were stored only as DPAPI ciphertext;
- task output contained fixed metadata only and no secret.

Only after all controls and the final DPAPI store succeeded did the wrapper delete
the compromised `sverify` exactly once. The final in-process projection contained
one `sverify2` and no `sverify`.

## Stop boundary

No Matrix message, S01, approval, environment write, MCP process stop/start or
reload, Git commit, or push occurred. The temporary replacement script was
removed. This result establishes a usable Git-external verifier credential but
does not prove that the currently running MCP process has loaded it.

The next separately gated mutation is to project the four verifier settings from
the DPAPI store plus the fixed approver sender into the MCP launch environment,
perform exactly one controlled MCP reload, and then run transport/schema and
fail-closed/valid-event read-only controls before any S01 activity.
