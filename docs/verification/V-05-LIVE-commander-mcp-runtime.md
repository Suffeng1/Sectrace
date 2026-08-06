# V-05-LIVE Commander MCP runtime diagnosis

Date: 2026-08-05

## Observed contradiction

After the stage B MCP initialize probes passed from both host and Commander
container, the operator observed Commander again returning the same HTTP 404
Matrix HTML response to S01. No Team chain followed. Screenshot identifiers
are intentionally neither transcribed nor persisted.

## Runtime registration checks

- Controller status for the exact Commander Worker contains one MCP server:
  sectrace, HTTP transport, host.docker.internal port 19090, path /mcp.
- OpenClaw's native MCP registry is empty. This is expected for this CRD because
  the installed schema declares that Worker mcpServers are callable through
  mcporter, not OpenClaw's native MCP registry.
- Commander has mcporter installed.
- Commander mcporter lists exactly one server, sectrace, with status ok and five
  tools.
- The five registered names exactly match the production prompts:
  sectrace.intake.create_incident, sectrace.evidence.analyze_case,
  sectrace.response.create_plan, sectrace.audit.build_bundle, and
  sectrace.ledger.get_trace.

This rules out a stale endpoint, an ignored CRD field, and a missing MCP
registration or proxy.

## Bounded log metadata

The latest bounded OpenClaw log sample contained many 404 and HTML markers but
no mcporter, SecTrace tool-name, or /mcp marker. No log body was recorded.

The evidence therefore indicates that Commander's model turn did not execute
the registered mcporter tool path. It appears to have followed a Web or Matrix
HTTP path instead. This is an inference from the metadata counts, not a claim
about unseen response content.

## Minimum fix scope

The production Worker prompts currently say to call named tools but do not
explicitly require the installed mcporter invocation path. A durable fix should
add an explicit mcporter-only instruction and prohibit direct HTTP or browser
fetches for MCP tools. Because every role invokes a SecTrace tool, apply the
same narrow clarification to all four production prompts.

Changing Worker prompt content requires updating the four committed Worker
YAML files and reapplying those exact Workers. The reconciler may recreate or
roll their containers, so this requires explicit authorization. Team
membership, Team YAML, MCP endpoint, and MCP server do not need changes.

No configuration, process, room, or resource changed during this diagnosis,
and S01 was not sent again.
