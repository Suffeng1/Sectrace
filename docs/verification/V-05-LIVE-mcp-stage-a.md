# V-05-LIVE MCP stage A

Date: 2026-08-05

## Authorized change

The committed MCP module was started through an exact Windows scheduled task
named SecTrace-MCP-V05 so that it survives the diagnostic command's process
job. The application remains bound only to 127.0.0.1 on port 19090. No Worker
resource or YAML was changed or restarted.

## Protocol probes

- Host initialize probe: HTTP 200, content type text/event-stream, JSON-RPC
  response present.
- Commander container DNS resolution for host.docker.internal: successful.
- Commander initialize probe to the committed URL: HTTP 421, no JSON-RPC
  response.
- Control probe over the same connection with only the HTTP Host header changed
  to the loopback authority: HTTP 200, content type text/event-stream, JSON-RPC
  response present.

All probes carried only MCP initialize metadata and no incident or credential
data.

## Conclusion

The durable listener, Docker host resolution, TCP reachability, /mcp path, and
MCP transport are working. The remaining incompatibility is HTTP authority
validation: the MCP server accepts the loopback Host authority but rejects
host.docker.internal with HTTP 421.

Stage B does not require a Worker endpoint change or Worker restart. The
minimum change is to preserve loopback binding and DNS-rebinding protection
while adding only host.docker.internal:19090 to the MCP transport's allowed
Host authorities, then restart only SecTrace-MCP-V05 and repeat both protocol
probes. This code/runtime change requires separate authorization.

No S01 was sent, no smoke resource was inspected or changed, and no credential
was read.
