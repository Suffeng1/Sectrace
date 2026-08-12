# SecTrace 项目完整交接文档

> 日期：2026-08-08 17:00  
> 编写者：WorkBuddy（只读诊断角色）  
> 接收者：Codex 新对话（将接替 WorkBuddy 的诊断 + Codex 的执行双重角色）

---

## 一、项目概览

### 1.1 基本信息

- **项目名称**：SecTrace — 安全事件多 Agent 协同审计系统
- **赛事**：GOAIHZ 大赛，赛道 Agent Infra（新智基座）
- **截止日期**：初赛 8/16（方案PPT），复赛 9/3（代码+Demo），决赛 9/22
- **项目目录**：`<repo-root>`
- **HiClaw 仓库位置**：`<local-agentteams-root>`（agentscope-ai/AgentTeams）
- **Obsidian 文档**：`<local-notes-dir>`

### 1.2 架构

4 个 Agent 角色链路：

```
Commander（事件指挥官） → Evidence（证据分析） → Response（处置规划） → Audit（审计复核）
                                                    ↓
                                            pending_approval（人工审批门）
                                                    ↓
                                              Audit（审计收尾）
```

通过共享文件系统 `/root/agentteams-fs/shared/tasks/` 传递 JSON handoff 文件，通过 Matrix 协议进行 Agent 间消息通信，通过 MCP 工具调用确定性服务。

### 1.3 技术栈

- **运行时**：HiClaw/AgentTeams（Docker 容器化），OpenClaw agent runtime
- **消息层**：Matrix/Synapse（嵌入 Controller 容器），通过 Higress 网关 18080 端口暴露
- **LLM**：DeepSeek（deepseek-chat）via Higress 代理 → api.deepseek.com
- **MCP 服务器**：Python FastMCP，端口 19090，5 个工具（即将新增第 6 个）
- **存储**：MinIO（Worker SOUL.md 持久化）
- **编排**：声明式 YAML（Worker + Team CR），嵌入式 k8s API

---

## 二、基础设施状态

### 2.1 Docker 容器（全部运行中）

| 容器名 | 端口映射 | 用途 |
|--------|----------|------|
| agentteams-controller | 18001, 18080, 18088 | 控制器 + Synapse + Higress 网关 + Element Web |
| agentteams-manager | 127.0.0.1:18888 | Manager agent（审批门、消息路由） |
| agentteams-worker-sectrace-commander | 13401 | 事件指挥官 |
| agentteams-worker-sectrace-evidence | 17803 | 证据分析 |
| agentteams-worker-sectrace-response | 10093 | 处置规划 |
| agentteams-worker-sectrace-audit | 13048 | 审计复核 |
| agentteams-worker-sectrace-smoke | 17709 | 冒烟测试（可忽略） |

### 2.2 访问地址

| 服务 | URL | 凭据 |
|------|-----|------|
| Higress 网关（Matrix API） | http://localhost:18080 | admin / <redacted-credential> |
| 控制台 | http://localhost:18001 | - |
| Element Web | http://localhost:18088 | admin / <redacted-credential> |
| Manager API | http://localhost:18888 | - |
| MCP 服务器 | http://localhost:19090 | Bearer token: `<redacted-credential>` |

### 2.3 关键配置文件

| 文件 | 位置 | 说明 |
|------|------|------|
| agentteams-manager.env | `<local-config-dir>/agentteams-manager.env` | Manager 环境变量 |
| start_hiclaw.py | `<local-agentteams-root>/start_hiclaw.py` | 自写启动脚本 |
| Worker YAMLs | `hiclaw/sectrace-agents/sectrace-{commander,evidence,response,audit}.yaml` | 4 个 Worker 声明 |
| Team YAML | `hiclaw/sectrace-agents/sectrace-audit-team.yaml` | Team 声明 |
| MCP 服务器源码 | `src/app/mcp_server.py` | 入口，BIND_HOST=0.0.0.0，端口 19090 |
| MCP 适配器 | `src/app/mcp_adapter.py` | 5 个工具定义（需新增第 6 个） |
| 领域契约 | `src/app/contracts.py` | IncidentCase, EvidenceItem, ResponsePlan, ApprovalRecord, AuditBundle |
| 审计服务 | `src/agents/audit/service.py` | build_audit_review，第 66 行检查 approval.status |
| 场景数据 | `data/scenarios/S01.json` | S01 演练场景 |

### 2.4 LLM 配置（已修复，当前正确）

```ini
# agentteams-manager.env
AGENTTEAMS_LLM_PROVIDER=deepseekv4flash
AGENTTEAMS_DEFAULT_MODEL=deepseek-chat
AGENTTEAMS_LLM_API_KEY=          # 留空！见下方说明
AGENTTEAMS_OPENAI_BASE_URL=https://api.deepseek.com/v1
```

**关键经验**：
- `AGENTTEAMS_LLM_API_KEY` 留空 → `setup-higress.sh` 跳过 AI Gateway 自动配置 → 保留用户手动在 Higress 中配的 `deepseekv4flash` provider
- OpenClaw 运行时用 `MANAGER_GATEWAY_KEY` 认证 Higress，不用 `AGENTTEAMS_LLM_API_KEY`
- `ManagerAgentEnv()` (config.go:811) 不传 `AGENTTEAMS_OPENAI_BASE_URL` 给 Manager 容器（控制器源码 bug，通过留空 LLM_API_KEY 绕过）
- CR `spec.model` 会覆盖容器 env 中的 `AGENTTEAMS_DEFAULT_MODEL`（worker_env.go:65-67），所以必须同时 patch CR + 改 YAML

### 2.5 嵌入式 k8s API

Controller 容器内运行 k8s API：
- API 地址：`https://127.0.0.1:6443`
- Token：`21db11272922c9efd8628aa795627a09fa9b83c40a25fcdbff0cb2133b519ac5`（在 `/data/agentteams-controller/pki/token.csv`）
- 可查询/patch Manager CR 和 Worker CR

### 2.6 Matrix 通信

- **Manager DM 房间**：`<matrix-room-or-event-id>`（admin 与 manager 的直接消息）
- **Commander 房间**：`<matrix-room-or-event-id>`
- **admin 用户 ID**：`<matrix-user-id>`
- **manager 用户 ID**：`<matrix-user-id>`
- **admin token 获取**：
  ```bash
  curl -s -X POST "http://localhost:18080/_matrix/client/r0/login" \
    -H "Content-Type: application/json" \
    -d '{"type":"m.login.password","user":"admin","password":"<redacted-credential>"}'
  ```

**关键经验**：Manager 的 `openclaw.json` 配置 `requireMention: true`，只处理带 `m.mentions` 元数据的消息。Element Web 在 DM 房间不弹成员列表，必须用 Matrix API 发送：

```bash
TXN="msg-$(date +%s)"
curl -s -X PUT "http://localhost:18080/_matrix/client/r0/rooms/<matrix-room-or-event-id>/send/m.room.message/$TXN" \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "msgtype": "m.text",
    "body": "<matrix-user-id> <消息内容>",
    "format": "org.matrix.custom.html",
    "formatted_body": "<a href=\"https://matrix.to/#/<matrix-user-id>\">@manager</a> <消息内容>",
    "m.mentions": {"user_ids": ["<matrix-user-id>"]}
  }'
```

---

## 三、已完成的工作

### 3.1 交付状态总览

| 编号 | 状态 | 说明 |
|------|------|------|
| P-00 | DONE | 项目初始化 |
| P-01 | DONE | TDD 规范 |
| R-00 | NON_BLOCKING_SECURITY_DEBT | 安全债务 |
| H-01 | DONE | HiClaw 运行时清理 |
| T-01~T-04 | DONE | 四角色开发 |
| T-05 | DONE | 集成演示 |
| V-01~V-04 | DONE | 单元验收 |
| V-05 | FAIL_LIVE_EVIDENCE | 实时证据失败（已通过后续修复解决） |
| R-06 | PASS | 双路径 stdout 解析 + mcporter rollout |
| V-06 | PASS | QA 验收 |
| R-07 | PASS | S01 链路打通（LLM 切换 + CR model 修复） |
| R-08 | **PENDING** | 审计审批门修复（当前阻塞项） |

### 3.2 R-07 完成的关键修复

1. **LLM 从 GLM-4.7/matrix.mzsjai.com（已失效 404）切换到 DeepSeek（deepseek-chat）**
   - 修改 `agentteams-manager.env`：`AGENTTEAMS_LLM_API_KEY=` 留空
   - 手动在 Higress 中配置 `deepseekv4flash` provider → `api.deepseek.com`
2. **Patch Manager CR `spec.model`**：`GLM-4.7` → `deepseek-chat`
3. **修改 4 个 Worker YAML**：`model: qwen3.6-plus` → `model: deepseek-chat`
4. **重建全部容器**：Controller + Manager + 5 Workers
5. **更新全部 SOUL.md 并同步 MinIO**

### 3.3 S01 链路验证结果

- Commander → Evidence → Response：全部正常，通过 mcporter 调用 MCP 工具
- Response plan `rp_tr_s01` 状态到达 `pending_approval`
- 通过 Matrix API 发送带 `m.mentions` 的批准消息，Manager 收到并转发给 Commander
- Commander 创建 audit handoff，启动 Audit worker
- **Audit 结果：`not_qualified`**（当前阻塞项）

---

## 四、当前阻塞项：R-08 审计审批门修复

### 4.1 问题根因

S01 审计返回 `audit_status: not_qualified`，核心错误：`approval.required`。

**根本原因**：MCP 服务器 `src/app/mcp_adapter.py` 只注册了 5 个工具，缺少 `sectrace.ledger.log_approval`。

```
TOOL_NAMES = (
    "sectrace.intake.create_incident",    # [0] 创建事件
    "sectrace.evidence.analyze_case",     # [1] 证据分析
    "sectrace.response.create_plan",      # [2] 创建处置计划（ApprovalRecord.status=pending）
    "sectrace.audit.build_bundle",        # [3] 构建审计包
    "sectrace.ledger.get_trace",          # [4] 查询账本
    # 缺少：sectrace.ledger.log_approval   # [5] 记录审批决定
)
```

`create_plan`（TOOL_NAMES[2]）创建 `ApprovalRecord(status="pending")`，但没有任何工具能把状态改成 `approved`。

`src/agents/audit/service.py:66` 严格检查：
```python
if approval is None or approval.status != "approved":
    _add_once(missing, "approval.required")
```

所以 audit 必然报 `approval.required`。

**流程缺陷**：Manager 收到 admin "批准" 后，只转发给 commander，没有调用 ledger 工具落账。Commander 也没有调用 ledger 工具更新审批状态。

### 4.2 修复方案（已写入 R-08-audit-fix.md）

完整指令在 `docs/handoffs/R-08-audit-fix.md`，共 6 个 Task：

1. **修改 `src/app/mcp_adapter.py`**：新增 `sectrace.ledger.log_approval` 工具
   - `TOOL_NAMES` 加第 6 项
   - `call_tool` 加新分支
   - 新增 `_log_approval` 方法：更新 approval.status，追加 ledger 记录
   - `create_mcp_server` 注册新 `@server.tool`
2. **更新 Manager SOUL.md**：收到 admin 批准后先调用 `log_approval` 落账，再转发 commander
3. **同步 MinIO**：`mc cp /root/manager-workspace/SOUL.md agentteams/agentteams-storage/agents/manager/SOUL.md`
4. **重启 MCP 服务器**
5. **重启 Manager 容器**
6. **验证**：重新发送审批消息，检查 audit_status 变为 `qualified`

### 4.3 当前 MCP 适配器代码（`src/app/mcp_adapter.py`）

完整源码已读取，关键结构：

- `SafeMCPAdapter` 类：内存态 trace 管理
- `call_tool` 方法：分发到 `_create_incident` / `_analyze` / `_plan` / `_audit` / `_envelope`(get_trace)
- `_plan` 方法（第 97-115 行）：创建 `ApprovalRecord(status="pending", timestamp=None)`
- `_audit` 方法（第 117-135 行）：调用 `build_audit_review`，传入 approval 和 ledger records
- `create_mcp_server` 函数：注册 5 个 `@server.tool`

### 4.4 当前领域契约（`src/app/contracts.py`）

```python
class ApprovalRecord(BaseModel):
    trace_id: str
    approver_role: Literal["human_operator"]
    status: Literal["not_requested", "pending", "approved", "rejected"]
    timestamp: datetime | None
```

`ApprovalRecord` 已支持 `approved` 状态和 `timestamp` 字段，无需修改 contracts.py。

### 4.5 Audit 判定逻辑（`src/agents/audit/service.py`）

第 66 行：
```python
if approval is None or approval.status != "approved":
    _add_once(missing, "approval.required")
```

只要 approval.status == "approved" 且 timestamp 不为 None，审计就会通过。

---

## 五、待完成任务清单

### 即时（R-08 修复）

1. 执行 `docs/handoffs/R-08-audit-fix.md` 的 6 个 Task
2. 重新触发 S01，验证 audit 返回 `qualified`
3. 截图确认 `audit_status` 和 `missing_requirements`

### 后续

4. **V-08 最终审计验收**：确认 S01 全链路 qualified 后，更新 `docs/verification/` 下的验收文档
5. **S-09 安全扫描**：对项目代码做安全扫描
6. **初赛 PPT 制作**（8/16 截止）：方案 PPT，需包含架构图、流程图、Demo 截图
7. **官号接手准备**：确保所有文档可追溯，handoff 文档链完整

---

## 六、关键源码文件索引

| 文件 | 行数 | 用途 |
|------|------|------|
| `src/app/mcp_server.py` | ~15 行 | MCP 服务器入口，BIND_HOST=0.0.0.0，端口 19090 |
| `src/app/mcp_adapter.py` | 164 行 | SafeMCPAdapter + create_mcp_server，5 个工具 |
| `src/app/contracts.py` | 64 行 | 领域模型：IncidentCase, EvidenceItem, ResponsePlan, ApprovalRecord, AuditBundle |
| `src/app/ledger.py` | - | AuditLedger，append-only 账本 |
| `src/app/main.py` | - | FastAPI 入口（如有 REST API 需要） |
| `src/agents/commander/service.py` | - | build_incident |
| `src/agents/evidence/service.py` | - | analyze_case |
| `src/agents/response/service.py` | - | create_response_plan |
| `src/agents/audit/service.py` | - | build_audit_review（第 66 行审批检查） |
| `data/scenarios/S01.json` | - | S01 演练场景数据 |
| `hiclaw/sectrace-agents/sectrace-*.yaml` | - | 4 个 Worker + 1 个 Team 声明 |
| `hiclaw/sectrace-agents/prompts/sectrace-*.md` | - | 4 个角色的 prompt 模板 |

---

## 七、SOUL.md 状态

### 7.1 Worker SOUL.md

4 个 Worker 的 SOUL.md 已由 Codex 更新并同步到 MinIO，容器重启后会从 MinIO 同步。

容器内路径：`/root/agentteams-fs/agents/<name>/SOUL.md`  
MinIO 路径：`agentteams/agentteams-storage/agents/<name>/SOUL.md`

每个 SOUL.md 包含完整的 SecTrace 角色指令：
- 角色定位和职责
- mcporter 工具调用规范
- handoff 文件格式和路径
- 安全约束（合成演练、无真实处置）

### 7.2 Manager SOUL.md

容器内路径：`/root/manager-workspace/SOUL.md`

当前状态：**缺少审批处理逻辑**。需要追加：收到 admin 批准/拒绝后，先调用 `sectrace.ledger.log_approval` 落账，再转发给 commander。

---

## 八、协作协议（必须遵守）

### 8.1 WorkBuddy 与 Codex 的分工

- **WorkBuddy（原角色）**：只读诊断 — 读文件、查容器日志、分析源码、整理 handoff 文档
- **Codex（原角色）**：执行修改 — 改代码、改 YAML、操作 Docker、重启服务、同步 MinIO

**如果新 Codex 对话同时承担两个角色**，则可以直接读写和执行，但建议保持文档化（每次修改都更新 handoff）。

### 8.2 用户偏好

- 用户通过截图反馈状态，需要明确告诉用户"在 00 对话框执行什么"
- 复杂指令写成 handoff 文件（放在 `docs/handoffs/`），用户直接复制
- 不要在聊天框里发多段代码（会复制错位）
- Codex 使用 UUAPI（uuapi.net）作为外接 API，与 AgentTeams 的 LLM API 是两套独立配置
- 报错日志要记录到项目文件中，后续换官号时需要知道运行到哪了

### 8.3 常用诊断命令

```bash
# 查看容器状态
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# 查看 Manager 日志
docker logs --tail=50 agentteams-manager 2>&1

# 查看 Worker 日志
docker logs --tail=50 agentteams-worker-sectrace-commander 2>&1

# 读取 Worker SOUL.md
docker exec agentteams-worker-sectrace-commander cat /root/agentteams-fs/agents/sectrace-commander/SOUL.md

# 读取 Manager SOUL.md
docker exec agentteams-manager cat /root/manager-workspace/SOUL.md

# 读取 Manager openclaw.json
docker exec agentteams-manager cat /root/manager-workspace/openclaw.json | python3 -m json.tool

# 查看任务目录
docker exec agentteams-worker-sectrace-audit ls -la /root/agentteams-fs/shared/tasks/task-20260808-042800/

# 查看 audit 结果
docker exec agentteams-worker-sectrace-audit cat /root/agentteams-fs/shared/tasks/task-20260808-042800/audit-commander-to-manager.json

# 查询 Manager CR
docker exec agentteams-controller sh -c 'curl -s -k --header "Authorization: Bearer <redacted-credential>" https://127.0.0.1:6443/apis/agentteams.io/v1beta1/namespaces/default/managers/default'

# 查询 Worker CR
docker exec agentteams-controller sh -c 'curl -s -k --header "Authorization: Bearer <redacted-credential>" https://127.0.0.1:6443/apis/agentteams.io/v1beta1/namespaces/default/workers/sectrace-commander'

# 检查 MCP 服务器
curl -s -o /dev/null -w '%{http_code}' http://localhost:19090/mcp -X POST -H 'Content-Type: application/json' -d '{"jsonrpc":"2.0","method":"initialize","id":1}'

# 检查 LLM 连通性
docker exec agentteams-manager curl -s -X POST http://agentteams-controller:8080/v1/chat/completions -H "Content-Type: application/json" -H "Authorization: Bearer <redacted-credential>" -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"hello"}],"max_tokens":10}'
```

---

## 九、已知问题和坑

### 9.1 Docker Desktop 稳定性

Docker Desktop 的 Linux 引擎在重建大量容器时可能崩溃（HTTP 500）。恢复方法：
1. Quit Docker Desktop
2. `wsl --shutdown`
3. 重启 Docker Desktop
4. 重新运行 `start_hiclaw.py`

### 9.2 CR spec.model 覆盖机制

`agentteams-controller/internal/service/worker_env.go:65-67`：
```go
if spec.Model != "" {
    env["AGENTTEAMS_DEFAULT_MODEL"] = spec.Model
}
```

CR 的 `spec.model` 字段会覆盖 Controller env 中的 `AGENTTEAMS_DEFAULT_MODEL`。改 env 不够，必须同时 patch CR。

### 9.3 AGENTTEAMS_LLM_API_KEY 的双重作用

- 非空 → `setup-higress.sh` 用它配置 AI Gateway（会覆盖用户手动配置）
- 留空 → `setup-higress.sh` 跳过 AI Gateway 配置（保留用户手动配置）

正确做法：留空，手动在 Higress 中配置 provider。

### 9.4 Matrix mention 机制

Manager 的 `openclaw.json` 配置 `requireMention: true`：
- 纯文本 `@manager` 不触发处理
- 必须有 `m.mentions` 元数据
- Element Web 在 DM 房间不弹成员列表
- 解决方案：用 Matrix API 发送带 `m.mentions` 的消息

### 9.5 MCP 服务器进程

MCP 服务器是后台 Python 进程，不是 Docker 容器。重启容器不会重启 MCP 服务器。需要手动：
```bash
pkill -f "mcp_server.py" || true
cd "<repo-root>"
nohup python -m src.app.mcp_server > mcp_server.log 2>&1 &
```

### 9.6 handoff 文件误报

Audit worker 曾报告 `handoff-commander-to-audit.json` 不存在，但实际文件存在于 `/root/agentteams-fs/shared/tasks/task-20260808-042800/handoff-commander-to-audit.json`。可能是 audit worker 基于 `approval.required` 错误推断了 handoff 缺失。修复 approval 工具后需验证是否仍报此错。

---

## 十、Handoff 文档链

| 文档 | 说明 |
|------|------|
| `docs/handoffs/H-R00-主控.md` | 初始主控 handoff |
| `docs/handoffs/H-H01-主控.md` | HiClaw 运行时清理 handoff |
| `docs/handoffs/H-T01~T05-*.md` | 四角色开发 handoff |
| `docs/handoffs/H-R06.md` | R-06 双路径修复 handoff |
| `docs/handoffs/R-07-workbuddy-diagnosis.md` | R-07 LLM 切换 + CR model 修复（v3） |
| `docs/handoffs/R-08-audit-fix.md` | **当前待执行**：审计审批门修复 |
| `docs/handoffs/H-R08.md` | R-08 结果记录（待创建） |
| `docs/verification/R-07-s01-dispatch.md` | R-07 S01 派发验证记录 |
| `docs/status.md` | 交付状态总表 |

---

## 十一、立即行动项

1. 打开 `docs/handoffs/R-08-audit-fix.md`，执行 6 个 Task
2. 执行完后验证 S01 audit 返回 `qualified`
3. 更新 `docs/status.md`：R-08 → DONE，V-05 → PASS
4. 开始准备初赛 PPT（8/16 截止）

---

*文档结束。如有疑问，可参考 `docs/handoffs/` 下的历史 handoff 文档，或查看本机未纳入仓库的 WorkBuddy 工作记忆。*
