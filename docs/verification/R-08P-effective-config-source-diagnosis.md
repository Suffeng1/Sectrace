# R-08P Effective Config 来源分层诊断

- 日期：2026-08-09
- 结论：`ROOT_CAUSE_CONFIRMED`
- 唯一来源层：effective JSON
- 安全边界：只输出布尔与计数；未读取或输出配置值、路径、环境变量、凭据、Matrix 标识、启动脚本或原始日志

## Effective Config 文件一致性

`openclaw config file` 因当前配置无效而不能正常返回结果，因此没有把该命令失败误判为路径不一致。

随后使用 OpenClaw 默认配置解析规则，在容器内部完成规范化比较：

- 默认配置定位可用：true
- 默认规范路径与 R-08M 编辑目标相等：true

一次补充 inode 比较受宿主格式影响，结果无效；一次容器内重复比较因 11.8 秒超时而停止，未重试。规范路径相等的原始布尔结果有效。

## JSON 层

只解析 effective JSON 中 `plugins.load.paths` 数组，并对精确旧 Matrix 路径计数：

- 数组存在：true
- 精确旧路径匹配数：1

未读取或输出数组其它值。

## Registry 层

官方 `plugins registry --json` 因当前配置无效不能生成 registry 视图。

随后仅检查当前/旧版两个官方精确持久化面：

| Registry 面 | 存在 | 旧路径计数 |
| --- | --- | --- |
| legacy plugin index | false | 不适用 |
| shared SQLite state DB | false | 不适用 |
| SQLite `installed_plugin_index` | false | 不适用 |

没有遍历其它数据库、表或状态文件。

因此 persisted plugin registry 不是当前旧 load-path 的来源。

## CLI Derived View

执行一次只读 `openclaw config validate`，只保留类别与计数：

- validate 成功：false
- CLI 判定 config invalid：true
- CLI 视图中精确旧路径匹配数：1

CLI 视图计数与 effective JSON 计数完全一致，且不存在 persisted registry。没有证据表明 CLI 额外派生第二条旧路径；CLI 只是验证 JSON 中已有的一条。

## 三层分类

| 层 | 旧路径是否存在 | 结论 |
| --- | --- | --- |
| effective JSON | 是，恰好 1 | **唯一持久来源** |
| persisted registry | 否 | 排除 |
| 独立 CLI derived view | 否 | CLI 仅反映 JSON 的同一条 |

## 与 R-08M/R-08O 的合并结论

- R-08M 的结构化编辑目标就是 effective config 文件，不是错文件。
- R-08O 证明对象存储 watcher 是 workspace 到对象存储的出站同步，不能把远端状态写回本地。
- Registry 不存在。
- 当前旧路径只持久化在 effective JSON。

因此 R-08M 删除后再次出现的剩余写入者只能位于 Manager 本地 supervisor/reconciliation 路径，而不是 registry、入站 mount watcher 或独立 CLI registry 派生层。

## 唯一最小修复授权建议

建议 R-08Q 严格限定为：

1. 暂停 Manager PID 1 supervisor，并同时保持其出站同步子进程暂停，避免把中间无效状态上传；
2. 在 effective JSON 中断言旧路径恰好 1 次并只删除该数组项；
3. 立即用结构化只读检查确认目标为 0、其它值语义不变；
4. 在 supervisor 仍暂停时仅执行一次 `openclaw plugins enable matrix`；
5. 只读确认 config valid、旧路径仍为 0；
6. 仅重启 Manager 一次，不先恢复中间进程；Docker 重启自然恢复 supervisor 与同步子进程；
7. 复核 bundled-only、duplicate-warning-absent、channel-online、sync-ready 四项脱敏布尔；
8. 任一门失败立即停止，不发送 S01。

如果重启后旧路径再次出现，则 supervisor 的启动模板才是最终源，必须停止并由用户授权修改模板；不得自动继续。

## 结论

`ROOT_CAUSE_CONFIRMED`

旧 Matrix load-path 当前唯一存在于 effective JSON。当前仍不能进入 S01 preflight。
