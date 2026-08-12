# H-R08AR Reboot/Resume Preflight 交接

日期：2026-08-09

## 状态

`QA_PENDING`

## 已完成

- 新增三级权威手册与纯只读 PowerShell JSON preflight。
- AGENTS 已要求 new conversation / computer reboot / runtime change 后选择 lowest necessary mode。
- README 已增加 Resume after reboot 入口。
- TDD RED：4 failed（功能缺失）。
- TDD GREEN：4 passed。
- `code` 实跑：`READY_CODE`。
- `runtime` 实跑：`BLOCKED_LOCAL_UI`，在 Docker/正式资源通过后安全短路；无任何启动或修改。
- `git diff --check`：passed。

## 安全结论

脚本不能启动、停止或重启任何服务，不能 apply/delete，不能发送 S01 或审批。MCP process/listener 缺失时会返回 `BLOCKED_MCP_SERVICE_NOT_RUNNING`，不得继续归因业务链。

`live` 只返回 `MANUAL_REQUIRED` 清单；任何消息仍需用户独立单发授权。

## QA

请 05 独立复跑聚焦测试，并静态审查脚本的只读边界、三模式顺序与 AGENTS 强制门。当前不 commit/push。

## Superseding correction

This section overrides the earlier local-UI and MCP-process wording in this
handoff. The current status remains `QA_PENDING`.

- The Python demo UI check is now `local_demo_ui_reachable`, state
  `optional`, and never blocks general runtime/live S01 preflight.
- Runtime now gates Controller API, model gateway, and Manager TCP
  reachability before production resource phases; any of those true core
  failures stops the script.
- `host_mcp_process_present` has been removed. MCP is classified only by
  listener, TCP, and initialize results; listener is not presented as process
  evidence.
- Targeted correction RED produced three expected failures; final focused
  suite is `7 passed in 0.02s`.
- Actual current-boot results are `code=READY_CODE` and
  `runtime/live=BLOCKED_DOCKER_ENGINE`. The live run did not reach Element or
  `MANUAL_REQUIRED`, which is the correct first-failure short circuit.

No runtime mutation, S01, approval, commit, or push occurred. Ask 05 for a
fresh independent QA; do not reuse prior R-08AR QA.
