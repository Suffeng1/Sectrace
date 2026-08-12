# R-08M Stale Matrix Load Path 精确删除验证

- 日期：2026-08-09
- 结论：`NEEDS_AUTHORIZATION`
- 安全边界：失败立即停止；未发送 S01、未审批、未 apply/delete、未修改 Worker/YAML/业务代码/MCP、未触碰 smoke、未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 结构化断言

Manager 内的结构化编辑器只输出目标计数和布尔结果：

- `plugins.load.paths` 数组存在：true
- 已禁用旧 Matrix 路径精确匹配次数：1

断言门通过后才允许删除。

## 精确删除

只删除该精确数组条目，使用同目录原子替换，并立即重新解析验证：

- 目标路径删除后匹配次数为 0：true
- 数组长度只减少 1：true
- 其它配置值语义保持不变：true

未运行 doctor，未处理 legacy Matrix group key，未读取或输出其它配置值。

## 唯一 Enable 命令

随后仅执行一次：

`openclaw plugins enable matrix`

结果：失败，退出码非零。

公开错误类别仍为：

- OpenClaw config invalid
- `plugins.load.paths` 再次包含指向已禁用旧 Matrix 插件目录的路径
- CLI 在 enable 变更前停止

这与写入后的即时结构化验证形成确定反证：目标条目在删除成功后、执行 enable 之前被活动中的 Manager 配置协调/重建机制重新注入。

## 失败停止

按照授权：

- enable 执行次数：1
- enable 成功：false
- Manager 重启次数：0
- 未再次删除或重试
- 未恢复旧插件
- 未运行 doctor
- 未执行四布尔运行态探针

## 四项布尔状态

| 项目 | R-08M 结果 |
| --- | --- |
| bundled-only | 未重新复核；R-08L 前置文件系统门为 true |
| duplicate-warning-absent | 未重新复核 |
| channel-online | 未复核 |
| sync-ready | 未复核 |

唯一 enable 命令失败，四项验收未完成，不能进入单次 S01 preflight。

## 根因修正

R-08J/R-08K 的“仅冷启动插件发现重新注入”范围不足。R-08M 证明：

- 即使不重启 Manager；
- 即使目标 load-path 精确删除并即时验证为 0；
- 活动运行时仍会在下一条官方 CLI 命令前重新建立该路径。

因此当前直接阻塞是：**Manager 活动配置协调器持有旧 Matrix load-path 的上游期望状态，并持续覆盖 workspace 配置。**

## 下一项唯一最小授权建议

建议 R-08N 先只读、不改配置：

1. 仅定位活动配置协调器的来源类别：Manager 内 supervisor、Controller reconciliation、挂载模板 watcher 或 OpenClaw gateway config watcher；
2. 只输出进程角色、父子关系和目标配置文件的写入者类别，不输出命令行参数值、环境变量、配置内容、标识或日志；
3. 确认唯一写入者后，再单独授权短暂停止该协调器、精确删除旧 load-path、enable bundled Matrix、仅恢复/重启 Manager 一次并复核四布尔。

未经 R-08N 不应继续重复 config 删除或 enable。

## 结论

`NEEDS_AUTHORIZATION`

当前不可进入单次 S01 preflight。
