# R-08AY Live Preflight and MCP Start

- Date: 2026-08-11
- Result: `MCP_TRANSPORT_READY_MANUAL_BROWSER_REQUIRED`
- Runtime mutation: one explicitly authorized MCP start call

## Preflight

The first sandboxed `live` preflight reported `BLOCKED_DOCKER_ENGINE` because the restricted process could not access the Docker named pipe. A read-only Docker query outside the sandbox confirmed Docker client and server version `29.4.0`. The same read-only preflight with Docker API access then passed Docker, Controller, Manager, core TCP endpoints, all four formal Workers, and the active Team, and stopped at `BLOCKED_MCP_SERVICE_NOT_RUNNING`.

## Authorized MCP start

After the user explicitly authorized `启动`, the launcher first asserted that no listener existed on port 19090 and issued exactly one hidden `python -m src.app.mcp_server` start from the formal project directory. The launcher process returned exit code 1 without observable JSON, so it was not retried. Post-start evidence established the actual outcome:

- Host MCP listener: pass
- Host TCP: pass
- Host MCP initialize: HTTP 2xx
- Commander container: running
- Commander DNS: pass
- Commander MCP TCP: pass
- Commander MCP initialize: HTTP 2xx
- Element page: reachable

The final preflight status was `MANUAL_REQUIRED`, not a transport failure.

## Browser gate

The existing browser harness reported Edge/Chrome running, daemon unavailable, and zero active browser connections. Current-session confirmation is still required for the logged-in Element account, correct Commander room, Matrix channel state, and Edge remote-debugging permission.

## Boundary

No retry, restart, configuration change, Matrix message, S01 dispatch, approval, smoke action, commit, or push occurred. This record proves current MCP transport readiness only; it does not prove an MCP process-restart persistence cycle or the four-role live chain.
