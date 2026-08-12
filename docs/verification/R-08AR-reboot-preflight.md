# R-08AR Reboot/Resume Preflight

日期：2026-08-09

结论：`QA_PENDING`

## 目标

为电脑重启、长时间停止、新 Codex 对话和有意义的运行态变化建立固定前置门，避免把未启动的 MCP 服务误诊为 Manager/Commander/业务链故障。

## 交付物

- `docs/runtime/reboot-preflight.md`：`code` / `runtime` / `live` 三级权威手册。
- `scripts/sectrace-preflight.ps1`：纯只读、机器可读 JSON preflight。
- `AGENTS.md`：新对话、电脑重启、运行态变化后的强制最低必要模式门。
- `README.md`：Resume after reboot 入口和链接。
- `tests/runtime/test_reboot_preflight.py`：最小静态安全测试。

## TDD 证据

### RED

先新增测试并运行：

```text
4 failed in 0.14s
```

失败原因均符合预期：脚本/手册缺失，AGENTS 强制门和 README 入口尚不存在。没有收集错误或测试语法错误。

### GREEN

实现最小功能后聚焦复跑：

```text
4 passed in 0.03s
```

测试覆盖：

- 三模式与安全 JSON 分类存在；
- `BLOCKED_MCP_SERVICE_NOT_RUNNING` 与 `MANUAL_REQUIRED` 存在；
- 脚本不含启动/停止/重启、Docker mutation、AgentTeams apply/delete、消息或审批命令；
- 脚本不读取计划任务 action/path、配置文件或原始日志；
- AGENTS 强制最低必要模式门；
- README 链接权威手册与脚本。

## 实际脚本验证

### `code`

结果：`READY_CODE`

- formal repository：true
- Git repository：true
- Python runtime：true
- duration：0.1 秒

### `runtime`

结果：`BLOCKED_LOCAL_UI`

在失败前通过：

- Docker engine
- production Controller
- production Manager
- Commander/Evidence/Response/Audit 四个正式 Worker
- production Team

本地 SecTrace UI reachability 为 false，脚本按顺序立即停止；未继续 Host MCP/Commander MCP 层，也未启动 UI、MCP 或任何资源。该结果是当前环境分类，不是实现失败。

## 只读与安全边界

- 脚本只有状态查询、TCP 和 MCP initialize 探针；不读取 initialize 响应正文。
- 输出仅包含安全类别、布尔、退出码、HTTP 类别与耗时。
- 不输出 PID、命令行、路径正文、环境变量、配置、日志、Matrix 标识或消息。
- `live` 在 runtime 通过后仅检查 Element 页面可达，并返回人工确认项；不读取浏览器会话。
- 历史 PASS 明确不能替代当前开机检查。
- 普通 code/docs 工作不要求 Docker 或 Element；任何 live S01 必须通过 live 门并另行取得单发授权。
- 脚本不是启动器；任何 runtime mutation 仍需逐项用户授权。
- 未触碰 `sectrace-smoke`，未 commit/push。

## 差异卫生

`git diff --check`：passed。

现有工作树的换行提示来自本票外既有修改；本票未改写这些文件。

## QA 请求

请 05 独立验证：

1. 三模式依赖顺序与最低必要模式是否符合手册；
2. runtime 的 MCP listener 缺失分类是否会短路为 `BLOCKED_MCP_SERVICE_NOT_RUNNING`；
3. 脚本是否确实无启动/重启/发送/审批/资源 mutation 能力；
4. live 是否只返回人工确认项且不读取浏览器会话；
5. 当前 `BLOCKED_LOCAL_UI` 是否是正确的失败即停投影。

## Superseding correction and re-verification

This section supersedes the earlier `BLOCKED_LOCAL_UI` observation and the
corresponding old QA question above. The current script uses
`local_demo_ui_reachable` only as an optional, non-blocking observation; it
is required only for local replay/demo work.

The correction added three targeted RED tests. They failed as expected against
the old design: missing optional demo behaviour, missing ordered Controller /
model gateway / Manager TCP gates, and the false
`host_mcp_process_present` category. The corrected focused suite is:

```text
7 passed in 0.02s
```

Actual read-only runs on this boot:

- `code`: `READY_CODE`.
- `runtime`: `BLOCKED_DOCKER_ENGINE` at the first true runtime dependency.
- `live`: `BLOCKED_DOCKER_ENGINE`; it correctly did not inspect Element or
  browser state, and therefore did not yet reach `MANUAL_REQUIRED`.

The current runtime order is core TCP reachability (Controller API 18001,
model gateway 18080, Manager 18888), production resource phases, optional
local demo UI, then MCP listener/TCP/initialize. Listener absence is classified
without asserting process existence. No component was started or changed.

05 must perform a fresh QA against this corrected state; prior QA PASS is not
valid for R-08AR.
