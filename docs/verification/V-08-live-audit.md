# V-08 R-08 审批门独立验收

## 1. R-08 技术修复结论

FAIL

- R-08 聚焦回归可复现：`11 passed`。
- 进程内 FastMCP 工具表包含 6 个工具，`sectrace.ledger.log_approval` 已注册。
- 运行中 Audit Worker 的 `mcporter list` 返回退出码 `0`，但本次脱敏摘要未枚举出工具名，不能单独作为 live schema 证明；R-08 文档已有“第六工具可见”的历史声明。
- 审批状态仅允许从 pending 进入 approved/rejected，重复审批以及 approved/rejected 互相覆盖会被 pending 门禁阻止。
- 未发现 `plan_ref` 与当前 ResponsePlan 的身份校验；调用者提供的 `approver` 未被限制为 `human_operator`，并被写入 ledger actor；`reason` 未进入审批账本记录。现有测试未覆盖这些边界，因此技术修复未达到独立安全验收要求。

## 2. H-08 人工审批证据结论

INCOMPLETE

- R-08 脱敏材料声明发送过一次合成 S01 审批消息并返回 HTTP 200，且最终 audit_status 为 qualified。
- 现有材料没有证明用户本人确认并执行审批；R-07 明确未执行人工审批。
- `docs/handoffs/H-R08.md` 仍停留在 `pending_approval`，并要求人工复核四角色证据。

## 3. V-08 现场审计结论

FAIL

- R-07 只观察到 Commander 和 pending_approval，未观察到独立 Evidence、Response、Audit 阶段消息，因此不能证明 Commander → Evidence → Response → approval → Audit 的完整顺序。
- R-08 声明 audit_status 为 qualified 且 `approval.required` 已消失，但未提供可独立核对的同一 trace_id、ApprovalRecord approved 时间戳和对应 approval ledger 事件的完整脱敏链。
- 材料声明未执行真实响应或处置动作；本次验收也未发送 S01、未再次审批、未连接真实系统。
- 已有验证材料未向本报告泄露凭据、Token、API Key、房间标识或原始敏感日志内容。

## 4. 全量测试结论

FAIL

- 完整 pytest：`37 passed, 2 failed`。
- 失败 1：Worker YAML 使用 `deepseek-chat`，测试仍断言 `qwen3.6-plus`。
- 失败 2：MCP 监听地址为 `0.0.0.0`，安全测试要求 `127.0.0.1`。
- 未为通过测试修改实现或测试。

## 5. 阻塞最终 V-05 的最小问题清单

1. 由 00 补齐 `plan_ref` 绑定、固定 `human_operator` 身份和 `reason` 审计持久化，并增加对应安全验证。
2. 形成可独立核对的同一 trace_id 四角色链、ApprovalRecord approved 时间戳及 approval ledger 事件证据。
3. 获取用户本人确认并执行人工审批的证据；管理员认证发送消息本身只证明技术路径，不等同于比赛要求的真实人工审批。
4. 处理两个全量回归失败的契约漂移，并重新取得可审计的第六工具 live schema 证据。
5. 同步 H-R08 的旧 pending_approval 状态与最终 QA 结论。

## 6. 下一步

回到 00 修复与补证，不进入 S-09。

## 结论

FAIL
