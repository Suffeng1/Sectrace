"""Executable Streamable HTTP MCP server for the six safe SecTrace tools."""

from pathlib import Path

from src.app.approval_verifier import matrix_approval_verifier_from_environment
from src.app.mcp_adapter import create_mcp_server


REPO_ROOT = Path(__file__).resolve().parents[2]
BIND_HOST = "127.0.0.1"
DOCKER_MCP_AUTHORITY = "host.docker.internal:19090"
server = create_mcp_server(
    REPO_ROOT / "data" / "scenarios",
    state_dir=REPO_ROOT / "data" / "mcp-state",
    approval_verifier=matrix_approval_verifier_from_environment(),
)
server.settings.host = BIND_HOST
transport_security = server.settings.transport_security
assert transport_security is not None
transport_security.allowed_hosts.append(DOCKER_MCP_AUTHORITY)


if __name__ == "__main__":
    server.settings.port = 19090
    server.run(transport="streamable-http")
