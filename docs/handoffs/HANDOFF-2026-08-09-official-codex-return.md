# SecTrace 官方 Codex 回切交接文档

> 交接日期：2026-08-09  
> 交接方向：外接 API 开发阶段 → 官方 Codex 账号  
> 项目目录：`<repo-root>`  
> 当前结论：代码侧 R-08B 已完成，现场链路仍阻塞在 `manager_consumption`，不得直接进入 S-09 或最终 V-05。

## 1. 接手人先做什么

官方 Codex 新对话开始后，先只读以下文件和 Git 状态，不要立即修改或重发 S01：

1. `<workspace-root>/00_全局控制台.md`
2. 项目 `AGENTS.md`
3. 本文件
4. `README.md`
5. `CONTEXT.md`
6. `docs/status.md`
7. `docs/contracts/system-contract.md`
8. `docs/verification/R-08B-approval-gate-hardening.md`
9. `docs/verification/R-08G-admin-origin-s01-dispatch.md`
10. `docs/verification/V-08-live-audit.md`
11. `docs/verification/R-08C-s01-dispatch-diagnosis.md`
12. `docs/verification/R-08D-corrected-manager-mention-dispatch.md`
13. `docs/verification/R-08E-manager-self-event-diagnosis.md`
14. `docs/handoffs/H-R08.md`
15. 当前 `git status --short --branch`、`git diff --check`、`git diff --stat` 和 `git log`

接手后的第一份回复只应说明：已完成项、未通过项、当前运行态、下一步最小只读诊断和所需授权。未获得用户明确授权前，不得重启、修改配置、发送 S01、审批、提交或推送。

## 2. 项目目标与安全边界

SecTrace 是 GOAIHZ Agent Infra 赛道项目，使用四个业务角色完成合成安全事件的可追溯协同：

```text
Manager → Commander → Evidence → Response → pending_approval
                                             ↓ 用户本人审批/拒绝
                                           Audit
```

核心技术包括 HiClaw/AgentTeams、OpenClaw Worker、Matrix/Synapse、Higress、Python FastMCP、哈希链审计账本和声明式 Worker/Team 资源。

必须持续遵守：

- 只处理合成或脱敏数据；S01 是当前唯一现场演示案例。
- 不连接、扫描或攻击真实系统。
- 不执行账号禁用、权限修改、删除、隔离等真实处置。
- 高风险计划必须停在 `pending_approval`。
- 只有用户本人可以完成比赛所需的人工批准或拒绝；Codex 不能代替用户。
- 不读取、输出、复制或提交 `.env`、API Key、Token、密码、Matrix 标识、原始敏感日志或本地启动脚本。
- apply、delete、restart、模型切换、MCP 配置变更、发送 S01、审批、commit 和 push 都必须逐项获得用户明确授权。

## 3. 当前 Git 与文件状态

### 3.1 分支和提交基线

- 当前分支：`codex/sectrace-bootstrap`
- 当前 HEAD：`07b6147 fix(runtime): harden MCP worker integration`
- 本地分支与 `origin/codex/sectrace-bootstrap` 指向同一已提交基线。
- 外接 API 阶段的 R-06～R-08G 修改尚未提交或推送。

### 3.2 当前工作树

工作树是脏的，至少包含 14 个已跟踪文件修改以及多份未跟踪 Handoff/Verification 文件。主要已跟踪修改包括：

- `README.md`
- 四份 `hiclaw/sectrace-agents/sectrace-*.yaml`
- `outputs/demo/demo-script.md`
- `outputs/demo/evidence-index.md`
- `src/app/mcp_adapter.py`
- `src/app/mcp_server.py`
- `src/skills/intake/normalize.py`
- Commander、MCP adapter 和 production resource 相关测试

当前 `git diff --stat` 记录 14 个已跟踪文件、约 271 行新增和 24 行删除；`git diff --check` 于 2026-08-09 复核通过。

不要使用 `git reset --hard`、`git checkout --` 或整文件覆盖。所有现有改动均视为用户资产；先读 diff，再做手术式修改。

### 3.3 暂未建立的旧计划文件

旧回切手册曾建议建立以下文件，但当前仓库未见：

- `docs/handoffs/EXTERNAL_API_BOOTSTRAP.md`
- `docs/handoffs/RUNTIME_CHECKPOINT.md`
- 模型供应商切换 ADR

本文件承担本次官方账号回切主入口。是否再拆分上述文件，由官方 00 主控在当前阻塞解决后决定，不要立即增加文档数量。

## 4. 已完成工作

### 4.1 既有完成项

- P-00、P-01：项目初始化、Contract 和 TDD 基线完成。
- H-01：HiClaw/AgentTeams schema、Worker/Team 创建和可见性验证完成；清理缺陷作为非阻塞债务保留。
- T-01～T-04：Commander、Evidence、Response、Audit 四角色代码与单元验收完成。
- T-05：本地集成演示、UI/API、MCP adapter 和资源定义完成。
- V-01～V-04：角色级 QA 完成。
- R-06/V-06：mcporter 显式调用、ToolResult/直接 envelope 双路径解析和运行时提示词修复已完成并验收。
- R-07：DeepSeek 模型和 CR 覆盖问题已修复，曾到达真实 `pending_approval`。

### 4.2 R-08 初始修复

初始 R-08 新增第六个 MCP 工具：

```text
sectrace.ledger.log_approval
```

该工具能把 `ApprovalRecord` 更新为 approved/rejected 并写入账本；一次合成运行曾得到 `audit_status=qualified`，但独立 V-08 认为安全边界和现场证据不足，因此不能作为最终通过。

### 4.3 R-08B 安全加固

R-08B 已完成以下代码侧加固：

- `plan_ref` 必须匹配当前 trace 的 `response_plan.plan_id`。
- approver 和账本 actor 固定为 `human_operator`。
- reason 只以 SHA-256 引用写入账本，原始自由文本不进入报告。
- 审批只允许 `pending → approved/rejected`。
- 重复审批和 approved/rejected 相互覆盖会在变更前被拒绝。
- 失败调用不得改变 ApprovalRecord 或账本。
- approved 和 rejected 路径均有独立测试。
- 四个正式 Worker YAML 和测试统一为 `deepseek-chat`。
- MCP 源码监听恢复为 `127.0.0.1`。
- README、MCP 说明和 Demo 材料已更新为六工具。

记录的验证结果：

- R-08B 边界测试：7 passed。
- 聚焦审批、绑定和资源测试：20 passed。
- 完整 pytest：47 passed。
- `git diff --check`：passed。

这些是外接 API 阶段记录的最近一次测试结果；官方账号接手后应在可写临时目录可用时重新复跑，不能把历史记录冒充新的运行结果。

### 4.4 MCP 运行时最近已验证事实

2026-08-08 最近一次现场记录证明：

- MCP 运行进程已更新并监听 `127.0.0.1`。
- 主机 initialize 返回 HTTP 200。
- Commander 和 Audit 容器通过 `host.docker.internal` initialize 均返回 HTTP 200。
- Commander 与 Audit 的 live schema 均显示六个工具，包含 `sectrace.ledger.log_approval`。

## 5. 当前唯一技术阻塞：Manager 不消费有效 S01 事件

### 5.1 R-08G 已证明的事实

R-08G 是当前最可信的现场证据：

- 临时认证成功。
- Matrix whoami 确认发送者为允许的人类 admin/operator。
- 发送者不是 Manager，也不是任何 Worker。
- 目标是 admin 可访问的唯一 Manager-Commander 入口 DM。
- 发送者具有成员资格和发送权限。
- `m.mentions` 只有一个目标，且目标角色是 Manager consumer。
- 消息是固定的合成 S01，不含真实数据或凭据。
- 实际发送 1 次，无自动重试和辅助消息。
- Matrix 接受并返回 HTTP 200。
- 使用当次内存关联信息执行精确单事件查询，确认事件存在、发送者角色正确、mention 目标正确。
- Manager 在 10 分钟有界观察期内没有消费或路由。
- Commander、Evidence、Response 均未出现。
- 未形成 trace、`pending_approval` 或 plan_ref。

因此第一处已确认失败层是：

```text
manager_consumption
```

不要再回到“房间是否正确、sender 是否 admin、mention 是否 Manager、Matrix 是否接受”这些已经由 R-08G 证明的假设，也不要再无界分页查旧的 R-08D 事件。

### 5.2 当前不能声称的内容

- 不能声称四角色现场链已经完成。
- 不能声称 H-08 用户人工审批已经完成。
- 不能声称 V-08 已通过；现有 `V-08-live-audit.md` 结论仍是 FAIL。
- 不能进入 S-09 或最终 V-05。
- 不能更新 `docs/status.md` 为 PASS。
- 不能提交或推送当前工作树。

## 6. 运行态重要变化（2026-08-09）

2026-08-09 接手检查时，Docker Desktop Linux engine 的 Docker API 不可连接，系统报告对应 named pipe 不存在。因此：

- 当前不能确认 Controller、Manager、四个正式 Worker、Team 或 smoke Worker 正在运行。
- 不能把 2026-08-08 的容器运行状态当作 2026-08-09 当前事实。
- 当前也未确认 18001、18080、18088、18888、19090 端口监听状态。

下一次恢复运行时必须先请用户明确授权启动/恢复 Docker Desktop，然后只读核对容器、端口和资源状态。不要在 Docker 未恢复时修改代码来解释运行时无响应。

## 7. 官方 Codex 的下一步最小任务

当前下一 Ticket 建议命名为：

```text
R-08H：Manager consumption 只读诊断
```

### 7.1 前置步骤

1. 请求用户授权恢复 Docker Desktop；只恢复运行环境，不改配置。
2. 只读确认 Controller、Manager、四个正式 Worker 和 Team 状态。
3. 只读确认 Manager Matrix channel 在线、当前 model 为 `deepseek-chat`、`requireMention=true`。
4. 不发送新的 S01，不审批，不重启单个资源，先完成诊断。

### 7.2 诊断重点

以 R-08G 的精确事实为起点，检查 Manager 从 Matrix sync 到任务路由之间的消费链：

- Manager 是否订阅/同步该入口 DM，而不仅是房间映射存在。
- sync token/监听循环是否在 R-08G 前后推进。
- 是否存在 sender allowlist、admin/operator 过滤、bot/DM 过滤或事件类型过滤。
- 是否要求 `formatted_body`、特定 `msgtype`、命令前缀或额外 Matrix metadata。
- `m.mentions` 的处理是否与 OpenClaw 当前版本预期一致。
- 是否被 ignored-event、deduplication、已读游标或 session 去重门禁丢弃。
- Manager SOUL、openclaw 配置和实际 channel handler 是否存在职责错位。
- 对比此前“审批消息被 Manager 消费”的成功事件与 R-08G，比较结构化元数据类别，不输出正文或标识。
- 检查 Manager 日志时只返回有界、脱敏的错误类别和时间，不返回原始日志。

诊断必须先给出证据、反证、根因排序和下一步精确授权。没有单一根因时不得猜测性重启、改 `requireMention` 或再发 S01。

### 7.3 诊断输出建议

只写：

```text
docs/verification/R-08H-manager-consumption-diagnosis.md
```

结论限定为：

- `ROOT_CAUSE_CONFIRMED`
- `NEEDS_AUTHORIZATION`
- `INCOMPLETE`

## 8. 解决当前阻塞后的固定顺序

只有 R-08H 找到根因并经用户授权完成最小修复后，才按以下顺序推进：

1. 05 独立 QA 验收最小修复。
2. 用户明确授权唯一一次新的合成 S01。
3. 观察同一 trace 的 Commander → Evidence → Response → `pending_approval`。
4. 到审批门立即停止，由用户本人执行一次批准或拒绝。
5. 继续只读观察 ApprovalRecord、approval ledger 事件和 Audit 结果。
6. 05 重新执行 V-08；只有 PASS 后才进入 S-09。
7. S-09：安全扫描、MCP/Higress 治理证据和秘密卫生。
8. 05 重跑最终 V-05。
9. V-05 PASS 后再制作初赛 PPT、Demo 截图和讲稿。
10. 最后进行文档收口、Git 审查、用户授权 commit/push 和官号长期接管。

## 9. 剩余债务与风险

### 9.1 安全债务

- `docs/status.md` 仍记录 `R-00 = NON_BLOCKING_SECURITY_DEBT`。
- 旧的完整 Handoff 和部分操作文档曾包含敏感凭据或认证示例；不要在新文档中复述任何值。
- 在提交未跟踪 Handoff 前必须先做脱敏审查，并由操作员确认相关凭据是否需要轮换。
- S-09 尚未完成，不能用普通文本搜索冒充权威安全扫描放行。

### 9.2 文档漂移

- `docs/status.md` 没有列出 R-06～R-08G 的细粒度状态，V-05 仍为 `FAIL_LIVE_EVIDENCE`；在 V-08 重新通过前保持失败是正确的。
- `docs/handoffs/H-R08.md` 中“运行时尚未重启”等描述已被 R-08B Phase 2 的后续事实覆盖，需要在链路真正恢复后统一更新。
- `docs/verification/V-08-live-audit.md` 是 R-08B 前的独立 FAIL 结论，必须保留；后续以新文件或明确追加方式复验，不得改写历史。
- 历史文件可能仍写“五个工具”，当前事实是六个；只更新当前权威说明，不重写历史证据。

### 9.3 运行时债务

- H-01 smoke Worker/Team 的清理缺陷仍是非阻塞债务，不得在当前诊断中顺手处理。
- Docker Desktop 当前不可连接；恢复后先核对，不能默认所有容器仍健康。
- Manager consumption 根因尚未确认。

### 9.4 Git 债务

- 当前大量已跟踪和未跟踪变更尚未形成经 QA 通过的提交。
- 不自动 push。
- 只有相关 QA PASS、秘密卫生复核和用户明确授权后，00 主控才可组织提交。

## 10. 对话框职责

- `00 SecTrace 主控与运行时集成`：授权后的运行时恢复/变更、跨文档整合、状态和 Git。
- `06 SecTrace 诊断与最小修复`：默认只读诊断；用户逐项授权后做最小修复。
- `05 SecTrace 独立 QA`：只读代码/运行时，只写 `docs/verification/`，不得改业务实现。

同一时刻最多一个对话框拥有业务或运行时写权限。执行顺序仍为：

```text
06 诊断 → 用户授权 → 06/00 最小修复 → 05 QA → 00 现场集成
```

## 11. 官方 Codex 新对话首条提示词

```text
你接手 SecTrace 项目，当前从外接 API 开发阶段回切到官方 Codex。

正式项目目录：
<repo-root>

先只读：
- <workspace-root>/00_全局控制台.md
- 项目 AGENTS.md
- docs/handoffs/HANDOFF-2026-08-09-official-codex-return.md
- README.md、CONTEXT.md、docs/status.md
- docs/contracts/system-contract.md
- docs/verification/R-08B-approval-gate-hardening.md
- docs/verification/R-08G-admin-origin-s01-dispatch.md
- docs/verification/V-08-live-audit.md
- 当前 Git log、status、diff

当前已知：R-08B 代码安全加固已完成并记录 47 passed；MCP 最近验证为回环监听和六工具；R-08G 已证明有效 admin sender、正确 Manager mention 和 Matrix HTTP 200，但 Manager 未消费，第一失败层为 manager_consumption。V-08 仍 FAIL。2026-08-09 Docker Desktop Linux engine 当前不可连接，必须先请求用户授权恢复并只读核对运行态。

绝对禁止读取或输出 .env、API Key、Token、密码、Matrix 标识、启动脚本或原始敏感日志。

先输出：
1. 外接 API 阶段实际完成项；
2. 已通过和未通过的验证；
3. 当前 Git/运行态；
4. R-08H Manager consumption 的最小只读诊断计划；
5. 需要用户明确授权的动作。

未获得明确许可前，不得修改代码或配置，不得启动/重启资源，不得发送 S01，不得审批，不得 commit/push。
```

## 12. 接手成功标准

官方账号完成以下事项后，才算真正无缝接手：

- 能准确复述 R-08B 与 R-08G 的差异。
- 不把历史 `qualified` 结果误当作当前 V-08 PASS。
- 不重复已经排除的 sender/mention/Matrix acceptance 假设。
- 先恢复并核对 Docker，再诊断 Manager consumption。
- 不在无授权情况下重发 S01、审批或重启。
- 保留当前脏工作树，不破坏外接 API 阶段资产。
- 所有后续结论均写入项目 Handoff/Verification，而不是只留在聊天记录中。

---

本交接文档不包含任何密钥、Token、密码、Matrix 房间/用户/事件标识、原始消息或原始日志。
