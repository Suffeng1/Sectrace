# R-08I Matrix Plugin 去重最小修复验证

- 日期：2026-08-09
- 结论：`NEEDS_AUTHORIZATION`
- 变更范围：仅移除 configured Matrix plugin override 的配置入口，并仅重启 Manager
- 安全边界：未发送或重试 S01，未审批，未 apply/delete，未修改 Worker/YAML/业务代码/MCP，未触碰 smoke，未读取或输出凭据、Matrix 标识、原始日志或启动脚本

## 官方机制确认

依据 OpenClaw 官方插件管理文档，`plugins uninstall <id> --keep-files` 会移除插件配置/注册关系并保留安装文件；插件变更后必须重启实际 Gateway。

本轮先执行只读 dry-run：

- 精确插件 ID：`matrix`
- dry-run 成功；
- 预览仅显示移除 config entry；
- 插件文件保持不变；
- 未显示其它插件或运行时资源变更。

## 执行结果

1. 执行 `openclaw plugins uninstall matrix --keep-files --force` 成功。
2. CLI 确认仅移除 Matrix plugin config entry，并要求重启 Gateway。
3. 仅对 Manager 容器执行一次滚动重启。
4. Manager 重启命令成功，容器恢复 running。
5. 重启后的第一个公开 OpenClaw health/help 初始化仍报告：
   - duplicate Matrix plugin ID：存在；
   - configured plugin 仍覆盖 bundled plugin。

这证明 config entry 的直接移除不是持久修复。Manager 启动期间存在更上游的配置/注册来源，会重新生成 configured Matrix override。

## 三布尔验收

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| channel online | 未安全取得 | `channels status --json` 和 `health --json` 包含完整 account/session 快照；在禁止读取 Matrix 标识的边界下未调用或解析 |
| sync-ready | 未安全取得 | 无不包含 account/标识的专用字段投影接口；未使用 credential probe |
| duplicate-warning 消失 | false | Manager 重启后公开 CLI 初始化仍稳定出现同一重复 ID 警告 |

`--probe` 会探测 channel credentials，因此未执行。完整 channel/health JSON 可能包含 Matrix account、recipient 或 session 信息，也未读取。

## 证据与反证

### 证据

- 官方 dry-run 与实际命令都确认直接 config entry 已被移除。
- Manager 只重启一次并恢复 running。
- 重启后重复警告重新出现，构成“启动期配置重新注入”的确定性信号。

### 反证

- 不能把 CLI 移除成功视为最终去重成功；重启后的运行态直接否定该结论。
- 不能声称 channel online 或 sync-ready，因为安全接口未提供所需的字段级投影。
- 不能进入单次 S01 preflight；重复插件与消费链状态仍未通过。

## 下一项精确授权

需要新的、单独授权的 R-08J：

1. 只读定位 Manager 启动期 Matrix plugin entry 的非敏感来源类别（Controller 生成、镜像默认、挂载模板或 OpenClaw registry），只输出来源类别和路径类型，不读取配置值、凭据、Matrix 标识或启动脚本正文；
2. 若来源唯一确认，再单独授权从该源移除重复 override；
3. 仅重启 Manager 一次；
4. 使用能够服务端投影的安全接口验证 online、sync-ready、duplicate-warning-absent 三个布尔值；
5. 三项全部为 true 后，才允许进入另行授权的单次 S01 preflight。

不得在 R-08J 中自动发送 S01、审批、修改 Worker/Team/MCP、处理 smoke、commit 或 push。

## 结论

`NEEDS_AUTHORIZATION`

当前不可进入单次 S01 preflight。
