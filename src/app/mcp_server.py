"""Executable Streamable HTTP MCP server for the five safe SecTrace tools."""

from pathlib import Path

from src.app.mcp_adapter import create_mcp_server


REPO_ROOT = Path(__file__).resolve().parents[2]
server = create_mcp_server(REPO_ROOT / "data" / "scenarios")


if __name__ == "__main__":
    server.settings.host = "0.0.0.0"
    server.settings.port = 19090
    server.run(transport="streamable-http")
