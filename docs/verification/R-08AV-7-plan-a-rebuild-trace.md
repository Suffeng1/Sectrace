# R-08AV-7 Plan A Rebuild Trace & Plan B Handoff

日期：2026-08-10

结论：`PLAN_A_EXECUTED_REBUILD_IN_PROGRESS`

## 背景

R-08AV-6 修复 Manager 崩溃循环后，S01 链路恢复推进，但 response worker 报 `stage_failed — unknown_trace_id`。根因：MCP 服务器为 11:22 启动的内存态新进程（`mcp_adapter.py:35 self.traces: dict`，无持久化），8/9 创建的 `tr_s01` 不在内存；Commander 基于 8/9 旧交接文件认为 incident 已建，未重新 `create_incident`。

## 方案选择（用户授权）

- **方案 A（立即执行）**：向 Commander 发送重建 trace 指令，重新 create_incident + 完整驱动 evidence→response→audit。
- **方案 B（留待 Codex）**：为 MCP 增加状态持久化，根治"进程重启丢失 trace"问题。

## 方案 A 执行记录（浏览器自动化，用户逐步授权）

1. 进入 `Worker: sectrace-commander` 房间（先前误在 Team: sectrace-audit-team，已切换）。
2. 构造结构化 mention：输入 `@` → 过滤输入 `sec` → 选中 `<matrix-user-id>`（`mx_UserPill` 确认）→ Enter。
3. 固定指令正文（12:10 发送，输入框清空、消息上屏确认）：
   > 由于 MCP 服务器今日重启，内存中的 trace 状态已丢失（response 阶段报 unknown trace_id）。请重新执行 sectrace.intake.create_incident 重建 trace_id=tr_s01（scenario=S01，仅 synthetic 数据），然后按 commander→evidence→response→audit 完整推进 JSON 交接；处置必须停在 pending_approval，不执行任何真实动作；出现审批门时等待人工决定。
4. 发送后观察（12:11）：
   - Commander 日志：`Incident created successfully (exit 0, valid envelope, trace_id=tr_s01). Now delegating the evidence-collection stage to the evidence worker.`
   - Evidence worker 日志：`I'll execute the evidence collection phase for trace_id=tr_s01.`

## 当前链路状态

| 阶段 | 状态 |
|---|---|
| Commander（重建 trace + 派发） | ✅ 完成（tr_s01 已重建于 MCP 内存） |
| Evidence（证据收集） | 🔄 执行中 |
| Response（处置规划） | ⏳ 待 evidence |
| Audit（审计复核） | ⏳ 待 response |
| 审批门 | ⏳ pending_approval 时停，由用户决定 |

## 方案 B：MCP 状态持久化（交接给 Codex 执行）

### 问题

`src/app/mcp_adapter.py:35` `self.traces: dict[str, dict] = {}` 为纯内存态。MCP 进程重启（如 11:22 手动启动、机器重启、进程崩溃）后，所有 trace 状态（IncidentCase/Evidence/Response/Audit/ApprovalRecord/Ledger）全部丢失，且无任何恢复机制。本次 `unknown_trace_id` 即因此发生。

### 建议修改（Codex 实施）

1. **持久化层**：在 `SafeMCPAdapter` 增加状态落盘：
   - 每次状态变更后（`_create_incident`/`_analyze_case`/`_create_plan`/`_log_approval`/`_audit`）写一份 `state.json`（或按 trace_id 分文件 `traces/<trace_id>.json`）到项目数据目录（如 `data/mcp-state/`）。
   - 启动时加载已有状态文件到 `self.traces`。
2. **文件格式**：使用 `model_dump(mode="json")` 序列化 trace 内各模型（IncidentCase、EvidenceItem、ResponsePlan、ApprovalRecord、LedgerRecord），保持 schema_version 兼容。
3. **原子写**：写临时文件 + `os.replace`，避免崩溃写坏状态。
4. **注意**：`data/scenarios/` 目录已有 S01 场景数据；建议状态目录独立为 `data/mcp-state/` 并加入 `.gitignore`（运行时数据，不应提交）。
5. **测试**：重启 MCP 进程后 `get_trace tr_s01` 仍返回完整状态；重跑 S01 验证链路不因重启中断。

### 验收标准

- MCP 重启后，`sectrace.ledger.get_trace trace_id=<已建trace>` 返回完整 ledger，而非 `unknown trace_id`。
- S01 全链路（含审批）在 MCP 重启前后均可推进。

## 停止条件

未重复发送 S01、未审批、未触碰 `sectrace-smoke`、未 commit/push。方案 B 仅记录于本文档，未对代码做任何修改（WorkBuddy 保持只读，代码改动由 Codex 执行）。
