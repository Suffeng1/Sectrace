# SecTrace

SecTrace is a safe, runnable Agent Infra competition demo: four role-separated Agents audit one fixed synthetic security incident through a deterministic, human-gated chain.

The repository includes Contract v1.0, Commander/Evidence/Response/Audit services, a tamper-evident ledger, five safe MCP tools, AgentTeams Worker/Team resource definitions, and a lightweight local replay UI. Production Worker YAML is committed but is not deployed by T-05.

All work uses synthetic or de-identified data. The demo never attacks, scans, or connects to real systems, and it does not perform security actions. High-risk conclusions are advice only and require human approval.

## Runtime safety

Runtime credentials are operator-provided local configuration and are never committed. Copy `hiclaw/.env.example` locally and fill values outside Git. The checked-in runtime inventory contains localhost service roles only; it is not a source of credentials or provider configuration.

Repository hygiene is enforced by `pytest tests/security/test_repository_hygiene.py -v`. Findings report only a repository-relative path and rule name.

## Local S01 replay

Run `python -m src.app.demo` for JSON output, or `python -m uvicorn src.app.main:app --host 127.0.0.1 --port 19080` for the local UI. Run `python -m src.app.mcp_server` for the five-tool Streamable HTTP MCP endpoint on port 19090. Full judge steps are in `outputs/demo/demo-script.md`.

The default high-risk replay remains `pending_approval` and records no real action. A local approved projection records only the human decision; the response plan still cannot become `executed`.
