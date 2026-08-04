# SecTrace S01 demo script

This script uses only the committed synthetic S01 scenario. It does not require HiClaw credentials and does not deploy Worker resources.

## 1. Verify

From the repository root, with the repository root on `PYTHONPATH`:

```powershell
python -m pytest -q -p no:cacheprovider tests
```

## 2. Replay the deterministic chain

```powershell
python -m src.app.demo
```

Check that the JSON shows:

- `trace_id` is `tr_s01` in every stage and ledger record;
- stages are Commander → Evidence → Response → Audit;
- the high-risk plan remains `pending_approval`;
- the default human approval record is `pending`;
- audit integrity is `passed`, while `approval.required` remains visible;
- the safety notice says no real action was executed.

## 3. Run the local UI

```powershell
python -m uvicorn src.app.main:app --host 127.0.0.1 --port 19080
```

Open `http://127.0.0.1:19080`, select “重放 S01”, and show the pending human gate and audit result.

## 4. Run the safe MCP endpoint

```powershell
python -m src.app.mcp_server
```

The Streamable HTTP endpoint is `http://127.0.0.1:19090/mcp`. It exposes exactly the five tools documented in `outputs/demo/evidence-index.md`. Unsupported or action-execution names are rejected.

## AgentTeams production-resource boundary

The four Worker files and `sectrace-audit-team.yaml` are committed reproduction assets only. T-05 does not apply or deploy them. The earlier H-01 smoke resources remain separate, and `H-01-RUNTIME-CLEANUP` is not handled by this demo.
