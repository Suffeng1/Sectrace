# R-08AJ 悬空插件引用精确修复验证

日期：2026-08-09

结论：`FAIL_AT_SYNC_READY`

## 安全边界

- 仅在 R-08AE 已确认的启动期权威结构化源中定位并删除唯一悬空插件引用。
- 未写 effective config，未修改凭据、channel 值、其它插件、模板语义、代码、YAML、MCP 或 smoke。
- 未运行 doctor；仅 restart Manager 一次；未发送 S01，未审批、apply/delete 或操作其它资源。
- 未输出配置正文、路径、值、凭据、标识、状态正文、日志或原始 stderr，未 commit/push。

## 权威源写前/写后断言

| 检查项 | 结果 |
|---|---:|
| effective unresolved reference count | 1 |
| target unresolvable | true |
| authority candidate count | 1 |
| authority source category | `controlled_mount_json_template` |
| template reference pre-count | 1 |
| pre-write assertion | true |
| write completed | true |
| template reference post-count | 0 |
| other template semantics unchanged | true |
| effective config written | false |

唯一悬空插件引用已从权威模板精确删除；其它模板语义保持不变。

## 单次 Restart 与 Config Valid 门

| 检查项 | 结果 |
|---|---:|
| Manager restarted once | true |
| Manager running | true |
| validator completed | true |
| config valid | true |

R-08AI 确认的全局配置校验阻断已解除。

## 五布尔复核

| 健康门 | 结果 |
|---|---:|
| old-path-not-reproduced | true |
| bundled-only | true |
| duplicate-warning-absent | true |
| channel-online | true |
| sync-ready | false |

所有公开状态探针均在有界窗口内完成。由于 sync-ready 为 false，按照授权立即停止，未重试或扩大范围。

## 证据与结论

- 启动期旧路径覆盖、重复插件、全局配置无效和 channel offline 均已被正向门排除。
- 当前唯一未通过的层是已在线 Matrix channel 的 sync loop 就绪状态。
- channel-online=true 不能替代 sync-ready；尚不能发送 S01。

## 资格判定

当前不具备单次 S01 preflight 资格。

## 唯一最小后续建议

建议 R-08AK 仅做纯只读 sync loop 初始化类别诊断：在 channel-online=true 前提下，以不含账户、房间、事件或 token 的公开状态投影，将 sync-ready=false 分类为 initial-sync pending / sync loop not started / sync transport error / sync state unavailable；只输出类别、布尔、计数和时间窗，不改配置、不 restart、不发送 S01。
