# R-08AD 纯只读五布尔复核

日期：2026-08-09

结论：`FAIL`

## 安全边界

- 仅执行有界、脱敏的配置计数与公开 OpenClaw 状态投影。
- 修正范围仅为 R-08AC 本地 PowerShell job 构造；未重跑维护事务。
- 未写入或补丁，未停止或重启 Manager，未发送 S01，未审批、apply/delete。
- 未修改代码、YAML、MCP 或 smoke，未输出配置正文、路径、凭据、标识、状态正文、原始日志或 stderr，未 commit/push。

## 五项布尔

| 健康门 | 结果 |
|---|---:|
| old-path 启动后不复现 | false |
| bundled-only | false |
| duplicate-warning-absent | true |
| channel-online | false |
| sync-ready | false |

辅助门：

- 所有公开状态探针均在有界窗口内完成：true
- Manager running：true

## 证据与反证

R-08AC 在 Manager 启动前已结构化证明旧 load-path 从 1 删除到 0；R-08AD 在同一次启动后的只读复核中确认其再次存在。因此旧路径由 Manager 启动期的上游期望状态重新生成，effective config 不是持久权威源。

`duplicate-warning-absent=true` 不能覆盖其它失败门：旧路径复现使 bundled-only 不成立，且 channel-online、sync-ready 均没有正向证据。

## 资格判定

当前不具备单次 S01 preflight 资格。

## 唯一最小修复建议

另行授权 R-08AE：仅在已确认的 Manager 启动期权威模板/生成源中，对同一旧 Matrix load-path 做一次精确结构化删除并设 bundled Matrix enabled=true；随后只启动或重启 Manager 一次并复核本票五项布尔。不得再次只修改 effective config。
