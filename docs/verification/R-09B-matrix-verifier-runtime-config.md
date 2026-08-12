# R-09B Matrix verifier runtime configuration

- Date: 2026-08-11
- Result: `STOPPED_AT_HUMAN_CREATE_CLIENT_FAILURE`
- Authorized scope: least-privilege Matrix verifier identity, Git-external
  configuration, one MCP reload, transport/schema/fail-closed verification
- Mutations attempted: one exact Human creation call
- MCP reloads: zero
- Matrix sends/S01/approval: zero

## Before state

The approved host-access runtime preflight returned `READY_RUNTIME`. The 19090
listener was one `python.exe` process running `python -m src.app.mcp_server` from
the formal repository. None of the four Matrix verifier environment variables was
present in that process.

The supported AgentTeams CLI reported zero existing Human resources. Its
`create human` interface supports Matrix account plus room access and accepts
bounded Worker access, so it was selected instead of reading browser credentials
or Synapse registration secrets.

## Single creation attempt

One call attempted to create `sectrace-approval-verifier` with:

- display name `SecTrace Approval Verifier`;
- permission level 0;
- accessible Worker exactly `sectrace-commander`;
- a non-sensitive read-only purpose note.

The call exited 1. Its output was captured and not displayed. The intended
credential bootstrap file is written only after exit 0, so no bootstrap file was
created.

## Failure localization

Read-only follow-up proved:

- Human list query succeeds and still returns total 0;
- no partial verifier Human exists;
- Controller logs contain no matching Human request in the bounded interval;
- installed `agt` help/binary confirms name and display-name requirements, but
  exposes no more precise client-side validation constraint.

The first failure layer is therefore the installed `agt create human` client
before a Controller/Matrix request. The failure cannot be attributed to Matrix,
room membership, Controller authorization, or MCP configuration.

## Stop boundary and next authorization

No retry, alternative account creation route, browser-token extraction, Synapse
secret read, environment write, process stop/start, or MCP reload occurred.

The narrow next ticket is one corrected supported CLI attempt with a shorter
username and only required/scope parameters:

`agt create human --name sverify --display-name "SecTrace Verifier" --accessible-workers sectrace-commander`

It must again capture all credential output without displaying values, stop on
failure, and create no Matrix message. Success would permit DPAPI protection of
the returned verifier credential and continuation of the already-authorized
single MCP reload sequence.
