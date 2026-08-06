from src.app.mcp_server import BIND_HOST, DOCKER_MCP_AUTHORITY, server


def test_mcp_server_binds_only_to_loopback() -> None:
    assert BIND_HOST == "127.0.0.1"
    assert server.settings.host == BIND_HOST


def test_mcp_transport_allows_only_expected_local_authorities() -> None:
    transport_security = server.settings.transport_security

    assert transport_security is not None
    assert transport_security.enable_dns_rebinding_protection is True
    assert DOCKER_MCP_AUTHORITY == "host.docker.internal:19090"
    assert transport_security.allowed_hosts == [
        "127.0.0.1:*",
        "localhost:*",
        "[::1]:*",
        DOCKER_MCP_AUTHORITY,
    ]
