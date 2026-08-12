# R-08K Bundled Matrix 去重修复验证

- 日期：2026-08-09
- 结论：`NEEDS_AUTHORIZATION`
- 运行时变更：仅 Manager
- 安全边界：未发送或重试 S01，未审批，未修改 Worker/Team/YAML/业务代码/MCP，未 apply/delete，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本，未 commit/push

## 路径安全门

变更前通过只读规范化与文件系统检查确认：

- 旧 configured Matrix plugin 源路径精确匹配预期镜像扩展路径；
- bundled Matrix plugin 路径精确匹配预期 dist-runtime 扩展路径；
- 禁用备份目标精确且不存在；
- 源与备份目标位于同一文件系统；
- bundled 目录存在。

## 可恢复变更

1. 将旧插件目录移动到同文件系统的禁用备份目录，不删除文件。
2. 首次官方卸载 dry-run 因残留 load-path 指向已移动目录而拒绝，未产生配置修改。
3. 在 Manager 尚未重启的情况下，将目录临时恢复。
4. 使用官方 `plugins uninstall matrix --keep-files --force` 成功移除旧 config entry/load-path 关系。
5. 再次把旧目录移动到禁用备份位置。
6. 只滚动重启 Manager 一次，Manager 恢复 running。

最终文件系统布尔状态：

- 旧插件发现路径为空：true
- 可恢复禁用备份存在：true
- bundled plugin 目录存在：true

## 三布尔验收

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| bundled 为唯一发现候选 | true | 旧发现路径为空、bundled 路径存在、禁用备份位于发现树外 |
| duplicate-warning 消失 | true | 重启后公开 health/help 初始化未出现 duplicate plugin ID 警告 |
| channel online | false（未正向确认） | Manager 内部对公开 health 文本做行级过滤，仅返回布尔摘要；无 online/connected/ready/healthy 正向标记 |
| sync-ready | false（未正向确认） | 同一安全摘要没有 Matrix sync-ready 正向标记 |

未调用 credential probe，未读取完整 channel/health JSON，也未输出 account、room、user、recipient 或 session 数据。

## 结论

镜像重复插件问题已消除，但 Manager Matrix channel 尚未被安全状态摘要确认在线或 sync-ready。按照“任一布尔失败立即停止”的授权门，本轮停止，不能进入单次 S01 preflight。

最可能原因是官方 uninstall 在移除旧 override config entry 时同时把 plugin ID 置于未启用状态；旧插件移出后，bundled 实现虽然是唯一候选，但没有 active config entry。

## 下一项唯一最小授权建议

建议 R-08L 严格限定为：

1. 使用 OpenClaw 官方命令仅启用 plugin ID `matrix`；
2. 不修改任何 Matrix channel 配置值；
3. 仅重启 Manager 一次；
4. 仅验证：
   - bundled Matrix 为唯一加载实现；
   - duplicate-warning-absent=true；
   - channel-online=true；
   - sync-ready=true；
5. 任一失败立即停止，不发送 S01。

R-08L 不得包含 S01、审批、Worker/Team/YAML/MCP 修改、apply/delete、smoke、commit 或 push。
