# R-08AC 最终维护补丁验证

日期：2026-08-09

结论：`INCOMPLETE`

## 安全边界

- 仅停止 Manager 一次、使用 R-08AB 已验证文件身份执行一次 helper 补丁、启动 Manager 一次。
- helper 使用同 Manager 镜像、精确 Node entrypoint、`network=none`、唯一 workspace bind、`--rm`。
- 未发送 S01、未审批、未 apply/delete，未修改 Worker/YAML/业务代码/MCP/smoke。
- 未输出配置正文、路径、凭据、标识、日志或原始 stderr，未 commit/push。

## 维护事务结果

| 检查项 | 结果 |
|---|---:|
| Manager stopped once | true |
| old Matrix load-path pre-count | 1 |
| pre-write assertion | true |
| config write completed | true |
| old Matrix load-path post-count | 0 |
| bundled Matrix enabled | true |
| other config semantics unchanged | true |
| helper auto-removed / residual 0 | true |
| Manager started once | true |
| Manager running after start | true |

补丁事务成功：只删除了唯一旧 Matrix load-path，并只将 bundled Matrix `enabled` 设为 true；写回后的配置与该两项内存期望完全语义相等。

## 启动后五项验收

启动后状态编排在公开 OpenClaw 状态探针执行前失败，公开失败类别为：本地 PowerShell 后台任务参数构造错误。按授权的“任一健康门失败立即停止、不重试”要求，本轮没有修正并重跑。

| 健康门 | R-08AC 结果 |
|---|---:|
| old path not reproduced after startup | 未完成 |
| bundled-only | 未完成 |
| duplicate-warning-absent | 未完成 |
| channel-online | 未完成 |
| sync-ready | 未完成 |

失败前已确认 Manager 正在运行；未发生第二次停止、启动或重启。

## 放行判定

当前不可进入单次 S01 preflight。配置补丁已完成，但启动后五项健康门没有形成有效证据。

## 唯一最小后续建议

另行授权一次纯只读 R-08AD：不再修改配置、不停止或重启 Manager，仅用修正后的有界状态投影复核上述五项布尔；全部为 true 后再判定是否进入单次 S01 preflight。
