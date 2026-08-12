# R-08L Bundled Matrix 启用验证

- 日期：2026-08-09
- 结论：`NEEDS_AUTHORIZATION`
- 授权命令：仅 `openclaw plugins enable matrix`
- 安全边界：失败立即停止；未发送 S01、未审批、未 apply/delete、未修改 Worker/YAML/业务代码/MCP、未触碰 smoke、未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 变更前安全门

- Manager：running
- 旧 configured plugin 发现路径为空：true
- 旧插件可恢复备份存在：true
- bundled plugin 目录存在：true

## 唯一命令结果

执行官方命令：

`openclaw plugins enable matrix`

结果：失败，退出码非零。

公开错误类别：

- OpenClaw config invalid
- `plugins.load.paths` 仍存在一个指向已禁用旧 Matrix 插件目录的路径
- CLI 在执行 enable 之前停止

错误同时提示存在 legacy Matrix group 配置键，但 R-08L 未授权运行 doctor 或修改 channel 配置，因此没有处理。

## 停止门

按照“失败立即停止”：

- Manager 重启次数：0
- 未再次运行 enable
- 未恢复旧插件
- 未修改或清除 load-path
- 未运行 `openclaw doctor --fix`
- 未执行 channel/sync 探针

## 四项布尔状态

| 项目 | R-08L 结果 |
| --- | --- |
| bundled-only | true（变更前文件系统门） |
| duplicate-warning-absent | 未重新探测；沿用 R-08K 当前运行态的 true，不冒充本轮新证据 |
| channel-online | 未复核 |
| sync-ready | 未复核 |

由于唯一 enable 命令失败，四项验收没有全部完成，不能进入单次 S01 preflight。

## 对 R-08K 推断的修正

R-08K 中“官方 uninstall 已清除 config/load-path 关系”的表述过强。R-08L 的 CLI 校验反证表明：

- config entry 已移除；
- 但至少一个旧插件 load-path 仍保留；
- 旧目录移出后，该残留路径使整个 OpenClaw 配置在插件命令入口处无效。

历史 R-08K 文档保留；本文件作为后续修正证据。

## 下一项唯一最小授权建议

建议 R-08M 仅授权：

1. 使用 OpenClaw 官方配置命令或等价的结构化编辑，仅删除 `plugins.load.paths` 中**精确匹配旧 Matrix 扩展路径**的单个条目；
2. 不读取或更改其它 config/channel 值，不运行 doctor；
3. 重新执行一次 `openclaw plugins enable matrix`；
4. 仅重启 Manager 一次；
5. 复核 bundled-only、duplicate-warning-absent、channel-online、sync-ready 四项脱敏布尔；
6. 任一失败立即停止，不发送 S01。

在变更前必须先以不输出配置值的结构化断言确认：目标旧路径匹配项恰好为 1；若不是 1，停止。

## 结论

`NEEDS_AUTHORIZATION`

当前不能进入单次 S01 preflight。
