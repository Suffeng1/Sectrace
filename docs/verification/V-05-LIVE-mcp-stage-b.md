# V-05-LIVE MCP stage B

Date: 2026-08-05

The MCP transport keeps DNS-rebinding protection enabled and remains bound only
to 127.0.0.1. Its Host allowlist contains the existing loopback authorities
plus the single Docker authority host.docker.internal:19090.

Read-only protocol verification after the runtime reload:

- Host MCP initialize: completed, HTTP 200, content type text/event-stream,
  JSON-RPC response present.
- Commander-container MCP initialize using the committed Worker URL: completed,
  curl exit code 0, HTTP 200, content type text/event-stream, JSON-RPC response
  present.

No response body, Matrix identifier, credential, or runtime secret was
recorded. No Worker YAML or Worker process changed, no S01 task was sent, and no
smoke resource was inspected.

Stage B passes. A new S01 submission is a separate externally visible action
and requires explicit operator authorization.
