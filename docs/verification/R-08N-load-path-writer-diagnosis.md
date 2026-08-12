# R-08N Stale Load Path 持续写入者诊断

- 日期：2026-08-09
- 结论：`ROOT_CAUSE_CONFIRMED`
- 唯一写入者类别：`mount watcher`（对象存储 workspace 同步客户端）
- 安全边界：仅进程角色、父子关系和来源类别；未读取或输出配置内容、环境变量、凭据、Matrix 标识、启动脚本、命令行参数或原始日志

## 进程树证据

Manager 容器的不含参数进程树只有以下运行角色：

1. PID 1：Manager supervisor
2. PID 1 的一个长期子进程：对象存储同步客户端

没有 OpenClaw gateway 进程，也没有独立 OpenClaw config watcher 进程。

更正说明：第一次 PID 查询因 PowerShell 保留变量名冲突导致父子字段无效；该次只保留“公开版本将 `mc` 识别为对象存储客户端”的有效事实。随后使用非保留变量重新查询，确认：

- 子进程角色：对象存储同步客户端
- 父进程：Manager PID 1 supervisor
- 工作目录类型：Manager workspace

三秒有界双采样中，同一个同步客户端进程持续存在，证明它不是一次性命令，而是长期 workspace watcher。

## 挂载关系证据

- Manager workspace：bind 挂载
- Controller 与 Manager 不共享该 workspace 的挂载源
- configured/bundled plugin 树均为 Manager 镜像文件系统

因此 Controller 不能通过共享文件系统直接重写 Manager workspace。

## 四类写入者判定

| 候选类别 | 判定 | 证据 |
| --- | --- | --- |
| Manager supervisor | 间接拥有 | PID 1 是同步客户端父进程，但没有证据表明 PID 1 自身直接写配置 |
| Controller reconciliation | 排除为直接写入者 | Controller 不共享 Manager workspace bind 源；R-08M 期间也没有 apply/update |
| mount watcher | **确认** | Manager supervisor 的长期对象存储同步子进程以 Manager workspace 为工作目录，并与 R-08M 的快速重新注入行为一致 |
| OpenClaw gateway watcher | 排除 | 当前 Manager 进程树中不存在 OpenClaw gateway；enable 命令也在 gateway 启动前的配置校验阶段失败 |

## 与 R-08M 的因果闭环

R-08M 已证明：

1. 旧 load-path 精确出现一次；
2. 本地结构化删除成功并即时验证为 0；
3. 未重启 Manager；
4. 下一条官方 CLI 命令前，旧路径已重新出现。

R-08N 证明同一时间存在唯一长期 workspace 同步客户端。它从上游权威副本恢复 Manager workspace，因此本地配置编辑会被覆盖。

## 唯一最小修复授权建议

建议 R-08O 分成严格的两阶段授权，避免复制或显示敏感配置：

### 阶段 A：权威副本的结构化不透明补丁

1. 仅暂停 Manager supervisor 下的精确 workspace 同步子进程，不停止 Controller、Worker、Team 或其它资源；
2. 使用同步客户端现有的本地运行上下文定位**权威对象的路径类型**，不输出对象名、alias、endpoint、凭据或配置内容；
3. 对权威对象在进程内执行结构化断言：旧 Matrix load-path 精确匹配 1 次；
4. 只删除该数组条目，不读取或修改其它值；
5. 将补丁后的同一对象写回原位置，不在聊天或仓库中落地配置副本；
6. 若不能在不暴露敏感配置的情况下完成，立即停止并由用户本人修改权威模板。

### 阶段 B：Manager 恢复

1. 让 workspace 从已修正的权威副本同步；
2. 仅执行一次 `openclaw plugins enable matrix`；
3. 仅重启 Manager 一次；
4. 复核 bundled-only、duplicate-warning-absent、channel-online、sync-ready 四项脱敏布尔；
5. 任一失败立即停止，不发送 S01。

该授权不得包含 S01、审批、Worker/Team/YAML/MCP 修改、apply/delete、smoke、commit 或 push。

## 结论

`ROOT_CAUSE_CONFIRMED`

唯一持续写入者类别是 Manager 内的对象存储 workspace mount watcher。当前不能进入单次 S01 preflight。
