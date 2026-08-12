# R-09B1 corrected Matrix verifier Human creation

- Date: 2026-08-11
- Result: `STOPPED_AT_PERMISSION_LEVEL_VALIDATION`
- Authorized mutation: one corrected supported Human creation call
- Human creation calls: one
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Preconditions

The candidate Human name `sverify` was absent before the call. R-09B had already
established a current `READY_RUNTIME` preflight and no Matrix verifier environment
configuration. The attempt used the supported Controller CLI and did not read a
browser credential or Synapse registration secret.

## Single corrected attempt

The exact request used:

`agt create human --name sverify --display-name "SecTrace Verifier" --accessible-workers sectrace-commander`

The call exited 1. Its complete error output was captured in a protected,
Git-external local file and was not printed. A later read-only, redacted
classification identified the server response as HTTP 500 with a Kubernetes
validation rejection: `spec.permissionLevel` had effective value 0, while the
schema requires a value greater than or equal to 1.

This evidence corrects the failure-layer hypothesis for this attempt: the request
reached the Controller and was rejected by resource validation. It does not prove
that Matrix account creation or room membership would succeed after validation.

## Postconditions and stop boundary

A supported read-only query after the failure returned `humans=[]` and `total=0`.
No partial Human or credential bootstrap exists. No third create call, alternate
account path, environment write, process stop/start, MCP reload, Matrix message,
S01, or approval occurred.

The minimum next mutation, if separately authorized, is exactly one supported
creation attempt with `--permission-level 1` and the same short name, display name,
and Commander-only access. It must capture credential output without displaying
values, stop on failure, and perform no Matrix send. Success alone would allow the
already-designed Git-external credential protection and separately gated MCP
reload sequence to continue.
