# R-09B4 Matrix password change

- Date: 2026-08-11
- Result: `STOPPED_OLD_CREDENTIAL_UNAVAILABLE`
- Authorized mutation: one standard Matrix password-change flow
- Matrix login calls: zero
- Matrix password-change calls: zero
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Preconditions

The current runtime preflight returned `READY_RUNTIME`. The wrapper validated its
syntax, current-user DPAPI round trip, and the expected Active, permission-level-1,
Commander-only `sverify` Human metadata before any Matrix request.

## Bounded initialization failures

Two local wrapper defects were corrected before credential access: a parenthesis
error in a `Test-Path` condition and a missing explicit load of the
`System.Security` assembly. Both failures occurred before a recovery store,
Matrix login, or password-change request.

The current Human projection then showed the expected user and room but no longer
included the one-time `initialPassword`. The protected R-09B3 create response was
checked in memory and also did not contain that field. No credential value was
printed during these checks.

## Stop decision

The old password exists only in the earlier task transcript where it was exposed.
Reinjecting that plaintext from a transcript into a command, patch, or process
argument would create another secret-bearing record, so the password-change flow
was not attempted. No generated replacement password, pending DPAPI store, final
DPAPI store, access token, or Matrix device was created.

The safe recovery candidate is a distinct verifier identity. It must be created
once with permission level 1 and Commander-only scope; the wrapper must capture
the one-time password from an in-process immediate projection, validate a new
Matrix login, and store the password/token with current-user DPAPI without
printing a generic Human object. Only after the new identity is fully usable may
the compromised `sverify` be deleted. This replacement requires separate explicit
authorization.
