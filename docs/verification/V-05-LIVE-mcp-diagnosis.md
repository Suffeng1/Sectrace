# V-05-LIVE Commander-to-MCP diagnosis

Date: 2026-08-05

## Human UI evidence

The operator observed the single S01 message in the correct Commander Worker
Room with a visible Manager mention to Commander. Commander responded with an
HTTP 404 HTML page. The Team Room had no new message. No screenshot identifier
is transcribed or persisted.

This proves Manager-to-Commander routing. The failing boundary is
Commander-to-MCP, before Leader-to-Team delegation.

## Read-only checks

- All four committed production Worker YAML files use the same endpoint:
  scheme HTTP, host host.docker.internal, port 19090, path /mcp, transport HTTP.
- At diagnosis time the host had no TCP listener on port 19090.
- A host request to the configured /mcp path could not obtain an HTTP response.
- The exact Commander container was found without enumerating smoke resources.
- Inside that container, host.docker.internal resolved successfully and curl
  was available, but the configured MCP URL produced no completed HTTP probe.

No request body or S01 task was sent during diagnosis.

## Conclusion

The currently proven failure is MCP listener lifecycle: the local MCP process
is no longer running. Until the listener is restored, path and container
reachability cannot be independently cleared as secondary causes. The earlier
HTML 404 remains valid point-in-time UI evidence but is not treated as proof
that the current listener serves the wrong route.

## Minimum staged repair

1. Start the committed MCP server as a durable local service on port 19090,
   retaining the current endpoint and safety policy.
2. Verify the host /mcp protocol response and the same URL from the Commander
   container without sending an incident.
3. Only if the container still cannot reach the listener, change the MCP
   exposure to a Docker-reachable but narrowly scoped interface or private
   container network, then update all four Worker endpoints consistently.

Stage 1 changes local runtime state and needs operator authorization. Stage 3
changes committed Worker configuration and may recreate or roll all four
Workers; it requires separate explicit authorization. No S01 retry should occur
until the connectivity probes pass.
