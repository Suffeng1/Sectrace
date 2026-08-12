# SecTrace：安全事件多 Agent 协同审计系统

SecTrace 是一个面向安全事件分析与审计演示的多 Agent 协作项目。系统将一条固定的合成安全事件交给四个职责隔离的 Agent，依次完成事件接收、证据关联、处置建议、人工审批和独立审计，并使用可校验的哈希账本保留完整轨迹。

> 本项目只处理合成或脱敏数据，不连接、扫描或操作真实系统。所有处置内容均为建议；高风险计划必须经过人工审批，而且任何计划都不能进入 `executed` 状态。

## 项目状态

- 核心功能、AgentTeams 现场链路、人工审批、MCP 安全边界及最终验收均已完成。
- V-08 clean distinct trace：PASS。
- S-09 Codex Security：PASS。
- V-05 最终验收：PASS。
- 当前全量测试：`114 passed`。

详细结果见 [交付状态](docs/status.md)、[V-05 最终验收](docs/verification/V-05-final-reconciliation.md) 和 [演示证据索引](outputs/demo/evidence-index.md)。

## 主要能力

### 四角色协作链

```text
Manager（仅路由）
  └─ Commander：接收并规范化事件，创建 IncidentCase
       └─ Evidence：关联已提供的合成证据，区分事实、推断和未知
            └─ Response：生成仅供参考的处置计划，进入 pending_approval
                 ├─ Human Operator：在 Matrix 中批准或拒绝
                 └─ Audit：校验对象、引用、审批和账本，生成 AuditReview
```

- `Commander`：事件入口、trace 创建与任务编排。
- `Evidence`：证据关联和风险路径分析，不补造缺失证据。
- `Response`：输出建议、验证步骤和回滚步骤，不执行处置。
- `Audit`：独立验证 Contract、跨阶段引用和哈希链。
- `Manager`：只负责 AgentTeams 消息与任务路由，不直接调用 SecTrace MCP。

### 可审计状态与人工门禁

- 五类 Pydantic v2 Contract：`IncidentCase`、`EvidenceItem`、`ResponsePlan`、`ApprovalRecord`、`AuditReview`。
- 所有阶段保持同一 `trace_id`，Response 与 Approval 绑定当前 `plan_ref`。
- 审计事件使用 canonical JSON 和 SHA-256 形成 append-only 哈希链。
- MCP 状态按 trace 写入 `data/mcp-state/`，使用临时文件、`fsync` 与 `os.replace` 原子替换。
- 重启时重新验证模型、阶段状态机、对象引用、审批语义、账本哈希以及派生 Audit；异常状态 fail closed。
- 同一场景可以通过安全的 `run_id` 创建独立 trace，避免覆盖已有不可变审计轨迹。

### 六个 MCP 工具

| 工具 | 作用 | 状态变化 |
| --- | --- | --- |
| `sectrace.intake.create_incident` | 从 S01–S24 合成场景创建事件 | 创建 trace |
| `sectrace.evidence.analyze_case` | 分析已提供证据 | 增加 Evidence |
| `sectrace.response.create_plan` | 生成建议型处置计划 | 进入 `pending_approval` |
| `sectrace.audit.build_bundle` | 构建并校验审计包 | 增加 Audit |
| `sectrace.ledger.get_trace` | 读取规范账本 | 只读 |
| `sectrace.ledger.log_approval` | 验证 Matrix 人工审批并记账 | 记录批准/拒绝 |

服务使用 MCP Streamable HTTP，默认监听 `127.0.0.1:19090/mcp`。未知工具、路径型 scenario/run ID、重复或越序阶段、错误 trace/plan、伪造审批和持久化篡改都会被拒绝。

## 技术栈

| 类别 | 技术 |
| --- | --- |
| 语言 | Python 3.11+ |
| 数据契约 | Pydantic v2 |
| MCP 服务 | MCP Python SDK、Streamable HTTP |
| Web 演示 | Starlette、Uvicorn、原生 HTML/JavaScript |
| 图关系 | NetworkX |
| 测试 | pytest、Playwright（可选浏览器测试） |
| Agent 编排 | AgentTeams / HiClaw、OpenClaw Worker runtime |
| 协作界面 | Matrix / Element |
| 模型入口 | Higress / AgentTeams model gateway |
| 运行环境 | Windows PowerShell、Docker Desktop |
| 审计完整性 | Canonical JSON、SHA-256 hash chain、原子 JSON 持久化 |

## 目录结构

```text
SecTrace/
├─ data/scenarios/                 # S01–S24 合成测试场景
├─ docs/
│  ├─ adr/                         # 架构决策
│  ├─ contracts/                   # 系统契约
│  ├─ runtime/                     # 重启、运行时和秘密处理说明
│  ├─ specs/                       # MVP 规格
│  └─ verification/                # 测试、现场链路和安全验收证据
├─ hiclaw/sectrace-agents/         # 四 Worker、Team YAML 与角色 Prompt
├─ outputs/demo/                   # 演示脚本和证据索引
├─ scripts/sectrace-preflight.ps1  # 纯只读恢复前置检查
├─ src/
│  ├─ agents/                      # Commander/Evidence/Response/Audit 服务
│  ├─ app/                         # Contract、账本、MCP、Web UI、编排器
│  └─ skills/                      # 四角色确定性业务规则
└─ tests/                           # 单元、集成、E2E、运行时和安全测试
```

## 快速开始：本地单机演示

本路径不需要 Docker、AgentTeams 或 Matrix，适合首次体验和开发测试。

### 1. 环境要求

- Git
- Python 3.11 或更高版本
- Windows PowerShell 7（运行 preflight 时需要）

Linux/macOS 可以运行 Python 演示和测试，但仓库提供的运行时 preflight 是 PowerShell 脚本，完整 AgentTeams 现场配置以 Windows + Docker Desktop 为验证环境。

### 2. 克隆仓库

```powershell
git clone https://github.com/Suffeng1/Sectrace.git
cd Sectrace
```

如果默认分支尚未合并本项目版本，请切换到发布分支：

```powershell
git switch codex/sectrace-bootstrap
```

### 3. 创建虚拟环境并安装依赖

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Linux/macOS 激活命令为：

```bash
source .venv/bin/activate
```

### 4. 运行只读代码前置检查

```powershell
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode code
```

期望输出中的 `status` 为 `READY_CODE`。

### 5. 运行测试

```powershell
python -m pytest -q -p no:cacheprovider
```

### 6. 命令行重放 S01

```powershell
python -m src.app.demo
```

输出应包含同一个 `trace_id=tr_s01`、四阶段结果、`pending_approval`、有效审计完整性以及“未执行真实动作”的安全提示。

### 7. 启动本地 Web 演示

```powershell
python -m uvicorn src.app.main:app --host 127.0.0.1 --port 19080
```

浏览器打开 <http://127.0.0.1:19080>，点击“重放 S01”。

## 启动 MCP 服务

### 无 Matrix 审批配置

```powershell
python -m src.app.mcp_server
```

端点为 <http://127.0.0.1:19090/mcp>。在此模式下，intake、Evidence、Response、Audit 和 ledger 读取功能可用；`log_approval` 会 fail closed，因为服务无法验证真实的人类来源。

### 配置 Matrix 人工审批

需要一个只能读取指定审批房间的 Matrix 服务账号。不要使用管理员 token，不要把凭据写进 Git、YAML、Prompt、任务消息或命令历史。

必须同时设置以下四个环境变量：

```powershell
$env:SECTRACE_MATRIX_HOMESERVER_URL = "https://your-matrix.example"
$env:SECTRACE_MATRIX_ACCESS_TOKEN = "<read-only-service-token>"
$env:SECTRACE_APPROVAL_ROOM_ID = "<approval-room-id>"
$env:SECTRACE_APPROVER_USER_ID = "<human-matrix-user-id>"
python -m src.app.mcp_server
```

也可以复制 `hiclaw/.env.example` 到 Git 忽略的本地配置文件，再由自己的进程管理器注入环境。四项必须全部存在或全部缺失；只配置一部分时服务会拒绝启动。

人工操作员在指定 Matrix 房间发送一条纯文本 JSON：

```json
{"schema_version":"1.0","action":"sectrace.approval","trace_id":"<trace_id>","plan_ref":"<plan_ref>","decision":"approved","reason":"synthetic operator review"}
```

`decision` 只能是 `approved` 或 `rejected`，`reason` 最长 500 字符。Commander 调用工具时只提交 Matrix `approval_event_id` 以及相同的 trace、plan 和 decision。服务端会自行读取事件、验证房间和发送者，并只在账本中保存事件 ID 与 reason 的 SHA-256，不保存 token、房间 ID、用户 ID、原始事件 ID或原始 reason。

## 完整部署：Docker + AgentTeams + Element

本仓库提供 SecTrace Worker、Team、Prompt 和 MCP 服务，但不重新分发 AgentTeams/HiClaw 平台本身。请先按照你采用的 AgentTeams 版本完成 Controller、Manager、model gateway、Matrix/Element 和 `agt` CLI 的安装，并确保 Docker Desktop 正常运行。

### 1. 端口约定

| 服务 | 默认地址/端口 |
| --- | --- |
| AgentTeams Controller API | `127.0.0.1:18001` |
| Model gateway / Higress | `127.0.0.1:18080` |
| Element | `http://127.0.0.1:18088` |
| AgentTeams Manager | `127.0.0.1:18888` |
| SecTrace 本地 UI（可选） | `127.0.0.1:19080` |
| SecTrace MCP | `127.0.0.1:19090` |

Worker 容器通过 `http://host.docker.internal:19090/mcp` 访问宿主机 MCP。源码已将该 authority 加入 MCP transport-security allowlist，但服务仍只绑定宿主机 loopback。

### 2. 准备模型与平台配置

四个 Worker YAML 默认使用：

```yaml
model: deepseek-chat
runtime: openclaw
```

请在 AgentTeams/Higress 中配置同名模型，或在四个 `hiclaw/sectrace-agents/sectrace-*.yaml` 中统一替换成你已配置的模型名。模型 API Key、Matrix token 和平台密码必须保存在平台的本地 secret/config 中，不要写入本仓库。

### 3. 启动 SecTrace MCP

先按上一节设置 Matrix 审批环境变量，再在仓库根目录运行：

```powershell
python -m src.app.mcp_server
```

### 4. 应用四个 Worker 与 Team

在已经安装并登录 `agt` CLI 的环境中执行：

```powershell
agt apply -f .\hiclaw\sectrace-agents\sectrace-commander.yaml
agt apply -f .\hiclaw\sectrace-agents\sectrace-evidence.yaml
agt apply -f .\hiclaw\sectrace-agents\sectrace-response.yaml
agt apply -f .\hiclaw\sectrace-agents\sectrace-audit.yaml
agt apply -f .\hiclaw\sectrace-agents\sectrace-audit-team.yaml
```

然后检查：

```powershell
agt get workers sectrace-commander -o json
agt get workers sectrace-evidence -o json
agt get workers sectrace-response -o json
agt get workers sectrace-audit -o json
agt get teams sectrace-audit-team -o json
```

四个 Worker 应为 `Running`，Team 应为 `Active`。资源字段随 AgentTeams 发行版变化时，先阅读 [兼容性说明](docs/runtime/hiclaw-compatibility.md)，不要猜测 CRD 字段。

### 5. 运行 runtime preflight

```powershell
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode runtime
```

该脚本依次验证 Docker、Controller、gateway、Manager、四 Worker、Team、MCP listener/TCP/initialize，以及 Commander 容器到 MCP 的 DNS/TCP/initialize。期望状态为 `READY_RUNTIME`。

preflight 是纯只读门禁，不会启动、停止、重启或修改任何服务。

### 6. 准备 Matrix/Element 操作

在任何真实 Matrix 消息或 S01 操作前运行：

```powershell
pwsh -File .\scripts\sectrace-preflight.ps1 -Mode live
```

自动检查通过后会返回 `MANUAL_REQUIRED`，提示人工确认：Element 已登录、房间正确、Matrix channel 在线以及当前没有未处理审批。完整规则见 [重启与恢复前置检查](docs/runtime/reboot-preflight.md)。

### 7. 安全执行边界

- 只发送合成场景 S01–S24。
- Manager 只能路由，不得配置或调用 SecTrace MCP。
- Commander 创建 Incident，并在人工事件出现后负责调用 `log_approval`。
- Evidence、Response、Audit 只调用各自允许的工具。
- 出现第一个失败立即停止；不要自动重试、改配置或走直接 HTTP 旁路。
- 到达 `pending_approval` 必须等待真实人工决定。
- 审批不等于执行，项目没有任何真实处置工具。

## MCP 调用示例

如果你的 MCP 客户端是 `mcporter`，可以按如下顺序操作一个新的独立合成 trace：

```powershell
mcporter call --server sectrace --tool sectrace.intake.create_incident scenario_id=S01 run_id=DEMO01
mcporter call --server sectrace --tool sectrace.evidence.analyze_case trace_id=tr_s01_demo01
mcporter call --server sectrace --tool sectrace.response.create_plan trace_id=tr_s01_demo01
mcporter call --server sectrace --tool sectrace.ledger.get_trace trace_id=tr_s01_demo01
```

此时必须停在 `pending_approval`。只有获得符合前述格式的 Matrix 人工事件后，Commander 才可执行：

```powershell
mcporter call --server sectrace --tool sectrace.ledger.log_approval trace_id=tr_s01_demo01 decision=approved plan_ref=rp_tr_s01_demo01 approval_event_id=<matrix_event_id>
```

工具的确切 CLI 参数形式可能随 MCP 客户端版本变化；以客户端的 `list-tools`/schema 输出为准，不要将审批者或 reason 作为调用参数。

## 测试与质量检查

```powershell
# 全量测试
python -m pytest -q -p no:cacheprovider

# 安全与仓库卫生
python -m pytest -q -p no:cacheprovider tests/security

# Git 空白和补丁检查
git diff --check
```

测试覆盖：Contract、四角色服务、24 个场景、MCP 状态机、重启持久化、篡改与重哈希攻击、路径/容量边界、Matrix 审批验证、运行时资源、浏览器演示和秘密扫描。

## 常见问题

### `BLOCKED_DOCKER_ENGINE`

确认 Docker Desktop 已启动，并且当前终端用户可以执行 `docker info`。

### `BLOCKED_MCP_SERVICE_NOT_RUNNING`

在仓库根目录和正确虚拟环境中运行 `python -m src.app.mcp_server`。不要通过 preflight 启动服务。

### Worker 无法连接 MCP

确认宿主机 `127.0.0.1:19090` 正在监听，容器能解析 `host.docker.internal`，并检查 Commander YAML 中的 MCP URL。依次排查 DNS、TCP、MCP initialize，不要直接修改防火墙或改成广域绑定。

### `log_approval` 被拒绝

检查四个 Matrix 环境变量是否同时设置，事件是否来自配置的房间和用户，JSON 是否精确绑定当前 trace、plan 与 decision，以及事件是否已过期或被重复使用。

### 重启后状态加载失败

服务会对任何不一致状态 fail closed。不要手工修复或回写 append-only 状态；保留文件用于诊断，并使用新的合法 `run_id` 创建独立 trace。

## Resume after reboot / 电脑重启后恢复

每次重启后都应重新运行最低必要级别的只读 preflight：代码工作使用
`code`，Docker/AgentTeams/MCP 工作使用 `runtime`，任何 Matrix 或 S01
操作前使用 `live`。历史 PASS 不能替代当前检查，preflight 也不负责启动
服务。完整步骤见 [重启与恢复前置检查](docs/runtime/reboot-preflight.md)。

## 安全设计与限制

- MCP 仅监听 loopback，并启用 Host authority 限制。
- 场景 ID 和 run ID 使用严格 allowlist；运行态 trace 数量有上限。
- 所有 mutating stage 在写入前执行顺序和幂等性检查。
- Matrix verifier 在服务端获取事件，不信任调用者声明的人类身份或理由。
- 持久化数据、日志和错误信息避免保存或回显秘密。
- 项目是竞赛/演示型审计系统，不是生产 SOC、EDR、SOAR 或自动响应平台。
- 完整 AgentTeams 安装、模型供应商账号和 Matrix 基础设施由部署者负责。

更多细节：

- [系统契约](docs/contracts/system-contract.md)
- [MVP 规格](docs/specs/mvp-spec.md)
- [AgentTeams 架构决策](docs/adr/ADR-001-agentteams-runtime.md)
- [Append-only 审计账本](docs/adr/ADR-002-append-only-audit-ledger.md)
- [秘密处理规则](docs/runtime/secret-handling.md)
- [演示步骤](outputs/demo/demo-script.md)

## 贡献

提交变更前请保持 synthetic-only、human-gated、trace continuity 和 no-real-action 四条边界，并运行完整测试与安全扫描。不要提交 `.env`、token、Matrix 标识、运行态 `data/mcp-state/`、浏览器登录截图或本地日志。

## License

仓库当前未附带开源许可证。除非仓库所有者后续明确添加 LICENSE，否则默认保留全部权利。
