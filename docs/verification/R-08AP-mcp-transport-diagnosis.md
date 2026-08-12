# R-08AP MCP Transport 分层诊断

日期：2026-08-09

结论：`ROOT_CAUSE_CONFIRMED`

第一失败层：`host_mcp_service_absent_or_stopped`

## 安全边界

- 仅执行秒级、确定性、可重复的只读分层反馈回路。
- 第一层失败即短路；未启动、停止或重启服务，未改配置或运行态，未发送 S01，未审批、apply/delete。
- 未读取或输出 PID、命令行、地址正文、路径、响应正文、凭据、Matrix 标识、配置正文、原始日志、启动脚本或 stderr。
- 未触碰 `sectrace-smoke`，未修改代码、YAML、MCP 或 Git。

## 分层反馈回路

固定顺序：

1. Host MCP 服务/进程存在性与目标 listener；
2. Host TCP；
3. Host MCP initialize；
4. Commander running；
5. Commander DNS；
6. Commander TCP；
7. 仅 TCP 成功后执行 Commander MCP initialize。

每层失败即停止，后续层标记为 `not_run`。本轮总耗时 2.5 秒。

## 脱敏结果

| 层 | 结果 | 退出码/类别 |
|---|---:|---|
| Existing MCP service task exists | true | 只读状态投影 |
| Existing MCP service task running | false | stopped/not-running |
| Host MCP process present | false | absent |
| Host target listener present | false | absent |
| Host TCP | not_run | -1 |
| Host MCP initialize | not_run | -1 |
| Commander running | not_run | 短路 |
| Commander DNS | not_run | -1 |
| Commander TCP | not_run | -1 |
| Commander MCP initialize | not_run | -1 |

## 假设判定

| 排序 | 假设 | 判定 |
|---:|---|---|
| 1 | MCP service/listener absent or stopped | **确认** |
| 2 | listener 存在但 bind scope 不可达 | 未执行；前置 listener 不存在 |
| 3 | Host firewall/Docker forwarding 拒绝 | 未执行；前置 listener 不存在 |
| 4 | Commander DNS/route | 未执行；前置 Host 层失败 |
| 5 | TCP 可达但 MCP initialize endpoint/protocol 失败 | 未执行；前置 Host 层失败 |

R-08AO 的 `connection_refused` 与本轮 Host service not-running、process absent、listener absent 构成闭环。当前不需要用防火墙、DNS、容器路由或协议问题解释该拒绝。

## 唯一最小修复授权建议

建议 R-08AQ 严格授权：

1. 仅启动一次已经存在的精确 MCP 计划任务，不改任务、代码、bind、allowlist、Worker 或 YAML；
2. 验证任务 running、Host listener、Host TCP 和 Host initialize；
3. Host 全部通过后，再只读验证 Commander running、DNS、TCP 与 MCP initialize；
4. 任一门失败立即停止，不重试、不 restart Worker/Manager、不重发 S01；
5. 全部分层门通过后，仍需另行授权新的唯一一次 S01，不能自动补发本次已失败事件。

## 当前资格

当前不能进入 S01 重发、pending_approval 或 V-08/V-05 放行。必须先恢复既有 MCP 服务并完成分层复核。
