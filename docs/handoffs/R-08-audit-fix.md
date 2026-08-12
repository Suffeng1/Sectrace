# R-08: 审计审批门修复 — 新增 ledger.log_approval 工具

## 背景

S01 审计返回 `audit_status: not_qualified`，根因是 MCP 服务器缺少审批记录工具。`ApprovalRecord` 在 `create_plan` 时被设为 `status=pending`，但没有工具能把它改成 `approved`，导致 `build_audit_review`（`src/agents/audit/service.py:66`）必然报 `approval.required`。

## Task 1：修改 `src/app/mcp_adapter.py`

### 1.1 在 `TOOL_NAMES` 元组末尾加一行

原代码：
```python
TOOL_NAMES = (
    "sectrace.intake.create_incident",
    "sectrace.evidence.analyze_case",
    "sectrace.response.create_plan",
    "sectrace.audit.build_bundle",
    "sectrace.ledger.get_trace",
)
```

改为：
```python
TOOL_NAMES = (
    "sectrace.intake.create_incident",
    "sectrace.evidence.analyze_case",
    "sectrace.response.create_plan",
    "sectrace.audit.build_bundle",
    "sectrace.ledger.get_trace",
    "sectrace.ledger.log_approval",
)
```

### 1.2 在 `call_tool` 方法中插入新分支

原代码（约第 56-58 行）：
```python
        if name == TOOL_NAMES[3]:
            return self._audit(trace_id)
        return self._envelope(trace_id, list(self.traces[trace_id]["ledger"].records))
```

改为：
```python
        if name == TOOL_NAMES[3]:
            return self._audit(trace_id)
        if name == TOOL_NAMES[5]:
            return self._log_approval(
                trace_id=trace_id,
                decision=arguments["decision"],
                approver=arguments.get("approver", "human_operator"),
                plan_ref=arguments["plan_ref"],
                reason=arguments.get("reason", ""),
            )
        return self._envelope(trace_id, list(self.traces[trace_id]["ledger"].records))
```

### 1.3 在 `_audit` 方法之后新增 `_log_approval` 方法

在 `def _audit(self, trace_id: str) -> dict:` 方法后面（`return self._envelope` 那行之后），加：

```python
    def _log_approval(
        self,
        *,
        trace_id: str,
        decision: str,
        approver: str,
        plan_ref: str,
        reason: str = "",
    ) -> dict:
        if trace_id not in self.traces:
            raise ValueError("unknown trace_id")
        state = self.traces[trace_id]
        if "approval" not in state:
            raise ValueError("no pending approval to log; create_plan first")
        if decision not in ("approved", "rejected"):
            raise ValueError("decision must be 'approved' or 'rejected'")

        from datetime import datetime, timezone

        state["approval"] = state["approval"].model_copy(
            update={
                "status": decision,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        ledger_record = state["ledger"].append(
            at=datetime.now(timezone.utc).isoformat(),
            actor=approver,
            event_type=f"approval.{decision}",
            payload_ref=f"approval:{plan_ref}",
        )
        return self._envelope(
            trace_id,
            {
                "approval": state["approval"].model_dump(mode="json"),
                "ledger_record": ledger_record,
            },
        )
```

### 1.4 在 `create_mcp_server` 函数中注册新工具

在 `return server` 之前，加：

```python
    @server.tool(name=TOOL_NAMES[5])
    def log_approval(
        trace_id: str,
        decision: str,
        plan_ref: str,
        approver: str = "human_operator",
        reason: str = "",
    ) -> dict:
        return adapter.call_tool(
            TOOL_NAMES[5],
            trace_id=trace_id,
            decision=decision,
            approver=approver,
            plan_ref=plan_ref,
            reason=reason,
        )
```

## Task 2：更新 Manager SOUL.md

在容器内 `/root/manager-workspace/SOUL.md` 的 `<!-- agentteams-builtin-end -->` 标记之后，追加以下内容：

```markdown

# SecTrace 审批处理

当收到人工管理员（admin）对某个 response plan 的批准或拒绝决定时，必须先调用 `sectrace.ledger.log_approval` 工具把决定写入账本，然后再转发给 commander。

## 批准流程

1. 收到 admin 的批准消息（包含 plan_ref，如 rp_tr_s01）
2. 调用工具：mcporter call --server sectrace --tool sectrace.ledger.log_approval trace_id=<trace_id> decision=approved plan_ref=<plan_ref> approver=human_operator
3. 检查退出码和 envelope：退出码 0 且 envelope 包含 approval.status=approved 和有效 ledger_record 则继续；退出码非 0 或 envelope 无效则向 admin 报告失败并停止
4. 转发给 sectrace-commander，指示推进 audit 阶段

## 拒绝流程

同上，但 decision=rejected，转发给 commander 指示停止处置。
```

## Task 3：同步 Manager SOUL.md 到 MinIO

```bash
mc alias list
mc cp /root/manager-workspace/SOUL.md agentteams/agentteams-storage/agents/manager/SOUL.md
```

## Task 4：重启 MCP 服务器

```bash
pkill -f "mcp_server.py" || true
cd /root/agentteams-fs/projects/project_005_SecTrace安全事件多Agent协同审计系统 && nohup python -m src.app.mcp_server > <local-runtime-temp> 2>&1 &
```

注意：MCP 服务器的实际工作目录和启动方式请根据现有进程确认。可以用 `ps aux | grep mcp_server` 查看当前启动方式。

## Task 5：重启 Manager 容器

```bash
docker restart agentteams-manager
```

## Task 6：验证

### 6.1 验证新工具已注册

```bash
docker exec agentteams-worker-sectrace-audit mcporter call --server sectrace --tool sectrace.ledger.get_trace trace_id=tr_s01
```

### 6.2 重新发送审批消息触发 Manager 调用 log_approval

通过 Matrix API 发送带 m.mentions 的批准消息（admin token 需重新获取）：

```bash
# 获取 token
TOKEN=$(curl -s -X POST "http://localhost:18080/_matrix/client/r0/login" \
  -H "Content-Type: application/json" \
  -d '{"type":"m.login.password","user":"admin","password":"<redacted-credential>"}' | python3 -c "import json,sys;print(json.load(sys.stdin)['access_token'])")

# 发送批准消息
TXN="approval-$(date +%s)"
curl -s -X PUT "http://localhost:18080/_matrix/client/r0/rooms/<matrix-room-or-event-id>/send/m.room.message/$TXN" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"msgtype":"m.text","body":"<matrix-user-id> 批准 rp_tr_s01","format":"org.matrix.custom.html","formatted_body":"<a href=\"https://matrix.to/#/<matrix-user-id>\">@manager</a> 批准 rp_tr_s01","m.mentions":{"user_ids":["<matrix-user-id>"]}}'
```

### 6.3 检查 audit 结果

```bash
docker exec agentteams-worker-sectrace-audit cat /root/agentteams-fs/shared/tasks/task-*/audit-commander-to-manager.json
```

确认：audit_status 不再是 not_qualified，missing_requirements 中不再有 approval.required。
