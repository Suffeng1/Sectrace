# SecTrace

SecTrace is a planned, safe demo for an Agent Infra competition: a multi-Agent collaboration workspace for auditing a fixed, synthetic security incident case.

This repository currently contains only the P-00 project bootstrap. It does not provide a working runtime, live integrations, or security operations. P-01 (the Contract v1.0 foundation) is next.

All work uses synthetic or de-identified data. The demo never attacks, scans, or connects to real systems, and it does not perform security actions. High-risk conclusions are advice only and require human approval.

## Runtime safety

Runtime credentials are operator-provided local configuration and are never committed. Copy `hiclaw/.env.example` locally and fill values outside Git. The checked-in runtime inventory contains localhost service roles only; it is not a source of credentials or provider configuration.

Repository hygiene is enforced by `pytest tests/security/test_repository_hygiene.py -v`. Findings report only a repository-relative path and rule name.
