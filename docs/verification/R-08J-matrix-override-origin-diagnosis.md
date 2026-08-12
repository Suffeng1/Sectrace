# R-08J Matrix Override 来源只读诊断

- 日期：2026-08-09
- 结论：`ROOT_CAUSE_CONFIRMED`
- 确认来源类别：`镜像默认`
- 输出边界：仅记录来源类别与抽象路径类型；不记录配置值、环境变量、凭据、Matrix 标识、日志或启动脚本内容

## 诊断范围

候选来源仅限：

1. Controller 生成
2. 镜像默认
3. 挂载模板
4. OpenClaw registry

本轮没有修改、移除或重启任何资源，没有发送 S01 或审批，没有 apply/delete，没有触碰 smoke，也没有 commit/push。

## 只读证据

### Docker 挂载拓扑

通过 Docker 服务端字段投影，仅检查预先确定的路径类别：

| 路径类别 | 挂载类型 |
| --- | --- |
| Manager workspace | bind |
| Manager config 子树的独立挂载 | 无 |
| configured plugin 扩展树 | 无 |
| bundled plugin 扩展树 | 无 |

因此：

- Manager 配置文件位于持久化 workspace bind 内；
- 旧 configured Matrix plugin 与 bundled Matrix plugin 都位于容器镜像文件系统，而不是独立 bind/volume 模板；
- configured plugin 的代码来源不是宿主机挂载模板。

### R-08I 重启反证

R-08I 已使用 OpenClaw 官方生命周期命令完成：

- dry-run 证明只移除 Matrix config entry；
- 实际命令确认 config entry 已移除；
- 插件文件被保留；
- Manager 重启后重复 plugin ID 警告重新出现。

OpenClaw 官方文档说明 uninstall 会移除 config entry、持久化插件索引记录以及关联 load-path 记录。直接 registry/config 关系已被删除但启动后重新出现，说明存量 registry 条目不是最终来源。

### 已安装插件事实

R-08H 的公开插件清单已经确认：

- 旧 configured Matrix plugin 属于镜像内的普通扩展树，版本落后于当前 OpenClaw core；
- bundled Matrix plugin 属于镜像内的 bundled/dist-runtime 扩展树；
- 两个入口哈希不同；
- 启动发现阶段由旧实现覆盖 bundled 实现。

本轮未再次读取完整插件 runtime JSON。

## 四类来源判定

| 候选类别 | 判定 | 依据 |
| --- | --- | --- |
| Controller 生成 | 排除为直接来源 | R-08I 只重启 Manager，没有执行 Controller apply/update；重复项仍由 Manager 冷启动恢复 |
| 镜像默认 | 确认 | 旧 configured plugin 位于非挂载的镜像扩展树；冷启动插件发现重新生成配置关系 |
| 挂载模板 | 排除为插件来源 | 两棵插件目录均没有 bind/volume 覆盖；workspace bind 只是生成配置的持久落点 |
| OpenClaw registry | 排除为最终来源 | 官方 uninstall 已移除 registry/config/load-path 关系；冷启动仍从镜像插件重新发现 |

## 有界不可用项

- 精确 `plugins inspect --runtime` 可能读取配置详情，因此未执行。
- Docker diff 路径元数据在 15 秒内超时，无输出后停止，未重试。
- 未读取启动脚本，因此不声称具体哪一行或哪个 bootstrap 函数执行了重新注册；这不影响来源类别判定。

## 根因

Manager 镜像同时包含旧 configured Matrix plugin 和当前 bundled Matrix plugin。冷启动插件发现会重新发现镜像默认扩展树中的旧实现，并在持久化 Manager workspace 中重建同 ID 的配置关系，导致旧实现覆盖 bundled 2026.4.14。

## 唯一最小修复授权建议

建议授权 R-08K，范围严格限定为：

1. 仅在 Manager 容器中把**镜像默认旧 Matrix 扩展目录**移动为同文件系统的禁用备份目录，不删除文件；
2. 再次使用官方命令仅移除由旧扩展生成的 Matrix config entry，保留文件；
3. 仅滚动重启 Manager 一次；
4. 仅验证三个脱敏布尔值：
   - bundled Matrix plugin 为唯一加载实现；
   - duplicate-warning 消失；
   - channel runtime / sync-ready 可由不含标识的安全状态接口确认；
5. 任一项失败立即停止，不发送 S01。

该授权不得包含 Worker/Team/YAML/MCP 修改、apply/delete、smoke、审批、S01、commit 或 push。

## 结论

`ROOT_CAUSE_CONFIRMED`

重新注入来源类别为：**镜像默认插件发现**。当前仍不可进入单次 S01 preflight，必须先完成单独授权的 R-08K。
