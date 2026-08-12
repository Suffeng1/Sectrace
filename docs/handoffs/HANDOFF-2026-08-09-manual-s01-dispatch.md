# SecTrace：手动 S01 派发与现场验证交接

> 日期：2026-08-09  
> 交接目的：在新的官方 Codex 对话中继续 **一次受控的合成 S01 现场诊断**。  
> 正式项目目录：`<repo-root>`

## 1. 当前结论

项目代码、四个业务角色、MCP 服务和 HiClaw/AgentTeams 资源均已完成本地测试与多轮运行时修复；最终现场验收仍未通过。

当前允许的唯一下一步，是在用户已登录的 Element（Matrix）界面中，以人类 admin/operator 身份 **仅发送一次** 固定的合成 S01，验证 `Manager → Commander` 是否重新消费和路由。该动作是诊断门，不是最终演示通过，也不是批准任何处置。

当前没有待点击的批准或拒绝按钮；如果后续出现 `pending_approval`，必须立即停止，由用户本人决定批准或拒绝。

## 2. 新对话必须先只读的文件

1. `<workspace-root>/00_全局控制台.md`
2. `AGENTS.md`
3. `docs/handoffs/HANDOFF-2026-08-09-official-codex-return.md`
4. 本文件
5. `README.md`、`CONTEXT.md`、`docs/status.md`
6. `docs/contracts/system-contract.md`
7. `docs/verification/V-08-live-audit.md`
8. `docs/verification/R-08G-admin-origin-s01-dispatch.md`
9. `docs/verification/R-08AE-authoritative-startup-source-repair.md`
10. `docs/verification/R-08AJ-unresolved-plugin-reference-repair.md`
11. `docs/verification/R-08AK-sync-loop-init-diagnosis.md`
12. `docs/verification/R-08AL-sync-lifecycle-projection.md`
13. `docs/verification/R-08AN-controlled-s01-dispatch.md`
14. 当前 Git：`git status --short --branch`、`git diff --check`、`git diff --stat`、`git log --oneline -12`

不要通过阅读、输出、复制或提交 `.env`、Token、密码、API Key、Matrix 房间/用户/事件标识、原始日志或启动脚本来补足上下文。

## 3. 已完成的关键事实

### 3.1 代码与资源

- P-00/P-01、T-01～T-05 和 V-01～V-04 已完成。
- 四个角色为 Commander、Evidence、Response、Audit；其高风险处置只能停在 `pending_approval`。
- MCP 已有六个工具，包含安全的审批账本写入工具 `sectrace.ledger.log_approval`。
- R-08B 已实现审批安全加固：计划必须绑定当前 trace、审批者固定为 `human_operator`、审批状态只能单向转换、失败调用不改审批记录或账本。
- 历史记录的 R-08B 测试为 47 passed；后续新对话应重新验证，不得把历史结果表述为本次新运行结果。

### 3.2 运行态修复（已持久化）

- 去除了旧 Matrix 插件路径与重复插件加载。
- 修复了启动权威模板中的单个悬空插件引用。
- 重启后已确认：旧路径不复现、仅 bundled Matrix 插件生效、重复插件告警消失、全局配置有效、Matrix channel online。
- 官方 OpenClaw Channels UI 已由用户观察到：Matrix `运行中=是`、`已配置=是`、`已连接=是`。
- 当前版本的安全 CLI 与脱敏日志均未暴露正向 `sync-ready` 生命周期字段；这只能记为 **同步状态不可观测**，不能断言同步成功或失败。

### 3.3 独立 QA 对本次诊断的门控

05 独立 QA 仅放行“一次诊断性 S01 派发”，前提为：

- 配置有效；
- Matrix channel online；
- 官方 UI 显示运行中、已配置、已连接；
- 用户明确授权单次 S01；
- 仅合成数据、固定 trace、无重试。

这不等于 `V-08` 或 `V-05` PASS。两份最终验收仍应保持未通过，直到完整现场链路、人工审批与独立复验完成。

## 4. 当前人工操作的位置与正确房间

用户已在 Element：`http://localhost:18088` 登录 admin/operator。

左侧房间列表中应进入：

```text
Worker: sectrace-commander
```

不要进入下列房间发送：

- `Leader DM: sectrace-commander`
- `Team: sectrace-audit-team`
- `Manager: default`
- 任何 `sectrace-smoke` 资源

`Worker: sectrace-commander` 是此前已验证的 Manager→Commander ingress Room；成员应包括 admin、Manager 与 Commander。

## 5. 一次 S01 的精确人工步骤

新对话必须先让用户完成“准备态确认”，再允许最后一次点击：

1. 用户进入 `Worker: sectrace-commander`。
2. 在输入框键入 `@`，在 UI 弹出的候选列表中**点击选择 Manager**，使其成为结构化 mention；不能只手打纯文本 `@manager`。
3. 紧接该 mention 粘贴下列固定正文，不附加任何其他消息、文件或解释：

```text
执行已部署 SecTrace 的合成场景 S01；仅使用 synthetic 数据，保持 trace_id=tr_s01，按 commander→evidence→response→audit 完成 JSON 交接；处置必须停在 pending_approval，不执行任何真实动作；出现审批门时等待人工决定。
```

4. 发送前，用户向新对话确认：`已在 Worker: sectrace-commander 选择了 Manager mention，正文已粘贴，准备单击一次发送。`
5. 新对话只能回复允许进行最后一步：点击一次 Send/发送。
6. 用户点击一次后回复 `已发送`；之后不允许再次发送、补发或换房间重试。

## 6. 发送后，新对话的受限任务

新对话应通知 `00 SecTrace 主控与运行时集成`：用户已通过 UI 单次发送 S01；00 只能做**有界只读观察**，不得发送、修改、重启或审批。

观察结果只记录下列脱敏状态，不输出 Matrix 标识、原始消息或原始日志：

| 阶段 | 可记录的结论 |
|---|---|
| 接收 | 是否可确认 Manager 接受/消费 |
| 路由 | 是否可确认 Manager→Commander 路由 |
| Agent 链 | Commander、Evidence、Response、Audit 分别是否启动 |
| trace | 是否出现 `tr_s01` 的合成链路 |
| 审批门 | 是否出现 `pending_approval` |
| 首个失败层 | 若失败，最早可证实的失败层与证据类别 |

00 应写新的 `docs/verification/R-08AO-*.md` 和 `docs/handoffs/H-R08AO.md`（沿用现有命名惯例），随后交给 05 做独立判断。

## 7. 审批与后续路线

若且仅若出现 `pending_approval`：

1. Codex 停止执行；不点击批准/拒绝。
2. 让用户只报告按钮精确文字，或提供遮去身份标识的裁剪截图。
3. 用户自行选择一次批准或拒绝；Codex 只读观察 ApprovalRecord、审批账本和 Audit 输出。
4. 05 重做 V-08。仅 V-08 PASS 后，才可进入 S-09 安全扫描与最终 V-05。

若 S01 接受但没有消费或路由：停止，不重试；记录首个失败层，提出新的最小只读诊断请求。

## 8. 不可违反的安全与协作边界

- 仅合成/脱敏数据；不攻击、扫描、连接真实安全系统或执行真实处置。
- 高风险动作永远只能停在 `pending_approval`。
- 只有用户可以批准或拒绝；Codex 不得模拟审批。
- 不读取或展示秘密、标识、原始日志、启动脚本。
- 不触碰遗留 `sectrace-smoke` Worker/Team。
- 不执行 `git reset --hard`、`git checkout --`、删除/prune 或自动 push。
- 当前工作树包含未提交的外接 API 阶段资产；视为用户资产，先审查后做最小修改。
- 任何运行时写入、restart、S01、审批、commit、push 都需在当次操作前取得用户明确授权。

## 9. 给新官方 Codex 对话的首条提示词

```text
你接手 SecTrace 的现场 S01 受控验证。正式项目目录：
<repo-root>

先只读：
- <workspace-root>/00_全局控制台.md
- AGENTS.md
- docs/handoffs/HANDOFF-2026-08-09-official-codex-return.md
- docs/handoffs/HANDOFF-2026-08-09-manual-s01-dispatch.md
- README.md、CONTEXT.md、docs/status.md
- docs/contracts/system-contract.md
- docs/verification/V-08-live-audit.md
- docs/verification/R-08G-admin-origin-s01-dispatch.md
- docs/verification/R-08AE-authoritative-startup-source-repair.md
- docs/verification/R-08AJ-unresolved-plugin-reference-repair.md
- docs/verification/R-08AK-sync-loop-init-diagnosis.md
- docs/verification/R-08AL-sync-lifecycle-projection.md
- docs/verification/R-08AN-controlled-s01-dispatch.md
- git status、diff check、diff stat、最近 log

当前只允许推进一次“诊断性合成 S01”人工 UI 派发：用户将在 Element 的 `Worker: sectrace-commander` 房间，用 UI mention 选择 Manager，再粘贴固定 S01。你必须先等用户确认已选 mention 且仅准备发送；之后只允许用户点击一次发送。你和 00 只能做有界只读观察，禁止重发、重启、改配置、审批、commit 或 push。

不能读取、输出或复制 .env、密码、Token、API Key、Matrix 标识、原始日志或启动脚本；不得触碰 sectrace-smoke。

请先简要汇报：当前运行时修复事实、为什么这次只是诊断门、发送前需要用户确认的精确语句。不要自行发送 S01。
```

## 10. 当前状态一句话

**运行时的插件/配置根因已经修复，Matrix 已在线且已连接；现在卡在受支持自动化入口不可用，因此要由用户在正确的 Worker Room 以结构化 Manager mention 人工单发 S01，再由 Codex 只读验收链路。**
